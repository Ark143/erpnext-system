import frappe
frappe.init("site1.local")
frappe.connect()

zero    = frappe.db.sql("SELECT COUNT(*) FROM tabItem WHERE disabled=0 AND (standard_rate IS NULL OR standard_rate = 0)")[0][0]
nonzero = frappe.db.sql("SELECT COUNT(*) FROM tabItem WHERE disabled=0 AND standard_rate > 0")[0][0]
total   = frappe.db.sql("SELECT COUNT(*) FROM tabItem WHERE disabled=0")[0][0]
total_ip= frappe.db.sql("SELECT COUNT(*) FROM tabItem t1 LEFT JOIN tabItem t2 ON 1=0")[0][0] if False else frappe.db.count("Item Price")
print(f"Total items (enabled): {total}")
print(f"Items with rate > 0:   {nonzero}")
print(f"Items with rate = 0:   {zero}")
print(f"Total Item Prices:     {total_ip}")

# Check products (non-service)
products = frappe.db.sql(
    "SELECT COUNT(*) FROM tabItem WHERE disabled=0 AND is_stock_item=1 AND standard_rate > 0"
)[0][0]
print(f"Stock items with rate: {products}")

sample = frappe.db.sql(
    "SELECT item_code, item_name, standard_rate FROM tabItem WHERE is_stock_item=1 AND standard_rate > 0 LIMIT 3",
    as_dict=True,
)
for s in sample:
    print("  SAMPLE:", s)
