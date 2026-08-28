import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

pages = frappe.db.sql('SELECT name, route, title FROM "tabWeb Page" WHERE route LIKE %s ORDER BY route', ('executive%',), as_dict=True)
print(f"Total Live Executive Web Pages: {len(pages)}")
for p in pages:
    print(f"  - http://erp.localhost/{p['route']:36s} | {p['title']}")
