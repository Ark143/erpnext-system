import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    item_group = filters.get("item_group")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Service"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 130},
        {"label": _("Count"), "fieldname": "service_count", "fieldtype": "Int", "width": 90},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sii.item_group IN ('Services','Labor','Service')"
    if company:
        conditions += " AND si.company = %(company)s"
    if item_group:
        conditions += " AND sii.item_group = %(item_group)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "service_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            sii.item_name,
            sii.item_code,
            sii.item_group,
            COUNT(sii.name) AS service_count,
            SUM(sii.amount) AS total_amount,
            ROUND(SUM(sii.amount) * 100.0 / SUM(SUM(sii.amount)) OVER (), 2) AS percentage
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name = sii.parent
        WHERE {conditions}
        GROUP BY sii.item_name, sii.item_code, sii.item_group
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
