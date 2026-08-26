import urllib.request
import json
import urllib.parse

base_url = "http://127.0.0.1:8000"

def test_api(qs):
    url = f"{base_url}/api/method/executive_dashboard?{qs}"
    req = urllib.request.Request(url, headers={"Host": "erp.localhost", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"URL: {qs} -> Status {resp.status}, Msg Type: {type(data.get('message'))}, Keys: {list(data.get('message', {}).keys()) if isinstance(data.get('message'), dict) else len(data.get('message', []))}")
    except Exception as e:
        print(f"URL: {qs} -> FAILED: {e}")

test_api("view=meta")
test_api("view=exec_summary&company=Ultra%20MRF%20Dau%20Main")
test_api("view=sales&company=Ultra%20MRF%20Dau%20Main")
