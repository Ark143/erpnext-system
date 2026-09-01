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
        print("LOGIN FAIL", s); sys.exit(1)
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf

csrf = get_csrf()
print("login OK")
STRIP = ["creation","modified","modified_by","owner","idx","docstatus","amended_from","__islocal",
         "__unsaved","_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype",
         "_last_updated","__version","lft","rgt","templates","print_formats","__assets","test_records",
         "default_print_format","track_changes","track_views","track_seen","notification_count",
         "permissions","states","links","actions","__workspace"]
def make_doc(name):
    doc = json.load(open(f"pos-static/doctype_defs/{name}.json", encoding="utf-8"))
    for k in STRIP: doc.pop(k, None)
    for k in list(doc.keys()):
        if k.startswith("__"): doc.pop(k, None)
    doc["custom"]=1; doc["module"]="Vehicle Management"; doc.pop("issingle", None)
    return doc

# blank cross links: Vehicle Estimate -> 'Converted Vehicle Job Order' (link to Vehicle Job Order)
# Vehicle Job Order -> 'Original Estimate / Quotation' (link to Vehicle Estimate)
ve = make_doc("vehicle_estimate")
for f in ve.get("fields",[]):
    if f.get("fieldname")=="converted_vehicle_job_order" or "Vehicle Job Order" in str(f.get("options","")):
        f["options"]=""
jo = make_doc("vehicle_job_order")
for f in jo.get("fields",[]):
    if f.get("fieldname") in ("original_estimate","original_estimate_quotation") or "Vehicle Estimate" in str(f.get("options","")):
        f["options"]=""
s,j = post("/api/resource/DocType", ve, csrf)
print(f"  vehicle_estimate: {s} {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:160]}")
s,j = post("/api/resource/DocType", jo, csrf)
print(f"  vehicle_job_order: {s} {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:160]}")
print("DONE")
