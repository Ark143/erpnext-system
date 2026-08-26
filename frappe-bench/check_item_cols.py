import frappe, json
frappe.init("site1.local")
frappe.connect()

cols = frappe.db.sql(
    "SELECT column_name FROM information_schema.columns WHERE table_name='tabItem' AND (column_name LIKE '%price%' OR column_name LIKE '%rate%')",
    as_dict=False,
)
print("Price/rate columns:", [c[0] for c in cols])

resp = frappe.db.sql(
    "SELECT item_code, item_name, standard_rate FROM tabItem WHERE disabled=0 LIMIT 5",
    as_dict=True,
)
print(json.dumps(resp, default=str, indent=2))
