import frappe, json, os
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
rows = frappe.get_all("Company", fields=["*"], limit_page_length=1000)
os.makedirs("/workspace/export_master", exist_ok=True)
with open("/workspace/export_master/Company.json","w",encoding="utf-8") as f:
    json.dump(rows, f, default=str, ensure_ascii=False)
print("Company exported:", len(rows))
for r in rows[:10]:
    print(" ", r.get("name"), "| default_curr:", r.get("default_currency"))
