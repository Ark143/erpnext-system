#!/usr/bin/env python3
import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# verify the workspace content no longer has the broken POS card
ws = frappe.get_doc("Workspace", "Vehicle Management")
data = json.loads(ws.content or "[]")
broken = [i for i in data if i.get("type") == "card" and i.get("data", {}).get("card_name")]
print("broken cards remaining:", broken)

# verify the POS shortcut resolves
sc = frappe.get_all("Workspace Shortcut", filters={"label": "POS"}, fields=["name", "label", "link_to", "type"])
print("POS shortcut:", sc)

# verify every shortcut referenced in content resolves to a real shortcut/card
shortcuts = {s.label: s for s in frappe.get_all("Workspace Shortcut", fields=["name","label","link_to","type"])}
for item in data:
    if item.get("type") == "shortcut":
        sn = item["data"]["shortcut_name"]
        ok = sn in shortcuts
        print(f"  shortcut ref {sn!r} -> {'OK ' + shortcuts[sn].type if ok else 'MISSING'}")

print("ALL OK" if not broken else "STILL BROKEN")
