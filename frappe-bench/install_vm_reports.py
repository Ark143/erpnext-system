import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

reports = [
    ('Monthly Sales Report', 'Sales Invoice', 'monthly_sales_report'),
    ('Detailed Sales Report', 'Sales Invoice', 'detailed_sales_report'),
    ('Sales by Product', 'Sales Invoice Item', 'sales_by_product'),
    ('Daily Collection Report', 'Payment Entry', 'daily_collection_report'),
    ('Monthly Job Orders', 'Vehicle Job Order', 'monthly_job_orders'),
    ('Detailed Job Orders', 'Vehicle Job Order', 'detailed_job_orders'),
    ('Mechanic Jobs', 'Vehicle Job Order', 'mechanic_jobs'),
    ('Mechanic Clock In/Out', 'Vehicle Job Order', 'mechanic_clock_in_out'),
    ('Due for Service', 'Vehicle Service Reminder', 'due_for_service'),
    ('Check Register', 'Payment Entry', 'check_register'),
    ('Purchase Order Report', 'Purchase Order', 'purchase_order_report'),
    ('Product Purchases', 'Purchase Receipt Item', 'product_purchases'),
    ('Vehicle Transactions', 'Customer Vehicle', 'vehicle_transactions'),
    ('Statement of Account', 'Sales Invoice', 'statement_of_account'),
    ('Sales Incentives', 'Sales Invoice', 'sales_incentives'),
    ('Loyalty Points', 'Loyalty Point Entry', 'loyalty_points'),
    ('Top Customers', 'Sales Invoice', 'top_customers'),
    ('Top Suppliers', 'Purchase Order', 'top_suppliers'),
    ('Top Selling Services', 'Sales Invoice Item', 'top_selling_services'),
    ('Top Selling Products', 'Sales Invoice Item', 'top_selling_products'),
    ('Top Vehicles Served', 'Vehicle Job Order', 'top_vehicles_served'),
    ('Inventory Summary', 'Stock Ledger Entry', 'inventory_summary'),
]

from frappe.utils import now_datetime
now = now_datetime()
created = 0
updated = 0

BASE_REPORT = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'apps/vehicle_management/vehicle_management/vehicle_management/report'
    )
)

for report_name, ref_doctype, folder in reports:
    # Read Python script
    py_path = os.path.join(BASE_REPORT, folder, f'{folder}.py')
    report_script = ''
    if os.path.exists(py_path):
        with open(py_path, 'r', encoding='utf-8') as f:
            report_script = f.read()

    # Read JS
    js_path = os.path.join(BASE_REPORT, folder, f'{folder}.js')
    js_content = ''
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

    exists = frappe.db.exists('Report', report_name)
    if not exists:
        insert_sql = (
            'INSERT INTO "tabReport" (name, report_name, ref_doctype, report_type, module, '
            'is_standard, disabled, creation, modified, modified_by, owner, docstatus, '
            'report_script, javascript, add_total_row) '
            'VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, 0, %s, %s, 1)'
        )
        frappe.db.sql(insert_sql, (
            report_name, report_name, ref_doctype, 'Script Report', 'Vehicle Management', 'Yes',
            now, now, 'Administrator', 'Administrator', report_script, js_content
        ))
        created += 1
        print(f'CREATED: {report_name}')
    else:
        update_sql = (
            'UPDATE "tabReport" SET ref_doctype=%s, report_type=%s, module=%s, is_standard=%s, '
            'disabled=0, report_script=%s, javascript=%s, modified=%s, modified_by=%s '
            'WHERE name=%s'
        )
        frappe.db.sql(update_sql, (
            ref_doctype, 'Script Report', 'Vehicle Management', 'Yes',
            report_script, js_content, now, 'Administrator', report_name
        ))
        updated += 1
        print(f'UPDATED: {report_name}')

frappe.db.commit()
print(f'\nDone! Created: {created}, Updated: {updated}')
