import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

# ===== FIX 1: Company Dashboard - vehicle_mix needs JOIN to Customer Vehicle for make =====
d = frappe.get_doc("Server Script", "VM Company Dashboard API")
s = d.script
old = '''# ---- Vehicle mix (make distribution) ----
vehicle_mix = q(f\"\"\"
    SELECT COALESCE(make, 'Unknown') AS make, COUNT(name) AS count
    FROM \"tabVehicle Job Order\"
    WHERE docstatus = 1
      AND job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY make
    ORDER BY count DESC
    LIMIT 8
\"\"\")'''
new = '''# ---- Vehicle mix (make distribution) ----
vehicle_mix = q(f\"\"\"
    SELECT COALESCE(cv.make, 'Unknown') AS make, COUNT(vjo.name) AS count
    FROM \"tabVehicle Job Order\" vjo
    LEFT JOIN \"tabCustomer Vehicle\" cv ON cv.name = vjo.vehicle
    WHERE vjo.docstatus = 1
      AND vjo.job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY cv.make
    ORDER BY count DESC
    LIMIT 8
\"\"\")'''
assert old in s, "vehicle_mix block not found"
s = s.replace(old, new)
d.script = s
d.save()
print("Company Dashboard: vehicle_mix JOIN fixed")

# ===== FIX 2: Executive Dashboard - repair the mangled cint helper =====
d2 = frappe.get_doc("Server Script", "Executive Dashboard API")
s2 = d2.script
# The earlier global int(->cint( replace mangled the helper into 'def ccint' calling 'cint'.
# Replace the broken helper block with a correct one.
bad = '''def ccint(v):
    try:
        return cint(flt(v) or 0)
    except Exception:
        return 0'''
good = '''def cint(v):
    try:
        return int(flt(v) or 0)
    except Exception:
        return 0'''
assert bad in s2, "bad helper not found: " + repr(s2[:200])
s2 = s2.replace(bad, good)
d2.script = s2
d2.save()
print("Executive Dashboard: cint helper repaired")
frappe.db.commit()
