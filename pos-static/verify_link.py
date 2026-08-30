import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
v = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html") or ""
print("DB has fixed link:", 'Form/Vehicle POS Invoice/"+r.name' in v)
print("DB still has broken link:", 'Form/POS Invoice/"+r.pos_invoice' in v)
# clear all caches that could hold the rendered page
frappe.cache.flushdb()
print("cache flushed")
