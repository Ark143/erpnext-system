import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))
import frappe
os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

COMPANIES = [
    ("Ultra MRF Dau Main","UMDM"),("Ultra MRF Dau Annex","UMDA"),
    ("Ultra MRF San Fernando","UMSF"),("Wheel Core","WCORE"),
    ("Ultra MRF Telebastagan","UMTEL"),("Automan Car Care Center","AUTOMAN"),
    ("The Wheelhub","WHUB"),("ULTRA MRF","UM"),
    ("Ultra MRF Warehouse Dau","UMDW"),("San Fernando Warehouse","SFWH"),
    ("Ultra MRF Mexico Warehouse","MEXWH"),
]
print(f"{'COMPANY':28} {'co?':4} {'wh?':4} {'bins':5} {'cc?':4} {'cash':5} {'debt':6} {'cred':6} {'sales':6} {'cogs':6}")
for name, abbr in COMPANIES:
    co = frappe.db.exists("Company", name)
    wh = f"Stores - {abbr}"
    whex = frappe.db.exists("Warehouse", wh)
    bins = frappe.db.count("Bin Location", {"warehouse": wh}) if whex else 0
    cc = frappe.db.exists("Cost Center", f"Main - {abbr}")
    cash = frappe.db.exists("Account", f"Cash - {abbr}")
    debt = frappe.db.exists("Account", f"Debtors - {abbr}")
    cred = frappe.db.exists("Account", f"Creditors - {abbr}")
    sales = frappe.db.exists("Account", f"Sales - {abbr}")
    cogs = frappe.db.exists("Account", f"Cost of Goods Sold - {abbr}")
    print(f"{name:28} {str(bool(co)):4} {str(bool(whex)):4} {bins:5} {str(bool(cc)):4} {str(bool(cash)):5} {str(bool(debt)):6} {str(bool(cred)):6} {str(bool(sales)):6} {str(bool(cogs)):6}")
print("ALL COMPANIES IN DB:")
for c in frappe.get_all("Company", fields=["name","abbr"]):
    print("  ", c.name, "(", c.abbr, ")")
frappe.db.close()
