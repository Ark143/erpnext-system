"""
Setup Number Cards, Dashboard Charts and configure Vehicle Management Workspace.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()
frappe.flags.in_developer_mode = True

print("=" * 65)
print("  CONFIGURING WORKSPACE CHARTS & NUMBER CARDS")
print("=" * 65)

# 1. Create Number Cards
CARDS = [
    {
        "name": "VM Total Job Orders",
        "label": "Total Job Orders",
        "document_type": "Vehicle Job Order",
        "function": "Count",
        "color": "#1a56db"
    },
    {
        "name": "VM Total Labor Revenue",
        "label": "Total Labor Revenue (PHP)",
        "document_type": "Vehicle Job Order",
        "function": "Sum",
        "aggregate_function_based_on": "total_labor",
        "color": "#046c4e"
    },
    {
        "name": "VM Total Parts Revenue",
        "label": "Total Parts & Tires Sales (PHP)",
        "document_type": "Vehicle Job Order",
        "function": "Sum",
        "aggregate_function_based_on": "total_parts",
        "color": "#7e3af2"
    },
    {
        "name": "VM Total Revenue",
        "label": "Lifetime Total Revenue (PHP)",
        "document_type": "Vehicle Job Order",
        "function": "Sum",
        "aggregate_function_based_on": "grand_total",
        "color": "#c27803"
    }
]

for c in CARDS:
    if frappe.db.exists("Number Card", c["name"]):
        doc = frappe.get_doc("Number Card", c["name"])
        doc.update(c)
        doc.save(ignore_permissions=True)
        print(f"  * Updated Number Card '{c['name']}'")
    else:
        doc = frappe.get_doc({
            "doctype": "Number Card",
            "name": c["name"],
            "module": "Vehicle Management",
            "is_standard": 1,
            "is_public": 1,
            **c
        })
        doc.insert(ignore_permissions=True)
        print(f"  + Created Number Card '{c['name']}'")

# 2. Create Dashboard Chart
CHART_NAME = "VM Job Orders by Company"
if frappe.db.exists("Dashboard Chart", CHART_NAME):
    chart = frappe.get_doc("Dashboard Chart", CHART_NAME)
    chart.type = "Bar"
    chart.save(ignore_permissions=True)
    print(f"  * Updated Dashboard Chart '{CHART_NAME}'")
else:
    chart = frappe.get_doc({
        "doctype": "Dashboard Chart",
        "name": CHART_NAME,
        "chart_name": CHART_NAME,
        "chart_type": "Group By",
        "document_type": "Vehicle Job Order",
        "group_by_based_on": "company",
        "group_by_type": "Count",
        "aggregate_function_based_on": "name",
        "type": "Bar",
        "is_public": 1,
        "is_standard": 0,
        "filters_json": "[]",
        "module": "Vehicle Management",
        "timespan": "Last Month",
        "time_interval": "Monthly"
    })
    chart.insert(ignore_permissions=True)
    print(f"  + Created Dashboard Chart '{CHART_NAME}'")

frappe.db.commit()
frappe.clear_cache()
print("Setup completed successfully!")
