import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
# delete test records created during sweep
for dt, prefix in [("Sales Order","SAL-ORD-2026-00001"),("Sales Invoice","ACC-SINV-2026-00140"),
    ("Quotation","SAL-QTN-2026-00003"),("Delivery Note","MAT-DN-2026-00001"),
    ("Purchase Order","PUR-ORD-2026-00013"),("Purchase Invoice","ACC-PINV-2026-00083"),
    ("Purchase Receipt","MAT-PRE-2026-00013"),("Stock Entry","MAT-STE-2026-00012"),
    ("Material Request","MAT-MR-2026-00002"),("Payment Entry","ACC-PAY-2026-00222"),
    ("Journal Entry","ACC-JV-2026-00001"),("Lead","CRM-LEAD-2026-00001"),
    ("Employee","HR-EMP-00191")]:
    if frappe.db.exists(dt, prefix):
        try:
            doc=frappe.get_doc(dt, prefix)
            if doc.docstatus==1: doc.cancel()
            frappe.delete_doc(dt, prefix, ignore_permissions=True, force=True)
            print("deleted", dt, prefix)
        except Exception as e:
            print("skip", dt, prefix, str(e)[:60])
frappe.db.commit()
print("cleanup done")
# confirm logo
ws=frappe.get_single("Website Settings")
print("app_logo:", ws.app_logo, "| favicon:", ws.favicon)
