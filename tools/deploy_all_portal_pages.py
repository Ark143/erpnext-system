import urllib.request, urllib.parse, json, http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f"{BASE}/api/method/login", data=data, headers=H))
print("[+] Logged into VPS")

pos_path = r"frappe-bench\apps\vehicle_management\vehicle_management\www\appointment.html"
with open(pos_path, "r", encoding="utf-8") as f:
    html = f.read()

def deploy_page_safely(page_name, route, title):
    # Step 1: Create minimal if not exists
    chk_req = urllib.request.Request(f"{BASE}/api/resource/Web%20Page/{urllib.parse.quote(page_name)}", headers={'Accept': 'application/json'})
    page_exists = False
    try:
        with op.open(chk_req) as res:
            if res.status == 200:
                page_exists = True
    except Exception:
        page_exists = False

    if not page_exists:
        init_payload = {
            'doctype': 'Web Page',
            'name': page_name,
            'title': title,
            'route': route,
            'published': 1,
            'content_type': 'HTML',
            'main_section_html': '<div id="portal-init">Loading ULTRA MRF Portal...</div>',
            'full_width': 1,
            'show_title': 0,
            'show_sidebar': 0
        }
        req_create = urllib.request.Request(
            f"{BASE}/api/resource/Web%20Page",
            data=urllib.parse.urlencode({'data': json.dumps(init_payload)}).encode(),
            headers=H
        )
        try:
            res_c = op.open(req_create)
            print(f"[+] Initialized Web Page '{page_name}' (HTTP {res_c.status})")
        except Exception as e:
            print(f"[-] Note on creation: {e}")

    # Step 2: PUT the rich HTML
    req_put = urllib.request.Request(
        f"{BASE}/api/resource/Web%20Page/{urllib.parse.quote(page_name)}",
        data=urllib.parse.urlencode({'data': json.dumps({
            'title': title,
            'route': route,
            'published': 1,
            'content_type': 'HTML',
            'main_section_html': html,
            'full_width': 1,
            'show_title': 0,
            'show_sidebar': 0
        })}).encode(),
        headers=H
    )
    req_put.get_method = lambda: 'PUT'
    try:
        res_put = op.open(req_put)
        print(f"[+] Successfully deployed rich HTML to '{page_name}' -> /{route} (HTTP {res_put.status})")
    except Exception as e:
        print(f"[-] PUT failed: {e}")

deploy_page_safely("appointment", "appointment", "ULTRA MRF - Appointment Scheduling & Customer VMS Portal")
deploy_page_safely("booking", "booking", "ULTRA MRF - Service Booking Portal")
deploy_page_safely("customer-portal", "customer-portal", "ULTRA MRF - Customer VMS Portal Hub")

# Test live fetch
req_test = urllib.request.Request(f"{BASE}/appointment", headers={'Accept': 'text/html'})
try:
    with op.open(req_test) as res_t:
        body = res_t.read().decode('utf-8')
        print(f"\n[+] Verified /appointment Live Status: HTTP {res_t.status} (Length: {len(body)} bytes)")
except Exception as e:
    print(f"[-] Test fetch failed: {e}")
