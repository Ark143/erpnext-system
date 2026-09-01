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

# find an existing Mode of Payment on cloud (unique name)
s,j = post("/api/method/frappe.client.get_list", {"doctype":"Mode of Payment","fields":["name"],"filters":[]}, csrf)
mops = [x.get("name") for x in (j.get("message") or [])]
print("cloud MOPs:", mops)
default_mop = mops[0] if mops else None

# 1) Cost Center: root ones need parent = "{Company} - {abbr}" (the existing group)
cc = json.load(open("pos-static/export/Cost_Center.json", encoding="utf-8"))
ok=dup=err=0
for r in cc:
    doc = {k:v for k,v in r.items() if k not in STRIP}
    doc["doctype"]="Cost Center"
    if doc.get("is_group") and not doc.get("parent_cost_center"):
        comp = doc.get("company")
        ab = "".join(c for c in comp.split()[-1].upper() if c.isalnum())[:4] if comp else ""
        # better: derive abbr from existing pattern; just use company name root
        doc["parent_cost_center"] = f"{comp} - " + (ab if ab else "UM")
        # Actually the existing root is named "<Company> - <abbr>"; for ULTRA MRF it's "ULTRA MRF - UM"
        if comp=="ULTRA MRF": doc["parent_cost_center"]="ULTRA MRF - UM"
        elif comp=="My Company": doc["parent_cost_center"]="My Company - MC"
        else:
            ab = {"Ultra MRF Dau Annex":"UMDA","Ultra MRF Dau Main":"UMDM","Ultra MRF Warehouse Dau":"UMDW",
                  "Ultra MRF San Fernando":"UMSF","San Fernando Warehouse":"SFWH","Ultra MRF Telebastagan":"UMTEL",
                  "Ultra MRF Telebastagan 2":"UMTEL2","Ultra MRF Mexico Warehouse":"MEXWH","Automan Car Care Center":"AUTOMAN",
                  "Wheel Core":"WCORE","The Wheelhub":"WHUB"}.get(comp,"UM")
            doc["parent_cost_center"]=f"{comp} - {ab}"
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s==200: ok+=1
    elif s==409: dup+=1
    else:
        if err<8: print(f"  CC FAIL {s} {doc.get('name')}: {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:180]}")
        err+=1
print(f"Cost Center: ok={ok} dup={dup} err={err}")

# 2) POS Profile: add a payments child row
pos = json.load(open("pos-static/export/POS_Profile.json", encoding="utf-8"))
ok=dup=err=0
for r in pos:
    doc = {k:v for k,v in r.items() if k not in STRIP and k!="payments"}
    doc["doctype"]="POS Profile"
    doc["letter_head"]=None
    if default_mop:
        doc["payments"]=[{"mode_of_payment": default_mop, "default":1, "docstatus":0, "idx":1}]
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s==200: ok+=1
    elif s==409: dup+=1
    else:
        if err<6: print(f"  POS FAIL {s} {doc.get('name')}: {str(j.get('exception') or j.get('_error_message') or j.get('message') or j.get('error'))[:180]}")
        err+=1
print(f"POS Profile: ok={ok} dup={dup} err={err}")
print("DONE")
