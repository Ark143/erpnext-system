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
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 180},
        {"label": _("Contact No"), "fieldname": "mobile_no", "fieldtype": "Data", "width": 130},
        {"label": _("Transactions"), "fieldname": "transactions", "fieldtype": "Int", "width": 120},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND si.company = %(company)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "transactions DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            si.customer,
            c.mobile_no,
            COUNT(si.name) AS transactions,
            SUM(si.grand_total) AS total_amount,
            ROUND(SUM(si.grand_total) * 100.0 / SUM(SUM(si.grand_total)) OVER (), 2) AS percentage
        FROM "tabSales Invoice" si
        LEFT JOIN "tabCustomer" c ON c.name = si.customer
        WHERE {conditions}
        GROUP BY si.customer, c.mobile_no
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
