# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BinLocation(Document):
	def validate(self):
		if not self.company and self.warehouse:
			self.company = frappe.db.get_value("Warehouse", self.warehouse, "company")
