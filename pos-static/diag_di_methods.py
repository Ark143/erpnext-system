import json, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/: ")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try: r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
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
# get Data Import docinfo / method list
s,j = post("/api/method/frappe.client.get_docinfo", {"doctype":"Data Import"}, csrf)
print("get_docinfo keys:", list(j.keys()) if isinstance(j,dict) else j)
# try the newer import endpoint names
for m in ["frappe.core.doctype.data_import.data_import.import_file",
          "frappe.core.doctype.data_import.data_import.upload_import_file",
          "frappe.core.doctype.data_import.exporter.export_data",
          "frappe.core.doctype.data_import.data_import.get_import_status"]:
    s2,j2 = post("/api/method/"+m, {}, csrf)
    print(m.split(".")[-1], "->", s2, (str(j2.get("exception","ok"))[:80] if s2!=200 else "OK"))
