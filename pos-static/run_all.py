import subprocess, os
tests = [
 ("Sales","Sales Order"),("Sales","Sales Invoice"),("Sales","Quotation"),("Sales","Delivery Note"),
 ("Purchase","Purchase Order"),("Purchase","Purchase Invoice"),("Purchase","Purchase Receipt"),
 ("Stock","Stock Entry"),("Stock","Material Request"),
 ("Accounts","Payment Entry"),("Accounts","Journal Entry"),
 ("CRM","Lead"),("HR","Employee"),
]
results=[]
for mod,name in tests:
    r = subprocess.run(
        ["/workspace/frappe-bench/env/bin/python","/tmp/one_txn.py",mod,name],
        capture_output=True, text=True, cwd="/workspace/frappe-bench", timeout=120)
    out = (r.stdout+r.stderr).strip().splitlines()
    line = out[-1] if out else ""
    ok = line.startswith("OK")
    results.append((mod,name,ok,line))
    print(f"{mod:12} {name:18} {'OK ' if ok else 'FAIL'} {line}", flush=True)
okc=sum(1 for r in results if r[2]); failc=len(results)-okc
print(f"\n=== {okc} OK / {failc} FAIL of {len(results)} ===")
for r in results:
    if not r[2]: print("  FAIL:", r[0], r[1], "->", r[3])
