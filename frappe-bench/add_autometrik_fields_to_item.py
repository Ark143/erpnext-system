import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_item_custom_fields():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    custom_fields = {
        "Item": [
            {
                "fieldname": "custom_print_display_name",
                "label": "Print Display Name",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "description": "Alternate product name printed on estimates, job orders, and invoices"
            },
            {
                "fieldname": "custom_part_no",
                "label": "Part Number",
                "fieldtype": "Data",
                "insert_after": "custom_print_display_name",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "description": "Internal or industry part number / barcode"
            },
            {
                "fieldname": "custom_manufacturer_no",
                "label": "Manufacturer / OEM Part No",
                "fieldtype": "Data",
                "insert_after": "custom_part_no",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "description": "OEM Original Equipment Manufacturer Part Number"
            },
            {
                "fieldname": "custom_product_category",
                "label": "Automotive Category",
                "fieldtype": "Select",
                "options": "\nEngine Compartment\nBrake System\nSuspension & Steering\nTransmission & Drivetrain\nElectrical & Battery\nFilters & Lubricants\nCooling & Heating\nExhaust & Fuel System\nTires & Wheels\nBody & Exterior\nInterior & Accessories\nTools & Equipment\nLabor & Services",
                "insert_after": "custom_manufacturer_no",
                "in_standard_filter": 1
            },
            {
                "fieldname": "custom_color",
                "label": "Color / Finish",
                "fieldtype": "Data",
                "insert_after": "custom_product_category"
            },
            {
                "fieldname": "custom_expiry_date",
                "label": "Expiry Date",
                "fieldtype": "Date",
                "insert_after": "custom_color"
            },
            {
                "fieldname": "custom_incentive",
                "label": "Technician / Sales Incentive",
                "fieldtype": "Currency",
                "insert_after": "custom_expiry_date"
            },
            {
                "fieldname": "custom_allow_zero_value",
                "label": "Allow Zero Value",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "custom_incentive"
            },
            # Storage & Physical Location
            {
                "fieldname": "custom_storage_section",
                "label": "Storage & Physical Location",
                "fieldtype": "Section Break",
                "insert_after": "custom_allow_zero_value",
                "collapsible": 1
            },
            {
                "fieldname": "custom_rack",
                "label": "Rack",
                "fieldtype": "Data",
                "insert_after": "custom_storage_section"
            },
            {
                "fieldname": "custom_shelf",
                "label": "Shelf",
                "fieldtype": "Data",
                "insert_after": "custom_rack"
            },
            {
                "fieldname": "custom_bin_location",
                "label": "Bin Location",
                "fieldtype": "Data",
                "insert_after": "custom_shelf"
            },
            {
                "fieldname": "custom_order_multiple",
                "label": "Order Multiple",
                "fieldtype": "Float",
                "default": "1.0",
                "insert_after": "custom_bin_location"
            },
            # Pricing & Margin Calculation
            {
                "fieldname": "custom_pricing_section",
                "label": "Autometrik Pricing & Margins",
                "fieldtype": "Section Break",
                "insert_after": "custom_order_multiple",
                "collapsible": 1
            },
            {
                "fieldname": "custom_purchase_cost",
                "label": "Purchase Cost",
                "fieldtype": "Currency",
                "insert_after": "custom_pricing_section"
            },
            {
                "fieldname": "custom_pricing_rule",
                "label": "Product Pricing Rule",
                "fieldtype": "Select",
                "options": "MARK-UP 50%\nMARK-UP 30%\nMARK-UP 20%\nMARK-UP 15%\nCOST PLUS\nFIXED PRICE",
                "default": "MARK-UP 50%",
                "insert_after": "custom_purchase_cost"
            },
            {
                "fieldname": "custom_markup_rate",
                "label": "Markup Rate (%)",
                "fieldtype": "Percent",
                "default": "50.0",
                "insert_after": "custom_pricing_rule"
            },
            {
                "fieldname": "custom_sell_price",
                "label": "Calculated Selling Price",
                "fieldtype": "Currency",
                "insert_after": "custom_markup_rate"
            },
            {
                "fieldname": "custom_margin_percent",
                "label": "Profit Margin (%)",
                "fieldtype": "Percent",
                "read_only": 1,
                "insert_after": "custom_sell_price"
            },
            # Vehicle Fitment Table
            {
                "fieldname": "custom_vehicle_compatibility_section",
                "label": "Vehicle Compatibility / Fitment",
                "fieldtype": "Section Break",
                "insert_after": "custom_margin_percent",
                "collapsible": 1
            },
            {
                "fieldname": "custom_vehicle_compatibility",
                "label": "Compatible Vehicles",
                "fieldtype": "Table",
                "options": "Item Vehicle Compatibility",
                "insert_after": "custom_vehicle_compatibility_section"
            },
            # Cross-Reference Interchange Table
            {
                "fieldname": "custom_cross_reference_section",
                "label": "Cross-Reference & Interchange Parts",
                "fieldtype": "Section Break",
                "insert_after": "custom_vehicle_compatibility",
                "collapsible": 1
            },
            {
                "fieldname": "custom_part_cross_references",
                "label": "Cross-Reference Parts",
                "fieldtype": "Table",
                "options": "Item Part Cross Reference",
                "insert_after": "custom_cross_reference_section"
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    print("Item custom fields created successfully!")

if __name__ == "__main__":
    setup_item_custom_fields()
