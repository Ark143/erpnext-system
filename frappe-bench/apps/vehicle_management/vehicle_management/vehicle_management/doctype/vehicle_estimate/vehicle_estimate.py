# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, now_datetime


class VehicleEstimate(Document):
	def validate(self):
		self.calculate_totals()
		self.fetch_vehicle_and_customer_details()

	def before_cancel(self):
		# If this Estimate was converted to a Job Order that is now itself
		# cancelled (or gone), clear the stale link and reset status.
		if self.job_order:
			jo_exists = frappe.db.exists("Vehicle Job Order", self.job_order)
			jo_cancelled = False
			if jo_exists:
				jo_cancelled = frappe.db.get_value("Vehicle Job Order", self.job_order, "docstatus") == 2
			if (not jo_exists) or jo_cancelled:
				self.db_set("job_order", None)
				self.db_set("status", "Draft")

	def calculate_totals(self):
		total_labor = 0.0
		for item in self.get("services", []):
			hours = flt(item.hours) or 1.0
			rate = flt(item.rate)
			disc = flt(item.discount_amount)
			item.total_amount = max(0.0, (hours * rate) - disc)
			total_labor += item.total_amount

		total_parts = 0.0
		for item in self.get("parts", []):
			qty = flt(item.qty) or 1.0
			rate = flt(item.rate)
			disc = flt(item.discount_amount)
			item.amount = max(0.0, (qty * rate) - disc)
			total_parts += item.amount

		self.total_labor = total_labor
		self.total_parts = total_parts
		self.net_total = total_labor + total_parts
		self.grand_total = max(0.0, self.net_total - flt(self.discount_amount))

	def fetch_vehicle_and_customer_details(self):
		if self.vehicle and not self.plate_no:
			veh = frappe.get_cached_doc("Customer Vehicle", self.vehicle)
			self.plate_no = veh.plate_no
			self.make = veh.make
			self.model = veh.model
			self.year_model = veh.year_model
			self.vin = veh.vin
			self.engine_no = veh.engine_no
			self.color = veh.color
			if not self.mileage:
				self.mileage = veh.current_mileage
				self.mileage_unit = veh.mileage_unit or "km"

	@frappe.whitelist()
	def make_job_order(self):
		"""Convert this Estimate into a Vehicle Job Order"""
		if self.job_order and frappe.db.exists("Vehicle Job Order", self.job_order):
			frappe.msgprint(_("Job Order {0} is already created for this Estimate.").format(
				f"<a href='/desk/vehicle-job-order/{self.job_order}'>{self.job_order}</a>"
			))
			return self.job_order

		jo = frappe.new_doc("Vehicle Job Order")
		jo.company = self.company
		jo.job_order_date = nowdate()
		jo.time_in = now_datetime()
		jo.customer = self.customer
		jo.customer_name = self.customer_name
		jo.contact_no = self.contact_no
		jo.vehicle = self.vehicle
		jo.plate_no = self.plate_no
		jo.make = self.make
		jo.model = self.model
		jo.year_model = self.year_model
		jo.vin = self.vin
		jo.engine_no = self.engine_no
		jo.color = self.color
		jo.mileage = self.mileage
		jo.mileage_unit = self.mileage_unit or "km"
		jo.service_advisor = self.service_advisor
		jo.customer_complaint = self.customer_complaint
		jo.estimate = self.name
		jo.discount_amount = flt(self.discount_amount)
		jo.remarks = f"Created from Estimate {self.name}"

		# Copy Services
		for s in self.get("services", []):
			jo.append("services", {
				"service_item": s.service_item,
				"description": s.description,
				"mechanic": s.mechanic,
				"hours": s.hours,
				"rate": s.rate,
				"discount_amount": s.discount_amount,
				"total_amount": s.total_amount,
			})

		# Copy Parts
		for p in self.get("parts", []):
			jo.append("parts", {
				"item_code": p.item_code,
				"item_name": p.item_name,
				"part_no": p.part_no,
				"qty": p.qty,
				"uom": p.uom,
				"rate": p.rate,
				"discount_amount": p.discount_amount,
				"amount": p.amount,
			})

		jo.insert(ignore_permissions=True)

		self.db_set("job_order", jo.name)
		self.db_set("status", "Converted to Job Order")

		frappe.msgprint(_("Vehicle Job Order {0} created successfully.").format(
			f"<a href='/desk/vehicle-job-order/{jo.name}'>{jo.name}</a>"
		))
		return jo.name
