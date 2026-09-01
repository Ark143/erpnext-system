#!/usr/bin/env python3
import frappe, json
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

# Scan EVERY workspace for broken card/shortcut refs (not just Vehicle Management)
print("=== all workspaces ===")
all_ws = frappe.get_all("Workspace", fields=["name"])
print("count:", len(all_ws))
for w in all_ws:
    doc = frappe.get_doc("Workspace", w.name)
    try:
        data = json.loads(doc.content or "[]")
    except Exception as e:
        print(f"  {w.name}: BAD JSON content ({e})")
        continue
    broken = []
    for item in data:
        if item.get("type") == "card" and item.get("data", {}).get("card_name"):
            cn = item["data"]["card_name"]
            # a card_name must resolve to a Workspace Shortcut or Card
            if not frappe.db.exists("Workspace Shortcut", {"label": cn}):
                broken.append(f"card_name={cn!r}")
    if broken:
        print(f"  {w.name}: BROKEN -> {broken}")

print("\n=== workspace_sidebar_item source: any sidebar item with missing label? ===")
# The get_route line 88 reads frappe.boot.workspace_sidebar_item[label.toLowerCase()]
# which is built from workspace shortcuts. Check all shortcuts resolve.
shorts = frappe.get_all("Workspace Shortcut", fields=["name","label","link_to","type","parent"])
print("total shortcuts:", len(shorts))
for s in shorts:
    if not s.label:
        print(f"  NULL-LABEL shortcut: {s.name} parent={s.parent}")

print("\nSCAN COMPLETE")
