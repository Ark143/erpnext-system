import frappe, json, os
SITE="site1.local"; SP="/workspace/frappe-bench/sites"
# 1) enable developer mode in site_config.json
cfg = os.path.join(SP, SITE, "site_config.json")
d = json.load(open(cfg))
d["developer_mode"] = 1
json.dump(d, open(cfg,"w"), indent=1)
print("developer_mode set in site_config")

# 2) add field in same process
frappe.init(site=SITE, sites_path=SP); frappe.connect()
meta = frappe.get_doc("DocType", "Stock Entry Detail")
if not any(f.fieldname=="secondary_item_type" for f in meta.fields):
    meta.append("fields", {"fieldname":"secondary_item_type","fieldtype":"Data","label":"Secondary Item Type","insert_after":"bom_secondary_item","hidden":1,"read_only":1})
    meta.save(ignore_permissions=True)
    print("field added")
else:
    print("field exists")
frappe.db.commit()
