import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
frappe.session.user = "Administrator"
frappe.form_dict = frappe._dict({"company":"ULTRA MRF","period":"this_year"})
try:
    doc = frappe.get_doc("Server Script", "VM Company Dashboard API")
    doc.script = doc.script  # ensure loaded
    # execute via safe_exec like the API does
    from frappe.utils.safe_exec import safe_exec
    safe_exec(doc.script, get_context=frappe._dict)
    print("OK message:", type(frappe.response.get("message")))
except Exception as e:
    tb = traceback.format_exc()
    # find the UndefinedTable line
    for line in tb.splitlines():
        if "UndefinedTable" in line or "tab" in line.lower() and "does not exist" in line:
            print("SQL ERR:", line)
    print(tb[-1200:])
