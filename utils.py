"""
Utility functions for Amazon Email Checker.
Contains the core functionality for checking emails and phone numbers.
"""
import sys
import threading
import time
from queue import Queue
from threading import Event
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from concurrent.futures import ThreadPoolExecutor, as_completed
from amazon_auth import Amazon
from phone_number_generator import generate_phone_number
from utils_io import safe_read_from_file, safe_write_to_file

# Constants for memory management
MAX_SET_SIZE = 100000  # Max numbers to store in memory
QUEUE_MAX_SIZE = 500   # Max numbers in working queue
CLEAR_THRESHOLD = 10000  # When to clear duplicates cache

def browse_file(result_text, stop_event, core_entry, signals):
    """Browse and load email list from a file."""
    filename = QFileDialog.getOpenFileName(filter="Text files (*.txt)")[0]
    if not filename:
        return
        
    emails = safe_read_from_file(filename)
    result_text.clear()
    stop_event.clear()
    
    try:
        num_cores = int(core_entry.text())
        if num_cores < 1:
            raise ValueError("The number of cores must be at least 1.")
        threading.Thread(
            target=main,
            args=(emails, signals, stop_event, num_cores),
            daemon=True
        ).start()
    except ValueError as e:
        QMessageBox.critical(None, "Invalid Input", str(e))

def generate_numbers(result_text, stop_event, core_entry, country_combobox, country_codes, signals):
    """Generate and check phone numbers for the selected country."""
    result_text.clear()
    stop_event.clear()
    try:
        num_cores = int(core_entry.text())
        country_name = country_combobox.currentText()
        if num_cores < 1:
            raise ValueError("The number of cores must be at least 1.")
        if not country_name:
            raise ValueError("Please select a country.")
        country_code = country_codes[country_name]
        threading.Thread(
            target=generate_and_check_numbers,
            args=(signals, stop_event, num_cores, country_code),
            daemon=True
        ).start()
    except ValueError as e:
        QMessageBox.critical(None, "Invalid Input", str(e))

def cancel_operations(stop_event):
    """Cancel ongoing operations."""
    if stop_event:
        stop_event.set()

def on_closing(root, stop_event):
    """Handle the closing of the application."""
    cancel_operations(stop_event)
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            thread.join(timeout=1.0)  # Add timeout to prevent hanging
    root.destroy()
    sys.exit()

def worker_amazon_check(number, stop_event: Event | None = None):
    """Check if a number or email is valid on Amazon.

    Returns a tuple: (number, is_valid, error)
    """
    try:
        # Cooperative cancellation before starting any network work
        if stop_event and stop_event.is_set():
            return (number, None, "Cancelled")

        # Do not pass stop_event into Amazon.check to match current signature
        is_valid, _ = Amazon(number).check()
        return (number, is_valid, None)
    except Exception as e:
        return (number, None, str(e))

def generate_and_check_numbers(signals, stop_event, num_cores, country_code):
    """Generate and check phone numbers with continuous processing pipeline."""
    # Use a bounded set with max size to prevent memory issues
    generated_numbers = set()
    
    # Shared work queue between producer and consumer
    work_queue = Queue(maxsize=QUEUE_MAX_SIZE)
    
    # Control flags
    producer_done = Event()
    
    # Statistics for dynamic optimization
    valid_count = 0
    error_count = 0
    processed_count = 0
    start_time = time.time()
    
    # Number producer
    def number_producer():
        try:
            while not stop_event.is_set():
                number = generate_phone_number(country_code)
                
                # Prevent unlimited growth of the set
                if len(generated_numbers) >= MAX_SET_SIZE:
                    # Remove oldest entries if needed
                    if len(generated_numbers) % CLEAR_THRESHOLD == 0:
                        # This is an approximate way to trim the set
                        generated_numbers.clear()
                        
                if number in generated_numbers:
                    continue
                    
                generated_numbers.add(number)
                work_queue.put(number)
                
                # Dynamic sleep based on queue fullness to balance CPU usage
                sleep_time = 0.01 if work_queue.qsize() > 400 else 0.001
                if len(generated_numbers) % 50 == 0:
                    time.sleep(sleep_time)
        finally:
            producer_done.set()
            # End signal for consumers
            for _ in range(num_cores):
                work_queue.put(None)
    
    # Number consumer/verifier
    def number_consumer():
        nonlocal valid_count, error_count, processed_count
        
        while not (producer_done.is_set() and work_queue.empty()) and not stop_event.is_set():
            try:
                number = work_queue.get(timeout=1.0)
                if number is None:  # End signal
                    break
                
                result = worker_amazon_check(number, stop_event)
                num, is_valid, error = result
                
                processed_count += 1
                if error:
                    error_count += 1
                    signals.append_text.emit(f"[!] Error ==> {error}")
                elif is_valid:
                    valid_count += 1
                    signals.append_text.emit(f"[+] Yes ==> {num}")
                    safe_write_to_file(f"Valid_{country_code}.txt", num)
                else:
                    signals.append_text.emit(f"[-] No ==> {num}")
                
                # Progress report at regular intervals
                if processed_count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    rate = processed_count / elapsed_time if elapsed_time > 0 else 0
                    progress = f"[*] Progress: {processed_count} numbers processed (Valid: {valid_count}, Errors: {error_count}, Rate: {rate:.2f} num/s)"
                    signals.append_text.emit(progress)
                    
            except Exception as e:
                if not stop_event.is_set():
                    signals.append_text.emit(f"[!] Consumer error ==> {str(e)}")
    
    # Start producer and consumer threads
    threading.Thread(target=number_producer, daemon=True).start()
    
    # Consumer thread pool
    consumer_threads = []
    for _ in range(num_cores):
        t = threading.Thread(target=number_consumer, daemon=True)
        t.start()
        consumer_threads.append(t)
    
    # Wait for all consumer threads to finish
    for t in consumer_threads:
        t.join()
    
    elapsed_time = time.time() - start_time
    rate = processed_count / elapsed_time if elapsed_time > 0 else 0
    signals.append_text.emit(f"[*] Completed: {processed_count} numbers processed, {valid_count} valid, {rate:.2f} num/s")

def main(emails, signals, stop_event, num_cores):
    """Main function to check emails with cooperative cancellation.

    Ensures that when stop_event is set, pending futures are cancelled and we do not
    wait for the entire pool to finish.
    """
    executor = ThreadPoolExecutor(max_workers=num_cores)
    try:
        futures = [executor.submit(worker_amazon_check, email, stop_event) for email in emails]

        for future in as_completed(futures):
            # If user requested cancellation, stop submitting/processing and cancel pending
            if stop_event.is_set():
                for f in futures:
                    f.cancel()
                # Do not wait for running tasks; cancel those not started
                executor.shutdown(wait=False, cancel_futures=True)
                return

            num, is_valid, error = future.result()
            if error:
                # Suppress noisy log on cooperative cancel
                if error != "Cancelled":
                    signals.append_text.emit(f"[!] Error ==> {error}")
            elif is_valid:
                safe_write_to_file("Valid.txt", num)
                signals.append_text.emit(f"[+] Yes ==> {num}")
            else:
                signals.append_text.emit(f"[-] No ==> {num}")
    finally:
        # Best-effort fast shutdown; if already shut down above, this is a no-op
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass