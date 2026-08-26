import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    customer = filters.get("customer")
    sales_person = filters.get("sales_person")

    columns = [
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Sales Person"), "fieldname": "sales_person", "fieldtype": "Data", "width": 130},
        {"label": _("Parts (PHP)"), "fieldname": "parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Discount"), "fieldname": "discount", "fieldtype": "Currency", "width": 130},
        {"label": _("Tax (PHP)"), "fieldname": "tax", "fieldtype": "Currency", "width": 120},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Parts Cost"), "fieldname": "parts_cost", "fieldtype": "Currency", "width": 130},
        {"label": _("Parts Profit"), "fieldname": "parts_profit", "fieldtype": "Currency", "width": 130},
        {"label": _("Service Profit"), "fieldname": "service_profit", "fieldtype": "Currency", "width": 130},
        {"label": _("Total Profit"), "fieldname": "total_profit", "fieldtype": "Currency", "width": 130},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    params = {"from_date": from_date, "to_date": to_date}
    if company:
        conditions += " AND si.company = %(company)s"
        params["company"] = company
    if customer:
        conditions += " AND si.customer = %(customer)s"
        params["customer"] = customer

    data = frappe.db.sql(
        """
        SELECT
            si.name,
            si.customer,
            (SELECT st.sales_person FROM "tabSales Team" st WHERE st.parent = si.name LIMIT 1) AS sales_person,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS parts,
            SUM(CASE WHEN sii.item_group IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS labor,
            si.discount_amount AS discount,
            si.total_taxes_and_charges AS tax,
            si.grand_total,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor')
                THEN COALESCE(sii.incoming_rate, 0) * sii.qty ELSE 0 END) AS parts_cost,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor')
                THEN sii.amount - COALESCE(sii.incoming_rate, 0) * sii.qty ELSE 0 END) AS parts_profit,
            SUM(CASE WHEN sii.item_group IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS service_profit,
            si.grand_total - SUM(COALESCE(sii.incoming_rate, 0) * sii.qty) AS total_profit,
            si.posting_date
        FROM "tabSales Invoice" si
        LEFT JOIN "tabSales Invoice Item" sii ON sii.parent = si.name
        WHERE """ + conditions + """
        GROUP BY si.name, si.customer, si.discount_amount, si.total_taxes_and_charges, si.grand_total, si.posting_date
        ORDER BY si.posting_date DESC
        """,
        params,
        as_dict=True,
    )

    return columns, data
