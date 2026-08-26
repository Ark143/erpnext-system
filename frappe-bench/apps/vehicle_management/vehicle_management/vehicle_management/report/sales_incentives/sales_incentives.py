import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    sales_person = filters.get("sales_person")

    columns = [
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 160},
        {"label": _("Reference"), "fieldname": "parent", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Invoice Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 160},
        {"label": _("Commission %"), "fieldname": "commission_rate", "fieldtype": "Percent", "width": 120},
        {"label": _("Commission Amt (PHP)"), "fieldname": "commission_amount", "fieldtype": "Currency", "width": 180},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
    ]

    params = {"from_date": from_date, "to_date": to_date}
    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND si.company = %(company)s"
        params["company"] = company
    if sales_person:
        conditions += " AND st.sales_person = %(sales_person)s"
        params["sales_person"] = sales_person

    data = frappe.db.sql(
        """
        SELECT
            st.sales_person,
            st.parent,
            si.customer,
            si.grand_total,
            COALESCE(st.commission_rate::numeric, 0) AS commission_rate,
            si.grand_total * COALESCE(st.commission_rate::numeric, 0) / 100 AS commission_amount,
            si.posting_date
        FROM "tabSales Team" st
        JOIN "tabSales Invoice" si ON si.name = st.parent AND st.parenttype = 'Sales Invoice'
        WHERE """ + conditions + """
        ORDER BY si.posting_date DESC, st.sales_person
        """,
        params,
        as_dict=True,
    )

    return columns, data
