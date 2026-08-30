import frappe, importlib
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
print("installed_apps:", frappe.get_installed_apps())
try:
    hooks=importlib.import_module("vehicle_management.hooks")
    print("hooks.app_icon =", getattr(hooks,"app_icon", "MISSING"))
    print("hooks.add_to_apps_screen =", getattr(hooks,"add_to_apps_screen", None))
except Exception as e:
    print("hooks import err:", e)
# check desk sidebar: the error is raised client-side; confirm the workspace icon is valid
ws=frappe.get_doc("Workspace","Vehicle Management")
print("VM workspace icon:", ws.icon, "| module:", ws.module, "| app:", ws.app)
