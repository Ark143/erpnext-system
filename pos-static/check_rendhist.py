import urllib.request, re
t = urllib.request.urlopen("http://localhost/pos-terminal", timeout=30).read().decode("utf-8", "replace")
# show renderHistory body + show() tab switch
i = t.find("renderHistory()")
print("=== renderHistory() ===")
print(t[i:i+900].replace("\n", " "))

# after a successful create_from_pos, does it switch to history view?
for kw in ["switchTab(\"history\")", "switchTab('history')", "renderHistory()", "tab=\"history\"", "this.renderHistory", "show(\"history\")", "openHistory"]:
    j = t.find(kw)
    print(f"\n--- {kw} @ {j} ---")
    if j >= 0:
        print(t[j-120:j+160].replace("\n", " "))
