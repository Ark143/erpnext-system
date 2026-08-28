import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
frappe.init('site1.local')
frappe.connect()

print("=== Bin Location Table Details ===")
if frappe.db.table_exists("Bin Location"):
    cols = [c[0] for c in frappe.db.sql("SELECT column_name FROM information_schema.columns WHERE table_name = 'tabBin Location'")]
    print("Columns:", cols)
    records = frappe.db.sql('SELECT * FROM "tabBin Location"', as_dict=True)
    print(f"Total Bin Location records: {len(records)}")
    for r in records[:5]:
        print("  Sample:", r)
else:
    print("tabBin Location table not found!")

print("\n=== tabBin (ERPNext Stock Balance) Details ===")
bin_cols = [c[0] for c in frappe.db.sql("SELECT column_name FROM information_schema.columns WHERE table_name = 'tabBin'")]
print("tabBin columns:", bin_cols)
bins = frappe.db.sql('SELECT name, item_code, warehouse, actual_qty, valuation_rate, stock_value FROM "tabBin" WHERE actual_qty > 0', as_dict=True)
print(f"Stocked items in tabBin: {len(bins)}")
for b in bins[:10]:
    print("  Bin balance:", b)

print("\n=== Warehouses by Company ===")
whs = frappe.db.sql('SELECT name, company, is_group FROM "tabWarehouse" WHERE is_group = 0 ORDER BY company', as_dict=True)
for w in whs[:15]:
    print(f"  {w['company']:30s} -> {w['name']}")
