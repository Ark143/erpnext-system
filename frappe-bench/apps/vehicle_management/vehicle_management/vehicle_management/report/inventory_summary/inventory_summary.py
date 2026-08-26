import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    item_group = filters.get("item_group")

    columns = [
        {"label": _("Product"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Part No"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Product Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 140},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 90},
        {"label": _("Inventory Value (PHP)"), "fieldname": "inventory_value", "fieldtype": "Currency", "width": 180},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
    ]

    conditions = "sle.posting_date <= %(to_date)s AND sle.is_cancelled = 0"
    if company:
        conditions += " AND sle.company = %(company)s"
    if item_group:
        conditions += " AND i.item_group = %(item_group)s"

    data = frappe.db.sql(
        f"""
        SELECT
            i.item_name,
            sle.item_code,
            i.item_group,
            SUM(sle.actual_qty) AS qty,
            SUM(sle.stock_value_difference) AS inventory_value,
            sle.warehouse
        FROM "tabStock Ledger Entry" sle
        JOIN "tabItem" i ON i.name = sle.item_code
        WHERE {conditions}
        GROUP BY sle.item_code, i.item_name, i.item_group, sle.warehouse
        HAVING SUM(sle.actual_qty) > 0
        ORDER BY i.item_group, i.item_name
        """,
        {"to_date": to_date, "company": company, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
