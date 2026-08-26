import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
        {"label": _("Contact No"), "fieldname": "mobile_no", "fieldtype": "Data", "width": 130},
        {"label": _("Points Earned"), "fieldname": "points_earned", "fieldtype": "Float", "width": 120},
        {"label": _("Points Redeemed"), "fieldname": "points_redeemed", "fieldtype": "Float", "width": 140},
        {"label": _("Current Points"), "fieldname": "current_points", "fieldtype": "Float", "width": 130},
        {"label": _("Total Transactions"), "fieldname": "total_transactions", "fieldtype": "Int", "width": 150},
        {"label": _("Loyalty Program"), "fieldname": "loyalty_program", "fieldtype": "Data", "width": 160},
    ]

    conditions = "lpe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND lpe.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            lpe.customer,
            c.mobile_no,
            SUM(CASE WHEN lpe.loyalty_points > 0 THEN lpe.loyalty_points ELSE 0 END) AS points_earned,
            SUM(CASE WHEN lpe.loyalty_points < 0 THEN ABS(lpe.loyalty_points) ELSE 0 END) AS points_redeemed,
            SUM(lpe.loyalty_points) AS current_points,
            COUNT(DISTINCT lpe.invoice) AS total_transactions,
            lpe.loyalty_program
        FROM "tabLoyalty Point Entry" lpe
        LEFT JOIN "tabCustomer" c ON c.name = lpe.customer
        WHERE {conditions}
        GROUP BY lpe.customer, c.mobile_no, lpe.loyalty_program
        ORDER BY current_points DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
