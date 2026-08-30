import urllib.request, re
html=urllib.request.urlopen("http://127.0.0.1:8000/login",timeout=8).read().decode()
links=re.findall(r'<link[^>]*icon[^>]*>', html)
print("icon links:", links or "NONE -> browser will request /favicon.ico (404, cosmetic)")
# also check desk
html2=urllib.request.urlopen("http://127.0.0.1:8000/desk",timeout=8).read().decode()
print("desk icon links:", re.findall(r'<link[^>]*icon[^>]*>', html2) or "NONE")
