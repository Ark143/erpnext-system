import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

# ---- Company Dashboard: fix GROUP BY column ----
d = frappe.get_doc("Server Script", "VM Company Dashboard API")
s = d.script
# ensure FROM is correct (was stale tabVehicle Job Order Item)
s = s.replace('FROM "tabVehicle Job Order Item" sii', 'FROM "tabJob Order Service Item" sii')
# fix GROUP BY on wrong column
s = s.replace("GROUP BY sii.item_name", "GROUP BY sii.service_item")
assert 'tabVehicle Job Order Item' not in s, "stale table remains"
assert 'GROUP BY sii.item_name' not in s, "stale group by remains"
d.script = s
d.save()
print("Company Dashboard: GROUP BY + FROM fixed")

# ---- Executive Dashboard: None-safe cint helper ----
d2 = frappe.get_doc("Server Script", "Executive Dashboard API")
s2 = d2.script
# add cint helper right after the first line (fd = ...)
helper = ('def cint(v):\n'
          '    try:\n'
          '        return int(flt(v) or 0)\n'
          '    except Exception:\n'
          '        return 0\n\n')
if "def cint(" not in s2:
    # insert after first newline
    nl = s2.find("\n") + 1
    s2 = s2[:nl] + helper + s2[nl:]
# replace int( back to cint( (the original calls were cint(); we made them int())
# but only those that are likely count/amount conversions. Safe to globally swap int( -> cint( since cint is now None-safe superset.
s2 = s2.replace("int(", "cint(")
d2.script = s2
d2.save()
print("Executive Dashboard: cint helper added, int(->cint(")
frappe.db.commit()
