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
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
        {"label": _("Service Advisor"), "fieldname": "service_advisor", "fieldtype": "Data", "width": 150},
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Time In"), "fieldname": "time_in", "fieldtype": "Data", "width": 120},
        {"label": _("Work Start"), "fieldname": "work_start_time", "fieldtype": "Data", "width": 120},
        {"label": _("Work End"), "fieldname": "work_end_time", "fieldtype": "Data", "width": 120},
        {"label": _("Time Out"), "fieldname": "time_out", "fieldtype": "Data", "width": 120},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if mechanic:
        conditions += " AND vjo.service_advisor LIKE %(mechanic)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.job_order_date,
            vjo.service_advisor,
            vjo.name,
            vjo.vehicle,
            COALESCE(CAST(vjo.time_in AS VARCHAR), '') AS time_in,
            COALESCE(CAST(vjo.work_start_time AS VARCHAR), '') AS work_start_time,
            COALESCE(CAST(vjo.work_end_time AS VARCHAR), '') AS work_end_time,
            COALESCE(CAST(vjo.time_out AS VARCHAR), '') AS time_out
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.job_order_date DESC, vjo.service_advisor
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "mechanic": f"%{mechanic}%" if mechanic else "%"},
        as_dict=True,
    )

    return columns, data
