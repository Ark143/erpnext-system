import requests
import json

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

# 1. Get all companies
companies = s.get(f"{BASE}/api/resource/Company?fields=" + json.dumps(["name", "abbr", "default_currency"])).json()["data"]
print(f"Total Companies: {len(companies)}")
for c in companies:
    print(f" - {c['name']} ({c['abbr']})")

# 2. Check Tax Templates
st = s.get(f"{BASE}/api/resource/Sales%20Taxes%20and%20Charges%20Template?fields=" + json.dumps(["name", "company"])).json().get("data", [])
print(f"\nExisting Sales Tax Templates ({len(st)}):")
for t in st:
    print(f" - {t['name']} ({t.get('company')})")

pt = s.get(f"{BASE}/api/resource/Purchase%20Taxes%20and%20Charges%20Template?fields=" + json.dumps(["name", "company"])).json().get("data", [])
print(f"\nExisting Purchase Tax Templates ({len(pt)}):")
for t in pt:
    print(f" - {t['name']} ({t.get('company')})")

# 3. Check BIR Form 2307 Print Formats & DocType
pf = s.get(f"{BASE}/api/resource/Print%20Format?filters=" + json.dumps([["doc_type", "in", ["Sales Invoice", "Purchase Invoice", "BIR Form 2307"]]])).json().get("data", [])
print(f"\nPrint Formats ({len(pf)}):")
for p in pf:
    print(f" - {p['name']}")

# 4. Check Client Scripts on Sales Invoice and Purchase Invoice
cs = s.get(f"{BASE}/api/resource/Client%20Script?filters=" + json.dumps([["dt", "in", ["Sales Invoice", "Purchase Invoice"]]])).json().get("data", [])
print(f"\nClient Scripts on Invoices ({len(cs)}):")
for c in cs:
    print(f" - {c['name']}")
