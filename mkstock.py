import frappe
frappe.init(site="erp.localhost", sites_path="/workspace/frappe-bench/sites")
frappe.connect(); frappe.set_user("Administrator")

script = """
def vm_pos_stock():
    fd = frappe.form_dict or {}
    raw = fd.get("codes") or ""
    codes = [c.strip() for c in str(raw).split(",") if c.strip()]
    result = {}
    if not codes:
        frappe.response["message"] = result
        return
    ph = ", ".join(["%s"] * len(codes))
    bins = frappe.db.sql('SELECT item_code, warehouse, actual_qty FROM "tabBin" WHERE item_code IN (' + ph + ') AND actual_qty <> 0', codes, as_dict=True)
    locs = frappe.db.sql('SELECT item_code, warehouse, bin_location FROM "tabStock Ledger Entry" WHERE item_code IN (' + ph + ') AND bin_location IS NOT NULL AND bin_location <> %s ORDER BY creation DESC', codes + [''], as_dict=True)
    binmap = {}
    for l in locs:
        key = l['item_code'] + '||' + l['warehouse']
        if key not in binmap:
            binmap[key] = l['bin_location']
    for b in bins:
        ic = b['item_code']
        if ic not in result:
            result[ic] = {'stock': 0, 'bins': []}
        qty = float(b['actual_qty'] or 0)
        result[ic]['stock'] = result[ic]['stock'] + qty
        loc = binmap.get(ic + '||' + b['warehouse'], '')
        result[ic]['bins'].append({'warehouse': b['warehouse'], 'qty': qty, 'bin': loc})
    for ic in result:
        result[ic]['stock'] = round(result[ic]['stock'], 2)
    frappe.response['message'] = result
vm_pos_stock()
"""

name = "VM POS Stock"
if frappe.db.exists("Server Script", name):
    d = frappe.get_doc("Server Script", name); d.script = script; d.save(ignore_permissions=True)
else:
    d = frappe.get_doc({"doctype": "Server Script", "name": name, "script_type": "API",
        "api_method": "vm_pos_stock", "allow_guest": 1, "enabled": 1, "script": script})
    d.insert(ignore_permissions=True)
try:
    exec(script); print("in-sandbox OK")
except Exception as e:
    print("IN-SANDBOX ERROR:", repr(e)[:200])
frappe.clear_cache(); frappe.db.commit()
print("created", name)
