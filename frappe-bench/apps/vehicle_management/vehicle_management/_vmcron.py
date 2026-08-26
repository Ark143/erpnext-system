import frappe, json

def run():
    out = {}
    def gl(dt, fields=None, filters=None, limit=200):
        try:
            return frappe.get_list(dt, fields=fields or ["name"], filters=filters or {}, limit=limit)
        except Exception as e:
            return f"ERR:{e}"

    out["companies"] = [c.name for c in gl("Company")]
    out["branches"] = [b.name for b in gl("Branch")]
    out["branches_with_company"] = [{"name": b.name, "company": b.company} for b in gl("Branch", ["name","company"])]
    # cost centers (with company)
    ccs = gl("Cost Center", ["name","company","is_group"])
    out["cost_centers_count"] = len(ccs)
    out["cost_centers_sample"] = ccs[:30]
    out["cost_centers_non_group"] = [c for c in ccs if not c.get("is_group")]
    out["sales_persons"] = [s.name for s in gl("Sales Person", limit=300)]
    out["customers"] = [c.name for c in gl("Customer", limit=300)]
    out["customer_vehicles"] = [{"name": v.name, "customer": v.customer, "make": v.make, "plate": v.plate_no} for v in gl("Customer Vehicle", ["name","customer","make","plate_no"], limit=300)]
    out["items"] = [i.name for i in gl("Item", {"is_stock_item": 1}, limit=300)]
    out["warehouses"] = [w.name for w in gl("Warehouse", {"is_group": 0}, limit=300)]
    out["suppliers"] = [s.name for s in gl("Supplier", limit=300)]
    # custom Bin Location doctype
    try:
        bl = frappe.get_list("Bin Location", ["name"], limit=300)
        out["bin_locations"] = [b.name for b in bl]
    except Exception as e:
        out["bin_locations"] = f"ERR:{e}"
    # inventory dimension
    try:
        dim = frappe.get_doc("Inventory Dimension", "Bin Location")
        out["invdim"] = {"name": dim.name, "fieldname": dim.fieldname, "type": dim.type, "reference_document": dim.reference_document}
    except Exception as e:
        out["invdim"] = f"ERR:{e}"
    # check custom field existence
    for dt in ["Vehicle Estimate","Vehicle Job Order","Vehicle Inspection"]:
        out.setdefault("cf", {})[dt] = {
            "sales_person": bool(frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "sales_person"})),
            "commission_amount": bool(frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "commission_amount"})),
            "branch": bool(frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "branch"})),
            "cost_center": bool(frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "cost_center"})),
        }
    # bin_location on SE/PR item
    out["se_item_binloc"] = bool(frappe.db.exists("Custom Field", {"dt": "Stock Entry Detail", "fieldname": "bin_location"}))
    out["pr_item_binloc"] = bool(frappe.db.exists("Custom Field", {"dt": "Purchase Receipt Item", "fieldname": "bin_location"}))
    print(json.dumps(out, indent=2, default=str))

if __name__ == "__main__":
    run()
