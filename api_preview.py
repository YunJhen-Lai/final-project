
#!/usr/bin/env python3
import requests, json, sys
from pathlib import Path

TDX_APP_ID = "e74106165-cd1d41f5-2b74-4438"
TDX_APP_SECRET = "b842e80b-389e-4930-892e-c6aefd36f92a"
API_KEY = None

def get_oauth2_token(app_id, app_secret):
    url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    try:
        resp = requests.post(url, data={"grant_type": "client_credentials", "client_id": app_id, "client_secret": app_secret}, timeout=30)
        resp.raise_for_status()
        return resp.json().get('access_token')
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def preview_api(url, api_key=None, app_id=None, app_secret=None):
    print(f"\n{'='*70}\nCalling API\n{'='*70}\nURL: {url}\n")
    headers = {}
    if app_id and app_secret and app_id != "your_app_id_here":
        print("Authenticating...")
        token = get_oauth2_token(app_id, app_secret)
        if not token: return
        headers["authorization"] = f"Bearer {token}"
        print("Authentication successful\n")
    elif api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"{'='*70}\nAPI Response\n{'='*70}\nStatus: {response.status_code}\nContent-Type: {response.headers.get('Content-Type', 'N/A')}\nSize: {len(response.content):,} bytes\n{'='*70}\n")
        try:
            data = response.json()
            text = json.dumps(data, ensure_ascii=False, indent=2)
        except:
            text = response.text
        lines = text.split('\n')
        print("Response Content (first 50 lines):\n" + "-"*70)
        for line in lines[:50]:
            print(line)
        print("-"*70)
        if len(lines) > 50:
            print(f"\nOmitted {len(lines) - 50} lines")
        print(f"\nTotal: {len(lines)} lines\n{'='*70}")
        save = input("Save to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename [api_response.json]: ").strip() or "api_response.json"
            Path(filename).write_text(text, encoding='utf-8')
            print(f"Saved to: {Path(filename).absolute()}")
        print(f"{'='*70}\n")
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == "__main__":
    url = input("API URL: ").strip()
    if not url:
        print("URL required")
        sys.exit(1)
    preview_api(url, api_key=API_KEY, app_id=TDX_APP_ID, app_secret=TDX_APP_SECRET)

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return{
            'content-type' : content_type,
            'grant_type' : grant_type,
            'client_id' : self.app_id,
            'client_secret' : self.app_key
        }

class data():

    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')

        return{
            'authorization': 'Bearer ' + access_token,
            'Accept-Encoding': 'gzip'
        }

if __name__ == '__main__':
    try:
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    except:
        a = Auth(app_id, app_key)
        auth_response = requests.post(auth_url, a.get_auth_header())
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    print(auth_response)
    pprint(auth_response.text)
    print(data_response)
    pprint(data_response.text)
