"""
Vehicle Management - POS API
Server-side data endpoints for the Vehicle POS web page.

The POS web page calls these whitelisted methods instead of hitting
frappe.client.get_list / frappe.db.get_value directly from the browser,
so all data access stays server-side (consistent with the dashboard_api
pattern used by the other VMS web dashboards).
"""

import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_meta():
	"""Companies + item-group categories for the POS filters."""
	companies = [
		c.name
		for c in frappe.get_all("Company", filters={"is_group": 0}, fields=["name"], order_by="name asc")
	]
	categories = [
		g.name
		for g in frappe.get_all(
			"Item Group", filters=[["Item Group", "is_group", "=", 0]], fields=["name"], order_by="name asc"
		)
	]
	return {"companies": companies, "categories": categories}


@frappe.whitelist()
def get_items(txt=None, category=None, company=None, start=0, limit=80):
	"""Search sellable items for the POS catalog grid."""
	filters = [["Item", "disabled", "=", 0], ["Item", "is_sales_item", "=", 1]]
	if category:
		filters.append(["Item", "item_group", "=", category])

	or_filters = None
	if txt:
		like = "%{}%".format(txt)
		or_filters = [
			["Item", "name", "like", like],
			["Item", "item_name", "like", like],
			["Item", "barcode", "like", like],
		]

	items = frappe.get_all(
		"Item",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "item_name", "standard_rate", "stock_uom", "item_group"],
		order_by="item_name asc",
		start=cint_safe(start),
		limit=cint_safe(limit),
	)

	out = []
	for it in items:
		out.append(
			{
				"code": it.name,
				"name": it.item_name or it.name,
				"rate": flt(it.standard_rate) or 0.0,
				"uom": it.stock_uom or "",
				"group": it.item_group or "",
			}
		)
	return out


@frappe.whitelist()
def get_customer_vehicle(vehicle):
	"""Resolve a Customer Vehicle -> its linked Customer (for auto-fill)."""
	if not vehicle:
		return {"customer": None}
	row = frappe.db.get_value(
		"Customer Vehicle", vehicle, ["customer", "customer_name", "plate_no"], as_dict=True
	)
	if not row:
		return {"customer": None}
	return {
		"customer": row.customer,
		"customer_name": row.customer_name,
		"plate_no": row.plate_no,
	}


@frappe.whitelist()
def search_vehicles(txt=None, limit=20):
	"""Autocomplete for Customer Vehicle (by plate / customer / name)."""
	or_filters = None
	if txt:
		like = "%{}%".format(txt)
		or_filters = [
			["Customer Vehicle", "name", "like", like],
			["Customer Vehicle", "plate_no", "like", like],
			["Customer Vehicle", "customer_name", "like", like],
		]
	rows = frappe.get_all(
		"Customer Vehicle",
		filters=[["Customer Vehicle", "docstatus", "!=", 2]],
		or_filters=or_filters,
		fields=["name", "plate_no", "customer", "customer_name"],
		order_by="plate_no asc",
		limit=cint_safe(limit),
	)
	return rows


@frappe.whitelist()
def get_cashier():
	"""Resolve the logged-in cashier's identity from their Employee record.

	Returns {user, email, employee, company, enabled}.
	- email / company are taken from the Employee whose user_id == session user
	  (the company "he belongs in" the Employee list).
	- Falls back to Cashier Profile company, then Global Defaults default_company.
	"""
	user = frappe.session.user
	email = user
	employee = None
	company = None
	emp = frappe.db.get_value(
		"Employee", {"user_id": user}, ["name", "employee_name", "company"], as_dict=True
	)
	if emp:
		employee = emp.get("name")
		if emp.get("company"):
			company = emp["company"]
	if not company:
		row = frappe.db.get_value("Cashier Profile", user, ["company", "enabled"], as_dict=True)
		if row and row.get("company"):
			company = row["company"]
			enabled = row.get("enabled") or 0
		else:
			company = frappe.db.get_single_value("Global Defaults", "default_company")
			enabled = 1
	else:
		# still honour Cashier Profile enabled flag if present
		row = frappe.db.get_value("Cashier Profile", user, "enabled", as_dict=True)
		enabled = (row.get("enabled") if row else 1) or 0
	return {"user": user, "email": email, "employee": employee, "company": company, "enabled": enabled}


@frappe.whitelist()
def get_history():
	"""Recent Vehicle POS Invoices created by the logged-in cashier."""
	user = frappe.session.user
	rows = frappe.get_all(
		"Vehicle POS Invoice",
		filters=[["Vehicle POS Invoice", "cashier", "=", user], ["Vehicle POS Invoice", "docstatus", "=", 1]],
		fields=["name", "posting_date", "customer_name", "vehicle", "total_amount", "paid_amount",
		        "payment_method", "company", "creation"],
		order_by="creation desc",
		limit_page_length=50,
	)
	return rows


def cint_safe(v):
	try:
		return int(v)
	except (TypeError, ValueError):
		return 0


@frappe.whitelist()
def get_stock(codes=None):
	"""Actual stock + warehouse/bin detail for a list of item codes (comma-separated).

	Returns {item_code: {"stock": <float>, "bins": [{"warehouse", "qty", "bin"}]}}.
	Stock comes from tabBin (authoritative on-hand per warehouse); bin_location from the
	latest tabStock Ledger Entry row that has one.
	"""
	if not codes:
		return {}
	result = {}
	code_list = [c.strip() for c in str(codes).split(",") if c.strip()]
	if not code_list:
		return {}
	placeholders = ", ".join(["%s"] * len(code_list))
	bins = frappe.db.sql(
		'SELECT item_code, warehouse, actual_qty FROM "tabBin" '
		"WHERE item_code IN ({}) AND actual_qty <> 0".format(placeholders),
		code_list,
		as_dict=True,
	)
	locs = frappe.db.sql(
		'SELECT item_code, warehouse, bin_location FROM "tabStock Ledger Entry" '
		"WHERE item_code IN ({}) AND bin_location IS NOT NULL AND bin_location <> %s "
		"ORDER BY creation DESC".format(placeholders),
		code_list + [""],
		as_dict=True,
	)
	binmap = {}
	for l in locs:
		key = l["item_code"] + "||" + l["warehouse"]
		if key not in binmap:
			binmap[key] = l["bin_location"]
	for b in bins:
		ic = b["item_code"]
		if ic not in result:
			result[ic] = {"stock": 0.0, "bins": []}
		qty = flt(b["actual_qty"] or 0)
		result[ic]["stock"] = result[ic]["stock"] + qty
		loc = binmap.get(ic + "||" + b["warehouse"], "")
		result[ic]["bins"].append({"warehouse": b["warehouse"], "qty": qty, "bin": loc})
	for ic in result:
		result[ic]["stock"] = round(result[ic]["stock"], 2)
	return result
