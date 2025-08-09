
import requests
import json
import re
from bs4 import BeautifulSoup


class Amazon:


    
    def __init__(self, num):
        self.url = "https://www.amazon.com/ap/signin"
        self.num = num
       




    def check(self):
        signin_url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fcss%2Fhomepage.html%3Fref_%3Dnav_ya_signin&openid.identity=http://specs.openid.net/auth/2.0/identifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.ns=http://specs.openid.net/auth/2.0"
        s = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0", "Referer": "https://www.amazon.com/gp/css/homepage.html"}
        r = s.get(signin_url, headers=headers, timeout=20)

        # Parse page data
        soup = BeautifulSoup(r.text, "html.parser")
        get_val = lambda n: (soup.find("input", {"name": n}) or {}).get("value")
        cookies = s.cookies.get_dict()

        # Extract hidden form fields
        hidden = {k: get_val(k) for k in ["workflowState", "appActionToken", "appAction", "subPageType", "prevRID", "openid.return_to", "create"]}

        # Extract metadata and JS variables
        m1 = soup.find("input", {"name": "metadata1"})
        fwcim_blob = (m1["value"] if m1 and m1.get("value") not in (None, "true") else None)
        script = soup.find("script", string=re.compile(r"ue_mid\s*="))
        js = script.string if script and script.string else (script.get_text() if script else "")
        rx = lambda pat: (re.search(pat, js).group(1) if re.search(pat, js) else None)
        ue_mid, ue_id, ue_sid, ue_pty = rx(r"ue_mid\s*=\s*'([^']+)'"), rx(r"ue_id\s*=\s*'([^']+)'"), rx(r"ue_sid\s*=\s*'([^']+)'"), rx(r'ue_pty\s*=\s*"([^"]+)"')

        # Prepare client data and options
        client_data = {"sessionId": ue_sid or cookies.get("session-id"), "marketplaceId": ue_mid or "ATVPDKIKX0DER", "rid": ue_id or r.headers.get("X-Amz-Rid"), "ubid": cookies.get("ubid-main", ""), "pageType": ue_pty, "appAction": hidden["appAction"] or "SIGNIN_PWD_COLLECT", "subPageType": hidden["subPageType"] or "SignInClaimCollect"}
        options = {"clientData": json.dumps(client_data, separators=(",", ":")), "challengeType": None, "locale": "en-US", "externalId": None, "enableHeaderFooter": True, "enableBypassMechanism": False, "enableModalView": False, "eventTrigger": "PageLoad", "aaExternalToken": None, "forceJsFlush": True, "aamationToken": None}

        # Post to verification endpoint
        post_headers = {**headers, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://www.amazon.com", "Referer": r.url}
        resp = s.post("https://www.amazon.com/aaut/verify/ap", params={"options": json.dumps(options, separators=(",", ":"))}, data=json.dumps({"context": None, "options": json.dumps(options, separators=(",", ":")), "fwcimBlob": fwcim_blob}), headers=post_headers, timeout=20)

        # Extract session token from response
        session_token = None
        if resp.headers.get("amz-aamation-resp"):
            try:
                aamation_data = json.loads(resp.headers.get("amz-aamation-resp"))
                session_token = aamation_data.get("clientSideContext")
                if not session_token and aamation_data.get("sessionToken"):
                    session_token_data = json.loads(aamation_data.get("sessionToken"))
                    print(f"Validation ID: {session_token_data.get('uniqueValidationId')}")
            except json.JSONDecodeError:
                print("Error parsing amz-aamation-resp header")

      

        # Final signin request
        signin_data = {"appActionToken": hidden["appActionToken"], "appAction": "SIGNIN_PWD_COLLECT", "subpageType": hidden["subPageType"], "prevRID": hidden["prevRID"], "workflowState": hidden["workflowState"], "session-token": session_token, "email": self.num, "password": ''}
        signin_cookies = {"ubid-main": cookies.get("ubid-main", ""), "session-id": cookies.get("session-id"), "session-id-time": cookies.get("session-id-time"), "i18n-prefs": "USD"}
        response = requests.post("https://www.amazon.com/ap/signin", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}, cookies=signin_cookies, data=signin_data).text


        if "ap_change_login_claim" in response or "auth-email-claim" in response or "auth-password-claim" in response:
            return True, response
        elif "There was a problem" in response:
            return False, response
        else:
            return False, response