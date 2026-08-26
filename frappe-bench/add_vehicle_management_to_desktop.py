import json
import frappe
from frappe.desk.doctype.desktop_icon.desktop_icon import clear_desktop_icons_cache

def add_vehicle_management_to_desktop():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    # 1. Create Workspace Sidebar if missing
    sidebar_name = "Vehicle Management"
    if not frappe.db.exists("Workspace Sidebar", sidebar_name):
        sidebar = frappe.new_doc("Workspace Sidebar")
        sidebar.name = sidebar_name
        sidebar.title = "Vehicle Management"
        sidebar.header_icon = "car"
        sidebar.app = "vehicle_management"
        sidebar.standard = 1
        
        items = [
            {"label": "Vehicle Management", "link_to": "Vehicle Management", "link_type": "Workspace", "type": "Link", "icon": "home"},
            {"label": "Customer Vehicles", "link_to": "Customer Vehicle", "link_type": "DocType", "type": "Link", "icon": "car"},
            {"label": "Vehicle Job Orders", "link_to": "Vehicle Job Order", "link_type": "DocType", "type": "Link", "icon": "tool"},
            {"label": "Vehicle Inspections", "link_to": "Vehicle Inspection", "link_type": "DocType", "type": "Link", "icon": "check-circle"},
            {"label": "Inspection Templates", "link_to": "Inspection Template", "link_type": "DocType", "type": "Link", "icon": "file-text"},
            {"label": "Service Reminders", "link_to": "Vehicle Service Reminder", "link_type": "DocType", "type": "Link", "icon": "bell"},
            {"label": "Vehicle Makes", "link_to": "Vehicle Make", "link_type": "DocType", "type": "Link", "icon": "tag"},
            {"label": "Vehicle Models", "link_to": "Vehicle Model", "link_type": "DocType", "type": "Link", "icon": "list"}
        ]
        for item in items:
            sidebar.append("items", item)
        sidebar.insert(ignore_permissions=True)
        print("Created Workspace Sidebar: Vehicle Management")

    # 2. Create / Update Desktop Icon
    icon_name = "Vehicle Management"
    if not frappe.db.exists("Desktop Icon", icon_name):
        d_icon = frappe.new_doc("Desktop Icon")
        d_icon.label = "Vehicle Management"
        d_icon.icon_type = "Link"
        d_icon.link_type = "Workspace Sidebar"
        d_icon.link_to = "Vehicle Management"
        d_icon.sidebar = "Vehicle Management"
        d_icon.app = "vehicle_management"
        d_icon.icon = "car"
        d_icon.standard = 1
        d_icon.hidden = 0
        d_icon.restrict_removal = 0
        d_icon.insert(ignore_permissions=True)
        print("Created Desktop Icon: Vehicle Management")
    else:
        frappe.db.set_value("Desktop Icon", icon_name, {
            "icon_type": "Link",
            "link_type": "Workspace Sidebar",
            "link_to": "Vehicle Management",
            "sidebar": "Vehicle Management",
            "app": "vehicle_management",
            "icon": "car",
            "hidden": 0,
            "standard": 1
        })
        print("Updated Desktop Icon: Vehicle Management")

    # 3. Update Desktop Layout for Administrator & all users
    vehicle_icon_data = {
        "label": "Vehicle Management",
        "bg_color": None,
        "link": None,
        "link_type": "Workspace Sidebar",
        "app": "vehicle_management",
        "icon_type": "Link",
        "parent_icon": "",
        "icon": "car",
        "link_to": "Vehicle Management",
        "idx": 0,
        "standard": 1,
        "logo_url": None,
        "hidden": 0,
        "name": "Vehicle Management",
        "restrict_removal": 0,
        "icon_image": None,
        "url": "/desk/vehicle-management",
        "child_icons": []
    }

    layouts = frappe.get_all("Desktop Layout", fields=["name", "layout", "user"])
    for l in layouts:
        try:
            layout_data = json.loads(l.layout) if l.layout else []
            # Check if Vehicle Management already in layout
            layout_data = [item for item in layout_data if item.get("label") != "Vehicle Management" and item.get("name") != "Vehicle Management"]
            layout_data.insert(0, vehicle_icon_data)
            frappe.db.set_value("Desktop Layout", l.name, "layout", json.dumps(layout_data))
            print(f"Added Vehicle Management to Desktop Layout for {l.name}")
        except Exception as e:
            print(f"Error updating layout for {l.name}: {e}")

    frappe.db.commit()
    clear_desktop_icons_cache("Administrator")
    frappe.clear_cache()
    print("Desktop Icon, Workspace Sidebar and Layout updated successfully!")

if __name__ == "__main__":
    add_vehicle_management_to_desktop()
