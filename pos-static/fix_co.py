import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
d = frappe.get_doc("Server Script", "VM Company Dashboard API")
s = d.script
s = s.replace(
'''    FROM "tabVehicle Job Order Item" sii
    JOIN "tabVehicle Job Order" vjo ON vjo.name = sii.parent''',
'''    FROM "tabJob Order Service Item" sii
    JOIN "tabVehicle Job Order" vjo ON vjo.name = sii.parent''')
s = s.replace(
'''    SELECT sii.item_name AS name,
           COUNT(sii.name) AS count,
           COALESCE(SUM(sii.amount), 0) AS revenue''',
'''    SELECT sii.service_item AS name,
           COUNT(sii.name) AS count,
           COALESCE(SUM(sii.total_amount), 0) AS revenue''')
assert 'tabVehicle Job Order Item' not in s, "leftover bad table"
d.script = s
d.save()
frappe.db.commit()
print("VM Company Dashboard API: fixed table + columns")
