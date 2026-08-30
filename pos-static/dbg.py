import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
try:
    print("WS exists:", frappe.db.exists("Website Settings"))
    if frappe.db.exists("Website Settings"):
        ws = frappe.get_doc("Website Settings")
        print("theme:", ws.website_theme)
        print("index:", ws.index_page)
    # try rendering the css include path
    from frappe.website.router import get_page_info
    print("OK")
except Exception:
    traceback.print_exc()
