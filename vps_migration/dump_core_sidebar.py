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

# dump "core" sidebar items fully
print("=== [core] sidebar items ===")
core = wsi.get("core")
print(json.dumps(core, indent=2)[:3000])

# dump desktop_icons with their link_type/label/link_to
print("\n=== desktop_icons (label, link_type, link_to, idx) ===")
for it in boot.get("desktop_icons") or []:
    print(f"  label={it.get('label')!r} link_type={it.get('link_type')!r} link_to={it.get('link_to')!r} icon_type={it.get('icon_type')!r} sidebar={it.get('sidebar')!r}")
