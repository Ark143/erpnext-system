import frappe, traceback, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
try:
    print("Website Theme Standard exists:", frappe.db.exists("Website Theme", "Standard"))
    if frappe.db.exists("Website Theme", "Standard"):
        doc = frappe.get_doc("Website Theme", "Standard")
        d = doc.as_dict()
        none_keys = [k for k,v in d.items() if v is None]
        print("none_keys:", none_keys[:20])
        print("custom_scss type:", type(getattr(doc,"custom_scss",None)))
        print("css_variables:", str(getattr(doc,"css_variables",None))[:120])
        # regenerate
        doc.save()
        print("Standard theme regenerated OK")
    print("WS exists:", frappe.db.exists("Website Settings"))
except Exception:
    traceback.print_exc()
