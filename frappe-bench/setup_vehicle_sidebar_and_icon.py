import frappe

def setup():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    ws_name = "Vehicle Management"

    # 1. Create or update Workspace Sidebar
    if frappe.db.exists("Workspace Sidebar", ws_name):
        frappe.delete_doc("Workspace Sidebar", ws_name, force=True)

    sb = frappe.new_doc("Workspace Sidebar")
    sb.title = ws_name
    sb.header_icon = "car"
    sb.standard = 1
    sb.app = "vehicle_management"

    # Items in sidebar
    items = [
        {"label": "Vehicle Management", "type": "Link", "link_type": "Workspace", "link_to": "Vehicle Management", "icon": "home", "child": 0},
        {"label": "Customer Vehicles", "type": "Link", "link_type": "DocType", "link_to": "Customer Vehicle", "icon": "car", "child": 0},
        {"label": "Vehicle Job Orders", "type": "Link", "link_type": "DocType", "link_to": "Vehicle Job Order", "icon": "tool", "child": 0},
        {"label": "Vehicle Inspections", "type": "Link", "link_type": "DocType", "link_to": "Vehicle Inspection", "icon": "check-circle", "child": 0},
        {"label": "Inspection Templates", "type": "Link", "link_type": "DocType", "link_to": "Inspection Template", "icon": "file-text", "child": 0},
        {"label": "Service Reminders", "type": "Link", "link_type": "DocType", "link_to": "Vehicle Service Reminder", "icon": "bell", "child": 0},
        {"label": "Vehicle Makes", "type": "Link", "link_type": "DocType", "link_to": "Vehicle Make", "icon": "tag", "child": 0},
        {"label": "Vehicle Models", "type": "Link", "link_type": "DocType", "link_to": "Vehicle Model", "icon": "list", "child": 0},
    ]

    for idx, item in enumerate(items, 1):
        sb.append("items", {
            "idx": idx,
            "label": item["label"],
            "type": item["type"],
            "link_type": item["link_type"],
            "link_to": item["link_to"],
            "icon": item["icon"],
            "child": item["child"],
            "collapsible": 1
        })

    sb.insert(ignore_permissions=True)
    print(f"Created Workspace Sidebar: {ws_name}")

    # 2. Create or update Desktop Icon
    if frappe.db.exists("Desktop Icon", ws_name):
        frappe.delete_doc("Desktop Icon", ws_name, force=True)

    icon = frappe.new_doc("Desktop Icon")
    icon.label = ws_name
    icon.icon_type = "Link"
    icon.link_type = "Workspace Sidebar"
    icon.link_to = ws_name
    icon.icon = "car"
    icon.bg_color = "blue"
    icon.standard = 1
    icon.app = "vehicle_management"
    icon.hidden = 0
    icon.idx = 1
    icon.insert(ignore_permissions=True)
    print(f"Created Desktop Icon: {ws_name}")

    # 3. Add Vehicle Management to user allowed modules
    frappe.db.commit()
    frappe.clear_cache()
    print("Sidebar and Desktop Icon setup successfully!")

if __name__ == "__main__":
    setup()
