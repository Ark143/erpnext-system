"""
Add Vehicle Details custom fields (tab) to transactional documents:
  - Quotation
  - Sales Order
  - Delivery Note
  - Sales Invoice

Run from frappe-bench/sites:
    ..\env\Scripts\python.exe ..\add_vehicle_fields_to_transactions.py
"""
import frappe

frappe.init("site1.local")
frappe.connect()

DOCTYPES = ["Quotation", "Sales Order", "Delivery Note", "Sales Invoice"]

# All fields to add — defined once, applied to each doctype
VEHICLE_FIELDS = [
    # ── Tab Break ────────────────────────────────────────────
    {
        "fieldname": "custom_vehicle_details_tab",
        "fieldtype": "Tab Break",
        "label": "Vehicle Details",
        "insert_after": "taxes_and_charges",
    },
    # ── Section: Vehicle Selection ────────────────────────────
    {
        "fieldname": "custom_vehicle_section",
        "fieldtype": "Section Break",
        "label": "Vehicle Selection",
    },
    {
        "fieldname": "custom_vehicle_plate",
        "fieldtype": "Link",
        "options": "Customer Vehicle",
        "label": "Vehicle Plate / Conduction Sticker",
        "in_list_view": 0,
        "search_index": 1,
    },
    {
        "fieldname": "custom_vehicle_job_order",
        "fieldtype": "Link",
        "options": "Vehicle Job Order",
        "label": "Linked Vehicle Job Order",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_col1",
        "fieldtype": "Column Break",
    },
    {
        "fieldname": "custom_vehicle_make",
        "fieldtype": "Link",
        "options": "Vehicle Make",
        "label": "Make",
        "read_only": 1,
        "fetch_from": "custom_vehicle_plate.make",
    },
    {
        "fieldname": "custom_vehicle_model",
        "fieldtype": "Link",
        "options": "Vehicle Model",
        "label": "Model",
        "read_only": 1,
        "fetch_from": "custom_vehicle_plate.model",
    },
    # ── Section: Vehicle Specifications ──────────────────────
    {
        "fieldname": "custom_vehicle_specs_section",
        "fieldtype": "Section Break",
        "label": "Vehicle Specifications",
    },
    {
        "fieldname": "custom_vehicle_year",
        "fieldtype": "Int",
        "label": "Year Model",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_color",
        "fieldtype": "Data",
        "label": "Color",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_transmission",
        "fieldtype": "Data",
        "label": "Transmission",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_fuel_type",
        "fieldtype": "Data",
        "label": "Fuel Type",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_col2",
        "fieldtype": "Column Break",
    },
    {
        "fieldname": "custom_vehicle_vin",
        "fieldtype": "Data",
        "label": "VIN / Chassis No",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_engine_no",
        "fieldtype": "Data",
        "label": "Engine No",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_mileage",
        "fieldtype": "Float",
        "label": "Odometer Reading",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_mileage_unit",
        "fieldtype": "Select",
        "options": "km\nmi",
        "label": "Mileage Unit",
        "default": "km",
        "read_only": 1,
    },
    # ── Section: Registration & Insurance ────────────────────
    {
        "fieldname": "custom_vehicle_reg_section",
        "fieldtype": "Section Break",
        "label": "Registration & Insurance",
    },
    {
        "fieldname": "custom_vehicle_registration_type",
        "fieldtype": "Data",
        "label": "Registration Type",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_col3",
        "fieldtype": "Column Break",
    },
    {
        "fieldname": "custom_vehicle_insurance_company",
        "fieldtype": "Data",
        "label": "Insurance Provider",
        "read_only": 1,
    },
    {
        "fieldname": "custom_vehicle_insurance_expiry",
        "fieldtype": "Date",
        "label": "Insurance Expiry Date",
        "read_only": 1,
    },
    # ── Section: Notes ────────────────────────────────────────
    {
        "fieldname": "custom_vehicle_notes_section",
        "fieldtype": "Section Break",
        "label": "Vehicle Notes",
    },
    {
        "fieldname": "custom_vehicle_notes",
        "fieldtype": "Small Text",
        "label": "Vehicle Notes / Special Instructions",
        "read_only": 1,
    },
]


def add_vehicle_fields(doctype):
    print(f"\n  Processing: {doctype}")
    created = 0
    skipped = 0

    for field_def in VEHICLE_FIELDS:
        fieldname = field_def["fieldname"]

        # Check if already exists
        if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
            skipped += 1
            continue

        cf = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": doctype,
            **field_def,
        })
        cf.insert(ignore_permissions=True)
        created += 1

    frappe.db.commit()
    print(f"    Created: {created}, Skipped: {skipped}")


def main():
    print("=== Adding Vehicle Details Tab to Transactional Documents ===")

    for doctype in DOCTYPES:
        add_vehicle_fields(doctype)

    print("\n=== Done! ===")
    print("Run: bench build --app vehicle_management")
    print("Then clear browser cache and reload.")


if __name__ == "__main__":
    main()
