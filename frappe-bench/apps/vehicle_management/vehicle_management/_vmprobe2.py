import frappe, json

def run():
    out = {}
    try:
        dim = frappe.get_doc("Inventory Dimension", "Bin Location")
        d = dim.as_dict()
        out["invdim"] = {k: d.get(k) for k in ["name","type","reference_document","validate_against","apply_to_all_items","disabled"] if k in d}
    except Exception as e:
        out["invdim"] = f"ERR:{e}"
    for dt in ["Stock Entry Detail","Purchase Receipt Item"]:
        try:
            cf = frappe.get_doc("Custom Field", {"dt": dt, "fieldname": "bin_location"})
            out[f"cf_{dt}"] = {"fieldtype": cf.fieldtype, "options": cf.options, "reqd": cf.reqd}
        except Exception as e:
            out[f"cf_{dt}"] = f"ERR:{e}"
    for dt in ["Stock Entry","Purchase Receipt"]:
        m = frappe.get_meta(dt)
        child = "Stock Entry Detail" if dt=="Stock Entry" else "Purchase Receipt Item"
        out[f"{dt}_has_branch"] = any(f.fieldname=="branch" for f in m.fields)
        out[f"{dt}_item_has_cost_center"] = any(f.fieldname=="cost_center" for f in frappe.get_meta(child).fields)
    it = frappe.get_all("Item", {"is_stock_item":1}, ["name","valuation_rate","stock_uom"], limit=3)
    out["sample_stock_items"] = it
    wh = frappe.get_all("Warehouse", {"is_group":0}, ["name","company"], limit=8)
    out["sample_warehouses"] = wh
    print(json.dumps(out, indent=2, default=str))

if __name__ == "__main__":
    run()
