import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    customer = filters.get("customer")

    columns = [
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Parts (PHP)"), "fieldname": "total_parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "total_labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if customer:
        conditions += " AND vjo.customer = %(customer)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.name,
            vjo.customer,
            vjo.plate_no,
            vjo.vehicle,
            vjo.status,
            vjo.sales_invoice,
            COALESCE(vjo.total_parts, 0) AS total_parts,
            COALESCE(vjo.total_labor, 0) AS total_labor,
            COALESCE(vjo.discount_amount, 0) AS discount_amount,
            COALESCE(vjo.grand_total, 0) AS grand_total,
            vjo.job_order_date
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.job_order_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "customer": customer},
        as_dict=True,
    )

    return columns, data
