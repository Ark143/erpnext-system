import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

companies = frappe.db.sql('SELECT name, abbr, default_currency FROM "tabCompany" WHERE name != %s ORDER BY name', ("My Company",), as_dict=True)
for c in companies:
    slug = frappe.scrub(c['name']).replace('_', '-')
    print(f"Company: {c['name']} -> Route: executive-{slug}")
