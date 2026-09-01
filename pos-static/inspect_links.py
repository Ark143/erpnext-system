import json, sys, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
DEFS = "C:/Users/josem/erpnext-system/pos-static/doctype_defs"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/:")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD})
    return None
csrf = get_csrf()
# print full error for the two failing ones
for name in ["vehicle_estimate","vehicle_job_order"]:
    doc = json.load(open(os.path.join(DEFS, name+".json"), encoding="utf-8"))
    print("====", name, "link/table fields ====")
    for f in doc.get("fields", []):
        if f.get("fieldtype") in ("Link","Table","Table MultiSelect"):
            print(f"  {f.get('fieldname')}: {f.get('fieldtype')} -> {f.get('options')}")
