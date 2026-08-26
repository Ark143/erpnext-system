"""
Generate all Vehicle Management report files based on Autometrik schemas.
"""
import os
import json

BASE = os.path.join(
    os.path.dirname(__file__),
    "apps", "vehicle_management", "vehicle_management",
    "vehicle_management", "report"
)


def make_json(name, ref_doctype="Sales Invoice", add_total=1):
    return {
        "add_total_row": add_total,
        "columns": [],
        "creation": "2026-08-25 00:00:00.000000",
        "disabled": 0,
        "docstatus": 0,
        "doctype": "Report",
        "filters": [],
        "idx": 0,
        "is_standard": "Yes",
        "letter_head": "",
        "module": "Vehicle Management",
        "name": name,
        "prepared_report": 0,
        "ref_doctype": ref_doctype,
        "report_name": name,
        "report_type": "Script Report",
        "roles": []
    }


REPORTS = {
    "monthly_sales_report": {
        "name": "Monthly Sales Report",
        "ref_doctype": "Sales Invoice",
        "python": '''import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": _("Sales"), "fieldname": "sales_count", "fieldtype": "Int", "width": 80},
        {"label": _("Parts (PHP)"), "fieldname": "parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount", "fieldtype": "Currency", "width": 130},
        {"label": _("Tax (PHP)"), "fieldname": "tax", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND si.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            TO_CHAR(si.posting_date, 'YYYY-MM') AS month,
            COUNT(si.name) AS sales_count,
            SUM(CASE WHEN sii.item_group IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS labor,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS parts,
            SUM(si.discount_amount) AS discount,
            SUM(si.total_taxes_and_charges) AS tax,
            SUM(si.grand_total) AS total_amount
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE {conditions}
        GROUP BY TO_CHAR(si.posting_date, 'YYYY-MM')
        ORDER BY month
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
        "filters": [
            {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date"},
            {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date"},
            {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company"},
        ]
    },
    "detailed_sales_report": {
        "name": "Detailed Sales Report",
        "ref_doctype": "Sales Invoice",
        "python": '''import frappe
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
        {"label": _("Parts Discount"), "fieldname": "parts_discount", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor Discount"), "fieldname": "labor_discount", "fieldtype": "Currency", "width": 130},
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
    if company:
        conditions += " AND si.company = %(company)s"
    if customer:
        conditions += " AND si.customer = %(customer)s"
    if sales_person:
        conditions += " AND si.sales_team LIKE %(sales_person)s"

    data = frappe.db.sql(
        f"""
        SELECT
            si.name,
            si.customer,
            (SELECT st.sales_person FROM `tabSales Team` st WHERE st.parent = si.name LIMIT 1) AS sales_person,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS parts,
            SUM(CASE WHEN sii.item_group IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS labor,
            0 AS parts_discount,
            0 AS labor_discount,
            si.discount_amount AS discount,
            si.total_taxes_and_charges AS tax,
            si.grand_total,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor') THEN COALESCE(sii.valuation_rate,0)*sii.qty ELSE 0 END) AS parts_cost,
            SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor') THEN sii.amount - COALESCE(sii.valuation_rate,0)*sii.qty ELSE 0 END) AS parts_profit,
            SUM(CASE WHEN sii.item_group IN ('Services','Labor') THEN sii.amount ELSE 0 END) AS service_profit,
            si.grand_total - SUM(COALESCE(sii.valuation_rate,0)*sii.qty) AS total_profit,
            si.posting_date
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE {conditions}
        GROUP BY si.name, si.customer, si.discount_amount, si.total_taxes_and_charges, si.grand_total, si.posting_date
        ORDER BY si.posting_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "customer": customer, "sales_person": f"%{sales_person}%" if sales_person else "%"},
        as_dict=True,
    )

    return columns, data
''',
    },
    "sales_by_product": {
        "name": "Sales by Product",
        "ref_doctype": "Sales Invoice Item",
        "python": '''import frappe
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
        {"label": _("Group"), "fieldname": "item_group_name", "fieldtype": "Data", "width": 120},
        {"label": _("Reference"), "fieldname": "parent", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Price"), "fieldname": "rate", "fieldtype": "Currency", "width": 110},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": _("Tax (PHP)"), "fieldname": "tax_amount", "fieldtype": "Currency", "width": 110},
        {"label": _("Total Amt (PHP)"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
        {"label": _("Cost (PHP)"), "fieldname": "cost", "fieldtype": "Currency", "width": 120},
        {"label": _("Profit (PHP)"), "fieldname": "profit", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin %"), "fieldname": "margin_pct", "fieldtype": "Percent", "width": 100},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND si.company = %(company)s"
    if item_group:
        conditions += " AND sii.item_group = %(item_group)s"
    if item:
        conditions += " AND sii.item_code = %(item)s"

    data = frappe.db.sql(
        f"""
        SELECT
            sii.item_group,
            sii.item_name,
            sii.item_code,
            sii.item_group AS item_group_name,
            sii.parent,
            si.posting_date,
            sii.rate,
            sii.qty,
            0 AS tax_amount,
            sii.amount,
            COALESCE(sii.valuation_rate,0) * sii.qty AS cost,
            sii.amount - COALESCE(sii.valuation_rate,0) * sii.qty AS profit,
            CASE WHEN sii.amount > 0 THEN ROUND((sii.amount - COALESCE(sii.valuation_rate,0)*sii.qty)/sii.amount*100,2) ELSE 0 END AS margin_pct
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE {conditions}
        ORDER BY si.posting_date DESC, sii.item_name
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "item_group": item_group, "item": item},
        as_dict=True,
    )

    return columns, data
''',
    },
    "daily_collection_report": {
        "name": "Daily Collection Report",
        "ref_doctype": "Payment Entry",
        "python": '''import frappe
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
    if company:
        conditions += " AND pe.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            pe.posting_date,
            pe.owner,
            pe.mode_of_payment,
            pe.name,
            pe.paid_amount
        FROM `tabPayment Entry` pe
        WHERE {conditions}
        ORDER BY pe.posting_date, pe.owner, pe.mode_of_payment
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "monthly_job_orders": {
        "name": "Monthly Job Orders",
        "ref_doctype": "Vehicle Job Order",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")

    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": _("Job Orders"), "fieldname": "jo_count", "fieldtype": "Int", "width": 100},
        {"label": _("Parts (PHP)"), "fieldname": "parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount", "fieldtype": "Currency", "width": 130},
        {"label": _("Tax (PHP)"), "fieldname": "tax", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            TO_CHAR(vjo.order_date, 'YYYY-MM') AS month,
            COUNT(vjo.name) AS jo_count,
            SUM(COALESCE(vjo.parts_total,0)) AS parts,
            SUM(COALESCE(vjo.labor_total,0)) AS labor,
            SUM(COALESCE(vjo.discount_amount,0)) AS discount,
            SUM(COALESCE(vjo.total_taxes_and_charges,0)) AS tax,
            SUM(COALESCE(vjo.grand_total,0)) AS total_amount
        FROM `tabVehicle Job Order` vjo
        WHERE {conditions}
        GROUP BY TO_CHAR(vjo.order_date, 'YYYY-MM')
        ORDER BY month
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "detailed_job_orders": {
        "name": "Detailed Job Orders",
        "ref_doctype": "Vehicle Job Order",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    customer = filters.get("customer")

    columns = [
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Parts (PHP)"), "fieldname": "parts_total", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "labor_total", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Tax (PHP)"), "fieldname": "total_taxes_and_charges", "fieldtype": "Currency", "width": 120},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Date"), "fieldname": "order_date", "fieldtype": "Date", "width": 110},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if customer:
        conditions += " AND vjo.customer = %(customer)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.name,
            vjo.customer,
            cv.license_plate AS plate_no,
            CONCAT(COALESCE(vm.make,''),' ',COALESCE(vmo.model,'')) AS vehicle,
            vjo.status,
            (SELECT si.name FROM `tabSales Invoice` si WHERE si.vehicle_job_order = vjo.name AND si.docstatus=1 LIMIT 1) AS sales_invoice,
            COALESCE(vjo.parts_total,0) AS parts_total,
            COALESCE(vjo.labor_total,0) AS labor_total,
            COALESCE(vjo.discount_amount,0) AS discount_amount,
            COALESCE(vjo.total_taxes_and_charges,0) AS total_taxes_and_charges,
            COALESCE(vjo.grand_total,0) AS grand_total,
            vjo.order_date
        FROM `tabVehicle Job Order` vjo
        LEFT JOIN `tabCustomer Vehicle` cv ON cv.name = vjo.customer_vehicle
        LEFT JOIN `tabVehicle Make` vm ON vm.name = cv.make
        LEFT JOIN `tabVehicle Model` vmo ON vmo.name = cv.model
        WHERE {conditions}
        ORDER BY vjo.order_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "customer": customer},
        as_dict=True,
    )

    return columns, data
''',
    },
    "mechanic_jobs": {
        "name": "Mechanic Jobs",
        "ref_doctype": "Vehicle Job Order",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    mechanic = filters.get("mechanic")

    columns = [
        {"label": _("Mechanic"), "fieldname": "mechanic", "fieldtype": "Data", "width": 150},
        {"label": _("Date"), "fieldname": "order_date", "fieldtype": "Date", "width": 110},
        {"label": _("JO #"), "fieldname": "job_order", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Service"), "fieldname": "service_name", "fieldtype": "Data", "width": 180},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Service Amount (PHP)"), "fieldname": "amount", "fieldtype": "Currency", "width": 160},
        {"label": _("JO Total (PHP)"), "fieldname": "jo_total", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if mechanic:
        conditions += " AND e.employee_name LIKE %(mechanic)s"

    data = frappe.db.sql(
        f"""
        SELECT
            COALESCE(e.employee_name, vjo.mechanic) AS mechanic,
            vjo.order_date,
            vji.parent AS job_order,
            vji.service_name,
            CONCAT(COALESCE(vm.make,''),' ',COALESCE(vmo.model,'')) AS vehicle,
            vji.amount,
            vjo.grand_total AS jo_total
        FROM `tabVehicle Job Order Item` vji
        JOIN `tabVehicle Job Order` vjo ON vjo.name = vji.parent
        LEFT JOIN `tabCustomer Vehicle` cv ON cv.name = vjo.customer_vehicle
        LEFT JOIN `tabVehicle Make` vm ON vm.name = cv.make
        LEFT JOIN `tabVehicle Model` vmo ON vmo.name = cv.model
        LEFT JOIN `tabEmployee` e ON e.name = vjo.mechanic
        WHERE {conditions}
        ORDER BY mechanic, vjo.order_date
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "mechanic": f"%{mechanic}%" if mechanic else "%"},
        as_dict=True,
    )

    return columns, data
''',
    },
    "mechanic_clock_in_out": {
        "name": "Mechanic Clock In/Out",
        "ref_doctype": "Vehicle Job Order",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    mechanic = filters.get("mechanic")

    columns = [
        {"label": _("Date"), "fieldname": "work_date", "fieldtype": "Date", "width": 110},
        {"label": _("Mechanic"), "fieldname": "mechanic", "fieldtype": "Data", "width": 150},
        {"label": _("JO #"), "fieldname": "job_order", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Service"), "fieldname": "service_name", "fieldtype": "Data", "width": 180},
        {"label": _("Clock In"), "fieldname": "clock_in", "fieldtype": "Datetime", "width": 140},
        {"label": _("Clock Out"), "fieldname": "clock_out", "fieldtype": "Datetime", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if mechanic:
        conditions += " AND e.employee_name LIKE %(mechanic)s"

    # Fallback: show job orders with mechanic assignments (clock in/out approximated by creation/modified)
    data = frappe.db.sql(
        f"""
        SELECT
            vjo.order_date AS work_date,
            COALESCE(e.employee_name, vjo.mechanic) AS mechanic,
            vjo.name AS job_order,
            vji.service_name,
            vjo.creation AS clock_in,
            vjo.modified AS clock_out
        FROM `tabVehicle Job Order Item` vji
        JOIN `tabVehicle Job Order` vjo ON vjo.name = vji.parent
        LEFT JOIN `tabEmployee` e ON e.name = vjo.mechanic
        WHERE {conditions}
        ORDER BY work_date DESC, mechanic
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "mechanic": f"%{mechanic}%" if mechanic else "%"},
        as_dict=True,
    )

    return columns, data
''',
    },
    "due_for_service": {
        "name": "Due for Service",
        "ref_doctype": "Vehicle Service Reminder",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate, add_days


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or nowdate()
    to_date = filters.get("to_date") or add_days(nowdate(), 30)
    company = filters.get("company")

    columns = [
        {"label": _("Service"), "fieldname": "service_type", "fieldtype": "Data", "width": 160},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Contact No"), "fieldname": "mobile_no", "fieldtype": "Data", "width": 130},
        {"label": _("Last Service"), "fieldname": "last_service_date", "fieldtype": "Date", "width": 120},
        {"label": _("Due Date"), "fieldname": "next_service_date", "fieldtype": "Date", "width": 110},
        {"label": _("Days Due"), "fieldname": "days_due", "fieldtype": "Int", "width": 90},
        {"label": _("Plate No"), "fieldname": "license_plate", "fieldtype": "Data", "width": 110},
    ]

    conditions = "vsr.next_service_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vsr.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vsr.service_type,
            vsr.customer,
            c.mobile_no,
            vsr.last_service_date,
            vsr.next_service_date,
            (vsr.next_service_date - CURRENT_DATE) AS days_due,
            cv.license_plate
        FROM `tabVehicle Service Reminder` vsr
        LEFT JOIN `tabCustomer` c ON c.name = vsr.customer
        LEFT JOIN `tabCustomer Vehicle` cv ON cv.name = vsr.customer_vehicle
        WHERE {conditions}
        ORDER BY vsr.next_service_date
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "check_register": {
        "name": "Check Register",
        "ref_doctype": "Payment Entry",
        "python": '''import frappe
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

    conditions = "pe.docstatus = 1 AND pe.mode_of_payment LIKE '%Check%' AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND pe.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            pe.name,
            pe.posting_date,
            pe.party AS party,
            pe.reference_no,
            pe.reference_date,
            pe.paid_amount
        FROM `tabPayment Entry` pe
        WHERE {conditions}
        ORDER BY pe.posting_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "purchase_order_report": {
        "name": "Purchase Order Report",
        "ref_doctype": "Purchase Order",
        "python": '''import frappe
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
        {"label": _("Invoice No"), "fieldname": "bill_no", "fieldtype": "Data", "width": 140},
        {"label": _("Invoice Date"), "fieldname": "bill_date", "fieldtype": "Date", "width": 110},
        {"label": _("Amount (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]

    conditions = "po.docstatus = 1 AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND po.company = %(company)s"
    if supplier:
        conditions += " AND po.supplier = %(supplier)s"

    data = frappe.db.sql(
        f"""
        SELECT
            po.name,
            po.transaction_date,
            po.supplier,
            po.bill_no,
            po.bill_date,
            po.grand_total,
            po.status
        FROM `tabPurchase Order` po
        WHERE {conditions}
        ORDER BY po.transaction_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "supplier": supplier},
        as_dict=True,
    )

    return columns, data
''',
    },
    "product_purchases": {
        "name": "Product Purchases",
        "ref_doctype": "Purchase Receipt Item",
        "python": '''import frappe
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
        FROM `tabPurchase Receipt Item` pri
        JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
        WHERE {conditions}
        ORDER BY pr.posting_date DESC, pri.item_name
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "supplier": supplier, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
''',
    },
    "vehicle_transactions": {
        "name": "Vehicle Transactions",
        "ref_doctype": "Customer Vehicle",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    customer = filters.get("customer")
    plate_no = filters.get("plate_no")

    columns = [
        {"label": _("JO #"), "fieldname": "job_order", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Contact No"), "fieldname": "mobile_no", "fieldtype": "Data", "width": 130},
        {"label": _("Plate No"), "fieldname": "license_plate", "fieldtype": "Data", "width": 110},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Mileage"), "fieldname": "mileage", "fieldtype": "Int", "width": 100},
        {"label": _("First Visit"), "fieldname": "first_visit", "fieldtype": "Date", "width": 110},
        {"label": _("Last Visit"), "fieldname": "last_visit", "fieldtype": "Date", "width": 110},
        {"label": _("Date"), "fieldname": "order_date", "fieldtype": "Date", "width": 110},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if customer:
        conditions += " AND vjo.customer = %(customer)s"
    if plate_no:
        conditions += " AND cv.license_plate LIKE %(plate_no)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.name AS job_order,
            vjo.customer,
            c.mobile_no,
            cv.license_plate,
            CONCAT(COALESCE(vm.make,''),' ',COALESCE(vmo.model,'')) AS vehicle,
            COALESCE(vjo.mileage, 0) AS mileage,
            MIN(vjo.order_date) OVER (PARTITION BY cv.name) AS first_visit,
            MAX(vjo.order_date) OVER (PARTITION BY cv.name) AS last_visit,
            vjo.order_date,
            COALESCE(vjo.grand_total, 0) AS grand_total
        FROM `tabVehicle Job Order` vjo
        LEFT JOIN `tabCustomer Vehicle` cv ON cv.name = vjo.customer_vehicle
        LEFT JOIN `tabCustomer` c ON c.name = vjo.customer
        LEFT JOIN `tabVehicle Make` vm ON vm.name = cv.make
        LEFT JOIN `tabVehicle Model` vmo ON vmo.name = cv.model
        WHERE {conditions}
        ORDER BY vjo.order_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "customer": customer, "plate_no": f"%{plate_no}%" if plate_no else "%"},
        as_dict=True,
    )

    return columns, data
''',
    },
    "statement_of_account": {
        "name": "Statement of Account",
        "ref_doctype": "Sales Invoice",
        "python": '''import frappe
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
        FROM `tabGL Entry` gl
        WHERE {conditions}
        ORDER BY gl.posting_date, gl.creation
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "customer": customer},
        as_dict=True,
    )

    return columns, data
''',
    },
    "sales_incentives": {
        "name": "Sales Incentives",
        "ref_doctype": "Sales Invoice",
        "python": '''import frappe
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
        {"label": _("Commission % "), "fieldname": "commission_rate", "fieldtype": "Percent", "width": 120},
        {"label": _("Commission Amt (PHP)"), "fieldname": "commission_amount", "fieldtype": "Currency", "width": 180},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND si.company = %(company)s"
    if sales_person:
        conditions += " AND st.sales_person = %(sales_person)s"

    data = frappe.db.sql(
        f"""
        SELECT
            st.sales_person,
            st.parent,
            si.customer,
            si.grand_total,
            st.commission_rate,
            si.grand_total * st.commission_rate / 100 AS commission_amount,
            si.posting_date
        FROM `tabSales Team` st
        JOIN `tabSales Invoice` si ON si.name = st.parent
        WHERE si.doctype = 'Sales Invoice' AND {conditions}
        ORDER BY si.posting_date DESC, st.sales_person
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "sales_person": sales_person},
        as_dict=True,
    )

    return columns, data
''',
    },
    "loyalty_points": {
        "name": "Loyalty Points",
        "ref_doctype": "Loyalty Point Entry",
        "python": '''import frappe
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
        FROM `tabLoyalty Point Entry` lpe
        LEFT JOIN `tabCustomer` c ON c.name = lpe.customer
        WHERE {conditions}
        GROUP BY lpe.customer, c.mobile_no, lpe.loyalty_program
        ORDER BY current_points DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "top_customers": {
        "name": "Top Customers",
        "ref_doctype": "Sales Invoice",
        "python": '''import frappe
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
        FROM `tabSales Invoice` si
        LEFT JOIN `tabCustomer` c ON c.name = si.customer
        WHERE {conditions}
        GROUP BY si.customer, c.mobile_no
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "top_suppliers": {
        "name": "Top Suppliers",
        "ref_doctype": "Purchase Order",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": _("PO Count"), "fieldname": "po_count", "fieldtype": "Int", "width": 100},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "po.docstatus = 1 AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND po.company = %(company)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "po_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            po.supplier,
            COUNT(po.name) AS po_count,
            SUM(po.grand_total) AS total_amount,
            ROUND(SUM(po.grand_total) * 100.0 / SUM(SUM(po.grand_total)) OVER (), 2) AS percentage
        FROM `tabPurchase Order` po
        WHERE {conditions}
        GROUP BY po.supplier
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
''',
    },
    "top_selling_services": {
        "name": "Top Selling Services",
        "ref_doctype": "Sales Invoice Item",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    item_group = filters.get("item_group")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Service"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 130},
        {"label": _("Count"), "fieldname": "service_count", "fieldtype": "Int", "width": 90},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sii.item_group IN ('Services','Labor','Service')"
    if company:
        conditions += " AND si.company = %(company)s"
    if item_group:
        conditions += " AND sii.item_group = %(item_group)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "service_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            sii.item_name,
            sii.item_code,
            sii.item_group,
            COUNT(sii.name) AS service_count,
            SUM(sii.amount) AS total_amount,
            ROUND(SUM(sii.amount) * 100.0 / SUM(SUM(sii.amount)) OVER (), 2) AS percentage
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE {conditions}
        GROUP BY sii.item_name, sii.item_code, sii.item_group
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
''',
    },
    "top_selling_products": {
        "name": "Top Selling Products",
        "ref_doctype": "Sales Invoice Item",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    item_group = filters.get("item_group")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Product"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Part No"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 130},
        {"label": _("Count"), "fieldname": "product_count", "fieldtype": "Int", "width": 90},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s AND sii.item_group NOT IN ('Services','Labor','Service')"
    if company:
        conditions += " AND si.company = %(company)s"
    if item_group:
        conditions += " AND sii.item_group = %(item_group)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "product_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            sii.item_name,
            sii.item_code,
            sii.item_group,
            COUNT(sii.name) AS product_count,
            SUM(sii.amount) AS total_amount,
            ROUND(SUM(sii.amount) * 100.0 / SUM(SUM(sii.amount)) OVER (), 2) AS percentage
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE {conditions}
        GROUP BY sii.item_name, sii.item_code, sii.item_group
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
''',
    },
    "top_vehicles_served": {
        "name": "Top Vehicles Served",
        "ref_doctype": "Vehicle Job Order",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    make = filters.get("make")
    sort_by = filters.get("sort_by") or "Total Amount"

    columns = [
        {"label": _("Make"), "fieldname": "make", "fieldtype": "Data", "width": 120},
        {"label": _("Model"), "fieldname": "model", "fieldtype": "Data", "width": 140},
        {"label": _("Count"), "fieldname": "visit_count", "fieldtype": "Int", "width": 90},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if make:
        conditions += " AND vm.make = %(make)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "visit_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            COALESCE(vm.make, 'Unknown') AS make,
            COALESCE(vmo.model, 'Unknown') AS model,
            COUNT(vjo.name) AS visit_count,
            SUM(COALESCE(vjo.grand_total, 0)) AS total_amount,
            ROUND(SUM(COALESCE(vjo.grand_total, 0)) * 100.0 / NULLIF(SUM(SUM(COALESCE(vjo.grand_total, 0))) OVER (), 0), 2) AS percentage
        FROM `tabVehicle Job Order` vjo
        LEFT JOIN `tabCustomer Vehicle` cv ON cv.name = vjo.customer_vehicle
        LEFT JOIN `tabVehicle Make` vm ON vm.name = cv.make
        LEFT JOIN `tabVehicle Model` vmo ON vmo.name = cv.model
        WHERE {conditions}
        GROUP BY COALESCE(vm.make,'Unknown'), COALESCE(vmo.model,'Unknown')
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "make": make},
        as_dict=True,
    )

    return columns, data
''',
    },
    "inventory_summary": {
        "name": "Inventory Summary",
        "ref_doctype": "Stock Ledger Entry",
        "python": '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    item_group = filters.get("item_group")

    columns = [
        {"label": _("Product"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Part No"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Product Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 140},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 90},
        {"label": _("Inventory Value (PHP)"), "fieldname": "inventory_value", "fieldtype": "Currency", "width": 180},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
    ]

    conditions = "sle.posting_date <= %(to_date)s AND sle.is_cancelled = 0"
    if company:
        conditions += " AND sle.company = %(company)s"
    if item_group:
        conditions += " AND i.item_group = %(item_group)s"

    data = frappe.db.sql(
        f"""
        SELECT
            i.item_name,
            sle.item_code,
            i.item_group,
            SUM(sle.actual_qty) AS qty,
            SUM(sle.stock_value_difference) AS inventory_value,
            sle.warehouse
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        WHERE {conditions}
        GROUP BY sle.item_code, i.item_name, i.item_group, sle.warehouse
        HAVING SUM(sle.actual_qty) > 0
        ORDER BY i.item_group, i.item_name
        """,
        {"to_date": to_date, "company": company, "item_group": item_group},
        as_dict=True,
    )

    return columns, data
''',
    },
}

FILTER_TEMPLATE = {
    "company": {"fieldname": "company", "label": "Company", "fieldtype": "Link", "options": "Company", "width": "200"},
    "from_date": {"fieldname": "from_date", "label": "From Date", "fieldtype": "Date", "default": "Today", "width": "100"},
    "to_date": {"fieldname": "to_date", "label": "To Date", "fieldtype": "Date", "default": "Today", "width": "100"},
    "customer": {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer"},
    "supplier": {"fieldname": "supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier"},
    "sales_person": {"fieldname": "sales_person", "label": "Sales Person", "fieldtype": "Link", "options": "Sales Person"},
    "mechanic": {"fieldname": "mechanic", "label": "Mechanic", "fieldtype": "Link", "options": "Employee"},
    "item": {"fieldname": "item", "label": "Product", "fieldtype": "Link", "options": "Item"},
    "item_group": {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Link", "options": "Item Group"},
    "plate_no": {"fieldname": "plate_no", "label": "Plate No", "fieldtype": "Data"},
    "make": {"fieldname": "make", "label": "Vehicle Make", "fieldtype": "Link", "options": "Vehicle Make"},
    "report_type": {"fieldname": "report_type", "label": "Format", "fieldtype": "Select", "options": "Activities\nOutstanding Invoices"},
    "sort_by": {"fieldname": "sort_by", "label": "Sort By", "fieldtype": "Select", "options": "Total Amount\nCount"},
}

REPORT_FILTERS = {
    "monthly_sales_report": ["company", "from_date", "to_date"],
    "detailed_sales_report": ["company", "from_date", "to_date", "customer", "sales_person"],
    "sales_by_product": ["company", "from_date", "to_date", "item", "item_group"],
    "daily_collection_report": ["company", "from_date", "to_date"],
    "monthly_job_orders": ["company", "from_date", "to_date"],
    "detailed_job_orders": ["company", "from_date", "to_date", "customer"],
    "mechanic_jobs": ["company", "from_date", "to_date", "mechanic"],
    "mechanic_clock_in_out": ["company", "from_date", "to_date", "mechanic"],
    "due_for_service": ["company", "from_date", "to_date"],
    "check_register": ["company", "from_date", "to_date"],
    "purchase_order_report": ["company", "from_date", "to_date", "supplier"],
    "product_purchases": ["company", "from_date", "to_date", "supplier", "item_group"],
    "vehicle_transactions": ["company", "from_date", "to_date", "customer", "plate_no"],
    "statement_of_account": ["company", "from_date", "to_date", "customer", "report_type"],
    "sales_incentives": ["company", "from_date", "to_date", "sales_person"],
    "loyalty_points": ["company", "from_date", "to_date"],
    "top_customers": ["company", "from_date", "to_date", "sort_by"],
    "top_suppliers": ["company", "from_date", "to_date", "sort_by"],
    "top_selling_services": ["company", "from_date", "to_date", "item_group", "sort_by"],
    "top_selling_products": ["company", "from_date", "to_date", "item_group", "sort_by"],
    "top_vehicles_served": ["company", "from_date", "to_date", "make", "sort_by"],
    "inventory_summary": ["company", "to_date", "item_group"],
}

created = []
errors = []

for folder, report_data in REPORTS.items():
    report_dir = os.path.join(BASE, folder)
    os.makedirs(report_dir, exist_ok=True)

    # Write JSON
    json_data = make_json(report_data["name"], report_data.get("ref_doctype", "Sales Invoice"))
    json_path = os.path.join(report_dir, f"{folder}.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=1)

    # Write Python
    py_path = os.path.join(report_dir, f"{folder}.py")
    with open(py_path, "w") as f:
        f.write(report_data["python"])

    # Write filters JS
    filters_list = REPORT_FILTERS.get(folder, ["company", "from_date", "to_date"])
    filters_js = []
    for fk in filters_list:
        ft = FILTER_TEMPLATE[fk].copy()
        filters_js.append(ft)

    js_content = f"""frappe.query_reports["{report_data['name']}"] = {{
\tfilters: {json.dumps(filters_js, indent=2).replace('"', '"')}
}};
"""
    js_path = os.path.join(report_dir, f"{folder}.js")
    with open(js_path, "w") as f:
        f.write(js_content)

    # Write __init__.py
    init_path = os.path.join(report_dir, "__init__.py")
    with open(init_path, "w") as f:
        f.write("")

    created.append(report_data["name"])
    print(f"  ✓ {report_data['name']}")

print(f"\n✅ Created {len(created)} reports successfully!")
print("\nReports created:")
for r in created:
    print(f"  - {r}")
