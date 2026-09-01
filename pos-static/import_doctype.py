import json, sys, urllib.request, urllib.parse, http.cookiejar, os, time
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, payload, csrf=None):
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=90); return r.status, json.loads(r.read().decode())
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
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype"]

def import_doc(doctype, export_file, extra_strip=None, threads=4, max_retries=4):
    extra_strip = extra_strip or []
    recs = json.load(open(export_file, encoding="utf-8"))
    print(f"\n=== {doctype}: {len(recs)} records from {os.path.basename(export_file)} ===")
    ok=dup=skip_fail=perm=err=0
    perm_stop=False
    def do_one(r):
        doc = dict(r)
        for k in STRIP + extra_strip: doc.pop(k, None)
        doc["doctype"] = doctype
        # try insert; on duplicate skip; on transient 429 retry
        last=None
        for attempt in range(max_retries):
            s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
            if s==200: return "ok"
            if s==409: return "dup"
            if s==403: return "perm"
            if s==429:  # rate limited
                time.sleep(2*(attempt+1)); continue
            if "LinkValidationError" in str(j.get("exception","")) or "could not find" in str(j.get("exception","")).lower():
                return ("linkfail", str(j.get("exception"))[:200])
            if s in (417,) and attempt < max_retries-1:
                time.sleep(1); continue
            return ("err", f"{s} {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:160]}")
        return last or "err"
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for i,res in enumerate(ex.map(do_one, recs), 1):
            if res=="ok": ok+=1
            elif res=="dup": dup+=1
            elif res=="perm": perm+=1; perm_stop=True
            elif isinstance(res,tuple) and res[0]=="linkfail": skip_fail+=1
            else: err+=1
            if i % 200 == 0:
                print(f"  progress {i}/{len(recs)} ok={ok} dup={dup} skip={skip_fail} err={err}")
            if perm_stop and perm>=1:
                print("  PERMISSION 403 — stopping this doctype"); break
    print(f"  RESULT {doctype}: ok={ok} dup={dup} linkfail={skip_fail} perm={perm} err={err}")
    return perm_stop

# doctype -> (export_file, extra_strip)
PLAN = [
    ("Cost Center", "pos-static/export/Cost_Center.json", []),
    ("Warehouse", "pos-static/export/Warehouse.json", []),
    ("Mode of Payment", "pos-static/export/Mode_of_Payment.json", []),
    ("POS Profile", "pos-static/export/POS_Profile.json", []),
    ("Item Group", "pos-static/export/Item_Group.json", []),
    ("Customer Group", "pos-static/export/Customer_Group.json", []),
    ("Supplier Group", "pos-static/export/Supplier_Group.json", []),
    ("Price List", "pos-static/export/Price_List.json", []),
    ("Vehicle Make", "pos-static/export/Vehicle_Make.json", []),
    ("Vehicle Model", "pos-static/export/Vehicle_Model.json", []),
]
for dt, f, extra in PLAN:
    if perm := import_doc(dt, f, extra):
        print(f"STOPPING — 403 on {dt}")
        break
print("\nDONE medium doctypes")
