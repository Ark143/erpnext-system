import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    mechanic = filters.get("mechanic")

    columns = [
        {"label": _("Service Advisor"), "fieldname": "service_advisor", "fieldtype": "Data", "width": 150},
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Labor (PHP)"), "fieldname": "total_labor", "fieldtype": "Currency", "width": 140},
        {"label": _("JO Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if mechanic:
        conditions += " AND vjo.service_advisor LIKE %(mechanic)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.service_advisor,
            vjo.job_order_date,
            vjo.name,
            vjo.vehicle,
            vjo.plate_no,
            COALESCE(vjo.total_labor, 0) AS total_labor,
            COALESCE(vjo.grand_total, 0) AS grand_total
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.service_advisor, vjo.job_order_date
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "mechanic": f"%{mechanic}%" if mechanic else "%"},
        as_dict=True,
    )

    return columns, data
