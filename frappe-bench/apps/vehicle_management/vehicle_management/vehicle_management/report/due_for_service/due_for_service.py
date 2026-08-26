import frappe
from frappe import _
from frappe.utils import nowdate, add_days


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or nowdate()
    to_date = filters.get("to_date") or add_days(nowdate(), 30)
    company = filters.get("company")

    columns = [
        {"label": _("Service Type"), "fieldname": "service_type", "fieldtype": "Data", "width": 160},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Last Service"), "fieldname": "last_service_date", "fieldtype": "Date", "width": 120},
        {"label": _("Next Service"), "fieldname": "next_service_date", "fieldtype": "Date", "width": 110},
        {"label": _("Days Due"), "fieldname": "days_due", "fieldtype": "Int", "width": 90},
    ]

    # Query last job orders per vehicle and estimate due date (mileage interval = 5000 km)
    conditions = "vjo.docstatus = 1"
    if company:
        conditions += " AND vjo.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            'PMS / Oil Change' AS service_type,
            vjo.customer,
            vjo.vehicle,
            vjo.plate_no,
            MAX(vjo.job_order_date) AS last_service_date,
            MAX(vjo.job_order_date) + INTERVAL '90 days' AS next_service_date,
            (MAX(vjo.job_order_date) + INTERVAL '90 days' - CURRENT_DATE) AS days_due
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        GROUP BY vjo.customer, vjo.vehicle, vjo.plate_no
        HAVING (MAX(vjo.job_order_date) + INTERVAL '90 days') BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY next_service_date
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
