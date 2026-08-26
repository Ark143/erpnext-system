import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    item_group = filters.get("item_group")
    item = filters.get("item")

    columns = [
        {"label": _("Type"), "fieldname": "item_group", "fieldtype": "Data", "width": 100},
        {"label": _("Product"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": _("Code/SKU"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Reference"), "fieldname": "parent", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Price"), "fieldname": "rate", "fieldtype": "Currency", "width": 110},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Total Amt (PHP)"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Cost (PHP)"), "fieldname": "cost", "fieldtype": "Currency", "width": 120},
        {"label": _("Profit (PHP)"), "fieldname": "profit", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin %"), "fieldname": "margin_pct", "fieldtype": "Percent", "width": 100},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    params = {"from_date": from_date, "to_date": to_date}
    if company:
        conditions += " AND si.company = %(company)s"
        params["company"] = company
    if item_group:
        conditions += " AND sii.item_group = %(item_group)s"
        params["item_group"] = item_group
    if item:
        conditions += " AND sii.item_code = %(item)s"
        params["item"] = item

    data = frappe.db.sql(
        """
        SELECT
            sii.item_group,
            sii.item_name,
            sii.item_code,
            sii.parent,
            si.posting_date,
            sii.rate,
            sii.qty,
            sii.amount,
            COALESCE(sii.incoming_rate, 0) * sii.qty AS cost,
            sii.amount - COALESCE(sii.incoming_rate, 0) * sii.qty AS profit,
            CASE WHEN sii.amount > 0
                THEN ROUND((sii.amount - COALESCE(sii.incoming_rate, 0) * sii.qty) / sii.amount * 100, 2)
                ELSE 0 END AS margin_pct
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name = sii.parent
        WHERE """ + conditions + """
        ORDER BY si.posting_date DESC, sii.item_name
        """,
        params,
        as_dict=True,
    )

    return columns, data
