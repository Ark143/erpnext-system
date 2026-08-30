import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
for name in ["VM POS Items","VM POS Meta","VM POS History","VM POS Stock","VM POS Cashier","VM POS Vehicles","VM POS Vehicle Customer"]:
    d = frappe.get_doc("Server Script", name)
    print(f"\n===== {name} (api={d.api_method}) =====")
    # print first 25 lines to see param reading
    print("\n".join(d.script.splitlines()[:25]))
