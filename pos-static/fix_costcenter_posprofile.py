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
        print("LOGIN FAIL", s); sys.exit(1)
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf

csrf = get_csrf()
print("login OK")
STRIP = ["creation","modified","modified_by","owner","idx","docstatus","lft","rgt","old_parent","_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype"]

# 1) fix Cost Center: need parent_cost_center = "Cost Centers - <abbr>" (auto root). Compute from company abbr.
def abbr_of(company):
    return {"My Company":"MC","ULTRA MRF":"UM","Ultra MRF Dau Annex":"UMDA","Ultra MRF Dau Main":"UMDM",
            "Ultra MRF Warehouse Dau":"UMDW","Ultra MRF San Fernando":"UMSF","San Fernando Warehouse":"SFWH",
            "Ultra MRF Telebastagan":"UMTEL","Ultra MRF Telebastagan 2":"UMTEL2","Ultra MRF Mexico Warehouse":"MEXWH",
            "Automan Car Care Center":"AUTOMAN","Wheel Core":"WCORE","The Wheelhub":"WHUB"}.get(company,"")

cc = json.load(open("pos-static/export/Cost_Center.json", encoding="utf-8"))
ok=dup=err=0
for r in cc:
    doc = {k:v for k,v in r.items() if k not in STRIP}
    doc["doctype"]="Cost Center"
    ab = abbr_of(doc.get("company") or r.get("company"))
    if not doc.get("parent_cost_center") and ab:
        doc["parent_cost_center"] = f"Cost Centers - {ab}"
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s==200: ok+=1
    elif s==409: dup+=1
    else:
        if err<6: print(f"  CC FAIL {s} {doc.get('name')}: {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:180]}")
        err+=1
print(f"Cost Center: ok={ok} dup={dup} err={err}")

# 2) fix POS Profile: null letter_head
pos = json.load(open("pos-static/export/POS_Profile.json", encoding="utf-8"))
ok=dup=err=0
for r in pos:
    doc = {k:v for k,v in r.items() if k not in STRIP}
    doc["doctype"]="POS Profile"
    doc["letter_head"]=None
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s==200: ok+=1
    elif s==409: dup+=1
    else:
        if err<6: print(f"  POS FAIL {s} {doc.get('name')}: {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:180]}")
        err+=1
print(f"POS Profile: ok={ok} dup={dup} err={err}")
print("DONE")
