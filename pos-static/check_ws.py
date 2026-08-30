import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
ws = frappe.get_single("Website Settings")
print("app_logo:", repr(ws.app_logo))
print("app_title:", repr(ws.app_title))
# navbar template source
import inspect
from frappe.website.template import get_navbar
print("navbar src snippet:")
src = inspect.getsource(get_navbar)
i = src.find("app_logo")
print(src[max(0,i-200):i+200] if i>=0 else "app_logo not in get_navbar")
