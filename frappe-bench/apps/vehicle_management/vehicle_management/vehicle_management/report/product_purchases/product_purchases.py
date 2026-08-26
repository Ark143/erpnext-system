import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    supplier = filters.get("supplier")
    item_group = filters.get("item_group")

    columns = [
        {"label": _("Product"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": _("Part No"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 120},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
        {"label": _("Price (PHP)"), "fieldname": "rate", "fieldtype": "Currency", "width": 120},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Total Amt (PHP)"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
    ]

    conditions = "pr.docstatus = 1 AND pr.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND pr.company = %(company)s"
    if supplier:
        conditions += " AND pr.supplier = %(supplier)s"
    if item_group:
        conditions += " AND pri.item_group = %(item_group)s"

    data = frappe.db.sql(
        f"""
        SELECT
            pri.item_name,
            pri.item_code,
            pri.item_group,
            pr.supplier,
            pri.rate,
            pri.qty,
            pri.amount,
            pr.posting_date
        FROM "tabPurchase Receipt Item" pri
        JOIN "tabPurchase Receipt" pr ON pr.name = pri.parent
        WHERE {conditions}
        ORDER BY pr.posting_date DESC, pri.item_name
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "supplier": supplier, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
