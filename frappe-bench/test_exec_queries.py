import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

co = "Ultra MRF Dau Main"

print("--- Testing GL Entry Query for Revenue & Expenses ---")
rev_exp = frappe.db.sql("""
    SELECT 
        a.root_type,
        SUM(gl.credit - gl.debit) as net_credit,
        SUM(gl.debit - gl.credit) as net_debit
    FROM "tabGL Entry" gl
    JOIN "tabAccount" a ON a.name = gl.account
    WHERE gl.company = %s AND gl.is_cancelled = 0
    GROUP BY a.root_type
""", (co,), as_dict=True)
print("Root types summary:", rev_exp)

print("\n--- Testing Accounts for Cash & Bank ---")
bank_cash = frappe.db.sql("""
    SELECT 
        gl.account,
        SUM(gl.debit - gl.credit) as balance
    FROM "tabGL Entry" gl
    JOIN "tabAccount" a ON a.name = gl.account
    WHERE gl.company = %s AND gl.is_cancelled = 0 AND a.account_type IN ('Bank', 'Cash')
    GROUP BY gl.account
""", (co,), as_dict=True)
print("Bank/Cash balances:", bank_cash)

print("\n--- Testing AR & AP ---")
ar_ap = frappe.db.sql("""
    SELECT 
        a.account_type,
        SUM(CASE WHEN a.account_type='Receivable' THEN gl.debit - gl.credit ELSE gl.credit - gl.debit END) as balance
    FROM "tabGL Entry" gl
    JOIN "tabAccount" a ON a.name = gl.account
    WHERE gl.company = %s AND gl.is_cancelled = 0 AND a.account_type IN ('Receivable', 'Payable')
    GROUP BY a.account_type
""", (co,), as_dict=True)
print("AR/AP:", ar_ap)

print("\n--- Testing Sales Invoices & Orders ---")
si = frappe.db.sql("""
    SELECT 
        COUNT(name) as cnt,
        COALESCE(SUM(grand_total), 0) as total,
        COALESCE(SUM(outstanding_amount), 0) as outstanding
    FROM "tabSales Invoice"
    WHERE company = %s AND docstatus = 1
""", (co,), as_dict=True)
print("Sales Invoices:", si)
