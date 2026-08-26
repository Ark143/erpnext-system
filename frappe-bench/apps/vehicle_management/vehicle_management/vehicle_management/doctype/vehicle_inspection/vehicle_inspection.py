# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VehicleInspection(Document):
	def validate(self):
		self.evaluate_overall_status()

	def evaluate_overall_status(self):
		has_critical = False
		has_minor = False
		for item in self.get("items", []):
			if item.status == "Immediate Action Required":
				has_critical = True
			elif item.status == "Requires Attention":
				has_minor = True

		if has_critical:
			self.overall_status = "Critical Action Required"
		elif has_minor:
			self.overall_status = "Minor Issues"
		else:
			self.overall_status = "Passed"

	@frappe.whitelist()
	def load_template_items(self):
		if not self.inspection_template:
			return

		template = frappe.get_doc("Inspection Template", self.inspection_template)
		self.items = []
		for t_item in template.get("items", []):
			self.append("items", {
				"category": t_item.category,
				"item_name": t_item.item_name,
				"status": "Pass / OK",
				"observation": t_item.standard_description or ""
			})
