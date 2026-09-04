# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt


def get_data():
	return {
		"fieldname": "estimate",
		"non_standard_fieldnames": {
			"Vehicle Job Order": "estimate",
		},
		"internal_links": {
			"Vehicle Job Order": "job_order",
			"Customer Vehicle": "vehicle",
			"Customer": "customer",
		},
		"transactions": [
			{
				"label": "Fulfillment",
				"items": ["Vehicle Job Order"],
			},
			{
				"label": "References",
				"items": ["Customer Vehicle", "Customer"],
			},
		],
	}
