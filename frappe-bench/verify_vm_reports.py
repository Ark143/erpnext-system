import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

reports = [
    'Monthly Sales Report', 'Detailed Sales Report', 'Sales by Product',
    'Daily Collection Report', 'Monthly Job Orders', 'Detailed Job Orders',
    'Mechanic Jobs', 'Mechanic Clock In/Out', 'Due for Service', 'Check Register',
    'Purchase Order Report', 'Product Purchases', 'Vehicle Transactions',
    'Statement of Account', 'Sales Incentives', 'Loyalty Points',
    'Top Customers', 'Top Suppliers', 'Top Selling Services',
    'Top Selling Products', 'Top Vehicles Served', 'Inventory Summary'
]

print('=== Report Verification ===')
all_ok = True
for r in reports:
    exists = frappe.db.exists('Report', r)
    status = 'OK' if exists else 'MISSING'
    if not exists:
        all_ok = False
    print(f'  [{status}] {r}')

print()
if all_ok:
    print('All 22 reports verified in database!')

print()
print('=== Testing Monthly Sales Report ===')
try:
    from vehicle_management.vehicle_management.report.monthly_sales_report.monthly_sales_report import execute
    cols, data = execute({'from_date': '2024-01-01', 'to_date': '2025-12-31'})
    print(f'  Columns: {len(cols)}, Rows: {len(data)}')
    print('  PASS')
except Exception as e:
    print(f'  FAIL: {e}')

print()
print('=== Testing Top Customers ===')
try:
    from vehicle_management.vehicle_management.report.top_customers.top_customers import execute
    cols, data = execute({'from_date': '2024-01-01', 'to_date': '2025-12-31'})
    print(f'  Columns: {len(cols)}, Rows: {len(data)}')
    if data:
        cust = data[0].get('customer', 'N/A')
        amt = data[0].get('total_amount', 0)
        print(f'  Top customer: {cust} = PHP {amt}')
    print('  PASS')
except Exception as e:
    print(f'  FAIL: {e}')

print()
print('=== Testing Detailed Job Orders ===')
try:
    from vehicle_management.vehicle_management.report.detailed_job_orders.detailed_job_orders import execute
    cols, data = execute({'from_date': '2024-01-01', 'to_date': '2025-12-31'})
    print(f'  Columns: {len(cols)}, Rows: {len(data)}')
    print('  PASS')
except Exception as e:
    print(f'  FAIL: {e}')

print()
print('=== Testing Inventory Summary ===')
try:
    from vehicle_management.vehicle_management.report.inventory_summary.inventory_summary import execute
    cols, data = execute({'to_date': '2025-12-31'})
    print(f'  Columns: {len(cols)}, Rows: {len(data)}')
    print('  PASS')
except Exception as e:
    print(f'  FAIL: {e}')
