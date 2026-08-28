import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe, traceback
from frappe.utils import nowdate

frappe.init('site1.local')
frappe.connect()

comp = 'Automan Car Care Center'
cust = frappe.get_all('Customer', limit=1)[0]['name']
item = frappe.get_all('Item', filters={'is_sales_item': 1, 'disabled': 0}, limit=1)[0]['name']

abbr = frappe.db.get_value('Company', comp, 'abbr')
income_acc = frappe.db.get_value('Company', comp, 'default_income_account') or f"Sales - {abbr}"
recv_acc = frappe.db.get_value('Company', comp, 'default_receivable_account') or f"Debtors - {abbr}"
cash_acc = frappe.db.get_value('Company', comp, 'default_cash_account') or f"Cash - {abbr}"
cost_center = frappe.db.get_value('Company', comp, 'cost_center') or f"Main - {abbr}"

print(f"Testing Sales Invoice for: {comp}, Cust: {cust}, Item: {item}")
print(f"Accounts: Income={income_acc}, Recv={recv_acc}, Cash={cash_acc}, CC={cost_center}")

try:
    si = frappe.get_doc({
        "doctype": "Sales Invoice",
        "company": comp,
        "customer": cust,
        "posting_date": nowdate(),
        "due_date": nowdate(),
        "currency": "PHP",
        "debit_to": recv_acc,
        "cost_center": cost_center,
        "update_stock": 0,
        "items": [
            {
                "item_code": item,
                "qty": 2,
                "rate": 1500.0,
                "income_account": income_acc,
                "cost_center": cost_center
            }
        ]
    })
    si.insert(ignore_permissions=True)
    print("Sales Invoice inserted:", si.name)
    si.submit()
    print("Sales Invoice submitted:", si.name, "Total:", si.grand_total)
    
    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "party_type": "Customer",
        "party": cust,
        "company": comp,
        "posting_date": nowdate(),
        "paid_from": recv_acc,
        "paid_to": cash_acc,
        "paid_amount": si.grand_total,
        "received_amount": si.grand_total,
        "target_exchange_rate": 1.0,
        "references": [
            {
                "reference_doctype": "Sales Invoice",
                "reference_name": si.name,
                "total_amount": si.grand_total,
                "outstanding_amount": si.grand_total,
                "allocated_amount": si.grand_total
            }
        ]
    })
    pe.insert(ignore_permissions=True)
    print("Payment Entry inserted:", pe.name)
    pe.submit()
    print("Payment Entry submitted:", pe.name)
    frappe.db.commit()
    print("SUCCESSFUL TEST TRANSACTION!")
except Exception as e:
    print("ERROR in test:")
    traceback.print_exc()
    frappe.db.rollback()
