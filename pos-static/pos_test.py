import urllib.request, urllib.parse, http.cookiejar, ssl

BASE = "http://10.88.0.2"
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def req(path, data=None, headers=None):
    url = BASE+path
    h = {"Content-Type":"application/x-www-form-urlencoded"}
    if headers: h.update(headers)
    body = urllib.parse.urlencode(data).encode() if data else None
    r = op.open(urllib.request.Request(url, data=body, headers=h), timeout=30)
    return r.status, r.read().decode("utf-8","replace")

print("1) desk (no auth) ->", req("/desk")[0])
print("2) login API      ->", req("/api/method/login", {"cmd":"login","usr":"administrator","pwd":"admin"})[0])
print("3) desk (auth)    ->", req("/desk")[0])

st, html = req("/pos-terminal")
print("4) pos-terminal   ->", st, "| bytes:", len(html))
for marker in ["vpos-root","vpos-mobile-cart-bar","vehicle-pos-terminal","@media (max-width:768px)"]:
    print("     contains", marker, ":", marker in html)

st2, body2 = req("/api/method/frappe.auth.get_logged_user")
print("5) get_logged_user->", st2, "|", body2[:120])
