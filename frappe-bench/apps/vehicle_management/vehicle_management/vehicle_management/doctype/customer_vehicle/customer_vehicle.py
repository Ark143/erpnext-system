# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate


class CustomerVehicle(Document):
	def validate(self):
		self.update_summary_metrics()

	def update_summary_metrics(self):
		"""Update lifetime statistics for this vehicle"""
		plate = self.plate_no or self.name
		if not plate or self.is_new():
			return

		# Job Orders metrics
		job_orders = frappe.get_all(
			"Vehicle Job Order",
			filters={"vehicle": plate, "docstatus": ["!=", 2]},
			fields=["name", "job_order_date", "mileage", "grand_total", "docstatus"],
			order_by="job_order_date desc",
		)

		self.total_visits = len(job_orders)

		if job_orders:
			latest_jo = job_orders[0]
			if latest_jo.get("job_order_date"):
				self.last_service_date = latest_jo.job_order_date
			max_mileage = max([flt(jo.mileage) for jo in job_orders if jo.mileage] + [flt(self.current_mileage)])
			self.latest_odometer = max_mileage
			if max_mileage > flt(self.current_mileage):
				self.current_mileage = max_mileage

		# Sales Invoices metrics
		invoices = frappe.get_all(
			"Sales Invoice",
			filters={"custom_vehicle_plate": plate, "docstatus": 1},
			fields=["grand_total", "outstanding_amount"],
		)

		total_invoiced = sum(flt(inv.grand_total) for inv in invoices)
		total_outstanding = sum(flt(inv.outstanding_amount) for inv in invoices if flt(inv.outstanding_amount) > 0)

		self.total_spent = total_invoiced
		self.unpaid_balance = total_outstanding


@frappe.whitelist()
def get_vehicle_transaction_history(vehicle):
	"""Returns complete transactional and service history for a Customer Vehicle"""
	if not vehicle:
		return {}

	plate = frappe.db.get_value("Customer Vehicle", vehicle, "plate_no") or vehicle

	# 0. Vehicle Estimates
	estimates = frappe.get_all(
		"Vehicle Estimate",
		filters={"vehicle": plate},
		fields=[
			"name",
			"estimate_date",
			"valid_till",
			"status",
			"total_labor",
			"total_parts",
			"discount_amount",
			"grand_total",
			"job_order",
		],
		order_by="estimate_date desc, creation desc",
	)

	# 1. Job Orders
	job_orders = frappe.get_all(
		"Vehicle Job Order",
		filters={"vehicle": plate},
		fields=[
			"name",
			"job_order_date",
			"posting_time",
			"status",
			"mileage",
			"mileage_unit",
			"total_labor",
			"total_parts",
			"discount_amount",
			"grand_total",
			"payment_status",
			"paid_amount",
			"outstanding_amount",
			"sales_invoice",
			"docstatus",
		],
		order_by="job_order_date desc, creation desc",
	)

	# Attach service items to each Job Order
	for jo in job_orders:
		services = frappe.get_all(
			"Job Order Service Item",
			filters={"parent": jo.name},
			fields=["service_item", "description", "hours", "rate", "total_amount"],
		)
		parts = frappe.get_all(
			"Job Order Part Item",
			filters={"parent": jo.name},
			fields=["item_name", "qty", "uom", "rate", "amount"],
		)
		jo["services_list"] = services
		jo["parts_list"] = parts

	# 2. Sales Invoices
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"custom_vehicle_plate": plate},
		fields=[
			"name",
			"posting_date",
			"due_date",
			"grand_total",
			"outstanding_amount",
			"status",
			"custom_vehicle_job_order",
			"docstatus",
		],
		order_by="posting_date desc, creation desc",
	)

	# 3. Vehicle Inspections
	inspections = frappe.get_all(
		"Vehicle Inspection",
		filters={"vehicle": plate},
		fields=[
			"name",
			"inspection_date",
			"inspection_template",
			"mechanic",
			"mileage",
			"overall_status",
			"docstatus",
		],
		order_by="inspection_date desc, creation desc",
	)

	# 4. Quotations
	quotations = frappe.get_all(
		"Quotation",
		filters={"custom_vehicle_plate": plate},
		fields=[
			"name",
			"transaction_date",
			"valid_till",
			"grand_total",
			"status",
			"custom_vehicle_job_order",
			"docstatus",
		],
		order_by="transaction_date desc, creation desc",
	)

	# 5. Sales Orders
	sales_orders = frappe.get_all(
		"Sales Order",
		filters={"custom_vehicle_plate": plate},
		fields=[
			"name",
			"transaction_date",
			"delivery_date",
			"grand_total",
			"status",
			"per_billed",
			"per_delivered",
			"custom_vehicle_job_order",
			"docstatus",
		],
		order_by="transaction_date desc, creation desc",
	)

	# 6. Service Reminders
	service_reminders = frappe.get_all(
		"Vehicle Service Reminder",
		filters={"vehicle": plate},
		fields=[
			"name",
			"service_type",
			"due_date",
			"due_mileage",
			"lead_days",
			"status",
			"reminder_message",
		],
		order_by="due_date desc, creation desc",
	)

	# Compute Summary Totals
	total_invoiced = sum(flt(inv.grand_total) for inv in invoices if inv.docstatus == 1)
	total_outstanding = sum(flt(inv.outstanding_amount) for inv in invoices if inv.docstatus == 1 and flt(inv.outstanding_amount) > 0)
	last_visit = job_orders[0].get("job_order_date") if job_orders else None

	mileages = [flt(jo.mileage) for jo in job_orders if jo.mileage] + [flt(insp.mileage) for insp in inspections if insp.mileage]
	latest_mileage = max(mileages) if mileages else frappe.db.get_value("Customer Vehicle", vehicle, "current_mileage") or 0.0

	return {
		"summary": {
			"total_spent": total_invoiced,
			"outstanding_balance": total_outstanding,
			"total_estimates": len(estimates),
			"total_job_orders": len(job_orders),
			"total_invoices": len(invoices),
			"total_inspections": len(inspections),
			"total_quotations": len(quotations),
			"total_sales_orders": len(sales_orders),
			"total_reminders": len(service_reminders),
			"last_visit_date": str(last_visit) if last_visit else "N/A",
			"latest_mileage": latest_mileage,
		},
		"estimates": estimates,
		"job_orders": job_orders,
		"invoices": invoices,
		"inspections": inspections,
		"quotations": quotations,
		"sales_orders": sales_orders,
		"service_reminders": service_reminders,
	}
