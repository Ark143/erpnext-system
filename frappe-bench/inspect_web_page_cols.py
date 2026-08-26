import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

cols = frappe.db.sql("SELECT column_name FROM information_schema.columns WHERE table_name='tabWeb Page' ORDER BY ordinal_position", as_dict=True)
print("Web Page columns:")
print([c['column_name'] for c in cols])
