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
print("workspace_sidebar_item keys:", list(wsi.keys()))

# For each desktop icon that is "Workspace Sidebar" type with EMPTY link_to,
# check its sidebar items for a Link with missing link_to/type
di = boot.get("desktop_icons") or []
for it in di:
    if it.get("link_type") == "Workspace Sidebar" and not it.get("link_to"):
        label = it.get("label")
        key = label.lower() if label else None
        sb = wsi.get(key) if key else None
        print(f"\n=== Desktop Icon {label!r} (empty link_to, Workspace Sidebar) ===")
        if sb is None:
            print("  NO sidebar entry in workspace_sidebar_item!")
            continue
        items = sb.get("items") or []
        print(f"  sidebar items: {len(items)}")
        for i in items:
            # look for Links with missing link_to or type
            if i.get("type") == "Link":
                lt = i.get("link_type"); lo = i.get("link_to")
                if not lo or not lt:
                    print(f"    !! BROKEN LINK: link_type={lt!r} link_to={lo!r} label={i.get('label')!r}")
                else:
                    print(f"    link ok: link_type={lt!r} link_to={lo!r}")
