import urllib.request, re
t = urllib.request.urlopen("http://localhost/pos-terminal", timeout=30).read().decode("utf-8", "replace")

# History tab logic
i = t.find("async history(")
print("=== history() ===")
print(t[i:i+700] if i >= 0 else "NOT FOUND")

# afterCheckout / after sale handling
for kw in ["afterCheckout", "afterSale", "VMSPOS", "showInvoice", "invoice no", "Invoice No", "pos_invoice", "clearCart", "Toast"]:
    j = t.find(kw)
    print(f"\n--- {kw} @ {j} ---")
    if j >= 0:
        print(t[j-80:j+200].replace("\n", " "))
