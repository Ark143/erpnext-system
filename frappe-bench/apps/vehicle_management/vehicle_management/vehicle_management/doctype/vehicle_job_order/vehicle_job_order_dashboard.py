# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt


def get_data():
	return {
		"fieldname": "custom_vehicle_job_order",
		"non_standard_fieldnames": {
			"Vehicle Estimate": "job_order",
			"Sales Invoice": "custom_vehicle_job_order",
			"Sales Order": "custom_vehicle_job_order",
			"Quotation": "custom_vehicle_job_order",
		},
		"internal_links": {
			"Vehicle Estimate": "estimate",
			"Customer Vehicle": "vehicle",
			"Customer": "customer",
		},
		"transactions": [
			{
				"label": "Origin",
				"items": ["Vehicle Estimate"],
			},
			{
				"label": "Billing & Invoicing",
				"items": ["Sales Invoice", "Sales Order", "Quotation"],
			},
			{
				"label": "References",
				"items": ["Customer Vehicle", "Customer"],
			},
		],
	}
