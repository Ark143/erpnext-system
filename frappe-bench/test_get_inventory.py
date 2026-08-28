import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe, traceback
frappe.init('site1.local')
frappe.connect()

from vehicle_management.vehicle_management.executive_dashboard import executive_dashboard

try:
    res = executive_dashboard(view='inventory', company='Automan Car Care Center')
    print("Success! Keys:", list(res.keys()))
    print("KPIs:", res['kpis'])
    print("Stock count:", len(res['stock_table']))
    print("Bin locs count:", len(res['bin_locations']))
except Exception as e:
    print("Exception in get_inventory:")
    traceback.print_exc()
