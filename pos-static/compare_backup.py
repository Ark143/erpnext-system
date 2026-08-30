import gzip, re, sys

backup = "/tmp/site1_local_database.sql.gz"
# tables to compare (name, live_count)
tables = [
    ("tabCustomer", 39466), ("tabItem", 10531), ("tabSales Invoice", 139),
    ("tabLead", None), ("tabOpportunity", None), ("tabSales Order", None),
    ("tabQuotation", None), ("tabJournal Entry", None), ("tabBrand", None),
    ("tabSupplier", 832), ("tabPurchase Order", 12), ("tabPurchase Invoice", 82),
    ("tabWarehouse", 76), ("tabStock Entry", 11), ("tabAccount", 1237),
    ("tabEmployee", 190), ("tabVehicle Job Order", 481), ("tabVehicle Inspection", 476),
    ("tabCustomer Vehicle", 38654), ("tabPayment Entry", 220), ("tabGL Entry", 906),
]

# parse COPY blocks: COPY public."TABLENAME" (cols) FROM stdin; ... data ... \.
counts = {}
cur = None
import io
with gzip.open(backup, "rt") as f:
    for line in f:
        m = re.match(r'COPY public\."([^"]+)" \(', line)
        if m:
            cur = m.group(1)
            counts[cur] = 0
            continue
        if cur is not None:
            if line.strip() == "\\.":
                cur = None
                continue
            counts[cur] += 1

print(f"{'DocType':<28}{'backup':>10}{'live':>10}  match")
print("-"*62)
allmatch = True
for t, live in tables:
    b = counts.get(t, "MISSING")
    livestr = str(live) if live is not None else "?"
    match = (b == live) if live is not None else True
    if not match: allmatch=False
    print(f"{t:<28}{str(b):>10}{livestr:>10}  {'OK' if match else 'DIFF!'}")
print("-"*62)
print("RESTORE FAITHFUL" if allmatch else "MISMATCH FOUND (restore dropped data)")
