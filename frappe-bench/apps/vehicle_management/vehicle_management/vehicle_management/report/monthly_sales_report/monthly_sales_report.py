import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": _("Sales"), "fieldname": "sales_count", "fieldtype": "Int", "width": 80},
        {"label": _("Parts (PHP)"), "fieldname": "parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount", "fieldtype": "Currency", "width": 130},
        {"label": _("Tax (PHP)"), "fieldname": "tax", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND si.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            TO_CHAR(si.posting_date, 'YYYY-MM') AS month,
            COUNT(si.name) AS sales_count,
            SUM(CASE WHEN sii.item_group IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS labor,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS parts,
            SUM(si.discount_amount) AS discount,
            SUM(si.total_taxes_and_charges) AS tax,
            SUM(si.grand_total) AS total_amount
        FROM "tabSales Invoice" si
        LEFT JOIN "tabSales Invoice Item" sii ON sii.parent = si.name
        WHERE {conditions}
        GROUP BY TO_CHAR(si.posting_date, 'YYYY-MM')
        ORDER BY month
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
