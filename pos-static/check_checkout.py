import urllib.request, re
t = urllib.request.urlopen("http://localhost/pos-terminal", timeout=30).read().decode("utf-8", "replace")

# the create_from_pos call site + surrounding success handler
j = t.find("create_from_pos")
print("=== around create_from_pos call ===")
print(t[j-200:j+700].replace("\n", " "))

# Whats the onclick of the checkout/pay button?
for kw in ["doCheckout", "checkout()", "payNow", "btnPay", "vpos-pay", "await this.checkout", "this.checkout"]:
    k = t.find(kw)
    print(f"\n--- {kw} @ {k} ---")
    if k >= 0:
        print(t[k-80:k+260].replace("\n", " "))
