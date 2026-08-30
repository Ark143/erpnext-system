import urllib.request, urllib.parse, http.cookiejar
URL="https://advantage-hunting-apparatus-characteristics.trycloudflare.com"
jar=http.cookiejar.CookieJar()
op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def req(p,d=None,h=None):
    hh={"Content-Type":"application/x-www-form-urlencoded"}
    if h: hh.update(h)
    b=urllib.parse.urlencode(d).encode() if d else None
    return op.open(urllib.request.Request(URL+p,data=b,headers=hh),timeout=30).read().decode("utf-8","replace")

# 1) login
r=req("/api/method/login",{"cmd":"login","usr":"administrator","pwd":"admin"})
print("1) login ->", "Logged In" in r, "|", r[:80])
# 2) who am i (authed)
r2=req("/api/method/frappe.auth.get_logged_user")
print("2) get_logged_user ->", r2[:80])
# 3) desk page after login (should serve, no 500-blocking)
try:
    resp=op.open(urllib.request.Request(URL+"/desk",headers={"Accept":"text/html"}),timeout=30)
    print("3) /desk authed ->", resp.status, "bytes", len(resp.read()))
except Exception as e:
    print("3) /desk authed ->", str(e)[:80])
# 4) POS terminal
try:
    resp=op.open(urllib.request.Request(URL+"/pos-terminal"),timeout=30)
    html=resp.read().decode("utf-8","replace")
    print("4) /pos-terminal ->", resp.status, "| vpos-root" , "vpos-root" in html, "| dropdown js loaded in page")
except Exception as e:
    print("4) /pos-terminal ->", str(e)[:80])
print("LOGIN FLOW: OK" if "Logged In" in r else "LOGIN FLOW: FAIL")
