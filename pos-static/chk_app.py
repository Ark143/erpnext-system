import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# frappe reads app_icon from hooks at get_app_info time
from frappe.utils.boot import get_apps_info
try:
    apps = get_apps_info()
    for a in apps:
        if "vehicle" in str(a.get("app_name","")).lower() or "vehicle" in str(a).lower():
            print("APP INFO:", a)
except Exception as e:
    print("get_apps_info err:", e)
# Also check installed_apps + desk sidebar items
print("installed_apps:", frappe.get_installed_apps())
# The desk sidebar icon comes from Workspace Sidebar / app icon. Check the vehicle_management app icon directly:
import importlib
try:
    hooks=importlib.import_module("vehicle_management.hooks")
    print("hooks.app_icon =", getattr(hooks,"app_icon", "MISSING"))
except Exception as e:
    print("hooks import err:", e)
