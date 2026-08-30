import frappe, re
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
wp=frappe.get_doc("Web Page","vehicle-pos-terminal")
html = wp.main_section_html or ""
refs = set(re.findall(r'[^"\' >]*ultra_mrf[^"\' >]*', html))
print("POS logo refs:", refs or "NONE")
# also check the navbar via Website Settings / standard template
ws = frappe.get_single("Website Settings")
print("Website Settings app_logo:", ws.app_logo)
