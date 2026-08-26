import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": _("Job Orders"), "fieldname": "jo_count", "fieldtype": "Int", "width": 100},
        {"label": _("Parts (PHP)"), "fieldname": "parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            TO_CHAR(vjo.job_order_date, 'YYYY-MM') AS month,
            COUNT(vjo.name) AS jo_count,
            SUM(COALESCE(vjo.total_parts, 0)) AS parts,
            SUM(COALESCE(vjo.total_labor, 0)) AS labor,
            SUM(COALESCE(vjo.discount_amount, 0)) AS discount,
            SUM(COALESCE(vjo.grand_total, 0)) AS total_amount
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        GROUP BY TO_CHAR(vjo.job_order_date, 'YYYY-MM')
        ORDER BY month
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
