import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_customer_custom_fields():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    custom_fields = {
        "Customer": [
            # Individual Fields
            {
                "fieldname": "custom_first_name",
                "label": "First Name",
                "fieldtype": "Data",
                "insert_after": "customer_type",
                "depends_on": "eval:doc.customer_type=='Individual'"
            },
            {
                "fieldname": "custom_last_name",
                "label": "Last Name",
                "fieldtype": "Data",
                "insert_after": "custom_first_name",
                "depends_on": "eval:doc.customer_type=='Individual'"
            },
            # Corporate Fields
            {
                "fieldname": "custom_business_style",
                "label": "Business Style",
                "fieldtype": "Data",
                "insert_after": "custom_last_name",
                "depends_on": "eval:doc.customer_type=='Company' || doc.customer_type=='Corporate'",
                "description": "Registered Business Name / Style for Official Receipts"
            },
            {
                "fieldname": "custom_contact_person",
                "label": "Contact Person",
                "fieldtype": "Data",
                "insert_after": "custom_business_style",
                "depends_on": "eval:doc.customer_type=='Company' || doc.customer_type=='Corporate'"
            },
            {
                "fieldname": "custom_office_no",
                "label": "Office Phone",
                "fieldtype": "Data",
                "insert_after": "custom_contact_person",
                "depends_on": "eval:doc.customer_type=='Company' || doc.customer_type=='Corporate'"
            },
            {
                "fieldname": "custom_office_fax",
                "label": "Office Fax",
                "fieldtype": "Data",
                "insert_after": "custom_office_no",
                "depends_on": "eval:doc.customer_type=='Company' || doc.customer_type=='Corporate'"
            },
            # Contact Information Section
            {
                "fieldname": "custom_contact_info_section",
                "label": "Autometrik Contact Information",
                "fieldtype": "Section Break",
                "insert_after": "custom_office_fax",
                "collapsible": 1
            },
            {
                "fieldname": "custom_mobile_no",
                "label": "Mobile Number",
                "fieldtype": "Data",
                "insert_after": "custom_contact_info_section"
            },
            {
                "fieldname": "custom_telephone_no",
                "label": "Telephone Number",
                "fieldtype": "Data",
                "insert_after": "custom_mobile_no"
            },
            {
                "fieldname": "custom_email_address",
                "label": "Email Address",
                "fieldtype": "Data",
                "options": "Email",
                "insert_after": "custom_telephone_no"
            },
            {
                "fieldname": "custom_address_text",
                "label": "Billing / Service Address",
                "fieldtype": "Small Text",
                "insert_after": "custom_email_address"
            },
            {
                "fieldname": "custom_notes",
                "label": "Customer Notes & Preferences",
                "fieldtype": "Small Text",
                "insert_after": "custom_address_text"
            },
            # Discounts & Tax Settings Section
            {
                "fieldname": "custom_discounts_tax_section",
                "label": "Automotive Discounts & Tax Settings",
                "fieldtype": "Section Break",
                "insert_after": "custom_notes",
                "collapsible": 1
            },
            {
                "fieldname": "custom_labor_discount_rate",
                "label": "Labor Discount Rate (%)",
                "fieldtype": "Percent",
                "default": "0.0",
                "insert_after": "custom_discounts_tax_section",
                "description": "Default percentage discount automatically applied to labor/services"
            },
            {
                "fieldname": "custom_product_discount_rate",
                "label": "Product Discount Rate (%)",
                "fieldtype": "Percent",
                "default": "0.0",
                "insert_after": "custom_labor_discount_rate",
                "description": "Default percentage discount automatically applied to parts/materials"
            },
            {
                "fieldname": "custom_is_vat_exempt",
                "label": "VAT Exempt",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "custom_product_discount_rate"
            },
            {
                "fieldname": "custom_is_zero_rated",
                "label": "Zero-Rated",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "custom_is_vat_exempt"
            },
            {
                "fieldname": "custom_allow_withholding_tax",
                "label": "Expanded Withholding Tax (EWT)",
                "fieldtype": "Check",
                "default": "0",
                "insert_after": "custom_is_zero_rated"
            },
            {
                "fieldname": "custom_withholding_tax_type",
                "label": "Withholding Tax Type",
                "fieldtype": "Select",
                "options": "1% (Purchases of Goods)\n2% (Purchases of Services)\n5% (Rentals / Leases)\n10% (Professional Fees)",
                "insert_after": "custom_allow_withholding_tax",
                "depends_on": "eval:doc.custom_allow_withholding_tax==1"
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    print("Customer custom fields created successfully!")

if __name__ == "__main__":
    setup_customer_custom_fields()
