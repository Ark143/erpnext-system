import frappe, os, json, shutil
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
OUT = "/workspace/doctype_defs"
os.makedirs(OUT, exist_ok=True)
base = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype"
count = 0
for dt in os.listdir(base):
    jp = os.path.join(base, dt, f"{dt}.json")
    if os.path.exists(jp):
        shutil.copy(jp, os.path.join(OUT, f"{dt}.json"))
        count += 1
print(f"copied {count} doctype defs to {OUT}")
# also list which doctypes have python controllers (need app code, not just schema)
for dt in sorted(os.listdir(base)):
    has_py = os.path.exists(os.path.join(base, dt, f"{dt}.py"))
    print(f"{dt}: controller={'YES' if has_py else 'no'}")
