import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
frappe.init('site1.local')
frappe.connect()

frappe.reload_doc('vehicle_management', 'doctype', 'job_order_part_item', force=True)
frappe.db.sql('ALTER TABLE "tabJob Order Part Item" ADD COLUMN IF NOT EXISTS uom varchar(140) DEFAULT \'PC\';')
frappe.db.sql('UPDATE "tabJob Order Part Item" SET uom = \'PC\' WHERE uom IS NULL OR uom = \'\';')
frappe.db.commit()
print("Reloaded job_order_part_item and ensured uom column successfully!")
