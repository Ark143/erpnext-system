import json, sys, urllib.request, urllib.parse, http.cookiejar, os

BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR")
PWD = os.environ.get("CLOUD_PWD")
DEFS = "C:/Users/josem/erpnext-system/pos-static/doctype_defs"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/:")
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    if csrf:
        req.add_header("X-Frappe-CSRF-Token", csrf)
    try:
        r = op.open(req, timeout=60)
        return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {"error": e.reason}
        return e.code, body

def get_csrf():
    s, j = post("/api/method/login", {"usr": USR, "pwd": PWD})
    if s != 200:
        print("LOGIN FAILED", s, j); sys.exit(1)
    csrf = None
    for domain in cj._cookies.values():
        for path in domain.values():
            for c in path.values():
                if c.name == "csrf_token":
                    csrf = c.value
    if not csrf and isinstance(j, dict):
        csrf = j.get("csrf_token")
    print("LOGIN OK, csrf present:", bool(csrf))
    return csrf

csrf = get_csrf()

# only the master-data relevant DocTypes still needed (transactional parents handled by app deploy later)
order = ["vehicle_service_reminder"]  # others already exist (409 -> OK)

# link options pointing to NOT-yet-existing doctypes -> blank (only these deferred parents)
DEFERRED_LINKS = {"Inspection Template","Vehicle Inspection","Vehicle Job Order","Vehicle Estimate",
                  "Vehicle POS Invoice","Job Order Service Item","Job Order Part Item","Vehicle Inspection Item"}

for name in order:
    fp = os.path.join(DEFS, name + ".json")
    if not os.path.exists(fp) or os.path.getsize(fp) == 0:
        print("SKIP (no def)", name); continue
    doc = json.load(open(fp, encoding="utf-8"))
    for k in ["creation","modified","modified_by","owner","idx","docstatus","amended_from",
              "__islocal","__unsaved","_comments","_assign","_user_tags","_liked_by","parent",
              "parentfield","parenttype","_last_updated","__version","lft","rgt",
              "templates","print_formats","__assets","test_records","default_print_format",
              "track_changes","track_views","track_seen","notification_count","permissions",
              "states","links","actions","__workspace"]:
        doc.pop(k, None)
    for k in list(doc.keys()):
        if k.startswith("__"):
            doc.pop(k, None)
    for fld in doc.get("fields", []):
        if fld.get("fieldtype") in ("Link","Table","Table MultiSelect") and fld.get("options") in DEFERRED_LINKS:
            fld["options"] = ""
    doc["custom"] = 1
    doc["module"] = "Vehicle Management"
    doc.pop("issingle", None)
    s, j = post("/api/resource/DocType", doc, csrf)
    if s in (200, 409):
        print(f"OK  {name} ({s})")
    else:
        msg = j.get("exception") or j.get("_error_message") or j.get("message") or j
        print(f"FAIL {name}: {s} {str(msg)[:200]}")
print("DONE")
