
import requests
from pprint import pprint
import json

app_id = 'e74106165-cd1d41f5-2b74-4438'
app_key = 'b842e80b-389e-4930-892e-c6aefd36f92a'

auth_url="https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?$top=30&$format=JSON"

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
    # --- Pretty print preview ---
    print('\n' + '-'*60)
    print('Preview (pretty):')
    try:
        parsed = json.loads(data_response.text)
        # If it's a list, show only the first 20 items for readability
        if isinstance(parsed, list):
            to_show = parsed[:20]
            print(json.dumps(to_show, ensure_ascii=False, indent=2))
            if len(parsed) > 20:
                print(f"\n... (shown 20 of {len(parsed)} items)")
        elif isinstance(parsed, dict):
            # Pretty print dict but if contains large arrays, truncate those
            # For top-level keys, show summaries for large lists
            display = {}
            for k, v in parsed.items():
                if isinstance(v, list):
                    display[k] = v[:20]
                    if len(v) > 20:
                        display[k] = {"_preview": v[:20], "_total": len(v)}
                else:
                    display[k] = v
            print(json.dumps(display, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except Exception:
        txt = data_response.text
        # show a reasonable preview length
        preview = txt if len(txt) <= 2000 else txt[:2000] + '\n... (truncated)'
        print(preview)
    print('-'*60)

    # Ask user whether to save
    try:
        save = input('\nSave response to file? (y/n): ').strip().lower()
    except Exception:
        save = 'n'
    if save == 'y':
        fname = input('Filename [api_response.json]: ').strip() or 'api_response.json'
        try:
            if 'parsed' in locals():
                with open(fname, 'w', encoding='utf-8') as fw:
                    json.dump(parsed, fw, ensure_ascii=False, indent=2)
            else:
                with open(fname, 'w', encoding='utf-8') as fw:
                    fw.write(txt)
            print(f"Saved to: {fname}")
        except Exception as e:
            print('Failed to save file:', e)
