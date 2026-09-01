#!/usr/bin/env python3
"""Patch frappe source: exclude 'Welcome Workspace' from module auto-sidebar generation.

Root cause of the desktop crash (TypeError: Cannot read properties of undefined reading
'toLowerCase' at slug/generate_route/get_route/DesktopIcon):
auto_generate_sidebar_from_module() builds a sidebar Link item for EVERY Workspace in a
module, including 'Welcome Workspace' (module Core). But get_desktop_page() EXCLUDES
'Welcome Workspace' from frappe.workspaces.pages, so clicking that sidebar item resolves
frappe.workspaces['welcome-workspace'] to undefined -> slug(undefined) crash.

Patch: skip 'Welcome Workspace' in create_sidebar_items() (the module-sidebar item loop).
"""
PATH = "/workspace/frappe-bench/apps/frappe/frappe/desk/doctype/workspace_sidebar/workspace_sidebar.py"
src = open(PATH).read()

old = "\t\tfor item in items:\n\t\t\titem_info = {\"label\": item, \"type\": \"Link\", \"link_type\": entity, \"link_to\": item, \"idx\": idx}\n"
new = "\t\tfor item in items:\n\t\t\tif entity_lower == \"workspace\" and item == \"Welcome Workspace\":\n\t\t\t\tcontinue  # excluded from frappe.workspaces; would crash the desk sidebar route\n\t\t\titem_info = {\"label\": item, \"type\": \"Link\", \"link_type\": entity, \"link_to\": item, \"idx\": idx}\n"

if old not in src:
    print("!! target not found (may already be patched or different formatting)")
    # try looser match
    i = src.find("for item in items:")
    print("for item in items: at", i)
    print(repr(src[i:i+160]))
    raise SystemExit(1)

src = src.replace(old, new, 1)
open(PATH, "w").write(src)
print("patched workspace_sidebar.py")

import ast
ast.parse(src)
print("syntax OK")
