import urllib.request, re
URL="http://localhost"
# 1) fetch login HTML, get bundle hashes
req=urllib.request.Request(URL+"/login", headers={"Cache-Control":"no-cache"})
html=urllib.request.urlopen(req, timeout=20).read().decode("utf-8","replace")
hashes=re.findall(r'(bootstrap-4-web\.bundle\.[A-Z0-9]+)\.js', html)
fw=re.findall(r'(frappe-web\.bundle\.[A-Z0-9]+)\.js', html)
print("login HTML references bootstrap-4-web:", hashes[:1], "frappe-web:", fw[:1])

# 2) fetch that bootstrap bundle, check dropdown plugin
burl=URL+"/assets/frappe/dist/js/"+hashes[0]+".js"
resp=urllib.request.urlopen(urllib.request.Request(burl, headers={"Cache-Control":"no-cache"}), timeout=20)
body=resp.read().decode("utf-8","replace")
print("bootstrap bundle HTTP:", resp.status, "has _jQueryInterface(dropdown):", "Dropdown._jQueryInterface" in body or "_jQueryInterface" in body, "len:", len(body))
# 3) cache-control header on HTML
hreq=urllib.request.urlopen(urllib.request.Request(URL+"/login", headers={"Cache-Control":"no-cache"}), timeout=20)
print("login HTML Cache-Control:", hreq.headers.get("Cache-Control"))
print("RESULT:", "SERVER OK (browser cache is the problem)" if "_jQueryInterface" in body else "SERVER STILL BROKEN")
