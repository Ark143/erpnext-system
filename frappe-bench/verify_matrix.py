import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe

frappe.init(site='erp.localhost')
frappe.connect()

companies = frappe.get_list("Company", filters={"name": ["!=", "My Company"]}, pluck="name")

print("=" * 95)
print(f"{'Company':32s} | {'SO':4s} | {'DN':4s} | {'SI':4s} | {'PO':4s} | {'PR':4s} | {'PI':4s} | {'STE':4s} | {'PayRecv':7s} | {'PayPay':6s}")
print("=" * 95)

for co in companies:
    so_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabSales Order" WHERE company=%s AND docstatus=1', (co,))[0][0]
    dn_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabDelivery Note" WHERE company=%s AND docstatus=1', (co,))[0][0]
    si_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabSales Invoice" WHERE company=%s AND docstatus=1', (co,))[0][0]
    po_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabPurchase Order" WHERE company=%s AND docstatus=1', (co,))[0][0]
    pr_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabPurchase Receipt" WHERE company=%s AND docstatus=1', (co,))[0][0]
    pi_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabPurchase Invoice" WHERE company=%s AND docstatus=1', (co,))[0][0]
    ste_cnt = frappe.db.sql('SELECT COUNT(*) FROM "tabStock Entry" WHERE company=%s AND docstatus=1', (co,))[0][0]
    pe_recv = frappe.db.sql('SELECT COUNT(*) FROM "tabPayment Entry" WHERE company=%s AND payment_type=%s AND docstatus=1', (co, 'Receive'))[0][0]
    pe_pay = frappe.db.sql('SELECT COUNT(*) FROM "tabPayment Entry" WHERE company=%s AND payment_type=%s AND docstatus=1', (co, 'Pay'))[0][0]
    
    print(f"{co:32s} | {so_cnt:4d} | {dn_cnt:4d} | {si_cnt:4d} | {po_cnt:4d} | {pr_cnt:4d} | {pi_cnt:4d} | {ste_cnt:4d} | {pe_recv:7d} | {pe_pay:6d}")

print("=" * 95)
