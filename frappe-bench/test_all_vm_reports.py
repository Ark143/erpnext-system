import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

test_cases = [
    ('monthly_sales_report', 'Monthly Sales Report', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('detailed_sales_report', 'Detailed Sales Report', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('sales_by_product', 'Sales by Product', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('daily_collection_report', 'Daily Collection Report', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('monthly_job_orders', 'Monthly Job Orders', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('detailed_job_orders', 'Detailed Job Orders', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('mechanic_jobs', 'Mechanic Jobs', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('mechanic_clock_in_out', 'Mechanic Clock In/Out', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('due_for_service', 'Due for Service', {'from_date': '2024-01-01', 'to_date': '2026-12-31'}),
    ('check_register', 'Check Register', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('purchase_order_report', 'Purchase Order Report', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('product_purchases', 'Product Purchases', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('vehicle_transactions', 'Vehicle Transactions', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('statement_of_account', 'Statement of Account', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('sales_incentives', 'Sales Incentives', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('loyalty_points', 'Loyalty Points', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('top_customers', 'Top Customers', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('top_suppliers', 'Top Suppliers', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('top_selling_services', 'Top Selling Services', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('top_selling_products', 'Top Selling Products', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('top_vehicles_served', 'Top Vehicles Served', {'from_date': '2024-01-01', 'to_date': '2025-12-31'}),
    ('inventory_summary', 'Inventory Summary', {'to_date': '2025-12-31'}),
]

passed = 0
failed = 0
failures = []

print('=== Full Report Execution Test ===\n')

import importlib
for folder, report_name, filters in test_cases:
    module_path = f'vehicle_management.vehicle_management.report.{folder}.{folder}'
    try:
        # Rollback any aborted transaction first
        try:
            frappe.db.rollback()
        except Exception:
            pass
        mod = importlib.import_module(module_path)
        importlib.reload(mod)
        cols, data = mod.execute(filters)
        status = 'PASS'
        info = f'{len(cols)} cols, {len(data)} rows'
        passed += 1
        print(f'  [PASS] {report_name:40s} ({info})')
    except Exception as e:
        failed += 1
        error_msg = str(e).split(chr(10))[0][:100]
        failures.append((report_name, error_msg))
        print(f'  [FAIL] {report_name:40s} -> {error_msg}')
        try:
            frappe.db.rollback()
        except Exception:
            pass

print(f'\n{"="*60}')
print(f'Results: {passed} passed, {failed} failed out of {passed+failed} tests')
if failures:
    print('\nFailed reports:')
    for name, err in failures:
        print(f'  - {name}: {err}')
else:
    print('ALL REPORTS PASSING!')
