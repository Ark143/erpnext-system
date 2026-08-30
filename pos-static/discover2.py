import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Server Scripts without 'method' field
try:
    ss = frappe.get_all("Server Script", fields=["name","script_type","enabled","doc_type"], limit=200)
    print("SERVER SCRIPTS:", len(ss))
    for s in ss:
        print("  ", s["name"], "|", s.get("script_type"), "| doc=", s.get("doc_type"), "| enabled=", s.get("enabled"))
except Exception as e:
    print("SS ERR:", e)
# Check if 'method' field exists on Server Script doctype
print("\nServer Script meta fields containing 'method':",
      [f.fieldname for f in frappe.get_meta("Server Script").fields if "method" in f.fieldname.lower()])
# Also list custom API / whitelisted via Server Script method-like
print("\nServer Script with api_method field?:", [f.fieldname for f in frappe.get_meta("Server Script").fields if "api" in f.fieldname.lower()])
