import frappe
frappe.init("site1.local")
frappe.connect()
total_ip = frappe.db.count("Item Price")
php_count = frappe.db.sql("SELECT count(*) FROM \"tabItem Price\" WHERE currency='PHP'")[0][0]
print(f"Total Item Prices now: {total_ip}")
print(f"PHP Item Prices: {php_count}")
