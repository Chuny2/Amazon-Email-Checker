import sys
import threading
import time
import random
from queue import Queue
from threading import Event
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from amazon_auth import Amazon
from phone_number_generator import format_phone_number, get_country_config, feistel_shuffle, get_feistel_params
from utils_io import stream_file_lines, ThreadSafeWriter
from constants import MAX_CORES, MAX_PREFIXES, MAX_PREFIX_LENGTH, QUEUE_MAX_SIZE, COUNTRY_NAME_TO_REGION

def on_browse_email_file(result_text, stop_event, core_entry, signals):
    """Browse and load email list from a file and start checking.
    
    Args:
        result_text (QTextBrowser): Text browser for displaying results.
        stop_event (Event): Event to signal stop.
        core_entry (QLineEdit): Entry for number of cores.
        signals (Signals): Signal object for UI updates.
    """
    filename = QFileDialog.getOpenFileName(filter="Text files (*.txt)")[0]
    if not filename:
        return
        
    try:
        with open(filename, "r", errors="ignore") as f:
            pass
        emails = stream_file_lines(filename)
    except Exception as e:
        QMessageBox.critical(None, "File Error", f"Could not access file: {e}")
        return

    result_text.clear()
    stop_event.clear()

    try:
        num_cores = int(core_entry.text())
        if num_cores < 1:
            raise ValueError("The number of threads must be at least 1.")
        if num_cores > MAX_CORES:
            raise ValueError(f"The number of threads cannot exceed {MAX_CORES}.")
        
        threading.Thread(
            target=check_email_list,
            args=(emails, signals, stop_event, num_cores),
            daemon=True
        ).start()
    except ValueError as e:
        QMessageBox.critical(None, "Invalid Input", str(e))

def on_generate_phones_clicked(result_text, stop_event, core_entry, country_combobox, prefix_entry, country_data, signals):
    """UI entry point for phone number generation and checking.
    
    Args:
        result_text (QTextBrowser): Text browser for displaying results.
        stop_event (Event): Event to signal stop.
        core_entry (QLineEdit): Entry for number of cores.
        country_combobox (QComboBox): ComboBox for selecting country.
        prefix_entry (QLineEdit): Entry for prefix.
        country_data (dict): Dictionary of country data.
        signals (Signals): Signal object for UI updates.
    """
    result_text.clear()
    stop_event.clear()
    try:
        num_cores = int(core_entry.text())
        if hasattr(country_combobox, 'currentCountryName'):
            country_name = country_combobox.currentCountryName()
        else:
            country_name = country_combobox.currentText()
            
        raw_prefix = prefix_entry.text().strip()
        prefix = [p.strip() for p in raw_prefix.split(',') if p.strip()] if ',' in raw_prefix else (raw_prefix if raw_prefix else None)
        
        if num_cores < 1:
            raise ValueError("The number of threads must be at least 1.")
        if num_cores > MAX_CORES:
            raise ValueError(f"The number of threads cannot exceed {MAX_CORES}.")

        # Prefix validation
        prefixes_to_check = prefix if isinstance(prefix, list) else ([prefix] if prefix else [])
        if len(prefixes_to_check) > MAX_PREFIXES:
            raise ValueError(f"Too many prefixes. Maximum allowed is {MAX_PREFIXES}.")
        for p in prefixes_to_check:
            if len(p) > MAX_PREFIX_LENGTH:
                raise ValueError(f"Prefix '{p}' is too long. Max length is {MAX_PREFIX_LENGTH}.")
            if not p.isdigit():
                raise ValueError(f"Prefix '{p}' contains invalid characters. Digits only.")

        if not country_name:
            raise ValueError("Please select a country.")
        
        if country_name not in COUNTRY_NAME_TO_REGION:
            raise ValueError(f"Selected country '{country_name}' is not recognized.")

        region = COUNTRY_NAME_TO_REGION[country_name]
        threading.Thread(
            target=check_phone_range,
            args=(signals, stop_event, num_cores, region, country_name, prefix),
            daemon=True
        ).start()
    except (ValueError, KeyError) as e:
        QMessageBox.critical(None, "Invalid Input", str(e))

def cancel_operations(stop_event):
    """Cancel ongoing operations and signal threads to stop.
    
    Args:
        stop_event (Event): Event to signal stop.
    """
    stop_event.set()
    print("[!] Cancellation signaled...")

def on_closing(root, stop_event):
    """Handle the closing of the application.
    
    Args:
        root (tk.Tk): The main application window.
        stop_event (Event): Event to signal stop.
    """
    cancel_operations(stop_event)
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            thread.join(timeout=1.0)
    sys.exit()

def verify_amazon_identifier(identifier, stop_event: Event | None = None):
    """Check if a number or email is valid on Amazon.
    
    Args:
        identifier (str): The identifier to check.
        stop_event (Event | None, optional): Event to signal stop. Defaults to None.
    
    Returns:
        tuple: A tuple containing the identifier, validation result, and error message.
    """
    try:
        if stop_event and stop_event.is_set():
            return (identifier, None, "Cancelled")
        is_valid, _ = Amazon(identifier).verify()
        return (identifier, is_valid, None)
    except Exception as e:
        return (identifier, None, str(e))

def _run_checker_engine(identifier_stream, signals, stop_event, num_cores, output_filename):
    """Run the checker engine.
    
    Args:
        identifier_stream (iterable): Stream of identifiers to process.
        signals (Signals): Signal object for UI updates.
        stop_event (Event): Event to signal stop.
        num_cores (int): Number of cores to use.
        output_filename (str): Output file name.
    """
    work_queue = Queue(maxsize=QUEUE_MAX_SIZE)
    
    stats = {
        "valid": 0,
        "error": 0,
        "processed": 0,
        "start_time": time.time()
    }
    lock = threading.Lock()

    def consumer(writer):
        while not stop_event.is_set():
            try:
                identifier = work_queue.get(timeout=0.2)
                if identifier is None: 
                    break
                
                ident, is_valid, error = verify_amazon_identifier(identifier, stop_event)
                
               
                if stop_event.is_set():
                    break

                with lock:
                    stats["processed"] += 1
                    if error:
                        if error != "Cancelled":
                            stats["error"] += 1
                            signals.append_text.emit(f"[!] Error ==> {error}")
                    elif is_valid:
                        stats["valid"] += 1
                        signals.append_text.emit(f"[+] Yes ==> {ident}")
                        writer.write(ident)
                    else:
                        signals.append_text.emit(f"[-] No ==> {ident}")
                    
                    if stats["processed"] % 50 == 0:
                        elapsed = time.time() - stats["start_time"]
                        rate = stats["processed"] / elapsed if elapsed > 0 else 0
                        signals.append_text.emit(f"[*] Progress: {stats['processed']} checked | Valid: {stats['valid']} | Rate: {rate:.2f}/s")
            except Exception as e:
                # Ignore Queue.Empty timeouts, but catch real errors
                if not stop_event.is_set() and not str(e).strip() == "":
                    signals.append_text.emit(f"[!] Worker Error: {e}")
                continue

    # Initialize concurrency
    with ThreadSafeWriter(output_filename) as shared_writer:
        # 1. Start Workers
        worker_threads = []
        for _ in range(num_cores):
            t = threading.Thread(target=consumer, args=(shared_writer,), daemon=True)
            t.start()
            worker_threads.append(t)

        # 2. Producer Logic
        try:
            for item in identifier_stream:
                if stop_event.is_set():
                    break
                while not stop_event.is_set():
                    try:
                        work_queue.put(item, timeout=0.1)
                        break
                    except:
                        continue
        except Exception as e:
            signals.append_text.emit(f"[!] Stream Error: {e}")
        finally:
            # 3. Shutdown Sequence
            if stop_event.is_set():
                try:
                    while not work_queue.empty():
                        work_queue.get_nowait()
                except: pass

            for _ in range(num_cores):
                try: work_queue.put(None, timeout=0.05)
                except: break

            #  Parallel wait with a logic-based deadline
            if stop_event.is_set():
                # If canceling, give workers a tiny window to abort, then move on
                deadline = time.time() + 0.5 
                for t in worker_threads:
                    remaining = deadline - time.time()
                    if remaining > 0:
                        t.join(timeout=remaining)
            else:
                # If finishing naturally, we MUST wait for every worker to hit a None sentinel.
                # This guarantees the "Completed" message is truly at the end.
                for t in worker_threads:
                    t.join() 


    # Final Stats
    elapsed_time = time.time() - stats["start_time"]
    rate = stats["processed"] / elapsed_time if elapsed_time > 0 else 0
    signals.append_text.emit(f"[*] Completed: {stats['processed']} total, {stats['valid']} valid, {rate:.2f} items/s")

def check_email_list(emails, signals, stop_event, num_cores):
    """Processes a list of emails using the unified engine.
    
    Args:
        emails (iterable): Stream of emails to process.
        signals (Signals): Signal object for UI updates.
        stop_event (Event): Event to signal stop.
        num_cores (int): Number of cores to use.
    """
    _run_checker_engine(emails, signals, stop_event, num_cores, "Valid.txt")

def check_phone_range(signals, stop_event, num_cores, region, country_name, prefix=None):
    """Processes a generated range of phone numbers using the unified engine.
    
    Args:
        signals (Signals): Signal object for UI updates.
        stop_event (Event): Event to signal stop.
        num_cores (int): Number of cores to use.
        region (str): Region of the country.
        country_name (str): Name of the country.
        prefix (str, optional): Prefix to use. Defaults to None.
    """
    config = get_country_config(region, prefix)
    range_limit = config[0]
    
    if range_limit <= 0:
        signals.append_text.emit("[!] Error: No valid range for this country/prefix.")
        return

    # Encapsulated Feistel logic
    num_bits, half_bits, mask = get_feistel_params(range_limit)
    session_seed = random.randint(0, 10**9)

    def phone_generator():
        for i in range(range_limit):
            if stop_event.is_set():
                break
            idx = feistel_shuffle(i, range_limit, session_seed, num_bits, half_bits, mask)
            yield format_phone_number(idx, config)

    _run_checker_engine(phone_generator(), signals, stop_event, num_cores, f"Valid_{country_name}.txt")