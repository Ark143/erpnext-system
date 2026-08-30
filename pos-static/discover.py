import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# 1) Web Pages
wps = frappe.get_all("Web Page", fields=["name","route","published"], limit=100)
print("WEB PAGES:", len(wps))
for w in wps:
    print("  ", w["name"], "| route=", w.get("route"), "| published=", w.get("published"))
# 2) Server Scripts (custom APIs)
ss = frappe.get_all("Server Script", fields=["name","script_type","method","enabled"], limit=100)
print("\nSERVER SCRIPTS:", len(ss))
for s in ss:
    print("  ", s["name"], "|", s.get("script_type"), "|", s.get("method"), "| enabled=", s.get("enabled"))
# 3) Dashboard Charts (were the trend ones)
dc = frappe.get_all("Dashboard Chart", fields=["name","report"], limit=200)
print("\nDASHBOARD CHARTS:", len(dc))
