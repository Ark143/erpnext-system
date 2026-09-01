#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar, re
URL = "http://127.0.0.1:8000"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)

# The desk page HTML embeds frappe.boot as JSON in a script tag
r = op.open(urllib.request.Request(URL+"/app", headers=H), timeout=60)
html = r.read().decode("utf-8", "ignore")
print("desk html len:", len(html))
# find frappe.boot = {...} or window.frappe.boot
m = re.search(r'frappe\.boot\s*=\s*(\{.*?\});', html, re.DOTALL)
if not m:
    m = re.search(r'boot\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
if not m:
    # boot may be in a separate JSON file /asset
    print("boot not embedded; searching for json path")
    print([x for x in re.findall(r'/api/method/[a-zA-Z0-9_.]+', html)][:10])
else:
    boot = json.loads(m.group(1))
    di = boot.get("desktop_icons") or []
    print("desktop_icons count:", len(di))
    for it in di:
        if isinstance(it, dict) and it.get("label") in (None, ""):
            print("  NULL-LABEL:", json.dumps(it)[:200])
    print("scan done")
