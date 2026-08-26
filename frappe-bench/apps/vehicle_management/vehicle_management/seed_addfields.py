import frappe

def add_cf(dt, fieldname, label, fieldtype, options="", default="", insert_after="company"):
    if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fieldname}):
        print(f"  skip existing {dt}.{fieldname}")
        return
    frappe.custom_field.add_custom_field(dt, {
        "fieldname": fieldname,
        "label": label,
        "fieldtype": fieldtype,
        "options": options,
        "default": default,
        "insert_after": insert_after,
    })
    print(f"  added {dt}.{fieldname}")

def main():
    for dt in ["Vehicle Estimate","Vehicle Job Order","Vehicle Inspection"]:
        print("DOCTYPE:", dt)
        add_cf(dt, "sales_person", "Sales Person", "Link", "Sales Person")
        add_cf(dt, "commission_amount", "Commission Amount", "Currency", "", "50")
        add_cf(dt, "branch", "Branch", "Link", "Branch")
        add_cf(dt, "cost_center", "Cost Center", "Link", "Cost Center")
    frappe.db.commit()
    print("CUSTOM FIELDS COMMITTED")
