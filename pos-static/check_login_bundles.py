import urllib.request

URL="https://advantage-hunting-apparatus-characteristics.trycloudflare.com"
html=urllib.request.urlopen(URL+"/login", timeout=25).read().decode("utf-8","replace")
import re
bundles=set(re.findall(r'([a-z0-9_-]+\.bundle\.[A-Z0-9]+\.js)', html))
print("BUNDLES REFERENCED BY /login:")
for b in sorted(bundles):
    print("  ", b)
print("references bootstrap-4-web:", any("bootstrap-4-web" in b for b in bundles))
