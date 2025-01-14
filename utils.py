import sys
import threading
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from concurrent.futures import ThreadPoolExecutor, as_completed
from amazon_auth import Amazon  # Updated import
from phone_number_generator import generate_phone_number

def browse_file(result_text, stop_event, core_entry, signals):
    """Browse and load email list from a file."""
    filename = QFileDialog.getOpenFileName(filter="Text files (*.txt)")[0]
    if filename:
        with open(filename, "r", encoding="Latin-1") as file:
            emails = file.read().splitlines()
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
            thread.join()
    root.destroy()
    sys.exit()

def worker_amazon_check(number):
    try:
        is_valid, _ = Amazon(number).check()
        return (number, is_valid, None)
    except Exception as e:
        return (number, None, str(e))

def generate_and_check_numbers(signals, stop_event, num_cores, country_code):
    """Generate and check phone numbers in batches."""
    generated_numbers = set()
    total_numbers = 1000
    batch_size = 100

    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        try:
            while len(generated_numbers) < total_numbers and not stop_event.is_set():
                batch_generated = 0
                while batch_generated < batch_size and len(generated_numbers) < total_numbers:
                    number = generate_phone_number(country_code)
                    if number in generated_numbers:
                        continue
                    generated_numbers.add(number)
                    futures.append(executor.submit(worker_amazon_check, number))
                    batch_generated += 1

                for future in as_completed(futures):
                    if stop_event.is_set():
                        break
                    num, is_valid, error = future.result()
                    if error:
                        signals.append_text.emit(f"[!] Error ==> {error}")
                    elif is_valid:
                        signals.append_text.emit(f"[+] Yes ==> {num}")
                        with open(f"Valid_{country_code}.txt", "a") as f:
                            f.write(f"{num}\n")
                    else:
                        signals.append_text.emit(f"[-] No ==> {num}")
                futures.clear()
        finally:
            executor.shutdown(wait=True, cancel_futures=True)

def main(emails, signals, stop_event, num_cores):
    """Main function to check emails."""
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(worker_amazon_check, email) for email in emails]
        for future in as_completed(futures):
            if stop_event.is_set():
                break
            num, is_valid, error = future.result()
            if error:
                signals.append_text.emit(f"[!] Error ==> {error}")
            elif is_valid:
                with open("Valid.txt", "a") as f:
                    f.write(f"{num}\n")
                signals.append_text.emit(f"[+] Yes ==> {num}")
            else:
                signals.append_text.emit(f"[-] No ==> {num}")