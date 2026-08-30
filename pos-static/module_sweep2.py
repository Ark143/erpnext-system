import frappe, traceback, importlib
SITE="site1.local"; SP="/workspace/frappe-bench/sites"

def fresh():
    # tear down any prior connection then reconnect in a fresh process-like way
    try: frappe.db.close()
    except: pass
    frappe.init(site=SITE, sites_path=SP)
    frappe.connect()

def co(): return "ULTRA MRF"
def first(doctype, **f):
    fresh()
    r = frappe.get_all(doctype, filters=f, limit=1, pluck="name")
    return r[0] if r else None

def run(mod, name, build):
    try:
        fresh()
        doc = build()
        doc.insert(ignore_permissions=True)
        n = doc.name
        try: doc.submit()
        except Exception: pass
        frappe.delete_doc(doc.doctype, n, ignore_permissions=True, force=True)
        frappe.db.commit()
        print(f"[{mod}] {name}: OK ({n})", flush=True)
        return True, n
    except Exception as e:
        print(f"[{mod}] {name}: FAIL {type(e).__name__}: {str(e)[:150]}", flush=True)
        try: frappe.db.rollback()
        except: pass
        return False, str(e)[:150]

item = lambda: first("Item", is_sales_item=1, disabled=0) or first("Item", disabled=0)
cust = lambda: first("Customer")
supp = lambda: first("Supplier")
wh   = lambda: first("Warehouse", company=co()) or first("Warehouse")
acc  = lambda: first("Account", company=co())

tests = []
tests.append(("Sales","Sales Order", lambda: frappe.get_doc({"doctype":"Sales Order","customer":cust(),"company":co(),"delivery_date":"2026-12-31","items":[{"item_code":item(),"qty":1,"rate":100,"warehouse":wh()}]})))
tests.append(("Sales","Sales Invoice", lambda: frappe.get_doc({"doctype":"Sales Invoice","customer":cust(),"company":co(),"posting_date":"2026-08-30","items":[{"item_code":item(),"qty":1,"rate":100,"warehouse":wh(),"income_account":acc()}]})))
tests.append(("Sales","Quotation", lambda: frappe.get_doc({"doctype":"Quotation","quotation_to":"Customer","party_name":cust(),"company":co(),"items":[{"item_code":item(),"qty":1,"rate":100}]})))
tests.append(("Sales","Delivery Note", lambda: frappe.get_doc({"doctype":"Delivery Note","customer":cust(),"company":co(),"posting_date":"2026-08-30","items":[{"item_code":item(),"qty":1,"warehouse":wh()}]})))
tests.append(("Purchase","Purchase Order", lambda: frappe.get_doc({"doctype":"Purchase Order","supplier":supp(),"company":co(),"schedule_date":"2026-12-31","items":[{"item_code":item(),"qty":1,"rate":80,"warehouse":wh()}]})))
tests.append(("Purchase","Purchase Invoice", lambda: frappe.get_doc({"doctype":"Purchase Invoice","supplier":supp(),"company":co(),"posting_date":"2026-08-30","items":[{"item_code":item(),"qty":1,"rate":80,"warehouse":wh(),"expense_account":acc()}]})))
tests.append(("Purchase","Purchase Receipt", lambda: frappe.get_doc({"doctype":"Purchase Receipt","supplier":supp(),"company":co(),"posting_date":"2026-08-30","items":[{"item_code":item(),"qty":1,"warehouse":wh()}]})))
tests.append(("Stock","Stock Entry", lambda: frappe.get_doc({"doctype":"Stock Entry","stock_entry_type":"Material Receipt","company":co(),"items":[{"item_code":item(),"qty":1,"t_warehouse":wh(),"basic_rate":50}]})))
tests.append(("Stock","Material Request", lambda: frappe.get_doc({"doctype":"Material Request","material_request_type":"Purchase","company":co(),"items":[{"item_code":item(),"qty":1,"schedule_date":"2026-12-31"}]})))
tests.append(("Accounts","Payment Entry", lambda: frappe.get_doc({"doctype":"Payment Entry","payment_type":"Pay","party_type":"Customer","party":cust(),"company":co(),"paid_amount":100,"received_amount":100,"paid_from":acc(),"paid_to":acc(),"posting_date":"2026-08-30"})))
tests.append(("Accounts","Journal Entry", lambda: frappe.get_doc({"doctype":"Journal Entry","company":co(),"posting_date":"2026-08-30","voucher_type":"Journal Entry","accounts":[{"account":acc(),"debit_in_account_currency":100},{"account":acc(),"credit_in_account_currency":100}]})))
tests.append(("CRM","Lead", lambda: frappe.get_doc({"doctype":"Lead","lead_name":"AUTOTEST LEAD","company_name":"AUTOTEST CO"})))
tests.append(("CRM","Opportunity", lambda: frappe.get_doc({"doctype":"Opportunity","opportunity_from":"Lead","party_name":first("Lead") or "AUTOTEST","company":co()})))
tests.append(("HR","Employee", lambda: frappe.get_doc({"doctype":"Employee","first_name":"AUTOTEST","company":co(),"date_of_joining":"2026-01-01"})))
tests.append(("HR","Attendance", lambda: frappe.get_doc({"doctype":"Attendance","employee":first("Employee",company=co()) or "HR-EMP-00001","attendance_date":"2026-08-30","status":"Present"})))
tests.append(("Projects","Project", lambda: frappe.get_doc({"doctype":"Project","project_name":"AUTOTEST PROJ","company":co()})))
def make_wo():
    bom = first("BOM")
    d = {"doctype":"Work Order","production_item":item(),"qty":1,"company":co(),"planned_start_date":"2026-08-30"}
    if bom: d["bom_no"] = bom
    return frappe.get_doc(d)
tests.append(("Manufacturing","Work Order", make_wo))

ok=0; fail=0
for mod,name,b in tests:
    r,msg = run(mod,name,b)
    if r: ok+=1
    else: fail+=1
print(f"\n=== RESULT: {ok} OK, {fail} FAIL of {len(tests)} ===")
