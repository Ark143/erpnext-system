# Copyright (c) 2026, Vehicle Management and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate


class VehiclePOSInvoice(Document):
	"""Vehicle POS Invoice.

	On submit this doctype posts a proper ERPNext POS Invoice so that
	accounting ledger entries, stock consumption and payments are handled
	correctly. This keeps the Vehicle Management POS in sync with the
	Financials module.
	"""

	def validate(self):
		self.calculate_totals()
		self.validate_payment()
		self.validate_vehicle_customer()

	def validate_vehicle_customer(self):
		"""The Customer must be the owner linked to the selected Customer Vehicle."""
		if not self.vehicle:
			return
		linked_customer = frappe.db.get_value("Customer Vehicle", self.vehicle, "customer")
		if linked_customer:
			linked_customer = " ".join(str(linked_customer).split())
		if self.customer:
			self.customer = " ".join(str(self.customer).split())
		if not linked_customer:
			frappe.throw(_("Selected Customer Vehicle has no linked Customer."))
		if self.customer and self.customer != linked_customer:
			frappe.throw(
				_("Customer {0} does not match the owner of Customer Vehicle {1} ({2}).").format(
					self.customer, self.vehicle, linked_customer
				)
			)
		# Always sync the correct owner from the vehicle.
		self.customer = linked_customer

	def before_save(self):
		self.calculate_totals()

	def calculate_totals(self):
		total_qty = 0.0
		total_amount = 0.0
		total_discount = 0.0
		for row in self.get("items") or []:
			qty = flt(row.qty) or 0.0
			rate = flt(row.rate) or 0.0
			disc_amt = flt(row.discount_amount) or 0.0
			row.amount = flt(qty * rate) - disc_amt
			total_qty += qty
			total_amount += flt(row.amount)
			total_discount += disc_amt
		self.total_qty = total_qty
		self.total_amount = total_amount
		self.total_discount = total_discount
		paid = flt(self.paid_amount) or 0.0
		self.balance_amount = flt(paid - total_amount)

	def validate_payment(self):
		if not self.items:
			frappe.throw(_("Please add at least one item to the POS invoice."))
		if flt(self.paid_amount) <= 0:
			frappe.throw(_("Paid Amount must be greater than zero."))
		if flt(self.paid_amount) < flt(self.total_amount):
			frappe.throw(_("Paid Amount cannot be less than Total Amount."))

	def on_submit(self):
		self.create_erpnext_pos_invoice()

	def on_cancel(self):
		if self.pos_invoice:
			try:
				inv = frappe.get_doc("POS Invoice", self.pos_invoice)
				if inv.docstatus == 1:
					inv.cancel()
			except Exception:
				frappe.log_error(frappe.get_traceback(), "Vehicle POS Invoice cancel")

	def create_erpnext_pos_invoice(self):
		if self.pos_invoice:
			return

		company = self.company or frappe.defaults.get_user_default("Company")
		# Reuse an already-open POS Opening Entry for this user (its profile/company
		# must match the POS Invoice we are about to create).
		existing = frappe.get_value(
			"POS Opening Entry",
			{"user": frappe.session.user, "status": "Open", "docstatus": 1},
			["pos_profile", "company"], as_dict=True,
		)
		if existing:
			pos_profile = existing["pos_profile"]
			if existing["company"]:
				company = existing["company"]
		else:
			pos_profile = self.ensure_pos_profile(company)
		self.ensure_pos_opening_entry(company, pos_profile)

		items = []
		for row in self.items:
			items.append(
				{
					"item_code": row.item_code,
					"qty": flt(row.qty),
					"rate": flt(row.rate),
					"discount_amount": flt(row.discount_amount),
					"uom": row.uom,
				}
			)

		mop = self.get_mode_of_payment(self.payment_method, company)

		inv = frappe.get_doc(
			{
				"doctype": "POS Invoice",
				"naming_series": "ACC-PSINV-.YYYY.-",
				"company": company,
				"customer": self.customer,
				"posting_date": getdate(self.posting_date) or nowdate(),
				"pos_profile": self.get_pos_profile(company),
				"items": items,
				"payments": [
					{
						"mode_of_payment": mop,
						"amount": flt(self.paid_amount),
					}
				],
				"vehicle_pos_invoice": self.name,
			}
		)
		inv.insert()
		inv.submit()
		self.db_set("pos_invoice", inv.name)
		frappe.msgprint(_("POS Invoice {0} created.").format(inv.name))

	def ensure_pos_profile(self, company):
		"""Create a default POS Profile for the company if none exists."""
		profile = self.get_pos_profile(company)
		if profile:
			return profile

		default_warehouse = (
			frappe.db.get_value("Company", company, "default_fg_warehouse")
			or frappe.db.get_value("Company", company, "default_in_transit_warehouse")
			or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
		)
		if not default_warehouse:
			frappe.throw(_("Please set a default warehouse for company {0}.").format(company))

		cash = self.get_mode_of_payment("Cash", company)
		income_account = frappe.db.get_value(
			"Company", company, "default_income_account"
		)
		if not income_account:
			frappe.throw(_("Please set a default income account for company {0}.").format(company))

		cost_center = (
			frappe.db.get_value("Company", company, "cost_center")
			or frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
		)
		if not cost_center:
			frappe.throw(_("Please set a Cost Center for company {0}.").format(company))

		profile_name = f"Vehicle POS - {company}"
		if frappe.db.exists("POS Profile", profile_name):
			return profile_name
		doc = frappe.get_doc(
			{
				"doctype": "POS Profile",
				"name": profile_name,
				"pos_profile_name": profile_name,
				"company": company,
				"warehouse": default_warehouse,
				"currency": frappe.db.get_value("Company", company, "default_currency") or "PHP",
				"income_account": income_account,
				"cost_center": cost_center,
				"payments": [{"default": 1, "mode_of_payment": cash}],
				"write_off_account": income_account,
				"write_off_cost_center": cost_center,
			}
		)
		doc.insert()
		return profile_name

	def ensure_pos_opening_entry(self, company, pos_profile):
		"""Reuse an already-open POS Opening Entry for the current user, else create one.
		Frappe blocks a 2nd open entry for the same user
		("Cashier is currently assigned to another POS") and the POS Invoice
		validation requires an open entry for the *specific* POS Profile
		("No open POS Opening Entry found"). We therefore REUSE any open entry for
		this user (do NOT cancel it -- cancelling can be blocked by unconsolidated
		invoices). The matching pos_profile/company is taken from that open entry
		by the caller so the POS Invoice validation stays consistent."""
		user = frappe.session.user
		existing = frappe.get_value(
			"POS Opening Entry",
			{"user": user, "status": "Open", "docstatus": 1},
			["name", "pos_profile"], as_dict=True,
		)
		if existing:
			return existing["name"]

		cash = self.get_mode_of_payment("Cash", company)
		entry = frappe.get_doc(
			{
				"doctype": "POS Opening Entry",
				"company": company,
				"pos_profile": pos_profile,
				"user": user,
				"posting_date": frappe.utils.nowdate(),
				"period_start_date": frappe.utils.now_datetime(),
				"balance_details": [{"mode_of_payment": cash, "opening_amount": 0}],
			}
		)
		entry.insert()
		entry.submit()
		frappe.db.commit()
		return entry.name

	def get_pos_profile(self, company):
		return frappe.db.get_value(
			"POS Profile", {"company": company, "disabled": 0}, "name"
		) or frappe.db.get_value("POS Profile", {"company": company}, "name")

	def get_mode_of_payment(self, method, company):
		"""Map a Vehicle POS payment method to an existing Mode of Payment."""
		mapping = {
			"Cash": "Cash",
			"Bank Transfer": "Wire Transfer",
			"Credit Card": "Credit Card",
			"GCash": "Cash",
			"Maya": "Cash",
			"Cheque": "Bank Draft",
		}
		mop = mapping.get(method, "Cash")
		if not frappe.db.exists("Mode of Payment", mop):
			mop = frappe.db.get_value("Mode of Payment", {"type": "Cash"}, "name") or "Cash"
		if not frappe.db.exists("Mode of Payment", mop):
			frappe.throw(_("Mode of Payment '{0}' is not configured.").format(mop))
		return mop


@frappe.whitelist()
def create_from_pos(data):
	"""Create and submit a Vehicle POS Invoice from the POS page."""
	import json as _json

	if isinstance(data, str):
		data = _json.loads(data)

	# normalize customer (collapse extra spaces, fuzzy-match if needed)
	cust = data.get("customer")
	if cust:
		cust = " ".join(str(cust).split())
		if not frappe.db.exists("Customer", cust):
			like = "%" + cust.replace(" ", "%") + "%"
			m = frappe.get_all("Customer", filters={"name": ["like", like]}, limit=1)
			if m:
				cust = m[0].name
		data["customer"] = cust
	# If a Customer Vehicle is provided, always use its real owning customer so the
	# Vehicle POS Invoice validation (customer must own the vehicle) never fails.
	veh = data.get("vehicle")
	if veh and frappe.db.exists("Customer Vehicle", veh):
		_vc = frappe.db.get_value("Customer Vehicle", veh, "customer")
		if _vc:
			cust = _vc
			data["customer"] = cust

	doc = frappe.get_doc(
		{
			"doctype": "Vehicle POS Invoice",
			"naming_series": "VMSPOS-.YYYY.-.#####",
			"customer": data.get("customer"),
			"vehicle": data.get("vehicle"),
			"company": data.get("company"),
			"paid_amount": flt(data.get("paid_amount")),
			"payment_method": data.get("payment_method") or "Cash",
			"cashier": frappe.session.user,
			"items": [
				{
					"item_code": it.get("item_code"),
					"qty": flt(it.get("qty")),
					"rate": flt(it.get("rate")),
					"discount_amount": flt(it.get("discount_amount")),
					"uom": it.get("uom"),
				}
				for it in (data.get("items") or [])
			],
		}
	)
	doc.insert()
	doc.submit()
	if flt(doc.paid_amount) >= flt(doc.total_amount):
		doc.db_set("status", "Paid")
	else:
		doc.db_set("status", "Unpaid")
	return {"name": doc.name, "pos_invoice": doc.pos_invoice}
