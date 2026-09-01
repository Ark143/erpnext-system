import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
name = "VMSPOS-2026-00004"
print("Vehicle POS Invoice exists:", frappe.db.exists("Vehicle POS Invoice", name))
doc = frappe.get_doc("Vehicle POS Invoice", name)
print("VMS fields: customer=", doc.customer, "company=", doc.company, "grand_total=", doc.grand_total, "docstatus=", doc.docstatus, "pos_invoice=", doc.pos_invoice)
print("ERPNext POS Invoice exists:", frappe.db.exists("POS Invoice", doc.pos_invoice))
pi = frappe.get_doc("POS Invoice", doc.pos_invoice)
print("POS Invoice: status=", pi.status, "grand_total=", pi.grand_total, "docstatus=", pi.docstatus, "is_pos=", pi.is_pos)
# cancel it cleanly to leave env tidy
try:
    frappe.delete_doc("Vehicle POS Invoice", name, force=True)
except Exception:
    d = frappe.get_doc("Vehicle POS Invoice", name); d.cancel()
frappe.db.commit()
print("after cleanup exists VMS:", frappe.db.exists("Vehicle POS Invoice", name))
