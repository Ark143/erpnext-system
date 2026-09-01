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
workspaces = boot.get("workspaces") or {}

print("=== frappe.workspaces (boot) — any missing title? ===")
if isinstance(workspaces, dict):
    for slug, w in workspaces.items():
        t = w.get("title") if isinstance(w, dict) else None
        if not t:
            print(f"  workspace slug={slug!r} MISSING title: {w}")
    print("  total workspaces:", len(workspaces))

print("\n=== sidebar Link items with link_type=Workspace, check their link_to resolves to a workspace with title ===")
for key, sb in wsi.items():
    items = sb.get("items") or []
    for i in items:
        if i.get("type") == "Link" and i.get("link_type") == "Workspace":
            lo = i.get("link_to")
            slug = lo.lower().replace(" ", "-") if lo else None
            w = workspaces.get(slug) if slug else None
            title = w.get("title") if isinstance(w, dict) else None
            print(f"  [{key}] Workspace link link_to={lo!r} slug={slug!r} -> title={title!r}")
