import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    supplier = filters.get("supplier")

    columns = [
        {"label": _("PO No"), "fieldname": "name", "fieldtype": "Link", "options": "Purchase Order", "width": 150},
        {"label": _("PO Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 110},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 160},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": _("% Received"), "fieldname": "per_received", "fieldtype": "Percent", "width": 100},
        {"label": _("Amount (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
    ]

    params = {"from_date": from_date, "to_date": to_date}
    conditions = "po.docstatus = 1 AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND po.company = %(company)s"
        params["company"] = company
    if supplier:
        conditions += " AND po.supplier = %(supplier)s"
        params["supplier"] = supplier

    data = frappe.db.sql(
        """
        SELECT
            po.name,
            po.transaction_date,
            po.supplier,
            po.status,
            po.per_received,
            po.grand_total
        FROM "tabPurchase Order" po
        WHERE """ + conditions + """
        ORDER BY po.transaction_date DESC
        """,
        params,
        as_dict=True,
    )

    return columns, data
