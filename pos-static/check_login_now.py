import urllib.request, re
URL="https://advantage-hunting-apparatus-characteristics.trycloudflare.com"
html=urllib.request.urlopen(URL+"/login", timeout=25).read().decode("utf-8","replace")
bundles=set(re.findall(r'([a-z0-9_-]+\.bundle\.[A-Z0-9]+\.js)', html))
print("BUNDLES REFERENCED BY /login:")
for b in sorted(bundles):
    print("  ", b)
print("references NEW bootstrap-4-web (MVRJUAWY):", any("MVRJUAWY" in b for b in bundles))
print("references NEW frappe-web (5Q2RSY42):", any("5Q2RSY42" in b for b in bundles))
