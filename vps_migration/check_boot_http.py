#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar
URL = "http://127.0.0.1:8000"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)

# fetch boot payload
r = op.open(urllib.request.Request(URL+"/api/method/frappe.desk.page.setup.setup?name=desktop", headers=H), timeout=60)
body = json.loads(r.read().decode())
boot = body.get("message", {})
print("boot keys:", list(boot.keys()))

di = boot.get("desktop_icons") or []
print("\ndesktop_icons count:", len(di))
for it in di:
    lbl = it.get("label")
    if lbl in (None, ""):
        print("  NULL-LABEL ICON:", json.dumps(it))
    # also flag icons whose link_type needs a label for slug
print("(scanned for null labels)")

wsi = boot.get("workspace_sidebar_item") or {}
print("\nworkspace_sidebar_item keys:", list(wsi.keys())[:20])
