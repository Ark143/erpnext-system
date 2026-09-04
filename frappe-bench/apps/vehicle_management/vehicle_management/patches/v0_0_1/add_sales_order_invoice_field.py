import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	"""
	Ensure Sales Order has sales_invoice custom field on PostgreSQL to prevent
	dashboard link query crashes.
	"""
	custom_fields = {
		"Sales Order": [
			{
				"fieldname": "sales_invoice",
				"label": "Sales Invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"hidden": 1,
				"read_only": 1,
				"insert_after": "naming_series"
			}
		]
	}
	create_custom_fields(custom_fields, ignore_validate=True)
