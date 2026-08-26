# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate

class VehicleJobOrder(Document):
	def validate(self):
		self.calculate_totals()
		# NOTE: vehicle info update moved to on_submit to avoid cross-document
		# writes on every draft save (was causing intermittent save errors / loops)

	def calculate_totals(self):
		total_labor = 0.0
		for row in self.get("services", []):
			hours = flt(row.hours) or 1.0
			rate = flt(row.rate)
			disc = flt(row.discount_amount)
			row.total_amount = max(0.0, (hours * rate) - disc)
			total_labor += row.total_amount
		self.total_labor = total_labor

		total_parts = 0.0
		for row in self.get("parts", []):
			qty = flt(row.qty) or 1.0
			rate = flt(row.rate)
			disc = flt(row.discount_amount)
			row.amount = max(0.0, (qty * rate) - disc)
			total_parts += row.amount
		self.total_parts = total_parts

		self.net_total = self.total_labor + self.total_parts
		overall_discount = flt(self.discount_amount)
		self.grand_total = max(0.0, self.net_total - overall_discount)

	def update_vehicle_info(self):
		if self.vehicle and self.mileage:
			veh = frappe.get_doc("Customer Vehicle", self.vehicle)
			if flt(self.mileage) > flt(veh.current_mileage):
				veh.current_mileage = self.mileage
			veh.last_service_date = self.job_order_date or nowdate()
			veh.flags.ignore_permissions = True
			veh.save()

	def on_submit(self):
		if self.status == "Draft":
			self.db_set("status", "Completed")
		# update vehicle mileage / last service date only on submit (not every save)
		self.update_vehicle_info()

	def before_cancel(self):
		# break the link to the Sales Invoice and reset payment/status so a
		# cancelled Job Order does not leave dangling/incorrect links
		if self.sales_invoice:
			self.db_set("sales_invoice", None)
		self.db_set("payment_status", "Unpaid")
		self.db_set("status", "Cancelled")
		# revert last_service_date on the vehicle if this JO set it most recently
		if self.vehicle:
			veh = frappe.get_doc("Customer Vehicle", self.vehicle)
			if veh.last_service_date and str(veh.last_service_date) == str(self.job_order_date or ""):
				prev = frappe.db.sql(
					"""SELECT MAX(job_order_date) AS d FROM "tabVehicle Job Order"
					   WHERE vehicle=%(v)s AND name!=%(n)s AND docstatus=1""",
					{"v": self.vehicle, "n": self.name}, as_dict=True)
				veh.last_service_date = prev[0].get("d") if prev and prev[0].get("d") else None
				veh.flags.ignore_permissions = True
				veh.save()

	@frappe.whitelist()
	def make_sales_invoice(self):
		if not self.customer:
			frappe.throw(_("Customer is required to create a Sales Invoice."))

		# Duplicate guard: if a Sales Invoice is already linked and still valid, reuse it
		if self.sales_invoice and frappe.db.exists("Sales Invoice", self.sales_invoice):
			si_docstatus = frappe.db.get_value("Sales Invoice", self.sales_invoice, "docstatus")
			if si_docstatus != 2:  # not cancelled
				frappe.msgprint(_("Sales Invoice {0} is already created for this Job Order.").format(
					f"<a href='/desk/sales-invoice/{self.sales_invoice}'>{self.sales_invoice}</a>"
				))
				return self.sales_invoice

		company = self.company or frappe.defaults.get_user_default("Company") or "ULTRA MRF"
		if not frappe.db.exists("Company", company):
			company = "ULTRA MRF"

		posting_date = nowdate()

		si = frappe.new_doc("Sales Invoice")
		si.company = company
		si.customer = self.customer
		si.posting_date = posting_date

		# Ensure due_date is never before posting_date
		if self.promised_date and getdate(self.promised_date) >= getdate(posting_date):
			si.due_date = getdate(self.promised_date)
		elif self.job_order_date and getdate(self.job_order_date) >= getdate(posting_date):
			si.due_date = getdate(self.job_order_date)
		else:
			si.due_date = posting_date

		# Link vehicle details to Sales Invoice
		if self.vehicle:
			si.custom_vehicle_plate = self.vehicle
		if self.mileage:
			si.custom_vehicle_mileage = self.mileage
		si.custom_vehicle_job_order = self.name

		income_account = frappe.db.get_value("Company", company, "default_income_account") or frappe.db.get_value("Account", {"company": company, "root_type": "Income", "is_group": 0}, "name")

		# Add Labor / Services
		for row in self.get("services", []):
			qty = flt(row.hours) or 1.0
			unit_rate = flt(row.rate)
			row_disc = flt(row.discount_amount)
			disc_per_unit = (row_disc / qty) if qty and row_disc else 0.0
			net_rate = max(0.0, unit_rate - disc_per_unit)
			item_dict = {
				"item_name": row.description or row.service_item or "Labor Service",
				"description": f"Service on {self.plate_no or self.vehicle or ''}: {row.description or ''}".strip(),
				"qty": qty,
				"price_list_rate": unit_rate,
				"discount_amount": disc_per_unit,
				"rate": net_rate,
			}
			if row.service_item and frappe.db.exists("Item", row.service_item):
				item_dict["item_code"] = row.service_item
			if income_account:
				item_dict["income_account"] = income_account
			si.append("items", item_dict)

		# Add Parts
		for row in self.get("parts", []):
			qty = flt(row.qty) or 1.0
			unit_rate = flt(row.rate)
			row_disc = flt(row.discount_amount)
			disc_per_unit = (row_disc / qty) if qty and row_disc else 0.0
			net_rate = max(0.0, unit_rate - disc_per_unit)
			item_dict = {
				"item_code": row.item_code if row.item_code and frappe.db.exists("Item", row.item_code) else None,
				"item_name": row.item_name or row.part_no or "Vehicle Part",
				"description": f"Part for {self.plate_no or self.vehicle or ''} (OEM: {row.part_no or 'N/A'})".strip(),
				"qty": qty,
				"price_list_rate": unit_rate,
				"discount_amount": disc_per_unit,
				"rate": net_rate,
			}
			if income_account:
				item_dict["income_account"] = income_account
			si.append("items", item_dict)

		si.set_missing_values()

		# Overall invoice additional discount
		if flt(self.discount_amount) > 0:
			si.apply_discount_on = "Grand Total"
			si.discount_amount = flt(self.discount_amount)

		si.calculate_taxes_and_totals()
		si.insert(ignore_permissions=True)

		self.db_set("sales_invoice", si.name)
		# NOTE: status "Invoiced" is set by the Sales Invoice submit hook
		# (sync_invoice_payment_to_job_order), not here, so a discarded draft
		# SI does not leave the JO falsely marked Invoiced.
		frappe.msgprint(_("Sales Invoice {0} created successfully.").format(f"<a href='/desk/sales-invoice/{si.name}'>{si.name}</a>"))
		return si.name


def sync_invoice_payment_to_job_order(doc, method=None):
	"""Hook triggered on Sales Invoice update/submit/cancel to sync linked Vehicle Job Order.
	Wired to on_update_after_submit and on_cancel in hooks.py."""
	# Skip credit/debit return documents — they would corrupt JO payment figures
	# with negative grand totals. The original SI's cancellation handles the reset.
	if getattr(doc, "is_return", 0):
		return

	jo_name = doc.get("custom_vehicle_job_order")
	if not jo_name:
		jo_name = frappe.db.get_value("Vehicle Job Order", {"sales_invoice": doc.name}, "name")

	if not jo_name or not frappe.db.exists("Vehicle Job Order", jo_name):
		return

	grand_total = flt(doc.grand_total)
	outstanding = flt(doc.outstanding_amount)
	paid = max(0.0, grand_total - outstanding)

	if doc.docstatus == 2:
		# Sales Invoice cancelled: break the link and reset the Job Order
		values_to_set = {
			"paid_amount": 0.0,
			"outstanding_amount": 0.0,
			"payment_status": "Unpaid",
			"sales_invoice": None,
			"status": "Cancelled",
		}
	else:
		if doc.docstatus == 1 and outstanding <= 0 and grand_total > 0:
			payment_status = "Paid"
			status = "Released"
		elif paid > 0:
			payment_status = "Partially Paid"
			status = "Invoiced"
		else:
			payment_status = "Unpaid"
			status = "Invoiced" if doc.docstatus == 1 else None

		values_to_set = {
			"paid_amount": paid,
			"outstanding_amount": outstanding,
			"payment_status": payment_status,
		}
		if status:
			values_to_set["status"] = status

	frappe.db.set_value("Vehicle Job Order", jo_name, values_to_set)
