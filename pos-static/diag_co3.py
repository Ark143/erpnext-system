import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
frappe.session.user = "Administrator"
frappe.form_dict = frappe._dict({"company":"ULTRA MRF","period":"this_year"})
# monkeypatch db.sql to print failing query
real = frappe.db.sql
def pat(q, *a, **k):
    try:
        return real(q, *a, **k)
    except Exception as e:
        print("FIRST SQL FAIL:", str(e)[:200])
        print("QUERY:", q[:300])
        raise
frappe.db.sql = pat
try:
    doc = frappe.get_doc("Server Script", "VM Company Dashboard API")
    from frappe.utils.safe_exec import safe_exec
    safe_exec(doc.script)
    print("OK message present:", "message" in (frappe.response or {}))
except Exception as e:
    print("RAISED:", type(e).__name__, str(e)[:200])
