#!/usr/bin/env python3
import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# The "core" sidebar items include "Welcome Workspace". Find the Workspace Sidebar / item source.
# workspace_sidebar_item boot comes from workspace sidebar records. Check the "Core" or "System" sidebar content.
sbs = frappe.get_all("Workspace Sidebar", fields=["name", "title", "module"])
print("Workspace Sidebars:", [(s.name, s.title, s.module) for s in sbs])

# Also check the workspace_sidebar_item source: it may come from 'Workspace Sidebar Item' child or from workspace 'sidebar' field
# Search all workspace docs for a 'sidebar' JSON or 'links' field referencing Welcome Workspace
for w in frappe.get_all("Workspace", fields=["name"]):
    doc = frappe.get_doc("Workspace", w.name)
    d = doc.as_dict()
    for field in ["sidebar", "links", "content"]:
        v = d.get(field)
        if isinstance(v, str) and "Welcome Workspace" in v:
            print(f"Workspace {w.name} field {field} references Welcome Workspace")
        elif isinstance(v, list):
            for item in v:
                s = json.dumps(item)
                if "Welcome Workspace" in s:
                    print(f"Workspace {w.name} field {field} item references Welcome Workspace: {s[:200]}")
print("scan done")
