"""
Processes all pending, draft, and incomplete Vehicle Job Orders in the system.
Ensures every Job Order is submitted (docstatus=1), linked to an approved
Sales Invoice (with 50% sales person commission allocated), paid in full via
Payment Entry, and marked as 'Released' with 'Paid' status.
"""

import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, now_datetime, add_days, flt

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

print("=" * 70)
print("  PROCESSING ALL PENDING & DRAFT VEHICLE JOB ORDERS")
print("=" * 70)

# Map companies to sales persons and abbr
COMPANY_SALES = {
    "Ultra MRF Dau Main": {"sales_person": "Emmanuel Ostria", "abbr": "UMDM"},
    "Ultra MRF Dau Annex": {"sales_person": "Christopher Lucero", "abbr": "UMDA"},
    "Ultra MRF San Fernando": {"sales_person": "Karen Cadion", "abbr": "UMSF"},
    "Wheel Core": {"sales_person": "Jericho Garcia", "abbr": "WCORE"},
    "Ultra MRF Telebastagan": {"sales_person": "Mark Anthony Cruz", "abbr": "UMTEL"},
    "Automan Car Care Center": {"sales_person": "Jonathan Dizon", "abbr": "AUTOMAN"},
    "The Wheelhub": {"sales_person": "Michael Ramos", "abbr": "WHUB"},
    "ULTRA MRF": {"sales_person": "Reynaldo Santos", "abbr": "UM"},
    "Ultra MRF Warehouse Dau": {"sales_person": "Danilo Perez", "abbr": "UMDW"},
    "San Fernando Warehouse": {"sales_person": "Eduardo Tan", "abbr": "SFWH"},
    "Ultra MRF Mexico Warehouse": {"sales_person": "Ramil Castro", "abbr": "MEXWH"},
    "My Company": {"sales_person": "Emmanuel Ostria", "abbr": "MC"}
}

# Fetch all VJOs
vjos = frappe.get_all("Vehicle Job Order", fields=["name", "company", "status", "payment_status", "docstatus", "sales_invoice"], order_by="creation asc")
print(f"Total VJOs found: {len(vjos)}")

processed_count = 0

for row in vjos:
    vjo_name = row.name
    doc = frappe.get_doc("Vehicle Job Order", vjo_name)
    company = doc.company or "Ultra MRF Dau Main"
    
    comp_info = COMPANY_SALES.get(company, {"sales_person": "Emmanuel Ostria", "abbr": "UMDM"})
    abbr = comp_info["abbr"]
    sales_person = comp_info["sales_person"]
    cost_center = f"Main - {abbr}"
    cash_account = f"Cash - {abbr}"
    debtors_account = f"Debtors - {abbr}"
    sales_account = f"Sales - {abbr}"
    warehouse = f"Stores - {abbr}"

    # Get active Bin Location for this warehouse if available
    bin_locs = frappe.get_all("Bin Location", filters={"warehouse": warehouse, "is_active": 1}, pluck="name")
    bin_location = bin_locs[0] if bin_locs else None

    print(f"\nProcessing [{vjo_name}] ({company} | Status: {doc.status} | DocStatus: {doc.docstatus})")

    # 1. Ensure Services are present
    if not doc.services:
        doc.append("services", {
            "service_item": "PMS LABOR (LIGHT)",
            "description": "PERIODIC MAINTENANCE SERVICE (PMS 20K)",
            "hours": 2.0,
            "rate": 950.0,
            "total_amount": 1900.0
        })
        doc.append("services", {
            "service_item": "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)",
            "description": "4-WHEEL COMPUTERIZED ALIGNMENT",
            "hours": 1.5,
            "rate": 1200.0,
            "total_amount": 1800.0
        })

    # 2. Ensure Parts are present
    if not doc.parts:
        doc.append("parts", {
            "item_code": "185/70 R14 YOKOHAMA ES32",
            "item_name": "185/70 R14 YOKOHAMA ES32 BLUEARTH",
            "qty": 4,
            "uom": "PC",
            "rate": 3650.0,
            "amount": 14600.0
        })
        doc.append("parts", {
            "item_code": "STRL-CAR PROTECT KIT (CAR CLEAN SET)",
            "item_name": "CAR PROTECTION & CLEAN KIT",
            "qty": 1,
            "uom": "PC",
            "rate": 350.0,
            "amount": 350.0
        })

    # 3. Recalculate totals
    doc.total_labor = sum(flt(s.total_amount) for s in doc.services)
    doc.total_parts = sum(flt(p.amount) for p in doc.parts)
    doc.net_total = doc.total_labor + doc.total_parts
    doc.grand_total = doc.net_total - flt(doc.discount_amount)
    doc.paid_amount = doc.grand_total
    doc.outstanding_amount = 0.0
    doc.status = "Completed"
    doc.payment_status = "Paid"
    doc.time_out = doc.time_out or now_datetime()

    # Save changes before submitting
    if doc.docstatus == 0:
        doc.save(ignore_permissions=True)
        doc.submit()
        print(f"  + Submitted VJO: {vjo_name}")
    else:
        doc.db_update()

    # 4. Check or Create Sales Invoice
    sinv_name = doc.sales_invoice
    if not sinv_name or not frappe.db.exists("Sales Invoice", sinv_name):
        # Create Sales Invoice
        grand_total = flt(doc.grand_total)
        commission_allocated = grand_total * 0.50

        sinv_items = []
        for p in doc.parts:
            sinv_items.append({
                "item_code": p.item_code,
                "item_name": p.item_name or frappe.db.get_value("Item", p.item_code, "item_name") or p.item_code,
                "qty": p.qty,
                "rate": p.rate,
                "income_account": sales_account,
                "cost_center": cost_center,
                "bin_location": bin_location
            })
        for s in doc.services:
            sinv_items.append({
                "item_code": s.service_item,
                "item_name": s.description or s.service_item,
                "qty": s.hours or 1.0,
                "rate": s.rate,
                "income_account": sales_account,
                "cost_center": cost_center
            })

        sinv = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": company,
            "customer": doc.customer,
            "posting_date": nowdate(),
            "due_date": nowdate(),
            "cost_center": cost_center,
            "debit_to": debtors_account,
            "update_stock": 0,
            "items": sinv_items,
            "sales_team": [
                {
                    "sales_person": sales_person,
                    "allocated_percentage": 100.0,
                    "commission_rate": 50.0,
                    "allocated_amount": commission_allocated,
                    "incentives": commission_allocated * 0.10
                }
            ]
        })
        sinv.insert(ignore_permissions=True)
        sinv.submit()
        sinv_name = sinv.name
        print(f"  + Created & Submitted Sales Invoice: {sinv_name} [50% Comm: {sales_person}]")

        # 5. Create Payment Entry
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": doc.customer,
            "company": company,
            "paid_from": debtors_account,
            "paid_to": cash_account,
            "paid_amount": sinv.grand_total,
            "received_amount": sinv.grand_total,
            "target_exchange_rate": 1.0,
            "cost_center": cost_center,
            "references": [
                {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": sinv.name,
                    "total_amount": sinv.grand_total,
                    "outstanding_amount": sinv.grand_total,
                    "allocated_amount": sinv.grand_total
                }
            ]
        })
        pe.insert(ignore_permissions=True)
        pe.submit()
        print(f"  + Created & Submitted Payment Entry: {pe.name}")

    # 6. Update VJO to Released and Paid
    frappe.db.set_value("Vehicle Job Order", vjo_name, {
        "status": "Released",
        "payment_status": "Paid",
        "sales_invoice": sinv_name,
        "paid_amount": doc.grand_total,
        "outstanding_amount": 0.0
    })

    frappe.db.commit()
    processed_count += 1
    print(f"  + [{vjo_name}] FULLY PROCESSED -> Released & Paid (Sales Invoice: {sinv_name})")

frappe.db.commit()
frappe.clear_cache()

print("\n" + "=" * 70)
print(f"  COMPLETED: {processed_count} Vehicle Job Orders processed to Released & Paid.")
print("=" * 70)
