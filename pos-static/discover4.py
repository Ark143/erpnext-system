import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
ss = frappe.get_all("Server Script", fields=["name","script_type","disabled","api_method"], limit=200)
print("SERVER SCRIPTS:", len(ss))
for s in ss:
    print("  ", s["name"], "|", s.get("script_type"), "| api=", s.get("api_method"), "| disabled=", s.get("disabled"))
