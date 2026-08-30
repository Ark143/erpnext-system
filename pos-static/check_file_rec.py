import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
rows = frappe.db.get_all("File", filters={"file_name": ["like", "%ultra_mrf_logo%"]},
                         fields=["name", "file_name", "file_url", "is_private", "attached_to_doctype"])
print("existing logo File records:", json.dumps(rows, default=str))
