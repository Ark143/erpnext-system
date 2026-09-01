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
        print("LOGIN FAIL", s, j.get("message") if isinstance(j,dict) else j); sys.exit(1)
    csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf

csrf = get_csrf()
print("login OK")

STRIP = ["creation","modified","modified_by","owner","idx","docstatus","lft","rgt","old_parent",
         "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype"]

recs = json.load(open("pos-static/export/Account.json", encoding="utf-8"))
print("total account export:", len(recs))

# order: groups first, then by depth (parent before child) via lft if present
recs_sorted = sorted(recs, key=lambda r: (0 if r.get("is_group") else 1, r.get("lft") or 0))

skip = dup = ok = fail = 0
failures = []
for r in recs_sorted:
    doc = dict(r)
    for k in STRIP: doc.pop(k, None)
    doc["doctype"] = "Account"
    name = doc.get("name")
    s,j = post("/api/method/frappe.client.insert", {"doc": doc}, csrf)
    if s == 200:
        ok += 1
    elif s == 409:
        dup += 1   # already existed (standard CoA auto-created)
    else:
        exc = str(j.get("exception") or j.get("_error_message") or j.get("message") or j.get("error"))[:160]
        # some are permission errors -> hard fail, stop and report
        if s == 403:
            fail += 1
            failures.append((name, f"403 {exc}"))
            print(f"  PERM FAIL {name}: {exc}")
            break
        else:
            fail += 1
            failures.append((name, f"{s} {exc}"))
            if len(failures) <= 10:
                print(f"  FAIL {s} {name}: {exc}")

print(f"RESULT account import: ok={ok} dup(skip)={dup} fail={fail}")
if failures:
    print("first failures:", failures[:10])
# re-count on cloud
s,j = post("/api/method/frappe.client.get_count", {"doctype":"Account"}, csrf)
print("Account count on cloud now:", s, j.get("message") if s==200 else j.get("exception"))
print("DONE")
