import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
COMPANY = "ULTRA MRF"
charts = frappe.get_all("Dashboard Chart", pluck="name")
fixed = []
for cname in charts:
    dc = frappe.get_doc("Dashboard Chart", cname)
    if dc.report_name and "trend" in dc.report_name.lower():
        fj = json.loads(dc.filters_json or "{}")
        if not fj.get("company"):
            fj["company"] = COMPANY
            dc.filters_json = json.dumps(fj)
            dc.save(ignore_permissions=True)
            fixed.append((cname, fj))
            print("FIXED:", cname, "->", dc.filters_json)
frappe.db.commit()
print("\nTotal trend charts fixed:", len(fixed))
