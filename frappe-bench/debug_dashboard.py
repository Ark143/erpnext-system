import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

print('=== TEST 1: Web Pages in DB ===')
wp = frappe.db.sql(
    "SELECT name, route, published, LENGTH(main_section) as html_len FROM \"tabWeb Page\" WHERE name IN ('vm-dashboard', 'vm-company-dashboard')",
    as_dict=True
)
if wp:
    for p in wp:
        print(f'  {p}')
else:
    print('  NO WEB PAGES FOUND!')

print('\n=== TEST 2: API Module Import ===')
try:
    from vehicle_management.vehicle_management.dashboard_api import get_all_companies_summary, get_company_dashboard
    print('  Import: OK')
except Exception as e:
    print(f'  Import FAILED: {e}')

print('\n=== TEST 3: API Execution ===')
try:
    result = get_all_companies_summary()
    print(f'  get_all_companies_summary: {len(result)} companies')
    if result:
        print(f'  First: {result[0]["name"]} - Revenue: {result[0]["ytd_revenue"]}')
except Exception as e:
    print(f'  FAILED: {e}')

print('\n=== TEST 4: API HTTP Endpoint via frappe ===')
try:
    resp = frappe.call(
        'vehicle_management.vehicle_management.dashboard_api.get_all_companies_summary'
    )
    print(f'  frappe.call result: {len(resp)} companies')
except Exception as e:
    print(f'  frappe.call FAILED: {e}')

print('\n=== TEST 5: Check whitelist registration ===')
try:
    import frappe.utils.response as fres
    from vehicle_management.vehicle_management.dashboard_api import get_company_dashboard
    print(f'  get_company_dashboard whitelisted: {getattr(get_company_dashboard, "__call__", None) is not None}')
    print(f'  has whitelist attr: {hasattr(get_company_dashboard, "__frappe_whitelist__")}')
except Exception as e:
    print(f'  Check FAILED: {e}')

print('\n=== TEST 6: Check main_section field ===')
col = frappe.db.sql(
    "SELECT column_name FROM information_schema.columns WHERE table_name='tabWeb Page' ORDER BY ordinal_position",
    as_dict=True
)
print('  WebPage columns:', [c['column_name'] for c in col])
