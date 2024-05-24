import requests
from tkinter import Tk, Label, Button, filedialog, Text, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH, END
from tkinter import ttk
import threading

requests.packages.urllib3.disable_warnings()

class Amazon:
    def __init__(self, num):
        self.url = "https://www.amazon.in/ap/signin"
        self.num = num

    def check(self):
        cookies = {
            "session-id": "257-5137331-1235762",
            "session-id-time": "2082787201l",
            "i18n-prefs": "INR",
            "csm-hit": "tb:KRSBW0V2ACBM980J65Q5+s-BF3ZD7MVBT0TT71A1VYP|1716399112161&t:1716399112161&adb:adblk_no",
            "ubid-acbin": "261-5105569-2756438",
            "session-token": "\"tyoeHgowknphx0Y/CBaiVwnBiwbhUb1PRTvQZQ+07Tq9rmkRD6bErsUDwgq6gu+tA53K6WEAMwOb3pN4Ti3PSFoo+I/Jt5qIEDEMHIeRo1CrE264ogGDHsjge/CwWUZ9bVZtbo32ej/ZPQdm8bYeu6TQhca+UH7Wm9OOwBGoPl7dfoUk79QLYEz69Tt3ik4zMJom8jfgI227qMPuaMaAsw==\""
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "DNT": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.amazon.in",
            "Connection": "close",
            "X-Forwarded-For": "127.0.0.1",
            "Referer": "https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        data = {
            "appActionToken": "aQoJnNOhIEqKqS6j2FeUcqjNASM4oj3D",
            "appAction": "SIGNIN_PWD_COLLECT",
            "subPageType": "SignInClaimCollect",
            "openid.return_to": "ape:aHR0cHM6Ly93d3cuYW1hem9uLmluLz9yZWZfPW5hdl95YV9zaWduaW4=",
            "prevRID": "ape:RTQ5MDBNTjBIMFhTM1NETjBNRzc=",
            "workflowState": "eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0.rDtIJvH94wJZNbT4IDcXaf1AzHHO5IfBNrTeyypVNQtp4CUZy8VV9A.NX4lP9WdTPXMcvdJ.3tkO-V5-1UrGB_vPd4lSOq1dccSSSyK0MX8bhbmphqYZFhssQSF6f5X0LojX2v1YVbRZoh2VgYFL1vMAl06U0HQcin3ccNFrNvLz7GYtjomj-kyNbD1hq9430zS4SqsrqhW2uAiha5ZaURVuXorj5OwHM5X-KI6OMKjohvbPlHT0Lf4bKmdmET64gUAW2tlr9NIwVd7djJ6YoTTDbUzjZlCO0RHLIM6yhzTkw3FUrhizuUNgdNupF9xXb9x-a_KVm9jyUn326QR6hYWO0F94zAtEKu-vq2bkLIC2IVdffg95v8ffxMOMgjSR1hhIm5fruXaXDNiyw1gJp4c19ylAtmU60WVPct1_76UdfD0jAArupD0HZnjsAil3lTfkQY4LB28UINKgYS23BrqWDkF_EHnWHPfwq2CLYrGaWo03Kgl_PY8LEjm73Rqf5O9pJTggtpsODTnMUMO2vrGhK6uWYBeXRmKxBOXPaezNoLRyIV2hknwa8wUsmxw5.laXYuNSbhLg4GN3MZpD8GA",
            "email": self.num,
            "password": '',
            "create": "0",
            "metadata1": "ECdITeCs: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"
        }
        res = requests.post(self.url, headers=headers, cookies=cookies, data=data).text

        if "ap_change_login_claim" in res:
            return True, res
        elif "There was a problem" in res:
            return False, res
        else:
            return False, res

def fun_action(num, text_widget):
    num = num.strip()
    if num.isnumeric() and "+" not in num:
        num = "+%s" % num
    while True:
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

def main(emails, text_widget):
    threads = []
    for email in emails:
        thread = threading.Thread(target=fun_action, args=(email, text_widget))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        with open(filename, "r", encoding="Latin-1") as file:
            emails = file.read().splitlines()
            result_text.delete(1.0, END)
            threading.Thread(target=main, args=(emails, result_text)).start()

root = Tk()
root.title("Amazon Email Checker")

style = ttk.Style()
style.theme_use("clam")

style.configure("TButton", font=("Helvetica", 12), background="#4CAF50", foreground="white", padding=10)
style.map("TButton", background=[("active", "#45a049")])

style.configure("TLabel", font=("Helvetica", 16), padding=10)
style.configure("TFrame", background="#f2f2f2")

frame = ttk.Frame(root, padding="10")
frame.pack(fill="both", expand=True)

label = ttk.Label(frame, text="Amazon Email Checker")
label.pack(pady=10)

button = ttk.Button(frame, text="Browse Email List", command=browse_file)
button.pack(pady=10)

result_frame = ttk.Frame(frame)
result_frame.pack(fill="both", expand=True)

scrollbar = Scrollbar(result_frame, orient=VERTICAL)
result_text = Text(result_frame, height=20, width=50, yscrollcommand=scrollbar.set, wrap="none", font=("Helvetica", 12), bg="#e0e0e0", fg="#000")
scrollbar.config(command=result_text.yview)
scrollbar.pack(side=RIGHT, fill=Y)
result_text.pack(side=LEFT, fill=BOTH, expand=True)

root.mainloop()
