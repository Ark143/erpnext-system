import sys, os, random
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe, traceback
from frappe.utils import nowdate, flt, add_days

frappe.init('site1.local')
frappe.connect()

comp = 'Ultra MRF Dau Main'
abbr = frappe.db.get_value('Company', comp, 'abbr')
income_acc = frappe.db.get_value('Company', comp, 'default_income_account') or f"Sales - {abbr}"
recv_acc = frappe.db.get_value('Company', comp, 'default_receivable_account') or f"Debtors - {abbr}"
cash_acc = frappe.db.get_value('Company', comp, 'default_cash_account') or f"Cash - {abbr}"
cost_center = frappe.db.get_value('Company', comp, 'cost_center') or f"Main - {abbr}"

customers = frappe.get_all('Customer', limit=20)
sales_items = frappe.get_all('Item', filters={'disabled': 0, 'is_sales_item': 1}, limit=20)

print(f"Testing 10 SI + PE for {comp}...")
success_si = 0
success_pe = 0

for i in range(10):
    cust = random.choice(customers)['name']
    sel_items = random.sample(sales_items, k=random.randint(1, 2))
    posting_date = add_days(nowdate(), -random.randint(0, 10))
    due_date = add_days(posting_date, 15)
    
    try:
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": comp,
            "customer": cust,
            "posting_date": posting_date,
            "due_date": due_date,
            "currency": "PHP",
            "debit_to": recv_acc,
            "cost_center": cost_center,
            "update_stock": 0,
            "items": [
                {
                    "item_code": it['name'],
                    "qty": random.randint(1, 4),
                    "rate": 1250.0,
                    "income_account": income_acc,
                    "cost_center": cost_center
                }
                for it in sel_items
            ]
        })
        si.insert(ignore_permissions=True)
        si.submit()
        success_si += 1
        
        # Payment Entry
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": cust,
            "company": comp,
            "posting_date": posting_date,
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
        pe.submit()
        success_pe += 1
        frappe.db.commit()
        print(f"  [{i+1}/10] OK: SI={si.name}, PE={pe.name}")
    except Exception as e:
        print(f"  [{i+1}/10] FAILED: {type(e).__name__} - {e}")
        frappe.db.rollback()

print(f"\nFinal: {success_si}/10 SI, {success_pe}/10 PE")
