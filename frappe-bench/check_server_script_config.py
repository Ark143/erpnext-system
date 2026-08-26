import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

# Check server script doctype
print("Server Script fields:")
cols = frappe.db.sql("SELECT column_name FROM information_schema.columns WHERE table_name='tabServer Script' ORDER BY ordinal_position", as_dict=True)
print([c['column_name'] for c in cols])

# Check if server scripts are enabled in site_config
site_config = frappe.get_site_config()
print("server_script_enabled in site_config:", site_config.get("server_script_enabled"))
