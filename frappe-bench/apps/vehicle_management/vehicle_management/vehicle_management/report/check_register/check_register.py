import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("CV No"), "fieldname": "name", "fieldtype": "Link", "options": "Payment Entry", "width": 150},
        {"label": _("CV Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Payee"), "fieldname": "party", "fieldtype": "Data", "width": 160},
        {"label": _("Check #"), "fieldname": "reference_no", "fieldtype": "Data", "width": 130},
        {"label": _("Check Date"), "fieldname": "reference_date", "fieldtype": "Date", "width": 110},
        {"label": _("Amount (PHP)"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 140},
    ]

    params = {"from_date": from_date, "to_date": to_date}
    conditions = "pe.docstatus = 1 AND pe.mode_of_payment ILIKE '%%Check%%' AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND pe.company = %(company)s"
        params["company"] = company

    data = frappe.db.sql(
        """
        SELECT
            pe.name,
            pe.posting_date,
            pe.party AS party,
            pe.reference_no,
            pe.reference_date,
            pe.paid_amount
        FROM "tabPayment Entry" pe
        WHERE """ + conditions + """
        ORDER BY pe.posting_date DESC
        """,
        params,
        as_dict=True,
    )

    return columns, data
