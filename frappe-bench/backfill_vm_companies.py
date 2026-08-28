import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
frappe.init('site1.local')
frappe.connect()

frappe.db.sql("""
    UPDATE "tabVehicle Job Order" jo
    SET company = COALESCE(e.company, 'ULTRA MRF')
    FROM "tabVehicle Estimate" e
    WHERE jo.estimate = e.name AND (jo.company IS NULL OR jo.company = '');
""")

frappe.db.sql("""
    UPDATE "tabVehicle Job Order"
    SET company = 'ULTRA MRF'
    WHERE company IS NULL OR company = '';
""")

frappe.db.sql("""
    UPDATE "tabVehicle Inspection" insp
    SET company = COALESCE(jo.company, 'ULTRA MRF')
    FROM "tabVehicle Job Order" jo
    WHERE insp.job_order = jo.name AND (insp.company IS NULL OR insp.company = '');
""")

frappe.db.sql("""
    UPDATE "tabVehicle Inspection"
    SET company = 'ULTRA MRF'
    WHERE company IS NULL OR company = '';
""")

frappe.db.commit()
print("Backfilled company on all Vehicle Job Orders and Inspections successfully!")
