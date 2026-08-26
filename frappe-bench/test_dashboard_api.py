import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

from vehicle_management.vehicle_management.dashboard_api import get_company_dashboard, get_all_companies_summary

print('=== COMPANY HUB TEST ===\n')
companies = get_all_companies_summary()
total_rev = sum(c['ytd_revenue'] for c in companies)
total_jo = sum(c['ytd_jo_count'] for c in companies)
print(f'Companies: {len(companies)}')
print(f'YTD Combined Revenue: PHP {total_rev:,.2f}')
print(f'YTD Combined JO Count: {total_jo}')
print()
for c in companies:
    print(f'  [{c["abbr"]:8s}] {c["name"][:30]:30s} Rev: PHP {c["ytd_revenue"]:>12,.0f}  JOs: {c["ytd_jo_count"]:>5}')

print('\n=== COMPANY DASHBOARD TEST (Ultra MRF Dau Main) ===\n')
data = get_company_dashboard(company='Ultra MRF Dau Main', period='all_time')
k = data['kpis']
print(f'Period: {data["from_date"]} to {data["to_date"]}')
print(f'Total Revenue:    PHP {k["total_revenue"]:>12,.2f}')
print(f'Invoice Count:         {k["invoice_count"]:>12,}')
print(f'Total Job Orders:      {k["total_jo"]:>12,}')
print(f'  Completed JOs:       {k["completed_jo"]:>12,}')
print(f'  In Progress:         {k["in_progress_jo"]:>12,}')
print(f'  Released:            {k["released_jo"]:>12,}')
print(f'Labor Revenue:    PHP {k["labor_revenue"]:>12,.2f}')
print(f'Parts Revenue:    PHP {k["parts_revenue"]:>12,.2f}')
print(f'Total Purchases:  PHP {k["total_purchases"]:>12,.2f}')
print(f'Unique Customers:      {k["unique_customers"]:>12,}')
print(f'Unique Vehicles:       {k["unique_vehicles"]:>12,}')
print(f'Total Commissions:PHP {k["total_commissions"]:>12,.2f}')
print(f'Total Collected:  PHP {k["total_collected"]:>12,.2f}')

print(f'\nRevenue Trend Months: {len(data["revenue_trend"])}')
print(f'Top Customers:        {len(data["top_customers"])}')
print(f'Top Vehicles:         {len(data["top_vehicles"])}')
print(f'Top Services:         {len(data["top_services"])}')
print(f'Top Products:         {len(data["top_products"])}')
print(f'Audit Trail Rows:     {len(data["audit_trail"])}')
print(f'Due for Service:      {len(data["due_for_service"])}')

if data["top_customers"]:
    tc = data["top_customers"][0]
    print(f'\nTop Customer: {tc["customer"]} - PHP {tc["total_spent"]:,.0f} ({tc["visits"]} visits)')

if data["audit_trail"]:
    at = data["audit_trail"][0]
    print(f'Latest Audit: [{at["doc_type"]}] {at["ref"]} - PHP {at["amount"]:,.0f} by {at["modified_by"]}')

print('\nALL TESTS PASSED!')
