import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

companies = frappe.db.sql(
    'SELECT name, abbr, default_currency, website, company_logo FROM "tabCompany" ORDER BY name',
    as_dict=True
)
for c in companies:
    print(c)

print(f'\nTotal: {len(companies)} companies')
