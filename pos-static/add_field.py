import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
dt = "Stock Entry Detail"
meta = frappe.get_doc("DocType", dt)
exists = [f.fieldname for f in meta.fields if f.fieldname == "secondary_item_type"]
if not exists:
    meta.append("fields", {
        "fieldname": "secondary_item_type",
        "fieldtype": "Data",
        "label": "Secondary Item Type",
        "insert_after": "bom_secondary_item",
        "hidden": 1,
        "read_only": 1,
    })
    meta.save(ignore_permissions=True)
    print("added field secondary_item_type")
else:
    print("field already exists")
frappe.db.commit()
