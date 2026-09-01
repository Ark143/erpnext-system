import json, sys, urllib.request, urllib.parse, http.cookiejar, os, time
from concurrent.futures import ThreadPoolExecutor
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
    if s!=200: print("LOGIN FAIL", s); sys.exit(1)
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": return c.value

csrf = get_csrf()
print("login OK (Item retry, PC->Nos remap)", flush=True)

# Remap PC -> Nos (cloud has Nos but not PC). Also remap PC in any uom field.
UOM_REMAPPING = {"PC": "Nos"}
STRIP = ["creation","modified","modified_by","owner","idx","docstatus","lft","rgt","old_parent",
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype","name"]
REMAPPING = {
    "Item": {"item_group": {"GENERAL REPAIRS": "Services", "OTHER SERVICES": "Services",
                             "TRANSMISSION": "TRANSMISSION", "Products": "Products", "Services": "Services"}},
}

def remap_doc(doc, doctype):
    for fld, mp in REMAPPING.get(doctype, {}).items():
        if doc.get(fld) in mp: doc[fld] = mp[doc[fld]]
    # UOM remap for Item stock_uom / uom / uoms
    if doctype == "Item":
        for f in ("stock_uom","uom"):
            if doc.get(f) in UOM_REMAPPING: doc[f] = UOM_REMAPPING[doc[f]]
        # child uom table: uom field
        for row in (doc.get("uoms") or []):
            if row.get("uom") in UOM_REMAPPING: row["uom"] = UOM_REMAPPING[row["uom"]]
    return doc

def import_doc(doctype, export_file, threads=6, max_retries=6):
    recs = json.load(open(export_file, encoding="utf-8"))
    print(f"\n=== {doctype}: {len(recs)} records (retry) ===", flush=True)
    ok=dup=linkfail=perm=err=0; failures=[]
    def clean(r):
        doc = {}
        for k,v in r.items():
            if k in STRIP: continue
            if v is None or v=="": continue
            doc[k]=v
        doc["doctype"]=doctype
        return remap_doc(doc, doctype)
    def do_one(r):
        doc = clean(r)
        for attempt in range(max_retries):
            s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
            if s==200: return "ok"
            if s==409: return "dup"
            if s==403: return "perm"
            if s==429:
                time.sleep(2*(attempt+1)); continue
            ex=str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))
            if "LinkValidationError" in ex or "could not find" in ex.lower() or "Group type" in ex:
                # if still a UOM linkfail we can't remap further
                return ("linkfail", ex[:200])
            if s==417 and attempt < max_retries-1:
                time.sleep(1); continue
            return ("err", f"{s} {ex[:160]}")
        return "err"
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for i,res in enumerate(ex.map(do_one, recs), 1):
            if res=="ok": ok+=1
            elif res=="dup": dup+=1
            elif res=="perm": perm+=1
            elif isinstance(res,tuple) and res[0]=="linkfail": linkfail+=1; failures.append(res[1])
            else: err+=1; failures.append(res[1] if isinstance(res,tuple) else str(res))
            if i % 2000 == 0:
                print(f"  progress {i}/{len(recs)} ok={ok} dup={dup} link={linkfail} err={err}", flush=True)
            if perm>=1:
                print("  PERMISSION 403 — stopping", flush=True); break
    print(f"  RESULT {doctype}: ok={ok} dup={dup} linkfail={linkfail} perm={perm} err={err}", flush=True)
    if failures: print("  sample failures:", failures[:5], flush=True)
    return perm

import_doc("Item", "pos-static/export/Item.json", threads=6)
print("\nDONE Item retry (PC->Nos)")
