import re
p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
s = open(p, encoding="utf-8").read()

# After the customer normalization block, before building the doc, resolve the
# customer from the linked Customer Vehicle when present (fixes
# "Customer X does not match the owner of Customer Vehicle Y" ValidationError).
anchor = "\tdata[\"customer\"] = cust\n"
addition = (
"\t# If a Customer Vehicle is provided, always use its real owning customer so the\n"
"\t# Vehicle POS Invoice validation (customer must own the vehicle) never fails.\n"
"\tveh = data.get(\"vehicle\")\n"
"\tif veh and frappe.db.exists(\"Customer Vehicle\", veh):\n"
"\t\t_vc = frappe.db.get_value(\"Customer Vehicle\", veh, \"customer\")\n"
"\t\tif _vc:\n"
"\t\t\tcust = _vc\n"
"\t\t\tdata[\"customer\"] = cust\n"
)

if anchor not in s:
    raise SystemExit("ANCHOR NOT FOUND")
if "always use its real owning customer" in s:
    print("ALREADY PATCHED")
else:
    s = s.replace(anchor, anchor + addition, 1)
    open(p, "w", encoding="utf-8").write(s)
    print("PATCHED create_from_pos: customer resolved from vehicle owner")
