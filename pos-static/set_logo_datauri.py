import frappe, base64, os
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
path = "/workspace/frappe-bench/sites/site1.local/public/files/ultra_mrf_logo.png"
with open(path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
data_uri = "data:image/png;base64," + b64
ws = frappe.get_single("Website Settings")
ws.app_logo = data_uri
ws.save(ignore_permissions=True)
frappe.db.commit()
# verify
ws2 = frappe.get_single("Website Settings")
print("app_logo now startswith data:image/png;base64:", ws2.app_logo.startswith("data:image/png;base64,"))
print("len:", len(ws2.app_logo))
