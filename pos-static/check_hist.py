import urllib.request, re
t = urllib.request.urlopen("http://localhost/pos-terminal", timeout=30).read().decode("utf-8", "replace")

# find the History tab button + its handler
i = t.find('History')
print("=== History mentions (tab/button) ===")
for m in re.finditer(r'.{40}History.{120}', t):
    print(" ", m.group(0).replace("\n", " "))

# get_history usage in page
for kw in ["get_history", "vpos-hist", "historyTab", "loadHistory", "showHistory", "this.history", "renderHistory"]:
    j = t.find(kw)
    print(f"\n--- {kw} @ {j} ---")
    if j >= 0:
        print(t[j-60:j+260].replace("\n", " "))
