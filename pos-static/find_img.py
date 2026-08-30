import urllib.request, re
for pg in ["/", "/pos-terminal"]:
    t = urllib.request.urlopen("http://localhost"+pg, timeout=30).read().decode("utf-8", "replace")
    for m in re.finditer(r'<img[^>]*ultra_mrf_logo[^>]*>', t):
        print(pg, "->", m.group(0)[:200])
        print("     context:", t[m.start()-60:m.start()+len(m.group(0))+20].replace("\n"," "))
