import urllib.request
import json

base_url = "http://127.0.0.1:8000"

companies = [
    "Ultra MRF Dau Main",
    "ULTRA MRF",
    "The Wheelhub",
    "Automan Car Care Center",
    "Ultra MRF San Fernando"
]

for co in companies:
    url = f"{base_url}/api/method/executive_dashboard?view=approvals&company={urllib.parse.quote(co)}"
    req = urllib.request.Request(url, headers={"Host": "erp.localhost"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            msg = data.get('message', [])
            print(f"Company: {co:30s} | HTTP {resp.status} | Cards: {len(msg)}")
            for c in msg[:3]:
                print(f"   -> {c['doctype']:22s}: Pending {c['count']}, Total: ₱{c['total']}")
    except Exception as e:
        print(f"Company: {co:30s} | ERROR: {e}")
