import json, sys, urllib.request, urllib.parse, http.cookiejar, os, time, re
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
    if s!=200: print("LOGIN FAIL", s); sys.exit(1)
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": return c.value

csrf = get_csrf()
print("login OK", flush=True)

# Fetch ALL customers (name, customer_name) via pagination
all_rows = []
start = 0
while True:
    s,j = post("/api/method/frappe.client.get_list",
               {"doctype":"Customer","fields":["name","customer_name"],
                "limit_page_length":1000,"limit_start":start}, csrf)
    page = j.get("message") or []
    if s!=200 or not page: break
    all_rows.extend(page)
    if len(page) < 1000: break
    start += 1000
    if start % 10000 == 0:
        print(f"  fetched {start}...", flush=True)

print(f"total cloud customers fetched: {len(all_rows)}", flush=True)

# identify duplicates: name matches "<customer_name> - <digits>"
canonical = {r["name"] for r in all_rows if r.get("customer_name")==r["name"]}
dup_rows = []
for r in all_rows:
    nm = r["name"]; cn = r.get("customer_name") or ""
    m = re.match(r"^(.*) - \d+$", nm)
    if m and m.group(1) in canonical:
        dup_rows.append(r)

print(f"DUPLICATES to delete: {len(dup_rows)}", flush=True)

# BACKUP: write duplicate names to local file before deletion
backup_path = "pos-static/export/duplicate_customers_backup.json"
json.dump({"duplicates": dup_rows, "total_cloud": len(all_rows)},
          open(backup_path, "w", encoding="utf-8"), indent=1)
print(f"backup written: {backup_path}", flush=True)

# also write the canonical+dup full name list for reference
json.dump([r["name"] for r in dup_rows],
          open("pos-static/export/dup_names.txt", "w", encoding="utf-8"), indent=1)
print("dup names list written", flush=True)
