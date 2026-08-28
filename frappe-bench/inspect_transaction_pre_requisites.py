import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
frappe.init('site1.local')
frappe.connect()

print("=== Items Sample ===")
items = frappe.db.sql("""
    SELECT name, item_name, item_group, stock_uom, is_sales_item, is_purchase_item, is_stock_item, valuation_rate
    FROM "tabItem"
    WHERE disabled = 0
    LIMIT 10
""", as_dict=True)
for it in items:
    print(it)

print("\n=== Income & Expense Accounts by Company ===")
companies = [c['name'] for c in frappe.get_all('Company', filters={'name': ['!=', 'My Company']})]
for comp in companies:
    inc = frappe.db.get_value('Company', comp, 'default_income_account')
    exp = frappe.db.get_value('Company', comp, 'default_expense_account')
    wh = frappe.db.sql('SELECT name FROM "tabWarehouse" WHERE company = %s AND is_group = 0 LIMIT 1', (comp,), as_dict=True)
    wh_name = wh[0]['name'] if wh else None
    print(f"  {comp:30s} -> Income: {str(inc):25s} | Expense: {str(exp):25s} | Warehouse: {str(wh_name)}")
