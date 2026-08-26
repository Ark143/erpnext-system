"""
Fix all VM report queries that use incorrect field names based on actual VJO schema.
VJO actual fields: name, vehicle, plate_no, customer, customer_name, contact_no, 
                   job_order_date, status, mileage, total_labor, total_parts, 
                   net_total, discount_amount, grand_total, sales_invoice, company
"""
import os

BASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'apps', 'vehicle_management', 'vehicle_management',
    'vehicle_management', 'report'
)

# Fixed detailed_job_orders.py
detailed_jo = '''import frappe
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
        {"label": _("Parts (PHP)"), "fieldname": "total_parts", "fieldtype": "Currency", "width": 130},
        {"label": _("Labor (PHP)"), "fieldname": "total_labor", "fieldtype": "Currency", "width": 130},
        {"label": _("Discount (PHP)"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 130},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if customer:
        conditions += " AND vjo.customer = %(customer)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.name,
            vjo.customer,
            vjo.plate_no,
            vjo.vehicle,
            vjo.status,
            vjo.sales_invoice,
            COALESCE(vjo.total_parts, 0) AS total_parts,
            COALESCE(vjo.total_labor, 0) AS total_labor,
            COALESCE(vjo.discount_amount, 0) AS discount_amount,
            COALESCE(vjo.grand_total, 0) AS grand_total,
            vjo.job_order_date
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.job_order_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company, "customer": customer},
        as_dict=True,
    )

    return columns, data
'''

# Fixed monthly_job_orders.py
monthly_jo = '''import frappe
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
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            TO_CHAR(vjo.job_order_date, \'YYYY-MM\') AS month,
            COUNT(vjo.name) AS jo_count,
            SUM(COALESCE(vjo.total_parts, 0)) AS parts,
            SUM(COALESCE(vjo.total_labor, 0)) AS labor,
            SUM(COALESCE(vjo.discount_amount, 0)) AS discount,
            SUM(COALESCE(vjo.grand_total, 0)) AS total_amount
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        GROUP BY TO_CHAR(vjo.job_order_date, \'YYYY-MM\')
        ORDER BY month
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
'''

# Fixed mechanic_jobs.py
mechanic_jobs = '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    mechanic = filters.get("mechanic")

    columns = [
        {"label": _("Service Advisor"), "fieldname": "service_advisor", "fieldtype": "Data", "width": 150},
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Labor (PHP)"), "fieldname": "total_labor", "fieldtype": "Currency", "width": 140},
        {"label": _("JO Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if mechanic:
        conditions += " AND vjo.service_advisor LIKE %(mechanic)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.service_advisor,
            vjo.job_order_date,
            vjo.name,
            vjo.vehicle,
            vjo.plate_no,
            COALESCE(vjo.total_labor, 0) AS total_labor,
            COALESCE(vjo.grand_total, 0) AS grand_total
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.service_advisor, vjo.job_order_date
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "mechanic": f"%{mechanic}%" if mechanic else "%"},
        as_dict=True,
    )

    return columns, data
'''

# Fixed mechanic_clock_in_out.py
mechanic_clock = '''import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or "2020-01-01"
    to_date = filters.get("to_date") or nowdate()
    company = filters.get("company")
    mechanic = filters.get("mechanic")

    columns = [
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
        {"label": _("Service Advisor"), "fieldname": "service_advisor", "fieldtype": "Data", "width": 150},
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Time In"), "fieldname": "time_in", "fieldtype": "Data", "width": 120},
        {"label": _("Work Start"), "fieldname": "work_start_time", "fieldtype": "Data", "width": 120},
        {"label": _("Work End"), "fieldname": "work_end_time", "fieldtype": "Data", "width": 120},
        {"label": _("Time Out"), "fieldname": "time_out", "fieldtype": "Data", "width": 120},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if mechanic:
        conditions += " AND vjo.service_advisor LIKE %(mechanic)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.job_order_date,
            vjo.service_advisor,
            vjo.name,
            vjo.vehicle,
            COALESCE(CAST(vjo.time_in AS VARCHAR), \'\') AS time_in,
            COALESCE(CAST(vjo.work_start_time AS VARCHAR), \'\') AS work_start_time,
            COALESCE(CAST(vjo.work_end_time AS VARCHAR), \'\') AS work_end_time,
            COALESCE(CAST(vjo.time_out AS VARCHAR), \'\') AS time_out
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.job_order_date DESC, vjo.service_advisor
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "mechanic": f"%{mechanic}%" if mechanic else "%"},
        as_dict=True,
    )

    return columns, data
'''

# Fixed vehicle_transactions.py
vehicle_tx = '''import frappe
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
        {"label": _("JO #"), "fieldname": "name", "fieldtype": "Link", "options": "Vehicle Job Order", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Contact No"), "fieldname": "contact_no", "fieldtype": "Data", "width": 130},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Mileage"), "fieldname": "mileage", "fieldtype": "Int", "width": 100},
        {"label": _("Date"), "fieldname": "job_order_date", "fieldtype": "Date", "width": 110},
        {"label": _("Total (PHP)"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if customer:
        conditions += " AND vjo.customer = %(customer)s"
    if plate_no:
        conditions += " AND vjo.plate_no LIKE %(plate_no)s"

    data = frappe.db.sql(
        f"""
        SELECT
            vjo.name,
            vjo.customer,
            vjo.contact_no,
            vjo.plate_no,
            vjo.vehicle,
            COALESCE(vjo.mileage, 0) AS mileage,
            vjo.job_order_date,
            COALESCE(vjo.grand_total, 0) AS grand_total
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        ORDER BY vjo.job_order_date DESC
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "customer": customer, "plate_no": f"%{plate_no}%" if plate_no else "%"},
        as_dict=True,
    )

    return columns, data
'''

# Fixed top_vehicles_served.py
top_vehicles = '''import frappe
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
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 200},
        {"label": _("Count"), "fieldname": "visit_count", "fieldtype": "Int", "width": 90},
        {"label": _("Total Amount (PHP)"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 160},
        {"label": _("Percentage"), "fieldname": "percentage", "fieldtype": "Percent", "width": 110},
    ]

    conditions = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    if company:
        conditions += " AND vjo.company = %(company)s"
    if make:
        conditions += " AND vjo.vehicle LIKE %(make)s"

    order_by = "total_amount DESC" if sort_by == "Total Amount" else "visit_count DESC"

    data = frappe.db.sql(
        f"""
        SELECT
            COALESCE(vjo.vehicle, \'Unknown\') AS vehicle,
            COUNT(vjo.name) AS visit_count,
            SUM(COALESCE(vjo.grand_total, 0)) AS total_amount,
            ROUND(
                SUM(COALESCE(vjo.grand_total, 0)) * 100.0 /
                NULLIF(SUM(SUM(COALESCE(vjo.grand_total, 0))) OVER (), 0),
                2
            ) AS percentage
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        GROUP BY COALESCE(vjo.vehicle, \'Unknown\')
        ORDER BY {order_by}
        LIMIT 50
        """,
        {"from_date": from_date, "to_date": to_date, "company": company,
         "make": f"%{make}%" if make else "%"},
        as_dict=True,
    )

    return columns, data
'''

# Fixed due_for_service.py
due_service = '''import frappe
from frappe import _
from frappe.utils import nowdate, add_days


def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("from_date") or nowdate()
    to_date = filters.get("to_date") or add_days(nowdate(), 30)
    company = filters.get("company")

    columns = [
        {"label": _("Service Type"), "fieldname": "service_type", "fieldtype": "Data", "width": 160},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 160},
        {"label": _("Plate No"), "fieldname": "plate_no", "fieldtype": "Data", "width": 110},
        {"label": _("Last Service"), "fieldname": "last_service_date", "fieldtype": "Date", "width": 120},
        {"label": _("Next Service"), "fieldname": "next_service_date", "fieldtype": "Date", "width": 110},
        {"label": _("Days Due"), "fieldname": "days_due", "fieldtype": "Int", "width": 90},
    ]

    # Query last job orders per vehicle and estimate due date (mileage interval = 5000 km)
    conditions = "vjo.docstatus = 1"
    if company:
        conditions += " AND vjo.company = %(company)s"

    data = frappe.db.sql(
        f"""
        SELECT
            \'PMS / Oil Change\' AS service_type,
            vjo.customer,
            vjo.vehicle,
            vjo.plate_no,
            MAX(vjo.job_order_date) AS last_service_date,
            MAX(vjo.job_order_date) + INTERVAL \'90 days\' AS next_service_date,
            (MAX(vjo.job_order_date) + INTERVAL \'90 days\' - CURRENT_DATE) AS days_due
        FROM "tabVehicle Job Order" vjo
        WHERE {conditions}
        GROUP BY vjo.customer, vjo.vehicle, vjo.plate_no
        HAVING (MAX(vjo.job_order_date) + INTERVAL \'90 days\') BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY next_service_date
        """,
        {"from_date": from_date, "to_date": to_date, "company": company},
        as_dict=True,
    )

    return columns, data
'''

files_to_write = {
    'detailed_job_orders': detailed_jo,
    'monthly_job_orders': monthly_jo,
    'mechanic_jobs': mechanic_jobs,
    'mechanic_clock_in_out': mechanic_clock,
    'vehicle_transactions': vehicle_tx,
    'top_vehicles_served': top_vehicles,
    'due_for_service': due_service,
}

for folder, content in files_to_write.items():
    py_path = os.path.join(BASE, folder, f'{folder}.py')
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed: {folder}')

print('\nAll files fixed!')
