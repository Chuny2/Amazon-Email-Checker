
import requests
import json
import re
import urllib3
from bs4 import BeautifulSoup

# Stop urllib3 from complaining about insecure requests (mostly for proxy stuff)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Switch this to True if you're using something like Burp or a local proxy
USE_PROXIES = False 

class Amazon:

    def __init__(self, num):
        self.url = "https://www.amazon.com/ap/signin"
        self.num = num

    def verify(self):
        # Default local proxy settings
        proxies = {
            "http": "http://127.0.0.1:8080",
            "https": "http://127.0.0.1:8080",
        }
        
        # This is the long URL Amazon uses to start the login flow
        signin_url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fcss%2Fhomepage.html%3Fref_%3Dnav_ya_signin&openid.identity=http://specs.openid.net/auth/2.0/identifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.ns=http://specs.openid.net/auth/2.0"
        
        s = requests.Session()
        
        if USE_PROXIES:
            s.proxies.update(proxies)
        
        s.verify = False # Ignore SSL errors

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Referer": "https://www.amazon.com/gp/css/homepage.html"
        }
        
        # Load the sign-in page first to get the tokens
        r = s.get(signin_url, headers=headers, timeout=20)

        # Scrape the page for all the hidden inputs and tokens
        soup = BeautifulSoup(r.text, "html.parser")
        get_val = lambda n: (soup.find("input", {"name": n}) or {}).get("value")
        cookies = s.cookies.get_dict()

        # These values are required for the POST request to work
        hidden = {k: get_val(k) for k in ["workflowState", "appActionToken", "appAction", "subPageType", "prevRID", "openid.return_to", "create"]}

        # Attempt to find tracking metadata and UE variables from scripts
        m1 = soup.find("input", {"name": "metadata1"})
        fwcim_blob = (m1["value"] if m1 and m1.get("value") not in (None, "true") else None)
        
        script = soup.find("script", string=re.compile(r"ue_mid\s*="))
        js = script.string if script and script.string else (script.get_text() if script else "")
        
        rx = lambda pat: (re.search(pat, js).group(1) if re.search(pat, js) else None)
        ue_mid, ue_id, ue_sid, ue_pty = rx(r"ue_mid\s*=\s*'([^']+)'"), rx(r"ue_id\s*=\s*'([^']+)'"), rx(r"ue_sid\s*=\s*'([^']+)'"), rx(r'ue_pty\s*=\s*"([^"]+)"')

        # Build the JSON payload for Amazon's verification endpoint
        client_data = {
            "sessionId": ue_sid or cookies.get("session-id"),
            "marketplaceId": ue_mid or "ATVPDKIKX0DER",
            "rid": ue_id or r.headers.get("X-Amz-Rid"),
            "ubid": cookies.get("ubid-main", ""),
            "pageType": ue_pty,
            "appAction": hidden["appAction"] or "SIGNIN_PWD_COLLECT",
            "subPageType": hidden["subPageType"] or "SignInClaimCollect"
        }
        
        options = {
            "clientData": json.dumps(client_data, separators=(",", ":")),
            "challengeType": None,
            "locale": "en-US",
            "externalId": None,
            "enableHeaderFooter": True,
            "enableBypassMechanism": False,
            "enableModalView": False,
            "eventTrigger": "PageLoad",
            "aaExternalToken": None,
            "forceJsFlush": True,
            "aamationToken": None
        }

        # Send the internal verification request that usually happens via JS
        post_headers = {**headers, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://www.amazon.com", "Referer": r.url}
        resp = s.post(
            "https://www.amazon.com/aaut/verify/ap", 
            params={"options": json.dumps(options, separators=(",", ":"))}, 
            data=json.dumps({"context": None, "options": json.dumps(options, separators=(",", ":")), "fwcimBlob": fwcim_blob}), 
            headers=post_headers, 
            timeout=20
        )

        # Pull the session token out of the custom header
        session_token = None
        if resp.headers.get("amz-aamation-resp"):
            try:
                aamation_data = json.loads(resp.headers.get("amz-aamation-resp"))
                session_token = aamation_data.get("clientSideContext")
                if not session_token and aamation_data.get("sessionToken"):
                    session_token_data = json.loads(aamation_data.get("sessionToken"))
                    # debug output just in case
                    print(f"Validation ID: {session_token_data.get('uniqueValidationId')}")
            except json.JSONDecodeError:
                print("Failed to parse the amz-aamation-resp header")

        # Now we try to login with the phone number
        signin_data = {
            "appActionToken": hidden["appActionToken"],
            "appAction": "SIGNIN_PWD_COLLECT",
            "subpageType": hidden["subPageType"],
            "prevRID": hidden["prevRID"],
            "workflowState": hidden["workflowState"],
            "session-token": session_token,
            "email": self.num,
            "password": '' # we don't need a real password to check if the account exists
        }
        
        signin_cookies = {
            "ubid-main": cookies.get("ubid-main", ""),
            "session-id": cookies.get("session-id"),
            "session-id-time": cookies.get("session-id-time"),
            "i18n-prefs": "USD"
        }
        
        response = requests.post(
            "https://www.amazon.com/ap/signin", 
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}, 
            cookies=signin_cookies, 
            data=signin_data, 
            proxies=proxies if USE_PROXIES else None, 
            verify=False
        ).text

        # If we see these strings, it means Amazon recognized the account and is asking for more info
        if "ap_change_login_claim" in response or "auth-email-claim" in response or "auth-password-claim" in response:
            return True, response
        elif "There was a problem" in response:
            return False, response
        else:
            return False, response