import json, urllib.request, urllib.parse, http.cookiejar, os, base64, sys
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
CSV = "C:/Users/josem/erpnext-system/pos-static/csv"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/: ")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try: r = op.open(req, timeout=120); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD}); csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf
csrf = get_csrf()

dt = sys.argv[1] if len(sys.argv)>1 else "Vehicle Model"
csv_path = os.path.join(CSV, dt.replace(" ", "_")+".csv")
with open(csv_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
# dedicated data import upload
s,j = post("/api/method/frappe.core.doctype.data_import.data_import.upload", {
    "filename": os.path.basename(csv_path),
    "import_type": "Insert New Records",
    "reference_doctype": dt,
    "file": b64,
    "submit_after_import": False,
    "skip_errors": True
}, csrf)
print("upload status:", s)
print("result:", json.dumps(j, default=str)[:400])
if s==200:
    di = j.get("message")
    di_name = di.get("name") if isinstance(di, dict) else None
    print("Data Import:", di_name)
    if di_name:
        s2,j2 = post(f"/api/method/frappe.core.doctype.data_import.data_import.start_import?data_import={urllib.parse.quote(di_name)}", {}, csrf)
        print("start_import:", s2, str(j2)[:150])
print("DONE")
