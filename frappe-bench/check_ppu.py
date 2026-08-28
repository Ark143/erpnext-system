import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

ppu = frappe.db.sql('SELECT parent, "user", "default" FROM "tabPOS Profile User"', as_dict=True)
print("POS Profile Users in DB:", ppu)

users = [r['name'] for r in frappe.db.sql('SELECT name FROM "tabUser" WHERE enabled = 1', as_dict=True)]
print("Enabled Users:", users[:10])
