import frappe, json, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()

results=[]
def step(mod, name, fn):
    try:
        msg = fn()
        results.append((mod, name, "OK", msg))
        print(f"[{mod}] {name}: OK - {msg}", flush=True)
    except Exception as e:
        results.append((mod, name, "FAIL", f"{type(e).__name__}: {str(e)[:120]}"))
        print(f"[{mod}] {name}: FAIL - {type(e).__name__}: {str(e)[:160]}", flush=True)

# helpers
def first(doctype, **f):
    r = frappe.get_all(doctype, filters=f, limit=1, pluck="name")
    return r[0] if r else None
def cust(): return first("Customer")
def supp(): return first("Supplier")
def item(): return first("Item", is_sales_item=1, disabled=0) or first("Item", disabled=0)
def wh(company="ULTRA MRF"): return first("Warehouse", company=company) or first("Warehouse")
def co(): return "ULTRA MRF"

# ---- SALES ----
def t_so():
    so=frappe.get_doc({"doctype":"Sales Order","customer":cust(),"company":co(),"delivery_date":"2026-12-31",
        "items":[{"item_code":item(),"qty":1,"rate":100,"warehouse":wh()}]})
    so.insert(ignore_permissions=True); n=so.name; so.submit(); frappe.delete_doc("Sales Order",n,ignore_permissions=True,force=True)
    return n
step("Sales","Sales Order",t_so)

def t_si():
    si=frappe.get_doc({"doctype":"Sales Invoice","customer":cust(),"company":co(),"posting_date":"2026-08-30",
        "items":[{"item_code":item(),"qty":1,"rate":100,"warehouse":wh(),"income_account":first("Account",company=co())}]})
    si.insert(ignore_permissions=True); n=si.name; si.submit(); frappe.delete_doc("Sales Invoice",n,ignore_permissions=True,force=True)
    return n
step("Sales","Sales Invoice",t_si)

def t_qt():
    q=frappe.get_doc({"doctype":"Quotation","quotation_to":"Customer","party_name":cust(),"company":co(),
        "items":[{"item_code":item(),"qty":1,"rate":100}]})
    q.insert(ignore_permissions=True); n=q.name; q.submit(); frappe.delete_doc("Quotation",n,ignore_permissions=True,force=True)
    return n
step("Sales","Quotation",t_qt)

def t_dn():
    dn=frappe.get_doc({"doctype":"Delivery Note","customer":cust(),"company":co(),"posting_date":"2026-08-30",
        "items":[{"item_code":item(),"qty":1,"warehouse":wh()}]})
    dn.insert(ignore_permissions=True); n=dn.name; dn.submit(); frappe.delete_doc("Delivery Note",n,ignore_permissions=True,force=True)
    return n
step("Sales","Delivery Note",t_dn)

# ---- PURCHASE ----
def t_po():
    po=frappe.get_doc({"doctype":"Purchase Order","supplier":supp(),"company":co(),"schedule_date":"2026-12-31",
        "items":[{"item_code":item(),"qty":1,"rate":80,"warehouse":wh()}]})
    po.insert(ignore_permissions=True); n=po.name; po.submit(); frappe.delete_doc("Purchase Order",n,ignore_permissions=True,force=True)
    return n
step("Purchase","Purchase Order",t_po)

def t_pi():
    pi=frappe.get_doc({"doctype":"Purchase Invoice","supplier":supp(),"company":co(),"posting_date":"2026-08-30",
        "items":[{"item_code":item(),"qty":1,"rate":80,"warehouse":wh(),"expense_account":first("Account",company=co())}]})
    pi.insert(ignore_permissions=True); n=pi.name; pi.submit(); frappe.delete_doc("Purchase Invoice",n,ignore_permissions=True,force=True)
    return n
step("Purchase","Purchase Invoice",t_pi)

def t_pr():
    pr=frappe.get_doc({"doctype":"Purchase Receipt","supplier":supp(),"company":co(),"posting_date":"2026-08-30",
        "items":[{"item_code":item(),"qty":1,"warehouse":wh()}]})
    pr.insert(ignore_permissions=True); n=pr.name; pr.submit(); frappe.delete_doc("Purchase Receipt",n,ignore_permissions=True,force=True)
    return n
step("Purchase","Purchase Receipt",t_pr)

# ---- STOCK ----
def t_se():
    se=frappe.get_doc({"doctype":"Stock Entry","stock_entry_type":"Material Receipt","company":co(),
        "items":[{"item_code":item(),"qty":1,"s_warehouse":None,"t_warehouse":wh(),"basic_rate":50}]})
    se.insert(ignore_permissions=True); n=se.name; se.submit(); frappe.delete_doc("Stock Entry",n,ignore_permissions=True,force=True)
    return n
step("Stock","Stock Entry",t_se)

def t_mr():
    mr=frappe.get_doc({"doctype":"Material Request","material_request_type":"Purchase","company":co(),
        "items":[{"item_code":item(),"qty":1,"schedule_date":"2026-12-31"}]})
    mr.insert(ignore_permissions=True); n=mr.name; mr.submit(); frappe.delete_doc("Material Request",n,ignore_permissions=True,force=True)
    return n
step("Stock","Material Request",t_mr)

# ---- ACCOUNTS ----
def t_pe():
    pe=frappe.get_doc({"doctype":"Payment Entry","payment_type":"Pay","party_type":"Customer","party":cust(),"company":co(),
        "paid_amount":100,"received_amount":100,"paid_from":first("Account",company=co()),"paid_to":first("Account",company=co()),
        "posting_date":"2026-08-30"})
    pe.insert(ignore_permissions=True); n=pe.name; pe.submit(); frappe.delete_doc("Payment Entry",n,ignore_permissions=True,force=True)
    return n
step("Accounts","Payment Entry",t_pe)

def t_je():
    a=first("Account",company=co())
    je=frappe.get_doc({"doctype":"Journal Entry","company":co(),"posting_date":"2026-08-30","voucher_type":"Journal Entry",
        "accounts":[{"account":a,"debit_in_account_currency":100},{"account":a,"credit_in_account_currency":100}]})
    je.insert(ignore_permissions=True); n=je.name; je.submit(); frappe.delete_doc("Journal Entry",n,ignore_permissions=True,force=True)
    return n
step("Accounts","Journal Entry",t_je)

# ---- CRM ----
def t_lead():
    l=frappe.get_doc({"doctype":"Lead","lead_name":"TEST LEAD AUTO","company_name":"TEST CO"})
    l.insert(ignore_permissions=True); n=l.name; frappe.delete_doc("Lead",n,ignore_permissions=True,force=True)
    return n
step("CRM","Lead",t_lead)

def t_opp():
    o=frappe.get_doc({"doctype":"Opportunity","opportunity_from":"Lead","party_name":first("Lead") or "TEST","company":co()})
    o.insert(ignore_permissions=True); n=o.name; o.submit(); frappe.delete_doc("Opportunity",n,ignore_permissions=True,force=True)
    return n
step("CRM","Opportunity",t_opp)

# ---- HR ----
def t_emp():
    e=frappe.get_doc({"doctype":"Employee","first_name":"AUTOTEST","company":co(),"date_of_joining":"2026-01-01"})
    e.insert(ignore_permissions=True); n=e.name; frappe.delete_doc("Employee",n,ignore_permissions=True,force=True)
    return n
step("HR","Employee",t_emp)

def t_at():
    a=frappe.get_doc({"doctype":"Attendance","employee":first("Employee",company=co()) or "HR-EMP-00001","attendance_date":"2026-08-30","status":"Present"})
    a.insert(ignore_permissions=True); n=a.name; frappe.delete_doc("Attendance",n,ignore_permissions=True,force=True)
    return n
step("HR","Attendance",t_at)

# ---- PROJECTS ----
def t_proj():
    p=frappe.get_doc({"doctype":"Project","project_name":"AUTOTEST PROJ","company":co()})
    p.insert(ignore_permissions=True); n=p.name; frappe.delete_doc("Project",n,ignore_permissions=True,force=True)
    return n
step("Projects","Project",t_proj)

# ---- MANUFACTURING ----
def t_wo():
    bom=first("BOM")
    if not bom: return "skipped (no BOM)"
    wo=frappe.get_doc({"doctype":"Work Order","production_item":item(),"bom_no":bom,"qty":1,"company":co(),"planned_start_date":"2026-08-30"})
    wo.insert(ignore_permissions=True); n=wo.name; frappe.delete_doc("Work Order",n,ignore_permissions=True,force=True)
    return n
step("Manufacturing","Work Order",t_wo)

print("\n=== SUMMARY ===")
for mod,name,st,msg in results:
    print(f"{mod:14} {name:18} {st}  {msg}")
fails=[r for r in results if r[2]=="FAIL"]
print(f"\nTOTAL: {len(results)} tested, {len(fails)} FAILED")
if fails:
    print("FAILURES:")
    for r in fails: print("  ", r)
