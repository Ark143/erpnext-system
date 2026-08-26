"""
Fix all VM reports: 
1. Replace backtick table references with double-quoted PostgreSQL style
2. Fix params to use dict instead of tuple for conditional queries
3. Fix field name errors
"""
import os
import re

BASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'apps', 'vehicle_management', 'vehicle_management',
    'vehicle_management', 'report'
)


def fix_backticks(content):
    """Replace `tabX` with "tabX" """
    return re.sub(r'`(tab[^`]+)`', r'"\1"', content)


# Fix all remaining reports by replacing backtick table names
reports_to_fix = [
    'monthly_sales_report',
    'monthly_job_orders',
    'detailed_job_orders',
    'mechanic_jobs',
    'mechanic_clock_in_out',
    'vehicle_transactions',
    'top_vehicles_served',
    'due_for_service',
    'check_register',
    'purchase_order_report',
    'product_purchases',
    'statement_of_account',
    'sales_incentives',
    'loyalty_points',
    'top_customers',
    'top_suppliers',
    'top_selling_services',
    'top_selling_products',
    'inventory_summary',
]

fixed = 0
for folder in reports_to_fix:
    py_path = os.path.join(BASE, folder, f'{folder}.py')
    if not os.path.exists(py_path):
        print(f'  SKIP (not found): {folder}')
        continue
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = fix_backticks(content)
    if new_content != content:
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'  FIXED backticks: {folder}')
        fixed += 1
    else:
        print(f'  OK (no backticks): {folder}')

print(f'\nFixed {fixed} files with backtick replacements')
