import frappe, json, random, os
from datetime import date

PROGRESS = r"C:\Users\josem\vmcreate_progress.txt"
SUMMARY  = r"C:\Users\josem\vmcreate_summary.txt"

COMPANY_PREFIX = {
    "My Company": "MC",
    "ULTRA MRF": "UM",
    "Ultra MRF Dau Annex": "UMDA",
    "Ultra MRF Dau Main": "UMDM",
    "Ultra MRF Warehouse Dau": "UMDW",
    "Ultra MRF San Fernando": "UMSF",
    "San Fernando Warehouse": "SFWH",
    "Ultra MRF Telebastagan": "UMTEL",
    "Ultra MRF Telebastagan 2": "UMTEL2",
    "Ultra MRF Mexico Warehouse": "MEXWH",
    "Automan Car Care Center": "AUTOMAN",
    "Wheel Core": "WCORE",
    "The Wheelhub": "WHUB",
}

def log(msg):
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ---- ensure custom fields exist (frappe 16 compatible) ----
def add_cf(dt, fieldname, label, fieldtype, options="", default="", insert_after="company"):
    if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
        return False
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": dt,
        "fieldname": fieldname,
        "label": label,
        "fieldtype": fieldtype,
        "options": options,
        "default": default,
        "insert_after": insert_after,
    }).insert()
    return True

def ensure_custom_fields():
    created = []
    for dt in ["Vehicle Estimate", "Vehicle Job Order", "Vehicle Inspection"]:
        for fld, lbl, ft, opt, dflt in [
            ("sales_person", "Sales Person", "Link", "Sales Person", ""),
            ("commission_amount", "Commission Amount", "Currency", "", "50"),
            ("branch", "Branch", "Link", "Branch", ""),
            ("cost_center", "Cost Center", "Link", "Cost Center", ""),
        ]:
            if add_cf(dt, fld, lbl, ft, opt, dflt):
                created.append(f"{dt}.{fld}")
    frappe.db.commit()
    return created

def default_series(doctype):
    f = frappe.get_meta(doctype).get_field("naming_series")
    if f and f.options:
        opts = [o.strip() for o in f.options.split("\n") if o.strip()]
        return opts[0]
    return None

def rc(lst):
    return random.choice(lst) if lst else None

def run():
    open(PROGRESS, "w").close()
    log("=== START ensure custom fields ===")
    cf = ensure_custom_fields()
    log("custom fields created: " + (",".join(cf) if cf else "none (already exist)"))

    # ---- gather reference data ----
    cost_centers = [{"name": c.name, "company": c.company}
                    for c in frappe.get_list("Cost Center", {"is_group": 0}, ["name", "company"])]
    branches = [b.name for b in frappe.get_list("Branch", ["name"])]
    sales_persons = [s.name for s in frappe.get_list("Sales Person", ["name"])]
    customers = [c.name for c in frappe.get_list("Customer", ["name"])]
    vehicles = [{"name": v.name, "customer": v.customer}
                for v in frappe.get_list("Customer Vehicle", ["name", "customer"])]
    items = [i.name for i in frappe.get_list("Item", ["name"], limit=2000)]
    stock_items = [{"name": i.name, "uom": i.stock_uom or "Nos"}
                   for i in frappe.get_list("Item", {"is_stock_item": 1}, ["name", "stock_uom"], limit=2000)]
    suppliers = [s.name for s in frappe.get_list("Supplier", ["name"])]
    binlocs = [b.name for b in frappe.get_list("Bin Location", ["name"], limit=2000)]
    wh_all = frappe.get_list("Warehouse", {"is_group": 0}, ["name", "company"])
    wh_by_co = {}
    for w in wh_all:
        wh_by_co.setdefault(w.company, []).append(w.name)
    bin_by_pref = {}
    for b in binlocs:
        pref = b.split("-")[0]
        bin_by_pref.setdefault(pref, []).append(b)

    log(f"cost_centers={len(cost_centers)} branches={len(branches)} sales_persons={len(sales_persons)} "
        f"vehicles={len(vehicles)} items={len(items)} stock_items={len(stock_items)} suppliers={len(suppliers)} binlocs={len(binlocs)}")

    today = date.today().isoformat()
    created = []
    errors = []

    def wh_for(company):
        return rc(wh_by_co.get(company)) or rc([w.name for w in wh_all])

    def bin_for(company):
        pref = COMPANY_PREFIX.get(company)
        if pref and bin_by_pref.get(pref):
            return rc(bin_by_pref[pref])
        return rc(binlocs)

    def make_vehicle_docs(company, branch, cost_center, sp, veh, cust, idx):
        names = {}
        try:
            est = frappe.get_doc({
                "doctype": "Vehicle Estimate",
                "naming_series": default_series("Vehicle Estimate"),
                "company": company,
                "estimate_date": today,
                "customer": cust,
                "vehicle": veh,
                "services": [{"service_item": rc(items), "description": "Periodic maintenance service",
                              "rate": round(random.uniform(300, 1500), 2), "hours": 1.0}],
                "parts": [{"item_code": (rc(stock_items) or {"name": rc(items)})["name"],
                           "qty": 1.0, "rate": round(random.uniform(100, 900), 2), "uom": "PC"}],
                "sales_person": sp, "commission_amount": 50.0,
                "branch": branch, "cost_center": cost_center,
            })
            est.insert()
            names["estimate"] = est.name
            created.append(est.name)
            log(f"[{idx}] Vehicle Estimate {est.name} OK (co={company}, br={branch}, cc={cost_center}, sp={sp}, veh={veh})")
        except Exception as e:
            errors.append({"type": "Vehicle Estimate", "company": company, "err": str(e)[:300]})
            log(f"[{idx}] Vehicle Estimate FAIL: {str(e)[:200]}")
        try:
            jo = frappe.get_doc({
                "doctype": "Vehicle Job Order",
                "naming_series": default_series("Vehicle Job Order"),
                "company": company,
                "vehicle": veh,
                "job_order_date": today,
                "services": [{"service_item": rc(items), "description": "Labor - diagnostics & repair",
                              "rate": round(random.uniform(300, 1500), 2), "hours": 1.0}],
                "parts": [{"item_code": (rc(stock_items) or {"name": rc(items)})["name"],
                           "qty": 1.0, "rate": round(random.uniform(100, 900), 2), "uom": "PC"}],
                "sales_person": sp, "commission_amount": 50.0,
                "branch": branch, "cost_center": cost_center,
            })
            if names.get("estimate"):
                jo.estimate = names["estimate"]
            jo.insert()
            try:
                jo.submit()
            except Exception as se:
                log(f"[{idx}] Vehicle Job Order {jo.name} insert OK, submit skipped: {str(se)[:120]}")
            created.append(jo.name)
            log(f"[{idx}] Vehicle Job Order {jo.name} OK")
        except Exception as e:
            errors.append({"type": "Vehicle Job Order", "company": company, "err": str(e)[:300]})
            log(f"[{idx}] Vehicle Job Order FAIL: {str(e)[:200]}")
        try:
            insp = frappe.get_doc({
                "doctype": "Vehicle Inspection",
                "naming_series": default_series("Vehicle Inspection"),
                "company": company,
                "inspection_date": today,
                "vehicle": veh,
                "items": [{"item_name": "Engine / Fluids", "status": "Pass / OK", "observation": "Within spec"},
                          {"item_name": "Brakes", "status": "Requires Attention", "observation": "Pad wear noted"}],
                "sales_person": sp, "commission_amount": 50.0,
                "branch": branch, "cost_center": cost_center,
            })
            insp.insert()
            try:
                insp.submit()
            except Exception as se:
                log(f"[{idx}] Vehicle Inspection {insp.name} insert OK, submit skipped: {str(se)[:120]}")
            created.append(insp.name)
            log(f"[{idx}] Vehicle Inspection {insp.name} OK")
        except Exception as e:
            errors.append({"type": "Vehicle Inspection", "company": company, "err": str(e)[:300]})
            log(f"[{idx}] Vehicle Inspection FAIL: {str(e)[:200]}")

    def make_p2p(company, branch, cost_center, idx):
        wh = wh_for(company)
        bl = bin_for(company)
        try:
            si = rc(stock_items) or {"name": rc(items), "uom": "Nos"}
            pr = frappe.get_doc({
                "doctype": "Purchase Receipt",
                "naming_series": default_series("Purchase Receipt"),
                "supplier": rc(suppliers),
                "company": company,
                "posting_date": today,
                "branch": branch,
                "items": [{
                    "item_code": si["name"],
                    "qty": 1.0,
                    "rate": round(random.uniform(50, 500), 2),
                    "uom": si["uom"],
                    "warehouse": wh,
                    "cost_center": cost_center,
                    "bin_location": bl,
                }],
            })
            pr.insert()
            try:
                pr.submit()
            except Exception as se:
                log(f"[{idx}] Purchase Receipt {pr.name} insert OK, submit skipped: {str(se)[:120]}")
            created.append(pr.name)
            log(f"[{idx}] Purchase Receipt {pr.name} OK wh={wh} bin={bl}")
        except Exception as e:
            errors.append({"type": "Purchase Receipt", "company": company, "err": str(e)[:300]})
            log(f"[{idx}] Purchase Receipt FAIL: {str(e)[:200]}")
        try:
            si2 = rc(stock_items) or {"name": rc(items), "uom": "Nos"}
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "naming_series": default_series("Stock Entry"),
                "stock_entry_type": "Material Receipt",
                "company": company,
                "branch": branch,
                "items": [{
                    "item_code": si2["name"],
                    "qty": 1.0,
                    "basic_rate": round(random.uniform(50, 500), 2),
                    "uom": si2["uom"],
                    "t_warehouse": wh,
                    "cost_center": cost_center,
                    "bin_location": bl,
                }],
            })
            se.insert()
            try:
                se.submit()
            except Exception as se:
                log(f"[{idx}] Stock Entry {se.name} insert OK, submit skipped: {str(se)[:120]}")
            created.append(se.name)
            log(f"[{idx}] Stock Entry {se.name} OK wh={wh} bin={bl}")
        except Exception as e:
            errors.append({"type": "Stock Entry", "company": company, "err": str(e)[:300]})
            log(f"[{idx}] Stock Entry FAIL: {str(e)[:200]}")

    n = len(cost_centers)
    for i, cc in enumerate(cost_centers):
        company = cc["company"]
        cost_center = cc["name"]
        branch = branches[i % len(branches)] if branches else None
        sp = rc(sales_persons)
        veh = rc(vehicles)
        cust = veh["customer"] or rc(customers)
        veh_name = veh["name"]
        log(f"--- [{i+1}/{n}] company={company} cost_center={cost_center} branch={branch} ---")
        make_vehicle_docs(company, branch, cost_center, sp, veh_name, cust, i+1)
        make_p2p(company, branch, cost_center, i+1)
        frappe.db.commit()

    summary = {
        "total_created": len(created),
        "created_names": created,
        "total_errors": len(errors),
        "errors": errors,
        "cost_centers_covered": n,
        "companies": sorted(set(c["company"] for c in cost_centers)),
        "branches_used": branches,
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write(json.dumps(summary, indent=2, default=str))
    log(f"=== DONE created={len(created)} errors={len(errors)} ===")
    print(json.dumps({"created": len(created), "errors": len(errors),
                      "cost_centers": n, "companies": len(summary['companies'])}, indent=2))
