import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    customer = filters.get("customer")
    plate_no = filters.get("plate_no")

    columns = [
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Contact No"), "fieldname": "contact_no", "fieldtype": "Data", "width": 130},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Mileage"), "fieldname": "mileage", "fieldtype": "Int", "width": 100},
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if customer:
        conditions += " AND vjo.customer = %(customer)s"
    if plate_no:
        conditions += " AND vjo.plate_no LIKE %(plate_no)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.name,
            vjo.customer,
            vjo.contact_no,
            vjo.plate_no,
            vjo.vehicle,
            COALESCE(vjo.mileage, 0) AS mileage,
            vjo.job_order_date,
            COALESCE(vjo.grand_total, 0) AS grand_total
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.job_order_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "customer": customer, "plate_no": f"%{plate_no}%" if plate_no else "%"},
        as_dict=True,
    )

    return columns, data
