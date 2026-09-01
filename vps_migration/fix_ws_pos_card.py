#!/usr/bin/env python3
"""Fix the 'POS' card reference in the Vehicle Management workspace that crashes
the desk (generate_route -> slug(undefined) -> toLowerCase TypeError).

Root cause: workspace content JSON has {"type":"card","data":{"card_name":"POS"}}
but no Workspace Card/Shortcut named "POS" exists, so the item has no `type`
and frappe.utils.generate_route() crashes on item.type.toLowerCase().
"""
import frappe, json

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# 1. Create a "POS" Workspace Shortcut pointing to the vehicle_pos Page (if missing)
if not frappe.db.exists("Workspace Shortcut", {"label": "POS"}):
    sc = frappe.get_doc({
        "doctype": "Workspace Shortcut",
        "label": "POS",
        "link_to": "vehicle_pos",
        "type": "Page",
        "parent": "Vehicle Management",
        "parenttype": "Workspace",
        "parentfield": "shortcuts",
    })
    sc.insert(ignore_permissions=True)
    print("created POS Workspace Shortcut:", sc.name)
else:
    print("POS shortcut already exists")

# 2. Fix the workspace content JSON: replace the broken "card_name":"POS" with a shortcut ref
ws = frappe.get_doc("Workspace", "Vehicle Management")
content = ws.content or "[]"
data = json.loads(content)
fixed = []
for item in data:
    # replace the broken POS card with a shortcut pointing to our new shortcut
    if item.get("type") == "card" and item.get("data", {}).get("card_name") == "POS":
        fixed.append({"id": "shortcuts_pos", "type": "shortcut", "data": {"shortcut_name": "POS", "col": 3}})
        print("replaced card_name:POS -> shortcut_name:POS")
    else:
        fixed.append(item)

ws.content = json.dumps(fixed)
ws.save(ignore_permissions=True)
frappe.db.commit()
print("workspace content fixed. new items:", len(fixed))
print("final content:", json.dumps(fixed))
