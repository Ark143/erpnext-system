# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt


def get_data():
	return {
		"fieldname": "vehicle",
		"non_standard_fieldnames": {
			"Sales Invoice": "custom_vehicle_plate",
			"Sales Order": "custom_vehicle_plate",
			"Quotation": "custom_vehicle_plate",
			"Delivery Note": "custom_vehicle_plate",
		},
		"transactions": [
			{
				"label": "Vehicle Operations",
				"items": ["Vehicle Estimate", "Vehicle Job Order", "Vehicle Inspection", "Vehicle Service Reminder"],
			},
			{
				"label": "Billing & Sales",
				"items": ["Sales Invoice", "Sales Order", "Quotation", "Delivery Note"],
			},
		],
	}
