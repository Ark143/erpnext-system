#!/usr/bin/env python3
import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# How does the desk get desktop icons? via frappe.boot.desktop_icons / workspace_sidebar_item
# Check the boot payload build path: frappe.desk.desktop.get_desktop_page
try:
    from frappe.desk.desktop import get_desktop_page
    page = get_desktop_page()
    print("desktop page keys:", list(page.keys()))
    for k in ["desktop_icons", "workspace_sidebar_item", "workspaces"]:
        v = page.get(k)
        if isinstance(v, list):
            print(f"\n{k}: {len(v)} items")
            for it in v:
                if isinstance(it, dict) and (it.get("label") in (None, "")):
                    print("  NULL-LABEL ICON:", it)
        elif isinstance(v, dict):
            print(f"\n{k}: dict with {len(v)} keys")
except Exception as e:
    import traceback; traceback.print_exc()
