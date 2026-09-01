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
ws = boot.get("workspaces")
print("workspaces type:", type(ws))
if isinstance(ws, dict):
    print("top-level keys:", list(ws.keys()))
    pages = ws.get("pages")
    print("pages type:", type(pages), "count:", len(pages) if isinstance(pages, list) else "n/a")
    if isinstance(pages, list) and pages:
        print("first page keys:", list(pages[0].keys()) if isinstance(pages[0], dict) else pages[0])
        # does each page have 'title'?
        for p in pages:
            if isinstance(p, dict) and not p.get("title"):
                print("  page MISSING title:", p.get("name"), p.get("slug"), list(p.keys()))
