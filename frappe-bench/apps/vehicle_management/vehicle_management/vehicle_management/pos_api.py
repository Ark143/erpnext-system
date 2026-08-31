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

	Returns the employee's company-details section fields:
	user, email, employee, employee_name, employee_number, designation,
	branch, department, reports_to (+ name), company, enabled.
	Falls back to Cashier Profile company, then Global Defaults default_company.
	"""
	user = frappe.session.user
	email = user
	out = {
		"user": user, "email": email, "employee": None, "employee_name": None,
		"employee_number": None, "designation": None, "branch": None,
		"department": None, "reports_to": None, "company": None, "enabled": 1,
	}
	emp = frappe.db.get_value(
		"Employee",
		{"user_id": user},
		["name", "employee_name", "employee_number", "designation", "branch",
		 "department", "reports_to", "company"],
		as_dict=True,
	)
	if emp:
		out["employee"] = emp.get("name")
		out["employee_name"] = emp.get("employee_name")
		out["employee_number"] = emp.get("employee_number")
		out["designation"] = emp.get("designation")
		out["branch"] = emp.get("branch")
		out["department"] = emp.get("department")
		out["reports_to"] = emp.get("reports_to")
		if emp.get("reports_to"):
			out["reports_to_name"] = frappe.db.get_value("Employee", emp["reports_to"], "employee_name")
		if emp.get("company"):
			out["company"] = emp["company"]
	if not out["company"]:
		row = frappe.db.get_value("Cashier Profile", user, ["company", "enabled"], as_dict=True)
		if row and row.get("company"):
			out["company"] = row["company"]
			out["enabled"] = row.get("enabled") or 0
		else:
			out["company"] = frappe.db.get_single_value("Global Defaults", "default_company")
			out["enabled"] = 1
	else:
		row = frappe.db.get_value("Cashier Profile", user, "enabled", as_dict=True)
		out["enabled"] = (row.get("enabled") if row else 1) or 0
	return out


@frappe.whitelist()
def get_history():
	"""Recent Vehicle POS Invoices created by the logged-in cashier (real-time)."""
	user = frappe.session.user
	rows = frappe.get_all(
		"Vehicle POS Invoice",
		filters=[["Vehicle POS Invoice", "cashier", "=", user], ["Vehicle POS Invoice", "docstatus", "=", 1]],
		fields=["name", "posting_date", "customer_name", "vehicle", "plate_no", "total_amount", "paid_amount",
		        "payment_method", "company", "pos_invoice", "creation"],
		order_by="creation desc",
		limit_page_length=200,
	)
	for r in rows:
		r["timestamp"] = _fmt_ts(r)
	return rows


def _fmt_ts(r):
	"""Human timestamp: YYYY-MM-DD HH:MM:SS from creation, fallback to posting_date."""
	c = r.get("creation") or ""
	if c:
		return str(c)[:19]
	return str(r.get("posting_date") or "")


@frappe.whitelist()
def get_receipt(name):
	"""Full receipt detail for a single Vehicle POS Invoice (for receipt printing)."""
	if not name:
		return {}
	doc = frappe.get_doc("Vehicle POS Invoice", name)
	roles = frappe.get_roles(frappe.session.user)
	if doc.cashier and doc.cashier != frappe.session.user and "System Manager" not in roles:
		frappe.throw("Not permitted", frappe.PermissionError)
	items = []
	for it in doc.get("items") or []:
		items.append({
			"item_code": it.item_code,
			"item_name": it.item_name,
			"uom": it.uom,
			"qty": flt(it.qty),
			"rate": flt(it.rate),
			"discount_amount": flt(it.discount_amount),
			"amount": flt(it.amount),
		})
	return {
		"name": doc.name,
		"posting_date": str(doc.posting_date or ""),
		"timestamp": str(doc.creation or "")[:19],
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"vehicle": doc.vehicle,
		"plate_no": doc.plate_no,
		"company": doc.company,
		"cashier": doc.cashier,
		"payment_method": doc.payment_method,
		"paid_amount": flt(doc.paid_amount),
		"total_amount": flt(doc.total_amount),
		"total_discount": flt(doc.total_discount),
		"balance_amount": flt(doc.balance_amount),
		"pos_invoice": doc.pos_invoice,
		"items": items,
	}


@frappe.whitelist()
def get_cashier_shift():
	"""Current open POS Opening Entry for the logged-in cashier (or closed)."""
	user = frappe.session.user
	e = frappe.db.get_value(
		"POS Opening Entry",
		{"user": user, "status": "Open", "docstatus": 1},
		["name", "pos_profile", "company", "period_start_date"],
		as_dict=True,
	)
	if e:
		opening_amount = 0.0
		try:
			bd = frappe.db.get_all("POS Opening Entry Detail", {"parent": e.name}, ["opening_amount"])
			opening_amount = sum(flt(x.opening_amount) for x in bd)
		except Exception:
			pass
		return {"open": True, "name": e.name, "pos_profile": e.pos_profile,
		        "company": e.company, "period_start_date": str(e.period_start_date or ""),
		        "opening_amount": opening_amount}
	return {"open": False, "name": None, "opening_amount": 0.0}


@frappe.whitelist()
def open_cashier(company=None, opening_amount=0):
	"""Open a POS Opening Entry for the logged-in cashier."""
	user = frappe.session.user
	existing = frappe.db.get_value(
		"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
	)
	if existing:
		return {"status": "already_open", "name": existing}
	if not company:
		company = (get_cashier() or {}).get("company")
	if not company:
		frappe.throw("Could not resolve a company for this cashier.")
	from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import VehiclePOSInvoice
	vpi = VehiclePOSInvoice({"doctype": "Vehicle POS Invoice"})
	pos_profile = vpi.ensure_pos_profile(company)
	cash = vpi.get_mode_of_payment("Cash", company)
	entry = frappe.get_doc({
		"doctype": "POS Opening Entry",
		"company": company,
		"pos_profile": pos_profile,
		"user": user,
		"posting_date": frappe.utils.nowdate(),
		"period_start_date": frappe.utils.now_datetime(),
		"balance_details": [{"mode_of_payment": cash, "opening_amount": flt(opening_amount)}],
	})
	entry.insert()
	entry.submit()
	frappe.db.commit()
	return {"status": "opened", "name": entry.name}


@frappe.whitelist()
def close_cashier(closing_amount=0):
	"""Close the cashier's open POS Opening Entry via a POS Closing Entry,
	recording the cashier's counted closing amount."""
	user = frappe.session.user
	opening_name = frappe.db.get_value(
		"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
	)
	if not opening_name:
		return {"status": "no_open_entry", "message": "No open POS Opening Entry found."}
	from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
	opening = frappe.get_doc("POS Opening Entry", opening_name)
	opening_amount = 0.0
	for b in opening.get("balance_details") or []:
		if (b.mode_of_payment or "").lower() == "cash":
			opening_amount = flt(b.opening_amount)
	closing = make_closing_entry_from_opening(opening)
	# record the cashier's counted cash (closing amount) on the Cash reconciliation row.
	# If there were no sales in the shift, make_closing_entry_from_opening leaves
	# payment_reconciliation empty — ensure a Cash row exists so the amount is recorded.
	rows = closing.get("payment_reconciliation") or []
	cash_rows = [r for r in rows if (r.get("mode_of_payment") or "").lower() == "cash"]
	if cash_rows:
		for r in cash_rows:
			r.opening_amount = opening_amount
			r.closing_amount = flt(closing_amount)
	else:
		closing.append("payment_reconciliation", {
			"mode_of_payment": opening.get("balance_details")[0].mode_of_payment if opening.get("balance_details") else "Cash",
			"opening_amount": opening_amount,
			"expected_amount": 0,
			"closing_amount": flt(closing_amount),
		})
	closing.insert()
	closing.submit()
	frappe.db.commit()
	return {"status": "closed", "name": closing.name}


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


@frappe.whitelist()
def vm_pos_items(txt=None, category=None, company=None):
    """POS catalog search (client calls this)."""
    return get_items(txt=txt, category=category, company=company)


@frappe.whitelist()
def vm_pos_vehicles(txt=None):
    """Customer Vehicle autocomplete (client calls this)."""
    return search_vehicles(txt=txt)


@frappe.whitelist()
def vm_pos_vehicle_customer(vehicle=None):
    """Resolve Customer Vehicle -> Customer (client calls this)."""
    return get_customer_vehicle(vehicle=vehicle)
