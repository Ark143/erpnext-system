import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# list tables containing 'Job Order'
rows = frappe.db.sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name ILIKE '%job order%' ORDER BY table_name", as_dict=True)
print("TABLES:", [r["table_name"] for r in rows])
# columns of Job Order Service Item
try:
    cols = frappe.db.sql('SELECT column_name FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position', "tabJob Order Service Item", as_dict=True)
    print("Job Order Service Item cols:", [c["column_name"] for c in cols])
except Exception as e:
    print("cols err:", e)
# Does Vehicle Job Order Item table exist?
try:
    frappe.db.sql('SELECT 1 FROM "tabVehicle Job Order Item" LIMIT 1', as_dict=True)
    print("tabVehicle Job Order Item: EXISTS")
except Exception as e:
    print("tabVehicle Job Order Item: MISSING")
