# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VehicleModel(Document):
	def autoname(self):
		if not self.make or not self.model_name:
			return
		clean_make = self.make.strip().upper()
		clean_model = self.model_name.strip().upper()
		self.name = f"{clean_make}-{clean_model}"

	def validate(self):
		if not self.make or not self.model_name:
			frappe.throw(_("Both Make and Model Name are required."), title=_("Missing Fields"))

		# Normalize to clean uppercase
		self.make = self.make.strip().upper()
		self.model_name = self.model_name.strip().upper()

		# Check for existing duplicate under the same Make (case-insensitive & whitespace-trimmed)
		existing = frappe.db.sql(
			"""
			SELECT name FROM "tabVehicle Model"
			WHERE UPPER(TRIM(make)) = %s 
			  AND UPPER(TRIM(model_name)) = %s 
			  AND name != %s
			LIMIT 1
			""",
			(self.make, self.model_name, self.name or ""),
			as_dict=True,
		)

		if existing:
			frappe.throw(
				_("Vehicle Model '{0}' already exists for Make '{1}' (Existing Record: {2}). Duplicate vehicle models are not allowed.").format(
					self.model_name, self.make, existing[0]["name"]
				),
				title=_("Duplicate Vehicle Model"),
			)

		# Ensure the Make exists in Vehicle Make
		if not frappe.db.exists("Vehicle Make", self.make):
			try:
				make_doc = frappe.get_doc({
					"doctype": "Vehicle Make",
					"make_name": self.make,
					"name": self.make
				})
				make_doc.insert(ignore_permissions=True)
			except Exception:
				pass
