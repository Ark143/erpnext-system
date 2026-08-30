F = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
t = open(F).read()
anchor = '\tif isinstance(data, str):\n\t\tdata = _json.loads(data)\n'
add = anchor + '\n\t# normalize customer (collapse extra spaces, fuzzy-match if needed)\n\tcust = data.get("customer")\n\tif cust:\n\t\tcust = " ".join(str(cust).split())\n\t\tif not frappe.db.exists("Customer", cust):\n\t\t\tlike = "%" + cust.replace(" ", "%") + "%"\n\t\t\tm = frappe.get_all("Customer", filters={"name": ["like", like]}, limit=1)\n\t\t\tif m:\n\t\t\t\tcust = m[0].name\n\t\tdata["customer"] = cust\n'
if anchor in t and "normalize customer" not in t:
    t = t.replace(anchor, add, 1)
    open(F, "w").write(t)
    print("patched:", "normalize customer" in t)
else:
    print("anchor not found or already patched; anchor_in=", anchor in t)
