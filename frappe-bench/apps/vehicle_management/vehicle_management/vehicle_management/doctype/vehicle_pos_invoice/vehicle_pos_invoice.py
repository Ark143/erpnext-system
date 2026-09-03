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
		raw_linked = frappe.db.get_value("Customer Vehicle", self.vehicle, "customer")
		linked_customer = resolve_customer(raw_linked)
		self.customer = resolve_customer(self.customer)
		if not linked_customer:
			frappe.throw(_("Selected Customer Vehicle has no linked Customer."))
		if self.customer and self.customer != linked_customer:
			if " ".join(str(self.customer).split()).lower() != " ".join(str(linked_customer).split()).lower():
				frappe.throw(
					_("Customer {0} does not match the owner of Customer Vehicle {1} ({2}).").format(
						self.customer, self.vehicle, linked_customer
					)
				)
		# Always sync the resolved customer
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

		plate = frappe.db.get_value("Customer Vehicle", self.vehicle, "plate_no") if self.vehicle else ""

		inv = frappe.get_doc(
			{
				"doctype": "POS Invoice",
				"naming_series": "ACC-PSINV-.YYYY.-",
				"company": company,
				"customer": self.customer,
				"posting_date": getdate(self.posting_date) or nowdate(),
				"pos_profile": pos_profile,
				"items": items,
				"payments": [
					{
						"mode_of_payment": mop,
						"amount": flt(self.paid_amount),
					}
				],
				"vehicle_pos_invoice": self.name,
				"custom_vehicle_pos_invoice": self.name,
				"custom_customer_vehicle": self.vehicle or "",
				"custom_plate_no": plate or "",
				"remarks": self.remarks or f"Vehicle POS Invoice: {self.name}",
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
		"""Reuse an already-open POS Opening Entry for this user/company/pos_profile, else create one."""
		user = frappe.session.user
		existing = frappe.get_value(
			"POS Opening Entry",
			{"user": user, "company": company, "pos_profile": pos_profile, "status": "Open", "docstatus": 1},
			["name", "pos_profile"], as_dict=True,
		)
		if existing:
			return existing["name"]

		# Close any other open shift for this user before opening the new company profile
		other_open = frappe.get_all(
			"POS Opening Entry",
			filters={"user": user, "status": "Open", "docstatus": 1},
			fields=["name"]
		)
		for o in other_open:
			frappe.db.set_value("POS Opening Entry", o.name, "status", "Closed", update_modified=False)

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
def get_mode_of_payment(method, company):
	"""Map a Vehicle POS payment method to an existing Mode of Payment."""
	mapping = {
		"Cash": "Cash",
		"Card": "Credit Card",
		"Credit Card": "Credit Card",
		"Debit Card": "Credit Card",
		"GCash": "Cash",
		"Maya": "Cash",
		"BDO": "Wire Transfer",
		"Bank Transfer": "Wire Transfer",
		"Cheque": "Bank Draft",
		"Check": "Check",
	}
	mop = mapping.get(method, "Cash")
	if not frappe.db.exists("Mode of Payment", mop):
		mop = frappe.db.get_value("Mode of Payment", {"type": "Cash"}, "name") or "Cash"
	if not frappe.db.exists("Mode of Payment", mop):
		frappe.throw(_("Mode of Payment '{0}' is not configured.").format(mop))
	return mop


def get_pos_profile(company):
	return frappe.db.get_value(
		"POS Profile", {"company": company, "disabled": 0}, "name"
	) or frappe.db.get_value("POS Profile", {"company": company}, "name")


def ensure_pos_profile(company):
	"""Create a default POS Profile for the company if none exists."""
	profile_name = get_pos_profile(company)
	if profile_name:
		return profile_name

	default_warehouse = (
		frappe.db.get_value("Company", company, "default_fg_warehouse")
		or frappe.db.get_value("Company", company, "default_in_transit_warehouse")
		or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
	)
	if not default_warehouse:
		frappe.throw(_("Please set a default warehouse for company {0}.").format(company))

	cash = get_mode_of_payment("Cash", company)
	income_account = frappe.db.get_value("Company", company, "default_income_account")
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


def ensure_pos_opening_entry(company, pos_profile):
	"""Reuse an already-open POS Opening Entry for this user/company/pos_profile, else create one."""
	user = frappe.session.user
	existing = frappe.get_value(
		"POS Opening Entry",
		{"user": user, "company": company, "pos_profile": pos_profile, "status": "Open", "docstatus": 1},
		["name", "pos_profile"], as_dict=True,
	)
	if existing:
		return existing["name"]

	other_open = frappe.get_all(
		"POS Opening Entry",
		filters={"user": user, "status": "Open", "docstatus": 1},
		fields=["name"]
	)
	for o in other_open:
		frappe.db.set_value("POS Opening Entry", o.name, "status", "Closed", update_modified=False)

	cash = get_mode_of_payment("Cash", company)
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


def resolve_customer(cust):
	"""Resolve customer name even if whitespace or casing varies between Customer and Vehicle."""
	if not cust:
		return cust
	cust_str = str(cust).strip()
	if frappe.db.exists("Customer", cust_str):
		return cust_str
	normalized = " ".join(cust_str.split())
	if frappe.db.exists("Customer", normalized):
		return normalized
	match = frappe.db.get_value("Customer", {"customer_name": normalized}, "name")
	if match:
		return match
	like = "%" + normalized.replace(" ", "%") + "%"
	m = frappe.get_all("Customer", filters={"name": ["like", like]}, limit=1)
	if m:
		return m[0].name
	return normalized


@frappe.whitelist()
def create_from_pos(data):
	"""Create and submit an official ERPNext POS Invoice directly from POS terminal."""
	import json as _json

	if isinstance(data, str):
		data = _json.loads(data)

	cust = resolve_customer(data.get("customer"))
	veh = data.get("vehicle")
	plate = ""
	if veh and frappe.db.exists("Customer Vehicle", veh):
		veh_row = frappe.db.get_value("Customer Vehicle", veh, ["customer", "plate_no"], as_dict=True)
		if veh_row:
			if veh_row.get("customer"):
				cust = resolve_customer(veh_row["customer"])
			plate = veh_row.get("plate_no") or ""
	data["customer"] = cust

	company = data.get("company") or frappe.defaults.get_user_default("Company")
	pos_profile = ensure_pos_profile(company)
	ensure_pos_opening_entry(company, pos_profile)

	items = [
		{
			"item_code": it.get("item_code"),
			"qty": flt(it.get("qty")),
			"rate": flt(it.get("rate")),
			"discount_amount": flt(it.get("discount_amount")),
			"uom": it.get("uom"),
		}
		for it in (data.get("items") or [])
	]

	method = data.get("payment_method") or "Cash"
	mop = get_mode_of_payment(method, company)
	paid_amount = flt(data.get("paid_amount"))
	remarks = (data.get("remarks") or data.get("notes") or "").strip()

	inv = frappe.get_doc(
		{
			"doctype": "POS Invoice",
			"naming_series": "ACC-PSINV-.YYYY.-",
			"company": company,
			"customer": cust,
			"posting_date": frappe.utils.nowdate(),
			"pos_profile": pos_profile,
			"items": items,
			"payments": [
				{
					"mode_of_payment": mop,
					"amount": paid_amount,
				}
			],
			"custom_customer_vehicle": veh or "",
			"custom_plate_no": plate,
			"remarks": remarks,
		}
	)
	inv.insert()
	inv.submit()
	return {"name": inv.name, "pos_invoice": inv.name}
