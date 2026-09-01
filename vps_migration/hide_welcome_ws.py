#!/usr/bin/env python3
"""Fix the desktop crash: hide the orphaned 'Welcome Workspace' workspace.

Frappe's own code (desktop.py, workspace_sidebar.py, desktop_icon.py) EXCLUDES
'Welcome Workspace' from the workspaces list (page.title != 'Welcome Workspace',
workspace.name != 'Welcome Workspace'), but this DB has a stale 'Welcome Workspace'
row that still leaks into the sidebar boot data as a Workspace-type link. When the
desk builds that link's route, frappe.workspaces[slug] is undefined -> generate_route
-> slug(undefined) -> TypeError. Hide it (non-destructive).
"""
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

if frappe.db.exists("Workspace", "Welcome Workspace"):
    frappe.db.set_value("Workspace", "Welcome Workspace", "is_hidden", 1)
    frappe.db.commit()
    print("hidden 'Welcome Workspace' (is_hidden=1)")
    v = frappe.db.get_value("Workspace", "Welcome Workspace", ["is_hidden", "title"], as_dict=True)
    print("verify:", v)
else:
    print("Welcome Workspace not found")
