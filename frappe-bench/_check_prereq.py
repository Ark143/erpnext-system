import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))
import frappe
os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("COMPANIES:", frappe.db.count("Company"))
wh = frappe.get_all("Warehouse", filters={"warehouse_name": ["like", "Stores - %"]}, fields=["name"])
print("STORES WAREHOUSES:", len(wh))
for w in wh: print("  WH:", w.name)
items = ["185/70 R14 YOKOHAMA ES32","WHEEL ALIGNMENT (TOE-IN, TOE-OUT)","PMS LABOR (LIGHT)","STRL-CAR PROTECT KIT (CAR CLEAN SET)"]
for it in items:
    print("ITEM", it, "->", frappe.db.exists("Item", it))
print("BIN LOCATIONS total:", frappe.db.count("Bin Location"))
print("SALES PERSONS:", frappe.db.count("Sales Person"))
print("CUSTOMER VEHICLES:", frappe.db.count("Customer Vehicle"))
bl = frappe.get_all("Bin Location", fields=["warehouse","name"])
from collections import Counter
c = Counter(b["warehouse"] for b in bl)
print("BIN LOCATIONS per warehouse:", dict(c.most_common(20)))
frappe.db.close()
