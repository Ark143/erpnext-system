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
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD}); return None
csrf = get_csrf()
STRIP = ["creation","modified","modified_by","owner","idx","docstatus","amended_from","__islocal","__unsaved",
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype","_last_updated",
         "__version","lft","rgt","templates","print_formats","__assets","test_records","default_print_format",
         "track_changes","track_views","track_seen","notification_count","permissions","states","links","actions","__workspace"]
def make_doc(name):
    doc = json.load(open(os.path.join(DEFS, name+".json"), encoding="utf-8"))
    for k in STRIP: doc.pop(k, None)
    for k in list(doc.keys()):
        if k.startswith("__"): doc.pop(k, None)
    # ensure a naming_series field exists (fixes Cashier Profile-style autoname errors)
    if doc.get("autoname") and "naming_series" in str(doc.get("autoname","")):
        if not any(f.get("fieldname")=="naming_series" for f in doc.get("fields",[])):
            doc["fields"].insert(0, {"label":"Naming Series","fieldname":"naming_series","fieldtype":"Data","hidden":1,"read_only":1})
    doc["custom"]=1; doc["module"]="Vehicle Management"; doc.pop("issingle", None)
    return doc
for name in ["vehicle_estimate","vehicle_job_order"]:
    doc = make_doc(name)
    s,j = post("/api/resource/DocType", doc, csrf)
    print(f"{'OK' if s in (200,409) else 'FAIL'} {name}: {s} {str(j.get('exception') or j.get('_error_message') or '')[:160]}")
# Cashier Profile: add naming_series field + proper autoname
cp = {
  "doctype":"DocType","name":"Cashier Profile","custom":1,"module":"Vehicle Management",
  "naming_rule":"By fieldname","autoname":"POSH-.#####",
  "fields":[
    {"label":"Naming Series","fieldname":"naming_series","fieldtype":"Data","hidden":1},
    {"label":"Cashier","fieldname":"cashier","fieldtype":"Link","options":"User","reqd":1},
    {"label":"POS Profile","fieldname":"pos_profile","fieldtype":"Link","options":"POS Profile"},
    {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
    {"label":"Active","fieldname":"active","fieldtype":"Check"}
  ],
  "permissions":[{"role":"System Manager","read":1,"write":1,"create":1,"delete":1}]
}
s,j = post("/api/resource/DocType", cp, csrf)
print(f"{'OK' if s in (200,409) else 'FAIL'} Cashier Profile: {s} {str(j.get('exception') or j.get('_error_message') or '')[:160]}")
print("DONE")
