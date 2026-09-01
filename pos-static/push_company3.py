import json, sys, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, payload, csrf=None):
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=120); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
    except Exception as e:
        return "ERR", {"error": str(e)}

def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
    if s!=200:
        print("LOGIN FAIL", s, j.get("message") if isinstance(j,dict) else j); sys.exit(1)
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf

csrf = get_csrf()
print("login OK")

# Only keep structural fields; let Frappe auto-create the standard chart of accounts.
KEEP = {"doctype","name","company_name","abbr","default_currency","country","is_group",
        "parent_company","domain","tax_id","date_of_establishment","date_of_incorporation",
        "website","phone_no","email","company_description","reporting_currency",
        "company_logo","create_chart_of_accounts_based_on","existing_company","chart_of_accounts"}

recs = json.load(open("pos-static/export/Company.json", encoding="utf-8"))
print("total companies in export:", len(recs))

def sort_key(r):
    return 0 if not r.get("parent_company") else 1
recs_sorted = sorted(recs, key=sort_key)

created = []
for r in recs_sorted:
    doc = {k: v for k, v in r.items() if k in KEEP}
    doc["doctype"] = "Company"
    if doc.get("parent_company"):
        doc["create_chart_of_accounts_based_on"] = "Existing Company"
        doc["existing_company"] = doc["parent_company"]
    else:
        doc["create_chart_of_accounts_based_on"] = "Standard Template"
        doc["chart_of_accounts"] = "Standard"
    name = doc.get("name")
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s == 200:
        created.append(name)
        print(f"  OK  {name}")
    else:
        exc = str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))[:240]
        if "already exists" in exc.lower() or s==409:
            created.append(name); print(f"  EXISTS {name}")
        else:
            print(f"  FAIL {s} {name}: {exc}")

print("created/exists:", created)
print("DONE")
