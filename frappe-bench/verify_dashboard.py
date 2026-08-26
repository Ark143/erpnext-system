import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

pages = frappe.db.sql(
    "SELECT name, route, published FROM \"tabWeb Page\" WHERE name IN ('vm-dashboard', 'vm-company-dashboard')",
    as_dict=True
)
for p in pages:
    print(p)

try:
    from vehicle_management.vehicle_management.dashboard_api import get_company_dashboard, get_all_companies_summary
    print('API import: OK')
    # Quick test
    result = get_all_companies_summary()
    print(f'Companies returned: {len(result)}')
    if result:
        print(f'First: {result[0]["name"]} - YTD Revenue: {result[0]["ytd_revenue"]}')
except Exception as e:
    print(f'API error: {e}')
