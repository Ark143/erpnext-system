import frappe, json

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# Module -> representative DocTypes to verify data + read access
modules = {
    "Core / Setup": ["User", "Role", "Module Def", "DocType", "Company", "Currency"],
    "CRM / Selling": ["Customer", "Customer Group", "Lead", "Opportunity", "Quotation", "Sales Order", "Sales Invoice"],
    "Buying / Purchasing": ["Supplier", "Supplier Group", "Purchase Order", "Purchase Invoice", "Item", "Item Group", "Brand"],
    "Stock": ["Warehouse", "Stock Entry", "Stock Ledger Entry", "Item Price", "Bin"],
    "Accounts": ["Account", "Cost Center", "Journal Entry", "Payment Entry", "GL Entry"],
    "HR": ["Employee", "Department", "Designation", "Attendance", "Salary Slip"],
    "Vehicle Management": ["Vehicle", "Vehicle Make", "Vehicle Model", "Vehicle Job Order", "Vehicle Inspection", "Customer Vehicle", "Vehicle Estimate"],
    "Website / POS": ["Web Page", "Web Form", "Blog Post"],
}

print("=== MODULE DATA VERIFICATION (site1.local, v16) ===")
all_ok = True
for mod, dts in modules.items():
    print(f"\n--- {mod} ---")
    for dt in dts:
        try:
            n = frappe.db.count(dt)
            sample = frappe.get_list(dt, fields=["name"], limit=1)
            s = sample[0]["name"] if sample else "(empty)"
            flag = "OK" if n >= 0 else "XX"
            print(f"  [{flag}] {dt:<28} count={n:<7} e.g. {s}")
        except Exception as e:
            all_ok = False
            print(f"  [XX] {dt:<28} ERROR: {str(e)[:70]}")

print("\n=== SUMMARY ===")
print("ALL MODULES READABLE" if all_ok else "SOME DOCTYPES FAILED (see above)")
