import urllib.request, urllib.parse, http.cookiejar, json

BASE = "http://localhost"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def req(method, path, data=None):
    url = BASE + path
    if method == "GET" and data:
        url += "?" + urllib.parse.urlencode(data)
    headers = {"Accept":"application/json"}
    if method == "POST" and data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    else:
        body = None
    r = op.open(urllib.request.Request(url, data=body, headers=headers, method=method), timeout=30)
    return r.status, r.read().decode()

r = req("POST", "/api/method/login", {"usr":"administrator","pwd":"admin"})
print("login:", r[0])
apis = ["vm_pos_meta","vm_pos_history","vm_pos_cashier","vm_pos_items","vm_pos_vehicles",
        "vm_pos_vehicle_customer","vm_pos_stock","executive_dashboard","vm_company_dashboard_api","vm_probe_api"]
for m in apis:
    try:
        # GET with no body (server scripts read form_dict; GET query params populate it)
        st, body = req("GET", f"/api/method/{m}")
        d = json.loads(body)
        msg = d.get("message")
        sz = len(msg) if isinstance(msg,(list,dict)) else 0
        print(f"OK   {m}: http={st} type={type(msg).__name__} size={sz}")
    except urllib.error.HTTPError as e:
        print(f"FAIL {m}: HTTP {e.code} {e.read().decode()[:130]}")
    except Exception as e:
        print(f"FAIL {m}: {type(e).__name__}: {str(e)[:130]}")
