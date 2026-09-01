import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
user = frappe.session.user
opens = frappe.get_all("POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, ["name"])
print("open entries:", opens)
for e in opens:
    try:
        from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
        doc = frappe.get_doc("POS Opening Entry", e["name"])
        closing = make_closing_entry_from_opening(doc)
        closing.insert()
        closing.submit()
        print("closing submitted:", closing.name, "docstatus:", closing.docstatus)
    except Exception as ex:
        print("CLOSE FAILED for", e["name"], "->", repr(ex)[:400])
        traceback.print_exc()
frappe.db.commit()
print("remaining open:", frappe.get_all("POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"))
