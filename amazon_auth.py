
import requests
from bs4 import BeautifulSoup
import threading

class Amazon:
    _session = requests.Session()
    _login_params = None
    _lock = threading.Lock()

    @classmethod
    def initialize_session(cls):
        """Initialize the session and fetch login parameters once at program start"""
        with cls._lock:
            if cls._login_params is None:
                print("[DEBUG] Initializing Amazon session and fetching login parameters...")
                instance = cls.__new__(cls) 
                cls._login_params = instance._fetch_login_params()
                print("[DEBUG] Login parameters successfully initialized!")
            else:
                print("[DEBUG] Login parameters already initialized, skipping...")

    
    def __init__(self, num):
        self.url = "https://www.amazon.com/ap/signin"
        self.num = num
       


    def _fetch_login_params(self):
        signin_url = (
            "https://www.amazon.com/ap/signin"
            "?openid.pape.max_auth_age=0"
            "&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fcss%2Fhomepage.html%3Fref_%3Dnav_ya_signin"
            "&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
            "&openid.assoc_handle=usflex"
            "&openid.mode=checkid_setup"
            "&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
            "&openid.ns=http://specs.openid.net/auth/2.0"
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Referer": "https://www.amazon.com/gp/css/homepage.html",
        }
        r = Amazon._session.get(signin_url, headers=headers, timeout=20)

        cookies = Amazon._session.cookies.get_dict()
        session_id = cookies.get("session-id")
        session_id_time = cookies.get("session-id-time")

        soup = BeautifulSoup(r.text, "html.parser")
        return {
            "session_id": session_id,
            "session_id_time": session_id_time,
            "workflowState": soup.find("input", {"name": "workflowState"})["value"],
            "appActionToken": soup.find("input", {"name": "appActionToken"})["value"],
            "appAction": soup.find("input", {"name": "appAction"})["value"],
        }


    def check(self):
        # Ensure login parameters are available
        if Amazon._login_params is None:
            raise RuntimeError("Amazon session not initialized! Call Amazon.initialize_session() first.")
            
        cookies = {
            "session-id": Amazon._login_params["session_id"],
            "session-id-time": Amazon._login_params["session_id_time"],
            "i18n-prefs": "USD",
            "csm-hit": "tb:Q76FPDADJWBXBDM2Z676+s-4PKF6AMM1FK89W6MZYX9|1716574702794&t:1716574702794&adb:adblk_yes",
            "ubid-main": "131-2205767-2293117",
            "session-token": "2bpZkWCCLpCI1rzdxMVY8EcbBTPY7in8WG6wTURWnddB6WmUjYdMO88o7HQXtea5BHUye+6Pqnzimq6JrrB+R8cmMcoD31RFxypnO9TqgCLt9aKiqdtBF2yXQ/4ga/+4zTdKBxIuRa8ALDPIj838yW89GMkfcEw4OYSctpIdvpBMyo4Jygf+pxOIOPpSnu2EP+VOytmyisRsDCTzG4ai+ALwSlesIUQzdSS4/lyGHv+XQFa2MaDQu4EyH1G4QyV9IOKPuc0W68N6RQp2SBqS4n+4F77Kg4h+qzh8wu4Ek0N/N2QTWvUb5ylnVroxq55xpEXcLV7wQwq+Uifs6HjlUqdfZBkxWZtm"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        }
        data = {
            "appActionToken": Amazon._login_params["appActionToken"],
            "appAction": "SIGNIN_PWD_COLLECT",
            "workflowState": Amazon._login_params["workflowState"],
            "email": self.num,
            "password": '',
 
        }

        proxies = {
            "http": "http://127.0.0.1:8080",
            "https": "http://127.0.0.1:8080"
        }

        res = requests.post(self.url, headers=headers, cookies=cookies, data=data, proxies=proxies, verify=False).text

        if "ap_change_login_claim" in res or "auth-email-claim" in res or "auth-password-claim" in res:
            return True, res
        elif "There was a problem" in res:
            return False, res
        else:
            return False, res