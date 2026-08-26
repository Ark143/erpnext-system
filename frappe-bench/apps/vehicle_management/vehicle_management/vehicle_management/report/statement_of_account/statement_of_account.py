import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    customer = filters.get("customer")
    report_type = filters.get("report_type") or "Activities"

    columns = [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Transaction"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 140},
        {"label": _("Reference No"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 160},
        {"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 110},
        {"label": _("Amount (PHP)"), "fieldname": "debit", "fieldtype": "Currency", "width": 140},
        {"label": _("Payment (PHP)"), "fieldname": "credit", "fieldtype": "Currency", "width": 140},
        {"label": _("Balance (PHP)"), "fieldname": "balance", "fieldtype": "Currency", "width": 140},
    ]

    if not customer:
        return columns, []

    conditions = """
        gl.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND gl.party_type = 'Customer'
        AND gl.party = %(customer)s
    """
    if company:
        conditions += " AND gl.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            gl.posting_date,
            gl.voucher_type,
            gl.voucher_no,
            null AS due_date,
            gl.debit,
            gl.credit,
            SUM(gl.debit - gl.credit) OVER (ORDER BY gl.posting_date, gl.creation) AS balance
        FROM "tabGL Entry" gl
        WHERE {conditions}
        ORDER BY gl.posting_date, gl.creation
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "customer": customer},
        as_dict=True,
    )

    return columns, data
