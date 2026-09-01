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
ws_pages = boot.get("workspaces", {}).get("pages") or []
# build slug->page and title->page maps
slug_map = {}
title_map = {}
for p in ws_pages:
    if isinstance(p, dict):
        nm = p.get("name")
        title = p.get("title")
        if nm: slug_map[nm.lower().replace(" ", "-")] = p
        if nm: slug_map[nm] = p
        if title: title_map[title] = p

print("=== workspace pages names ===")
for p in ws_pages:
    print("  ", p.get("name"), "| title=", p.get("title"))

# The desktop.js does: frappe.workspaces[slug(link_to)]  BUT workspaces is {pages,...}
# Actually check: does the code use frappe.workspaces (dict) or frappe.boot.workspaces.pages?
# Let's see what generate_route gets. But first, find sidebar Links with link_type=Workspace whose
# link_to is NOT in ws_pages (by name/title).
print("\n=== sidebar Workspace links whose target is NOT in workspaces.pages ===")
for key, sb in wsi.items():
    items = sb.get("items") or []
    for i in items:
        if i.get("type") == "Link" and i.get("link_type") == "Workspace":
            lo = i.get("link_to")
            if lo and lo not in title_map and lo not in slug_map:
                print(f"  [{key}] link_to={lo!r} NOT FOUND in workspaces.pages")
