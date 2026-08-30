import urllib.request, re
t = urllib.request.urlopen("http://localhost/pos-terminal", timeout=30).read().decode("utf-8", "replace")
# find logo references
for m in re.finditer(r'[^\"\x27 ]*ultra_mrf_logo[^\"\x27 )]*', t):
    print("PAGE ref:", m.group(0))
# also context
i = t.find("ultra_mrf_logo")
print("--- context ---")
print(t[i-120:i+60].replace("\n", " "))
