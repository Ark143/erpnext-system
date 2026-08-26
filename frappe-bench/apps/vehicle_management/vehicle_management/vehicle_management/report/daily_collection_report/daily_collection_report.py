import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or nowdate()
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Cashier / User"), "fieldname": "owner", "fieldtype": "Data", "width": 150},
        {"label": _("Payment Method"), "fieldname": "mode_of_payment", "fieldtype": "Data", "width": 150},
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Link", "options": "Payment Entry", "width": 150},
        {"label": _("Total Payment (PHP)"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "pe.docstatus = 1 AND pe.payment_type = 'Receive' AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    params = {"from_date": from_date, "to_date": to_date}
    if company:
        conditions += " AND pe.company = %(company)s"
        params["company"] = company

    data = frappe.db.sql(
        """
        SELECT
            pe.posting_date,
            pe.owner,
            pe.mode_of_payment,
            pe.name,
            pe.paid_amount
        FROM "tabPayment Entry" pe
        WHERE """ + conditions + """
        ORDER BY pe.posting_date, pe.owner, pe.mode_of_payment
        """,
        params,
        as_dict=True,
    )

    return columns, data
