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
di = boot.get("desktop_icons") or []
print("total desktop_icons:", len(di))
for i, it in enumerate(di):
    lbl = it.get("label")
    typ = it.get("icon_type")
    lt = it.get("link_type")
    name = it.get("name") or it.get("idx")
    # flag any that would crash get_route: non-folder, no sidebar, no label
    if typ != "Folder" and not it.get("sidebar") and lbl in (None, ""):
        print(f"  [{i}] CRASH-CANDIDATE: name={name!r} label={lbl!r} icon_type={typ!r} link_type={lt!r}")
    # also show any with missing label at all
    if lbl in (None, ""):
        print(f"  [{i}] NO-LABEL: name={name!r} icon_type={typ!r} link_type={lt!r} keys={list(it.keys())}")
print("done")
