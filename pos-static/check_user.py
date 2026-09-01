import json, urllib.request, urllib.parse, http.cookiejar, os
BASE = "https://demoerpnext.s.frappe.cloud"
USR = os.environ.get("CLOUD_USR"); PWD = os.environ.get("CLOUD_PWD")
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def post(path, payload, csrf=None):
    path = urllib.parse.quote(path, safe="/: ")
    req = urllib.request.Request(BASE+path, json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Accept","application/json")
    if csrf: req.add_header("X-Frappe-CSRF-Token", csrf)
    try: r = op.open(req, timeout=60); return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {"error": e.reason}
        return e.code, body
def get_csrf():
    s,j = post("/api/method/login", {"usr":USR,"pwd":PWD}); csrf=None
    for d in cj._cookies.values():
        for p in d.values():
            for c in p.values():
                if c.name=="csrf_token": csrf=c.value
    return csrf
csrf = get_csrf()
# current user + roles
s,j = post("/api/method/frappe.realtime.get_user_info", {}, csrf)
print("user info:", j.get("message") if s==200 else j)
s2,j2 = post("/api/resource/User", {"filters":["email", "=", USR], "fields":["name","roles"]}, csrf)
print("user doc:", j2.get("message") if s2==200 else j2)
# try get_roles
s3,j3 = post("/api/method/frappe.client.get_roles", {"doctype":"User","txt":USR}, csrf)
print("roles via get_roles:", j3.get("message") if s3==200 else j3)
