import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": _("PO Count"), "fieldname": "po_count", "fieldtype": "Int", "width": 100},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "po.docstatus = 1 AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND po.company = %(company)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "po_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            po.supplier,
            COUNT(po.name) AS po_count,
            SUM(po.grand_total) AS total_amount,
            ROUND(SUM(po.grand_total) * 100.0 / SUM(SUM(po.grand_total)) OVER (), 2) AS percentage
        FROM "tabPurchase Order" po
        WHERE {conditions}
        GROUP BY po.supplier
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
