
import requests
from pprint import pprint
import json

app_id = 'e74106165-cd1d41f5-2b74-4438'
app_key = 'b842e80b-389e-4930-892e-c6aefd36f92a'

auth_url="https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/SectionShape/City/Taichung"

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
    # --- Response summary and readable preview (first 20 items) ---
    try:
        print('\n' + '='*80)
        print('Response Summary')
        print('='*80)
        # auth_response may be present
        try:
            print(f"Auth response status: {getattr(auth_response, 'status_code', 'N/A')}")
        except NameError:
            pass
        print(f"Data response status: {getattr(data_response, 'status_code', 'N/A')}")
        print(f"Content-Type: {data_response.headers.get('Content-Type', 'N/A')}")
        print(f"Size: {len(data_response.content):,} bytes")
        print('-'*80)

        parsed = None
        txt = data_response.text
        try:
            parsed = json.loads(txt)
        except Exception:
            parsed = None

        if parsed is not None:
            # If list, show first 20
            if isinstance(parsed, list):
                to_show = parsed[:20]
                print('Preview (first 20 items):')
                print(json.dumps(to_show, ensure_ascii=False, indent=2))
                if len(parsed) > 20:
                    print(f"\n... (shown 20 of {len(parsed)} items)")
            elif isinstance(parsed, dict):
                # find first list field to preview
                found = False
                for k, v in parsed.items():
                    if isinstance(v, list):
                        print(f"Preview of first 20 items under key '{k}':")
                        print(json.dumps(v[:20], ensure_ascii=False, indent=2))
                        if len(v) > 20:
                            print(f"\n... (shown 20 of {len(v)} items)")
                        found = True
                        break
                if not found:
                    # pretty print the dict (with truncated lists)
                    trimmed = {}
                    for k, v in parsed.items():
                        if isinstance(v, list):
                            trimmed[k] = {'_preview': v[:20], '_total': len(v)}
                        else:
                            trimmed[k] = v
                    print('Preview (trimmed dict):')
                    print(json.dumps(trimmed, ensure_ascii=False, indent=2))
        else:
            # fallback to text preview
            preview = txt if len(txt) <= 2000 else txt[:2000] + '\n... (truncated)'
            print('Response (text preview):')
            print(preview)

        print('='*80)

        # prompt to save
        try:
            save = input('\nSave response to file? (y/n): ').strip().lower()
        except Exception:
            save = 'n'
        if save == 'y':
            fname = input('Filename [api_response.json]: ').strip() or 'api_response.json'
            try:
                if parsed is not None:
                    with open(fname, 'w', encoding='utf-8') as fw:
                        json.dump(parsed, fw, ensure_ascii=False, indent=2)
                else:
                    with open(fname, 'w', encoding='utf-8') as fw:
                        fw.write(txt)
                print(f"Saved to: {fname}")
            except Exception as e:
                print('Failed to save file:', e)
    except Exception as e:
        print('Preview error:', e)

    # --- Show first 20 items (added preview) ---
    try:
        print('\n' + '='*60)
        print('Quick preview: first 20 items')
        if 'parsed' in locals():
            if isinstance(parsed, list):
                show = parsed[:20]
                print(json.dumps(show, ensure_ascii=False, indent=2))
                if len(parsed) > 20:
                    print(f"\n... (shown 20 of {len(parsed)} items)")
            elif isinstance(parsed, dict):
                # find the first list in the dict values
                found = False
                for k, v in parsed.items():
                    if isinstance(v, list):
                        print(f"First 20 items under key '{k}':")
                        print(json.dumps(v[:20], ensure_ascii=False, indent=2))
                        if len(v) > 20:
                            print(f"\n... (shown 20 of {len(v)} items)")
                        found = True
                        break
                if not found:
                    print('Parsed JSON is an object with no list fields to preview.')
            else:
                print('Parsed JSON is not a list or object; cannot list items.')
        else:
            print('No parsed JSON available to preview first 20 items.')
        print('='*60 + '\n')
    except Exception as e:
        print('Preview error:', e)
