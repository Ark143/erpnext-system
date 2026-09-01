import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
user = frappe.session.user
print("session user:", user)
opens = frappe.get_all("POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, ["name","pos_profile","company"])
print("open entries for user:", opens)
for e in opens:
    try:
        d = frappe.get_doc("POS Opening Entry", e["name"])
        d.cancel()
        print("cancelled:", e["name"])
    except Exception as ex:
        print("CANCEL FAILED for", e["name"], "->", repr(ex)[:300])
        traceback.print_exc()
frappe.db.commit()
print("remaining open:", frappe.get_all("POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"))
