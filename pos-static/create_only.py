import frappe, sys, io, traceback
SITE="site1.local"; SP="/workspace/frappe-bench/sites"
frappe.init(site=SITE, sites_path=SP); frappe.connect()
co="ULTRA MRF"
def first(d, **f):
    r=frappe.get_all(d, filters=f, limit=1, pluck="name"); return r[0] if r else None
item = first("Item", is_sales_item=1, disabled=0) or first("Item", disabled=0)
cust = first("Customer"); supp = first("Supplier")
wh   = first("Warehouse", company=co) or first("Warehouse")
inc = first("Account", company=co, is_group=0, root_type="Income")
exp = first("Account", company=co, is_group=0, root_type="Expense")
specs = {
 "Sales Order": {"doctype":"Sales Order","customer":cust,"company":co,"delivery_date":"2026-12-31","items":[{"item_code":item,"qty":1,"rate":100,"warehouse":wh}]},
 "Sales Invoice": {"doctype":"Sales Invoice","customer":cust,"company":co,"posting_date":"2026-08-30","items":[{"item_code":item,"qty":1,"rate":100,"warehouse":wh,"income_account":inc}]},
 "Quotation": {"doctype":"Quotation","quotation_to":"Customer","party_name":cust,"company":co,"items":[{"item_code":item,"qty":1,"rate":100}]},
 "Delivery Note": {"doctype":"Delivery Note","customer":cust,"company":co,"posting_date":"2026-08-30","items":[{"item_code":item,"qty":1,"warehouse":wh}]},
 "Purchase Order": {"doctype":"Purchase Order","supplier":supp,"company":co,"schedule_date":"2026-12-31","items":[{"item_code":item,"qty":1,"rate":80,"warehouse":wh}]},
 "Purchase Invoice": {"doctype":"Purchase Invoice","supplier":supp,"company":co,"posting_date":"2026-08-30","items":[{"item_code":item,"qty":1,"rate":80,"warehouse":wh,"expense_account":exp}]},
 "Purchase Receipt": {"doctype":"Purchase Receipt","supplier":supp,"company":co,"posting_date":"2026-08-30","items":[{"item_code":item,"qty":1,"warehouse":wh}]},
 "Stock Entry": {"doctype":"Stock Entry","stock_entry_type":"Material Receipt","company":co,"items":[{"item_code":item,"qty":1,"t_warehouse":wh,"basic_rate":50}]},
 "Material Request": {"doctype":"Material Request","material_request_type":"Purchase","company":co,"items":[{"item_code":item,"qty":1,"schedule_date":"2026-12-31","warehouse":wh}]},
 "Payment Entry": {"doctype":"Payment Entry","payment_type":"Pay","party_type":"Customer","party":cust,"company":co,"paid_amount":100,"received_amount":100,"paid_from":inc,"paid_to":exp,"posting_date":"2026-08-30"},
 "Journal Entry": {"doctype":"Journal Entry","company":co,"posting_date":"2026-08-30","voucher_type":"Journal Entry","accounts":[{"account":inc,"debit_in_account_currency":100},{"account":exp,"credit_in_account_currency":100}]},
 "Lead": {"doctype":"Lead","lead_name":"AUTOTEST LEAD","company_name":"AUTOTEST CO"},
 "Employee": {"doctype":"Employee","first_name":"AUTOTEST","company":co,"date_of_joining":"2026-01-01","gender":"Male","date_of_birth":"1990-01-01"},
}
name=sys.argv[1]
buf=io.StringIO()
try:
    d=frappe.get_doc(specs[name]); d.insert(ignore_permissions=True)
    frappe.db.commit()
    print("CREATE OK:", d.name)
except Exception:
    traceback.print_exc(file=buf)
    print("CREATE FAIL:", buf.getvalue().splitlines()[-1][:160])
    try: frappe.db.rollback()
    except: pass
