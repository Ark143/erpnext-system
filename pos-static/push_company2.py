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

STRIP = ["creation","modified","modified_by","owner","idx","docstatus","lft","rgt","old_parent",
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype",
         "default_bank_account","default_cash_account","default_receivable_account",
         "default_payable_account","write_off_account","default_expense_account",
         "default_income_account","default_discount_account","unrealized_profit_loss_account",
         "exchange_gain_loss_account","cost_center","default_letter_head","default_holiday_list",
         "default_finance_book",
         # mandatory round-off / depreciation links that must be auto-created
         "round_off_account","round_off_cost_center","accumulated_depreciation_account",
         "depreciation_cost_center","default_round_off_account"]

recs = json.load(open("pos-static/export/Company.json", encoding="utf-8"))
print("total companies in export:", len(recs))

def sort_key(r):
    return 0 if not r.get("parent_company") else 1
recs_sorted = sorted(recs, key=sort_key)

created = []
for r in recs_sorted:
    doc = dict(r)
    for k in STRIP: doc.pop(k, None)
    doc["doctype"] = "Company"
    doc["create_chart_of_accounts_based_on"] = "Standard Template"
    doc["chart_of_accounts"] = "Standard"
    name = doc.get("name")
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s == 200:
        created.append(name)
        print(f"  OK  {name}")
    else:
        exc = str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))[:220]
        # If company already exists, mark and continue (children still need parent)
        if "already exists" in exc.lower() or s==409:
            created.append(name)
            print(f"  EXISTS {name}")
        else:
            print(f"  FAIL {s} {name}: {exc}")
            # don't abort children; parent may still be there from a prior run

print("created/exists:", created)
print("DONE")
