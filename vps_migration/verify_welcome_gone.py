#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar, re
URL = "http://127.0.0.1:8000"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)
r = op.open(urllib.request.Request(URL+"/app", headers=H), timeout=60)
html = r.read().decode("utf-8", "ignore")
m = re.search(r'frappe\.boot\s*=\s*(\{.*?\});', html, re.DOTALL)
boot = json.loads(m.group(1))
wsi = boot.get("workspace_sidebar_item") or {}
# check if 'Welcome Workspace' still appears anywhere in sidebar items
found = []
for key, sb in wsi.items():
    for i in (sb.get("items") or []):
        if "Welcome Workspace" in json.dumps(i):
            found.append((key, i.get("label"), i.get("link_type")))
print("Welcome Workspace still in sidebar:", found if found else "NO (clean)")
