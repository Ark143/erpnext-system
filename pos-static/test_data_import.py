import json, urllib.request, urllib.parse, http.cookiejar, os, base64
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
CSV = "C:/Users/josem/erpnext-system/pos-static/csv"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None, files=None):
    path = urllib.parse.quote(path, safe="/: ")
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE+path, data=data, method="POST")
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
cookies = "; ".join(f"{c.name}={c.value}" for d in cj._cookies.values() for p in d.values() for c in p.values())

# 1) upload the CSV as a File via upload_file method
dt = "Vehicle Model"
csv_path = os.path.join(CSV, dt.replace(" ", "_")+".csv")
with open(csv_path, "rb") as f:
    content = base64.b64encode(f.read()).decode()
s,j = post("/api/method/upload_file", {
    "filename": os.path.basename(csv_path),
    "filedata": content,
    "doctype": "Data Import",
    "fieldname": "import_file",
    "is_private": 1
}, csrf)
print("upload:", s, j.get("message",{}).get("name") if s==200 else j)
file_url = j.get("message",{}).get("file_url") if s==200 else None
print("file_url:", file_url)

# 2) create Data Import
if file_url:
    s2,j2 = post("/api/method/frappe.client.insert", {"doc": {
        "doctype": "Data Import",
        "reference_doctype": dt,
        "import_type": "Insert New Records",
        "import_file": file_url,
        "submit_after_import": 0,
        "skip_errors": 1
    }}, csrf)
    print("create DI:", s2, j2.get("message",{}).get("name") if s2==200 else j2)
    di_name = j2.get("message",{}).get("name") if s2==200 else None
    # 3) start import
    if di_name:
        s3,j3 = post(f"/api/method/frappe.core.doctype.data_import.data_import.start_import?data_import={urllib.parse.quote(di_name)}", {}, csrf)
        print("start_import:", s3, str(j3)[:150])
print("DONE")
