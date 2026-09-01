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

# Find every Link item with type=="Link" but missing link_type or link_to
print("=== Scanning all sidebar items for Link with missing link_type/link_to ===")
found = 0
for key, sb in wsi.items():
    items = sb.get("items") or []
    for i in items:
        if i.get("type") == "Link":
            lt = i.get("link_type")
            lo = i.get("link_to")
            if lt in (None, "") or lo in (None, ""):
                found += 1
                print(f"  [{key}] Link MISSING: link_type={lt!r} link_to={lo!r} label={i.get('label')!r} keys={list(i.keys())}")
print("total broken links:", found)

# Also: for each desktop icon, confirm which ones have link_type="Workspace Sidebar" and whether sidebar key exists
di = boot.get("desktop_icons") or []
print("\n=== Desktop icons with Workspace Sidebar type, sidebar lookup ===")
for it in di:
    if it.get("link_type") == "Workspace Sidebar":
        lbl = it.get("label")
        key = lbl.lower() if lbl else None
        exists = key in wsi
        if not exists:
            print(f"  icon label={lbl!r} -> sidebar key {key!r} MISSING")
print("done")
