import urllib.request, urllib.parse, http.cookiejar, json, ssl

BASE = "http://localhost"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def post(path, data=None, raw=False):
    url = BASE + path
    if raw:
        req = urllib.request.Request(url, data=data.encode() if isinstance(data,str) else data,
                                     headers={"Content-Type":"application/json","Accept":"application/json"})
    else:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                     headers={"Content-Type":"application/json","Accept":"application/json"})
    return op.open(req, timeout=30)

# login
r = post("/api/method/login", {"usr":"administrator","pwd":"admin"})
print("login:", r.status, r.read().decode()[:60])
apis = ["vm_pos_history","vm_pos_cashier","vm_pos_stock","vm_pos_vehicle_customer",
        "vm_pos_vehicles","vm_pos_items","vm_pos_meta","executive_dashboard",
        "vm_company_dashboard_api","vm_probe_api"]
for m in apis:
    try:
        r = post(f"/api/method/{m}")
        body = r.read().decode()
        d = json.loads(body)
        msg = d.get("message")
        sz = len(msg) if isinstance(msg,(list,dict)) else (str(msg)[:40] if msg else "empty")
        print(f"OK   {m}: http={r.status} msg={type(msg).__name__} size={len(msg) if isinstance(msg,(list,dict)) else 0}")
    except urllib.error.HTTPError as e:
        print(f"FAIL {m}: HTTP {e.code} {e.read().decode()[:120]}")
    except Exception as e:
        print(f"FAIL {m}: {type(e).__name__}: {str(e)[:120]}")
