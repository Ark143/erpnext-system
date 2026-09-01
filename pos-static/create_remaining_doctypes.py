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
    if s!=200: print("LOGIN FAIL",s,j); sys.exit(1)
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf
csrf = get_csrf()

STRIP = ["creation","modified","modified_by","owner","idx","docstatus","amended_from","__islocal",
         "__unsaved","_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype",
         "_last_updated","__version","lft","rgt","templates","print_formats","__assets","test_records",
         "default_print_format","track_changes","track_views","track_seen","notification_count",
         "permissions","states","links","actions","__workspace"]

def make_doc(name, doc=None):
    if doc is None:
        doc = json.load(open(os.path.join(DEFS, name+".json"), encoding="utf-8"))
    for k in STRIP: doc.pop(k, None)
    for k in list(doc.keys()):
        if k.startswith("__"): doc.pop(k, None)
    doc["custom"]=1; doc["module"]="Vehicle Management"; doc.pop("issingle", None)
    return doc

# 4 transactional parents (child tables now exist, links intact)
for name in ["vehicle_pos_invoice","vehicle_inspection","vehicle_estimate","vehicle_job_order"]:
    fp = os.path.join(DEFS, name+".json")
    if not os.path.exists(fp) or os.path.getsize(fp)==0:
        print("SKIP no def", name); continue
    doc = make_doc(name)
    s,j = post("/api/resource/DocType", doc, csrf)
    print(f"{'OK' if s in (200,409) else 'FAIL'} {name}: {s} {str(j.get('exception') or j.get('_error_message') or '')[:120]}")

# Cashier Profile minimal (no json existed)
cp = {
  "doctype":"DocType","name":"Cashier Profile","custom":1,"module":"Vehicle Management",
  "naming_rule":"By fieldname","autoname":"naming_series:",
  "fields":[
    {"label":"Cashier","fieldname":"cashier","fieldtype":"Link","options":"User","reqd":1},
    {"label":"POS Profile","fieldname":"pos_profile","fieldtype":"Link","options":"POS Profile"},
    {"label":"Branch","fieldname":"branch","fieldtype":"Link","options":"Branch"},
    {"label":"Active","fieldname":"active","fieldtype":"Check"}
  ],
  "permissions":[{"role":"System Manager","read":1,"write":1,"create":1,"delete":1}]
}
s,j = post("/api/resource/DocType", cp, csrf)
print(f"{'OK' if s in (200,409) else 'FAIL'} Cashier Profile: {s} {str(j.get('exception') or j.get('_error_message') or '')[:120]}")
print("DONE")
