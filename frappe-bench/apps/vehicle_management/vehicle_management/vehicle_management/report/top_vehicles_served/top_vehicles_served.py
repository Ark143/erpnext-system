import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    make = filters.get("make")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 200},
        {"label": _("Count"), "fieldname": "visit_count", "fieldtype": "Int", "width": 90},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if make:
        conditions += " AND vjo.vehicle LIKE %(make)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "visit_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            COALESCE(vjo.vehicle, 'Unknown') AS vehicle,
            COUNT(vjo.name) AS visit_count,
            SUM(COALESCE(vjo.grand_total, 0)) AS total_amount,
            ROUND(
                SUM(COALESCE(vjo.grand_total, 0)) * 100.0 /
                NULLIF(SUM(SUM(COALESCE(vjo.grand_total, 0))) OVER (), 0),
                2
            ) AS percentage
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        GROUP BY COALESCE(vjo.vehicle, 'Unknown')
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "make": f"%{make}%" if make else "%"},
        as_dict=True,
    )

    return columns, data
