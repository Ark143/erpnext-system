import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
name = "VMSPOS-2026-00004"
print("Vehicle POS Invoice exists:", frappe.db.exists("Vehicle POS Invoice", name))
doc = frappe.get_doc("Vehicle POS Invoice", name)
print("VMS: customer=", doc.customer, "company=", doc.company, "docstatus=", doc.docstatus, "pos_invoice=", doc.pos_invoice)
print("ERPNext POS Invoice exists:", frappe.db.exists("POS Invoice", doc.pos_invoice))
# clean up cleanly (cancel both)
try:
    frappe.get_doc("Vehicle POS Invoice", name).cancel()
except Exception as e:
    print("cancel VMS err (ok if already):", repr(e)[:120])
frappe.db.commit()
print("after cleanup VMS exists:", frappe.db.exists("Vehicle POS Invoice", name))
