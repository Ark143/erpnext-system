import urllib.request, urllib.parse, http.cookiejar, re
URL="http://localhost"
jar=http.cookiejar.CookieJar()
op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def req(p,d=None):
    hh={"Content-Type":"application/x-www-form-urlencoded"}
    b=urllib.parse.urlencode(d).encode() if d else None
    return op.open(urllib.request.Request(URL+p,data=b,headers=hh),timeout=30).read().decode("utf-8","replace")
r=req("/api/method/login",{"cmd":"login","usr":"administrator","pwd":"admin"})
print("1) login ->", "Logged In" in r)
r2=req("/api/method/frappe.auth.get_logged_user")
print("2) user ->", r2[:60])
try:
    resp=op.open(urllib.request.Request(URL+"/desk"),timeout=30); print("3) /desk ->", resp.status)
except Exception as e: print("3) /desk ->", str(e)[:50])
# verify fixed bundle referenced
html=op.open(urllib.request.Request(URL+"/login"),timeout=30).read().decode("utf-8","replace")
print("4) login references MVRJUAWY (fixed bootstrap):", "MVRJUAWY" in html)
print("5) login references 5Q2RSY42 (fixed frappe-web):", "5Q2RSY42" in html)
print("LOGIN FLOW:", "OK" if "Logged In" in r else "FAIL")
