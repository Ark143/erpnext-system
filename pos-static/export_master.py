import frappe, json, os
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

OUT = "/workspace/export_master"
os.makedirs(OUT, exist_ok=True)

# Master-data DocTypes to migrate (verified counts; excludes transactions)
dtypes = [
    "Item Group", "Customer Group", "Supplier Group", "Price List",
    "Vehicle Make", "Vehicle Model",
    "Warehouse", "Account", "Cost Center", "POS Profile", "Mode of Payment", "Bin",
    "Cashier Profile", "Inspection Template", "Item Part Cross Reference", "Item Vehicle Compatibility",
    "Supplier", "Item", "Customer", "Customer Vehicle",
]

for dt in dtypes:
    try:
        rows = frappe.get_all(dt, fields=["*"], limit_page_length=100000)
    except Exception as e:
        print(f"SKIP {dt}: {e}")
        continue
    path = os.path.join(OUT, f"{dt.replace(' ', '_')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, default=str, ensure_ascii=False)
    print(f"{dt}: {len(rows)} -> {path}")
print("DONE")
