import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
d = frappe.get_doc("Server Script", "VM Company Dashboard API")
s = d.script
# Build a vjo-qualified company filter for the JOIN query
old = '''    FROM "tabVehicle Job Order" vjo
    LEFT JOIN "tabCustomer Vehicle" cv ON cv.name = vjo.vehicle
    WHERE vjo.docstatus = 1
      AND vjo.job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY cv.make'''
# replace the {co_filter} inside vehicle_mix with a vjo-qualified one
new = '''    FROM "tabVehicle Job Order" vjo
    LEFT JOIN "tabCustomer Vehicle" cv ON cv.name = vjo.vehicle
    WHERE vjo.docstatus = 1
      AND vjo.job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter_vjo}
    GROUP BY cv.make'''
assert old in s, "vehicle_mix WHERE not found"
s = s.replace(old, new)
# define co_filter_vjo near co_filter definition
s = s.replace(
    'if company:\n    co_filter = " AND company = %(company)s"\n    co_params["company"] = company',
    'if company:\n    co_filter = " AND company = %(company)s"\n    co_filter_vjo = " AND vjo.company = %(company)s"\n    co_params["company"] = company\nelse:\n    co_filter_vjo = ""'
)
d.script = s
d.save()
frappe.db.commit()
print("Company Dashboard: vehicle_mix company qualified")
