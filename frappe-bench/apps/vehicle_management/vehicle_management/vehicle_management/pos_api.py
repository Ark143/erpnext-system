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
def get_items(txt=None, category=None, company=None, only_stock=0, start=0, limit=80):
	"""Search sellable items for the POS catalog grid, with optional in-stock filter."""
	only_stock = cint_safe(only_stock)
	where_clauses = ["i.disabled = 0", "i.is_sales_item = 1"]
	params = []

	if category:
		where_clauses.append("i.item_group = %s")
		params.append(category)

	if txt:
		like = "%{}%".format(txt)
		where_clauses.append("(i.name LIKE %s OR i.item_name LIKE %s OR i.barcode LIKE %s)")
		params.extend([like, like, like])

	wh_join = ""
	if company:
		wh_join = 'JOIN "tabWarehouse" w ON w.name = b.warehouse AND w.company = %s'
		params.append(company)

	if only_stock:
		sql = f"""
			SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
			       i.stock_uom as uom, i.item_group as `group`, i.image as image,
			       COALESCE(SUM(b.actual_qty), 0) as stock
			FROM "tabItem" i
			JOIN "tabBin" b ON b.item_code = i.name AND b.actual_qty > 0
			{wh_join}
			WHERE {" AND ".join(where_clauses)}
			GROUP BY i.name, i.item_name, i.standard_rate, i.stock_uom, i.item_group, i.image
			HAVING SUM(b.actual_qty) > 0
			ORDER BY stock DESC, i.item_name ASC
			LIMIT {cint_safe(limit)} OFFSET {cint_safe(start)}
		"""
		rows = frappe.db.sql(sql, tuple(params), as_dict=True)
		for r in rows:
			r["stock"] = round(flt(r["stock"]), 2)
			r["rate"] = round(flt(r["rate"]), 2)
		return rows

	sql = f"""
		SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
		       i.stock_uom as uom, i.item_group as `group`, i.image as image,
		       COALESCE((
		           SELECT SUM(b.actual_qty) FROM "tabBin" b 
		           WHERE b.item_code = i.name AND b.actual_qty > 0
		       ), 0) as stock
		FROM "tabItem" i
		WHERE {" AND ".join(where_clauses)}
		ORDER BY i.item_name ASC
		LIMIT {cint_safe(limit)} OFFSET {cint_safe(start)}
	"""
	rows = frappe.db.sql(sql, tuple(params), as_dict=True)
	for r in rows:
		r["stock"] = round(flt(r["stock"]), 2)
		r["rate"] = round(flt(r["rate"]), 2)
	return rows


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
def get_history(period=None, from_date=None, to_date=None, company=None, search=None):
	"""Recent standard ERPNext POS Invoices (ACC-PSINV-...) with real-time filters."""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_manager = "System Manager" in roles or "Accounts Manager" in roles or user == "Administrator"

	filters = [["docstatus", "<", 2]]

	# If not manager, restrict to cashier or cashier's company
	if not is_manager:
		cashier_company = frappe.db.get_value("Employee", {"user_id": user}, "company") or frappe.db.get_value("Cashier Profile", user, "company")
		if cashier_company:
			filters.append(["company", "=", cashier_company])
		else:
			filters.append(["owner", "=", user])
	elif company:
		filters.append(["company", "=", company])

	# Date filtering
	today_str = frappe.utils.today()
	if period == "today":
		filters.append(["posting_date", "=", today_str])
	elif period == "month":
		import datetime
		now = datetime.date.today()
		first_day = now.replace(day=1).strftime("%Y-%m-%d")
		filters.append(["posting_date", ">=", first_day])
		filters.append(["posting_date", "<=", today_str])
	elif from_date or to_date:
		if from_date:
			filters.append(["posting_date", ">=", from_date])
		if to_date:
			filters.append(["posting_date", "<=", to_date])

	or_filters = None
	if search:
		like = f"%{search.strip()}%"
		or_filters = [
			["name", "like", like],
			["customer_name", "like", like],
			["custom_plate_no", "like", like],
			["custom_customer_vehicle", "like", like],
		]

	rows = frappe.get_all(
		"POS Invoice",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "posting_date", "customer_name", "custom_customer_vehicle as vehicle",
		        "custom_plate_no as plate_no", "grand_total as total_amount", "paid_amount",
		        "company", "creation", "status", "remarks", "owner as cashier"],
		order_by="creation desc",
		limit_page_length=200,
	)
	for r in rows:
		r["timestamp"] = _fmt_ts(r)
		r["pos_invoice"] = r["name"]
		mop = frappe.db.get_value("Sales Invoice Payment", {"parent": r["name"]}, "mode_of_payment")
		r["payment_method"] = mop or "Cash"
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
def get_pos_profiles_for_user(company=None):
	"""Return available POS Profiles the logged-in user can use.

	Each profile record in ERPNext contains an optional child table 'applicable_for_users'
	(Has Role). If it is empty the profile is available to everyone; if it has rows the user
	must appear in at least one row.  We also restrict to profiles for the given company when
	`company` is supplied.

	Returns a list of {name, company, warehouse} dicts, plus a flat list of the distinct
	companies across all returned profiles so the UI can build its company selector.
	"""
	user = frappe.session.user
	filters = {"disabled": 0}
	if company:
		filters["company"] = company

	profiles = frappe.get_all(
		"POS Profile",
		filters=filters,
		fields=["name", "company", "warehouse"],
		order_by="company asc, name asc",
	)

	visible = []
	for p in profiles:
		# Check if the profile is restricted to specific users
		applicable_users = frappe.get_all(
			"POS Profile User",
			filters={"parent": p.name},
			fields=["user"],
		)
		# If no users set → available to all; else user must be in the list
		if not applicable_users or any(u.user == user for u in applicable_users):
			visible.append(p)

	companies = sorted({p.company for p in visible if p.company})
	return {"profiles": [dict(p) for p in visible], "companies": companies}


@frappe.whitelist()
def get_cashier_today_sales():
	"""Total sales (paid_amount) for the current cashier today, scoped to their company.

	Used by the Closing Entry modal to display an informational 'Today Sales' amount.
	Looks at POS Invoice records posted today where the cashier (owner) is the current user.
	"""
	user = frappe.session.user
	today = frappe.utils.today()

	# Determine the cashier's active company from the open shift, employee, or cashier profile
	company = None
	open_entry = frappe.db.get_value(
		"POS Opening Entry",
		{"user": user, "status": "Open", "docstatus": 1},
		"company",
	)
	if open_entry:
		company = open_entry
	else:
		emp_company = frappe.db.get_value("Employee", {"user_id": user}, "company")
		company = emp_company or frappe.db.get_value("Cashier Profile", user, "company")

	filters = [
		["posting_date", "=", today],
		["docstatus", "<", 2],
		["owner", "=", user],
	]
	if company:
		filters.append(["company", "=", company])

	rows = frappe.get_all(
		"POS Invoice",
		filters=filters,
		fields=["grand_total", "paid_amount", "status"],
	)
	total_sales = sum(flt(r.get("grand_total") or 0) for r in rows)
	total_paid = sum(flt(r.get("paid_amount") or 0) for r in rows)
	return {
		"company": company or "",
		"today": today,
		"total_invoices": len(rows),
		"total_sales": round(total_sales, 2),
		"total_paid": round(total_paid, 2),
	}


@frappe.whitelist()
def open_cashier(company=None, opening_amount=0, pos_profile=None):
	"""Open a POS Opening Entry for the logged-in cashier.

	Parameters
	----------
	company        : Company name (auto-resolved from employee/cashier profile if omitted)
	opening_amount : Cash amount the cashier counted at shift start
	pos_profile    : Explicit POS Profile to use.  When supplied, company is derived from
	                 the profile if not also supplied.  When omitted, the profile is
	                 auto-resolved via ensure_pos_profile().

	Returns {status, name} where status is one of:
	  - "already_open"  : shift already open for this user
	  - "opened"        : new POS Opening Entry created and submitted
	  - throws          : no company, no pos_profile found
	"""
	user = frappe.session.user
	existing = frappe.db.get_value(
		"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
	)
	if existing:
		return {"status": "already_open", "name": existing}

	# ── Resolve company ───────────────────────────────────────────────────────────
	if pos_profile and not company:
		company = frappe.db.get_value("POS Profile", pos_profile, "company")
	if not company:
		company = (get_cashier() or {}).get("company")
	if not company:
		frappe.throw("Could not resolve a company for this cashier.")

	# ── Resolve POS Profile ───────────────────────────────────────────────────────
	if not pos_profile:
		# Try to find one via the VehiclePOSInvoice helper (existing behaviour)
		try:
			from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import VehiclePOSInvoice
			vpi = VehiclePOSInvoice({"doctype": "Vehicle POS Invoice"})
			pos_profile = vpi.ensure_pos_profile(company)
		except Exception:
			pos_profile = None
	if not pos_profile:
		pos_profile = frappe.db.get_value(
			"POS Profile",
			{"company": company, "disabled": 0},
			"name",
		)
	if not pos_profile:
		frappe.throw(
			"No POS Profile found for company <b>{}</b>. "
			"Please create a POS Profile for this company first.".format(company)
		)

	# ── Resolve Cash mode of payment ─────────────────────────────────────────────
	try:
		from vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import VehiclePOSInvoice
		vpi = VehiclePOSInvoice({"doctype": "Vehicle POS Invoice"})
		cash = vpi.get_mode_of_payment("Cash", company)
	except Exception:
		cash = "Cash"

	# ── Create and submit the POS Opening Entry ───────────────────────────────────
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
	return {"status": "opened", "name": entry.name, "pos_profile": pos_profile, "company": company}


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
def vm_pos_items(txt=None, category=None, company=None, only_stock=0):
    """POS catalog search (client calls this)."""
    return get_items(txt=txt, category=category, company=company, only_stock=only_stock)


@frappe.whitelist()
def vm_pos_vehicles(txt=None):
    """Customer Vehicle autocomplete (client calls this)."""
    return search_vehicles(txt=txt)


@frappe.whitelist()
def vm_pos_vehicle_customer(vehicle=None):
    """Resolve Customer Vehicle -> Customer (client calls this)."""
    return get_customer_vehicle(vehicle=vehicle)


@frappe.whitelist()
def vm_post_asset_depreciations(posting_date=None):
    """Run depreciation scheduler to post all due depreciation entries."""
    from erpnext.assets.doctype.asset.depreciation import post_depreciation_entries
    date = posting_date or frappe.utils.nowdate()
    post_depreciation_entries(date=date)
    
    jes = frappe.get_all(
        "Journal Entry",
        filters={"voucher_type": "Depreciation Entry"},
        fields=["name", "posting_date", "total_debit", "user_remark"],
        order_by="creation desc",
        limit=50
    )
    assets = frappe.get_all(
        "Asset",
        fields=["name", "asset_name", "gross_purchase_amount", "value_after_depreciation", "status"],
        order_by="creation desc",
        limit=20
    )
    
    return {
        "status": "success",
        "posted_date": date,
        "journal_entries_count": len(jes),
        "recent_journal_entries": jes,
        "assets": assets
    }


# Compatibility patch: ensure Exporter and BaseDocument gracefully handle list-valued metadata fields
try:
    import json
    from frappe.model.base_document import BaseDocument
    from frappe.core.doctype.data_import.exporter import Exporter

    _orig_get_valid_dict = BaseDocument.get_valid_dict

    def _safe_get_valid_dict(self, convert_dates_to_str=False, ignore_nulls=False, ignore_virtual=False):
        for df in self.meta.get("fields"):
            val = self.get(df.fieldname)
            if isinstance(val, (list, dict)) and df.fieldtype not in frappe.model.table_fields:
                if df.fieldtype in ("Code", "Small Text", "Data", "Text", "Long Text", "JSON"):
                    self.set(df.fieldname, json.dumps(val, separators=(",", ":")))
        return _orig_get_valid_dict(self, convert_dates_to_str, ignore_nulls, ignore_virtual)

    BaseDocument.get_valid_dict = _safe_get_valid_dict

    def _safe_serialize_exportable_fields(self):
        fields = []
        for key, exportable_fields in self.exportable_fields.items():
            for _df in exportable_fields:
                if hasattr(_df, "as_dict"):
                    try:
                        df = _df.as_dict()
                    except Exception:
                        df = frappe._dict(_df.__dict__)
                else:
                    df = _df.copy()

                df.is_child_table_field = key != self.doctype
                if df.is_child_table_field:
                    df.child_table_df = self.meta.get_field(key)
                fields.append(df)
        return fields

    Exporter.serialize_exportable_fields = _safe_serialize_exportable_fields
except Exception:
    pass

try:
    from frappe.utils.nestedset import get_descendants_of
    import erpnext.selling.report.item_wise_sales_history.item_wise_sales_history as iwsh
    
    def _safe_iwsh_get_data(filters):
        data = []
        company_list = []
        if filters.get("company"):
            company_list = get_descendants_of("Company", filters.get("company"))
            company_list.append(filters.get("company"))

        customer_details = iwsh.get_customer_details()
        item_details = iwsh.get_item_details()
        sales_order_records = iwsh.get_sales_order_details(company_list, filters)

        for record in sales_order_records:
            customer_record = customer_details.get(record.customer)
            item_record = item_details.get(record.item_code)
            row = {
                "item_code": record.get("item_code"),
                "item_name": item_record.get("item_name") if item_record else record.get("item_code"),
                "item_group": item_record.get("item_group") if item_record else "",
                "description": record.get("description"),
                "quantity": record.get("qty"),
                "uom": record.get("uom"),
                "rate": record.get("base_rate"),
                "amount": record.get("base_amount"),
                "sales_order": record.get("name"),
                "transaction_date": record.get("transaction_date"),
                "customer": record.get("customer"),
                "customer_name": customer_record.get("customer_name") if customer_record else record.get("customer"),
                "customer_group": customer_record.get("customer_group") if customer_record else "",
                "territory": record.get("territory"),
                "project": record.get("project"),
                "delivered_quantity": flt(record.get("delivered_qty")),
                "billed_amount": flt(record.get("billed_amt")),
                "company": record.get("company"),
            }
            row["currency"] = frappe.get_cached_value("Company", row["company"], "default_currency")
            data.append(row)
        return data

    def _safe_iwsh_get_sales_order_details(company_list, filters):
        db_so = frappe.qb.DocType("Sales Order")
        db_so_item = frappe.qb.DocType("Sales Order Item")

        query = (
            frappe.qb.from_(db_so)
            .inner_join(db_so_item)
            .on(db_so_item.parent == db_so.name)
            .select(
                db_so.name,
                db_so.customer,
                db_so.transaction_date,
                db_so.territory,
                db_so.project,
                db_so.company,
                db_so_item.item_code,
                db_so_item.description,
                db_so_item.qty,
                db_so_item.uom,
                db_so_item.base_rate,
                db_so_item.base_amount,
                db_so_item.delivered_qty,
                (db_so_item.billed_amt * db_so.conversion_rate).as_("billed_amt"),
            )
            .where(db_so.docstatus == 1)
        )

        if company_list:
            query = query.where(db_so.company.isin(tuple(company_list)))

        if filters.get("item_group"):
            query = query.where(db_so_item.item_group == filters.item_group)

        if filters.get("from_date"):
            query = query.where(db_so.transaction_date >= filters.from_date)

        if filters.get("to_date"):
            query = query.where(db_so.transaction_date <= filters.to_date)

        if filters.get("item_code"):
            query = query.where(db_so_item.item_code == filters.item_code)

        if filters.get("customer"):
            query = query.where(db_so.customer == filters.customer)

        return query.run(as_dict=1)

    iwsh.get_data = _safe_iwsh_get_data
    iwsh.get_sales_order_details = _safe_iwsh_get_sales_order_details
except Exception:
    pass


