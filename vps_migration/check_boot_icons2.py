#!/usr/bin/env python3
import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# Boot payload desktop icons come from get_workspace_sidebar_items + get_desktop_page
try:
    from frappe.desk.desktop import get_workspace_sidebar_items
    items = get_workspace_sidebar_items()
    print("type:", type(items))
    if isinstance(items, dict):
        print("keys:", list(items.keys()))
        # find icons with null label
        def scan(obj, path=""):
            if isinstance(obj, dict):
                if obj.get("label") in (None, "") and ("name" in obj or "link_to" in obj or "type" in obj):
                    print("NULL-LABEL at", path, ":", {k: obj.get(k) for k in ("name","label","link_to","link_type","type")})
                for k, v in obj.items():
                    scan(v, path + "/" + str(k))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    scan(v, path + f"[{i}]")
        scan(items)
        print("scan complete")
except Exception as e:
    import traceback; traceback.print_exc()

# Also: get_desktop_page requires 'page' — call with a page name
try:
    from frappe.desk.desktop import get_desktop_page
    p = get_desktop_page("desktop")
    print("\ndesktop page keys:", list(p.keys()) if isinstance(p, dict) else type(p))
    di = p.get("desktop_icons") if isinstance(p, dict) else None
    if di:
        print("desktop_icons count:", len(di))
        for it in di:
            if isinstance(it, dict) and (it.get("label") in (None, "")):
                print("  NULL-LABEL:", it)
except Exception as e:
    import traceback; traceback.print_exc()
