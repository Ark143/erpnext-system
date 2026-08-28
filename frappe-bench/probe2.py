import frappe
print("CONNECTED SITE:", frappe.local.site)
for dt in ["Company","Cost Center","Warehouse","Sales Person","Customer Vehicle","Bin Location",
           "Vehicle Estimate","Vehicle Job Order","Vehicle Inspection","Purchase Order",
           "Purchase Receipt","Purchase Invoice","Sales Invoice","Payment Entry","Stock Entry"]:
    try:
        print("  ", dt, frappe.db.count(dt))
    except Exception as e:
        print("  ", dt, "ERR", e)
