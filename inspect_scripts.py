import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()

for name in ["Executive Dashboard API", "VM Company Dashboard API"]:
    try:
        doc = frappe.get_doc("Server Script", name)
        print("=" * 90)
        print("NAME:", name)
        print("api_method:", doc.api_method)
        print("disabled:", doc.disabled)
        print("script_len:", len(doc.script))
        print("-" * 90)
        print(doc.script)
        print("=" * 90)
    except Exception as e:
        print("ERR", name, repr(e))

tables = [
    "tabVehicle Job Order",
    "tabJob Order Service Item",
    "tabJob Order Part Item",
    "tabVehicle Estimate",
    "tabVehicle Inspection",
    "tabSales Invoice",
    "tabCustomer Vehicle",
    "tabVehicle Make",
    "tabVehicle Model",
    "tabBin Location",
    "tabBin",
]
print("\n\n########## SCHEMA ##########")
for t in tables:
    try:
        cols = frappe.db.sql(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position",
            t,
            as_dict=True,
        )
        print("TABLE:", repr(t), "->", [c["column_name"] for c in cols])
    except Exception as e:
        print("TABLE:", repr(t), "ERR", repr(e))
