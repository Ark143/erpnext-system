import os
import json
import frappe

def create_doctypes():
    frappe.init('site1.local')
    frappe.connect()

    module = "Vehicle Management"
    base_path = os.path.abspath(os.path.join(frappe.get_app_path("vehicle_management"), "vehicle_management", "doctype"))
    os.makedirs(base_path, exist_ok=True)

    doctypes_def = [
        # 1. Vehicle Make
        {
            "name": "Vehicle Make",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 0,
            "naming_rule": "By fieldname",
            "autoname": "field:make_name",
            "fields": [
                {"fieldname": "make_name", "fieldtype": "Data", "label": "Make Name", "reqd": 1, "unique": 1},
                {"fieldname": "logo", "fieldtype": "Attach Image", "label": "Logo"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        # 2. Vehicle Model
        {
            "name": "Vehicle Model",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 0,
            "autoname": "format:{make}-{model_name}",
            "fields": [
                {"fieldname": "make", "fieldtype": "Link", "options": "Vehicle Make", "label": "Make", "reqd": 1, "in_list_view": 1},
                {"fieldname": "model_name", "fieldtype": "Data", "label": "Model Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "category", "fieldtype": "Select", "options": "Sedan\nSUV\nPickup\nHatchback\nCoupe\nVan\nTruck\nMotorcycle\nOther", "label": "Body Type"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        # 3. Customer Vehicle
        {
            "name": "Customer Vehicle",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 0,
            "naming_rule": "By fieldname",
            "autoname": "field:plate_no",
            "search_fields": "customer,customer_name,make,model,vin,contact_no",
            "title_field": "plate_no",
            "fields": [
                {"fieldname": "sec_id", "fieldtype": "Section Break", "label": "Identification & Ownership"},
                {"fieldname": "plate_no", "fieldtype": "Data", "label": "Plate No / Conduction Sticker", "reqd": 1, "unique": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "customer_name", "fieldtype": "Data", "label": "Customer Name", "fetch_from": "customer.customer_name", "read_only": 1},
                {"fieldname": "col_break_1", "fieldtype": "Column Break"},
                {"fieldname": "contact_no", "fieldtype": "Data", "label": "Contact No", "fetch_from": "customer.mobile_no", "in_list_view": 1},
                {"fieldname": "email", "fieldtype": "Data", "label": "Email", "fetch_from": "customer.email_id"},
                {"fieldname": "status", "fieldtype": "Select", "options": "Active\nIn Service\nInactive", "default": "Active", "label": "Status"},

                {"fieldname": "sec_specs", "fieldtype": "Section Break", "label": "Vehicle Specifications"},
                {"fieldname": "make", "fieldtype": "Link", "options": "Vehicle Make", "label": "Make", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "model", "fieldtype": "Link", "options": "Vehicle Model", "label": "Model", "in_list_view": 1},
                {"fieldname": "year_model", "fieldtype": "Int", "label": "Year Model"},
                {"fieldname": "color", "fieldtype": "Data", "label": "Color"},
                {"fieldname": "col_break_2", "fieldtype": "Column Break"},
                {"fieldname": "vin", "fieldtype": "Data", "label": "VIN / Chassis No", "in_list_view": 1},
                {"fieldname": "engine_no", "fieldtype": "Data", "label": "Engine No"},
                {"fieldname": "transmission", "fieldtype": "Select", "options": "Automatic\nManual\nCVT\nDual Clutch\nEV / Single Speed", "label": "Transmission"},
                {"fieldname": "cylinders", "fieldtype": "Int", "label": "Cylinders", "default": "4"},
                {"fieldname": "fuel_type", "fieldtype": "Select", "options": "Gasoline\nDiesel\nHybrid\nElectric", "default": "Gasoline", "label": "Fuel Type"},

                {"fieldname": "sec_mileage", "fieldtype": "Section Break", "label": "Mileage & Service History"},
                {"fieldname": "current_mileage", "fieldtype": "Float", "label": "Current Odometer Reading"},
                {"fieldname": "mileage_unit", "fieldtype": "Select", "options": "km\nmi", "default": "km", "label": "Mileage Unit"},
                {"fieldname": "last_service_date", "fieldtype": "Date", "label": "Last Service Date", "read_only": 1},
                {"fieldname": "col_break_3", "fieldtype": "Column Break"},
                {"fieldname": "registration_type", "fieldtype": "Select", "options": "Private\nCommercial\nGovernment", "default": "Private", "label": "Registration Type"},
                {"fieldname": "insurance_company", "fieldtype": "Data", "label": "Insurance Provider"},
                {"fieldname": "insurance_expiry_date", "fieldtype": "Date", "label": "Insurance Expiry Date"},

                {"fieldname": "sec_notes", "fieldtype": "Section Break", "label": "Notes & Remarks"},
                {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes / Special Instructions"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        # 4. Job Order Service Item (Child Table)
        {
            "name": "Job Order Service Item",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "service_item", "fieldtype": "Link", "options": "Item", "label": "Service / Labor Item", "in_list_view": 1},
                {"fieldname": "description", "fieldtype": "Small Text", "label": "Description / Scope of Work", "reqd": 1, "in_list_view": 1},
                {"fieldname": "mechanic", "fieldtype": "Data", "label": "Assigned Mechanic", "in_list_view": 1},
                {"fieldname": "hours", "fieldtype": "Float", "label": "Hours", "default": "1.0", "in_list_view": 1},
                {"fieldname": "rate", "fieldtype": "Currency", "label": "Hourly Rate / Fee", "reqd": 1, "in_list_view": 1},
                {"fieldname": "discount_amount", "fieldtype": "Currency", "label": "Discount", "default": "0"},
                {"fieldname": "total_amount", "fieldtype": "Currency", "label": "Total Amount", "read_only": 1, "in_list_view": 1},
                {"fieldname": "next_service_date", "fieldtype": "Date", "label": "Next Due Date"}
            ],
            "permissions": []
        },
        # 5. Job Order Part Item (Child Table)
        {
            "name": "Job Order Part Item",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "item_code", "fieldtype": "Link", "options": "Item", "label": "Part Item Code", "in_list_view": 1},
                {"fieldname": "item_name", "fieldtype": "Data", "label": "Part Name", "fetch_from": "item_code.item_name", "in_list_view": 1},
                {"fieldname": "part_no", "fieldtype": "Data", "label": "OEM Part No", "in_list_view": 1},
                {"fieldname": "qty", "fieldtype": "Float", "label": "Qty", "default": "1.0", "reqd": 1, "in_list_view": 1},
                {"fieldname": "rate", "fieldtype": "Currency", "label": "Unit Price", "reqd": 1, "in_list_view": 1},
                {"fieldname": "discount_amount", "fieldtype": "Currency", "label": "Discount", "default": "0"},
                {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "read_only": 1, "in_list_view": 1}
            ],
            "permissions": []
        },
        # 6. Vehicle Job Order
        {
            "name": "Vehicle Job Order",
            "module": module,
            "custom": 0,
            "is_submittable": 1,
            "istable": 0,
            "autoname": "naming_series:",
            "search_fields": "vehicle,plate_no,customer,customer_name",
            "title_field": "plate_no",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "options": "JO-.YYYY.-.#####", "default": "JO-.YYYY.-.#####", "label": "Series"},
                {"fieldname": "sec_header", "fieldtype": "Section Break", "label": "Customer & Vehicle Information"},
                {"fieldname": "vehicle", "fieldtype": "Link", "options": "Customer Vehicle", "label": "Vehicle", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "plate_no", "fieldtype": "Data", "label": "Plate No", "fetch_from": "vehicle.plate_no", "read_only": 1, "in_list_view": 1},
                {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "fetch_from": "vehicle.customer", "read_only": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "customer_name", "fieldtype": "Data", "label": "Customer Name", "fetch_from": "vehicle.customer_name", "read_only": 1},
                {"fieldname": "contact_no", "fieldtype": "Data", "label": "Contact No", "fetch_from": "vehicle.contact_no", "read_only": 1},
                {"fieldname": "col_break_1", "fieldtype": "Column Break"},
                {"fieldname": "job_order_date", "fieldtype": "Date", "label": "Job Order Date", "default": "Today", "reqd": 1, "in_list_view": 1},
                {"fieldname": "promised_date", "fieldtype": "Datetime", "label": "Promised Delivery Date"},
                {"fieldname": "status", "fieldtype": "Select", "options": "Draft\nIn Progress\nPending Parts\nCompleted\nInvoiced\nReleased\nCancelled", "default": "Draft", "label": "Status", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "service_advisor", "fieldtype": "Link", "options": "User", "label": "Service Advisor"},
                {"fieldname": "mileage", "fieldtype": "Float", "label": "Odometer (In)"},
                {"fieldname": "mileage_unit", "fieldtype": "Select", "options": "km\nmi", "default": "km", "label": "Unit"},

                {"fieldname": "sec_complaint", "fieldtype": "Section Break", "label": "Customer Request / Complaints"},
                {"fieldname": "customer_complaint", "fieldtype": "Small Text", "label": "Customer Request & Problem Description"},

                {"fieldname": "sec_services", "fieldtype": "Section Break", "label": "Labor & Services"},
                {"fieldname": "services", "fieldtype": "Table", "options": "Job Order Service Item", "label": "Labor & Service Items"},

                {"fieldname": "sec_parts", "fieldtype": "Section Break", "label": "Parts & Materials"},
                {"fieldname": "parts", "fieldtype": "Table", "options": "Job Order Part Item", "label": "Replacement Parts & Consumables"},

                {"fieldname": "sec_totals", "fieldtype": "Section Break", "label": "Totals & Accounting Summary"},
                {"fieldname": "total_labor", "fieldtype": "Currency", "label": "Total Labor Amount", "read_only": 1},
                {"fieldname": "total_parts", "fieldtype": "Currency", "label": "Total Parts Amount", "read_only": 1},
                {"fieldname": "col_break_2", "fieldtype": "Column Break"},
                {"fieldname": "net_total", "fieldtype": "Currency", "label": "Subtotal", "read_only": 1},
                {"fieldname": "discount_amount", "fieldtype": "Currency", "label": "Additional Overall Discount", "default": "0"},
                {"fieldname": "grand_total", "fieldtype": "Currency", "label": "Total Amount Due", "read_only": 1},

                {"fieldname": "sec_billing", "fieldtype": "Section Break", "label": "Invoicing & Payment Status"},
                {"fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "label": "Linked Sales Invoice", "read_only": 1},
                {"fieldname": "payment_status", "fieldtype": "Select", "options": "Unpaid\nPartially Paid\nPaid", "default": "Unpaid", "label": "Payment Status", "read_only": 1},
                {"fieldname": "paid_amount", "fieldtype": "Currency", "label": "Paid Amount", "read_only": 1},
                {"fieldname": "outstanding_amount", "fieldtype": "Currency", "label": "Outstanding Balance", "read_only": 1}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}]
        },
        # 7. Inspection Template Item (Child Table)
        {
            "name": "Inspection Template Item",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "category", "fieldtype": "Data", "label": "Inspection Category", "reqd": 1, "in_list_view": 1},
                {"fieldname": "item_name", "fieldtype": "Data", "label": "Inspection Check Item", "reqd": 1, "in_list_view": 1},
                {"fieldname": "standard_description", "fieldtype": "Small Text", "label": "Standard Criteria / Instructions"}
            ],
            "permissions": []
        },
        # 8. Inspection Template
        {
            "name": "Inspection Template",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 0,
            "naming_rule": "By fieldname",
            "autoname": "field:template_name",
            "fields": [
                {"fieldname": "template_name", "fieldtype": "Data", "label": "Template Name", "reqd": 1, "unique": 1, "in_list_view": 1},
                {"fieldname": "description", "fieldtype": "Small Text", "label": "Description"},
                {"fieldname": "sec_items", "fieldtype": "Section Break", "label": "Checklist Items"},
                {"fieldname": "items", "fieldtype": "Table", "options": "Inspection Template Item", "label": "Inspection Checklist"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        },
        # 9. Vehicle Inspection Item (Child Table)
        {
            "name": "Vehicle Inspection Item",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "category", "fieldtype": "Data", "label": "Category", "in_list_view": 1},
                {"fieldname": "item_name", "fieldtype": "Data", "label": "Item Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "status", "fieldtype": "Select", "options": "Pass / OK\nRequires Attention\nImmediate Action Required\nNot Applicable", "default": "Pass / OK", "label": "Status", "reqd": 1, "in_list_view": 1},
                {"fieldname": "observation", "fieldtype": "Small Text", "label": "Technician Observations", "in_list_view": 1},
                {"fieldname": "estimated_cost", "fieldtype": "Currency", "label": "Estimated Repair Cost"}
            ],
            "permissions": []
        },
        # 10. Vehicle Inspection
        {
            "name": "Vehicle Inspection",
            "module": module,
            "custom": 0,
            "is_submittable": 1,
            "istable": 0,
            "autoname": "naming_series:",
            "search_fields": "vehicle,plate_no,customer,customer_name",
            "title_field": "plate_no",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "options": "INSP-.YYYY.-.#####", "default": "INSP-.YYYY.-.#####", "label": "Series"},
                {"fieldname": "sec_header", "fieldtype": "Section Break", "label": "Inspection Header"},
                {"fieldname": "inspection_date", "fieldtype": "Date", "label": "Inspection Date", "default": "Today", "reqd": 1, "in_list_view": 1},
                {"fieldname": "vehicle", "fieldtype": "Link", "options": "Customer Vehicle", "label": "Vehicle", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "plate_no", "fieldtype": "Data", "label": "Plate No", "fetch_from": "vehicle.plate_no", "read_only": 1, "in_list_view": 1},
                {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "fetch_from": "vehicle.customer", "read_only": 1, "in_list_view": 1},
                {"fieldname": "customer_name", "fieldtype": "Data", "label": "Customer Name", "fetch_from": "vehicle.customer_name", "read_only": 1},
                {"fieldname": "col_break_1", "fieldtype": "Column Break"},
                {"fieldname": "inspection_template", "fieldtype": "Link", "options": "Inspection Template", "label": "Template", "in_list_view": 1},
                {"fieldname": "mechanic", "fieldtype": "Data", "label": "Inspected By (Mechanic)", "in_list_view": 1},
                {"fieldname": "mileage", "fieldtype": "Float", "label": "Current Odometer Reading"},
                {"fieldname": "overall_status", "fieldtype": "Select", "options": "Passed\nMinor Issues\nCritical Action Required", "default": "Passed", "label": "Overall Result"},

                {"fieldname": "sec_remarks", "fieldtype": "Section Break", "label": "Diagnostic Findings & Remarks"},
                {"fieldname": "general_remarks", "fieldtype": "Small Text", "label": "General Findings & Recommendations"},

                {"fieldname": "sec_items", "fieldtype": "Section Break", "label": "Inspection Checklist"},
                {"fieldname": "items", "fieldtype": "Table", "options": "Vehicle Inspection Item", "label": "Checklist Items"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}]
        },
        # 11. Vehicle Service Reminder
        {
            "name": "Vehicle Service Reminder",
            "module": module,
            "custom": 0,
            "is_submittable": 0,
            "istable": 0,
            "autoname": "naming_series:",
            "search_fields": "vehicle,plate_no,customer,service_type",
            "title_field": "plate_no",
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "options": "REM-.YYYY.-.#####", "default": "REM-.YYYY.-.#####", "label": "Series"},
                {"fieldname": "sec_info", "fieldtype": "Section Break", "label": "Reminder Details"},
                {"fieldname": "vehicle", "fieldtype": "Link", "options": "Customer Vehicle", "label": "Vehicle", "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "plate_no", "fieldtype": "Data", "label": "Plate No", "fetch_from": "vehicle.plate_no", "read_only": 1, "in_list_view": 1},
                {"fieldname": "customer", "fieldtype": "Link", "options": "Customer", "label": "Customer", "fetch_from": "vehicle.customer", "read_only": 1, "in_list_view": 1},
                {"fieldname": "customer_name", "fieldtype": "Data", "label": "Customer Name", "fetch_from": "vehicle.customer_name", "read_only": 1},
                {"fieldname": "contact_no", "fieldtype": "Data", "label": "Mobile No", "fetch_from": "vehicle.contact_no", "read_only": 1},
                {"fieldname": "col_break_1", "fieldtype": "Column Break"},
                {"fieldname": "service_type", "fieldtype": "Data", "label": "Service Due", "reqd": 1, "in_list_view": 1},
                {"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date", "in_list_view": 1, "in_standard_filter": 1},
                {"fieldname": "due_mileage", "fieldtype": "Float", "label": "Target Mileage Due"},
                {"fieldname": "lead_days", "fieldtype": "Int", "default": "7", "label": "Lead Time (Days)"},
                {"fieldname": "status", "fieldtype": "Select", "options": "Pending\nSent\nBooked\nOverdue\nCancelled", "default": "Pending", "label": "Status", "in_list_view": 1, "in_standard_filter": 1},

                {"fieldname": "sec_msg", "fieldtype": "Section Break", "label": "Message Content"},
                {"fieldname": "reminder_message", "fieldtype": "Small Text", "label": "SMS / Email Message"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
        }
    ]

    for d in doctypes_def:
        folder_name = frappe.scrub(d["name"])
        target_dir = os.path.join(base_path, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        json_path = os.path.join(target_dir, f"{folder_name}.json")
        py_path = os.path.join(target_dir, f"{folder_name}.py")
        js_path = os.path.join(target_dir, f"{folder_name}.js")

        doctype_dict = {
            "doctype": "DocType",
            "name": d["name"],
            "module": d["module"],
            "custom": d.get("custom", 0),
            "is_submittable": d.get("is_submittable", 0),
            "istable": d.get("istable", 0),
            "editable_grid": 1 if d.get("istable") else 0,
            "track_changes": 1,
            "engine": "InnoDB",
            "autoname": d.get("autoname"),
            "naming_rule": d.get("naming_rule"),
            "search_fields": d.get("search_fields"),
            "title_field": d.get("title_field"),
            "fields": d.get("fields", []),
            "permissions": d.get("permissions", [])
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doctype_dict, f, indent=1)

        # Generate basic python file
        class_name = d["name"].replace(" ", "")
        py_code = f"""# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class {class_name}(Document):
	pass
"""
        if not os.path.exists(py_path):
            with open(py_path, "w", encoding="utf-8") as f:
                f.write(py_code)

        # Generate basic js file
        js_code = f"""// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("{d['name']}", {{
	refresh(frm) {{
	}},
}});
"""
        if not os.path.exists(js_path):
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(js_code)

        print(f"Generated DocType files for {d['name']}")

    print("All DocTypes generated successfully!")

if __name__ == "__main__":
    create_doctypes()
