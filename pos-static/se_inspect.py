import frappe, sys, io, traceback
SITE="site1.local"; SP="/workspace/frappe-bench/sites"
frappe.init(site=SITE, sites_path=SP); frappe.connect()
co="ULTRA MRF"
def first(d, **f):
    r=frappe.get_all(d, filters=f, limit=1, pluck="name"); return r[0] if r else None
item = first("Item", is_sales_item=1, disabled=0) or first("Item", disabled=0)
wh   = first("Warehouse", company=co) or first("Warehouse")
buf=io.StringIO()
try:
    d=frappe.get_doc({"doctype":"Stock Entry","stock_entry_type":"Material Receipt","company":co,
        "items":[{"item_code":item,"qty":1,"t_warehouse":wh,"basic_rate":50}]})
    d.insert(ignore_permissions=True)
    print("INSERT OK:", d.name)
except Exception:
    traceback.print_exc(file=buf)
    print("INSERT FAIL:")
    print(buf.getvalue()[-2000:])
    try: frappe.db.rollback()
    except: pass
