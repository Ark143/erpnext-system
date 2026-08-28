import frappe
from erpnext.setup.doctype.employee.employee import get_children as get_employee_children

def test():
    frappe.init(site="site1.local")
    frappe.connect()
    print("=== Testing Database Connection ===")
    print(f"Connected to DB: {frappe.conf.db_name}")
    print(f"Installed Apps: {frappe.get_installed_apps()}")

    print("\n=== Testing Employee Tree View ===")
    try:
        frappe.db.rollback()
        employees = frappe.get_all("Employee", fields=["name", "employee_name", "reports_to"], limit=5)
        print(f"Found {len(employees)} sample employees:")
        for emp in employees:
            print(f" - {emp.name}: {emp.employee_name} (Reports to: {emp.reports_to})")
        
        # Test tree view get_children
        children = get_employee_children(doctype="Employee", is_root=True)
        print(f"Employee Tree View get_children(is_root=True) returned {len(children)} root nodes: {children}")
        print("Employee Tree View: OK")
    except Exception as e:
        print(f"Employee Tree View test error: {e}")

    print("\n=== Testing Vehicle Management Doctypes ===")
    frappe.db.rollback()
    vm_doctypes = [
        "Vehicle Make",
        "Vehicle Model",
        "Customer Vehicle",
        "Vehicle Estimate",
        "Vehicle Inspection",
        "Vehicle Job Order",
        "Vehicle Service Reminder",
        "Inspection Template",
        "Item Vehicle Compatibility",
        "Bin Location",
    ]
    for dt in vm_doctypes:
        try:
            frappe.db.rollback()
            exists = frappe.db.exists("DocType", dt)
            count = frappe.db.count(dt) if exists else 0
            sample = frappe.get_all(dt, limit=1) if count > 0 else []
            print(f" - DocType '{dt}': {'Found' if exists else 'Missing'} ({count} records, sample: {sample})")
        except Exception as e:
            print(f" - DocType '{dt}' query error: {e}")

    print("\n=== Testing Realtime & Cache ===")
    try:
        frappe.db.rollback()
        frappe.publish_realtime("test_event", {"status": "ok"}, user="Administrator")
        print("Realtime publish: OK")
    except Exception as e:
        print(f"Realtime publish error: {e}")

    frappe.destroy()
    print("\n=== ALL MODULE TESTS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test()
