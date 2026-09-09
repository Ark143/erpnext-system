# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, nowdate, add_months, getdate

EXECUTIVE_ROLES = {
	"Administrator",
	"System Manager",
	"CEO",
	"Director",
	"Executive",
	"Operation",
	"Operations",
	"Operations Manager",
	"Finance",
	"Finance Manager",
	"Financial Officer",
	"Accounting",
	"Accounts Manager",
	"Accounts User",
	"Auditor",
}


@frappe.whitelist()
def get_user_analytics_permissions(user=None):
	"""
	Returns user permissions for Vehicle Management Analytics:
	- can_view_all: bool (True if Admin, System Manager, CEO, Operations, Finance, Accounting)
	- allowed_companies: list of company names the user is permitted to view
	- default_company: primary company for the user
	"""
	if not user:
		user = frappe.session.user

	all_companies = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name asc")]
	all_companies = [c for c in all_companies if c != "My Company"]

	# Administrator always has full access
	if user == "Administrator":
		return {
			"can_view_all": True,
			"allowed_companies": all_companies,
			"default_company": "All Companies",
		}

	user_roles = set(frappe.get_roles(user))

	# Check if user has any executive / leadership role
	is_executive = bool(user_roles.intersection(EXECUTIVE_ROLES))

	if is_executive:
		return {
			"can_view_all": True,
			"allowed_companies": all_companies,
			"default_company": "All Companies",
		}

	# For non-executive users: Determine allowed companies based on Employee record, User Permissions, and User Defaults
	allowed_companies = set()

	# 1. From Employee details (employee user company tag)
	emp_companies = frappe.get_all(
		"Employee",
		filters={"user_id": user, "status": "Active"},
		pluck="company",
	)
	for comp in emp_companies:
		if comp:
			allowed_companies.add(comp)

	# Fallback if employee is not marked Active
	if not allowed_companies:
		emp_companies = frappe.get_all(
			"Employee",
			filters={"user_id": user},
			pluck="company",
		)
		for comp in emp_companies:
			if comp:
				allowed_companies.add(comp)

	# 2. From User Permission DocType
	user_perms = frappe.get_all(
		"User Permission",
		filters={"user": user, "allow": "Company"},
		pluck="for_value",
	)
	for comp in user_perms:
		if comp:
			allowed_companies.add(comp)

	# 3. From User Default Company
	user_default = frappe.defaults.get_user_default("Company", user)
	if user_default and user_default in all_companies:
		allowed_companies.add(user_default)

	allowed_list = sorted(list(allowed_companies))
	default_company = allowed_list[0] if allowed_list else (all_companies[0] if all_companies else "")

	return {
		"can_view_all": False,
		"allowed_companies": allowed_list,
		"default_company": default_company,
	}


@frappe.whitelist()
def get_vehicle_management_analytics(company=None, timespan="Last 30 Days", from_date=None, to_date=None):
	"""
	Returns consolidated analytics for Vehicle Management:
	1. Top Selling Services & Labor
	2. Top Selling Items & Parts
	3. Top Selling Tires & Mags / Wheels
	4. Job Order & Revenue performance by Company / Branch
	5. Summary KPIs
	Enforces role and employee-based branch scoping.
	"""
	user_perm = get_user_analytics_permissions()
	can_view_all = user_perm["can_view_all"]
	allowed_companies = user_perm["allowed_companies"]

	# Filters
	filters = {"docstatus": ["!=", 2]}

	if not can_view_all:
		if not allowed_companies:
			# User has no company assigned
			return {
				"summary": {
					"total_revenue": 0.0,
					"total_labor": 0.0,
					"total_parts": 0.0,
					"total_jos": 0,
					"avg_ticket": 0.0,
					"unique_vehicles": 0,
				},
				"top_services": [],
				"top_parts": [],
				"top_tires_mags": [],
				"company_performance": [],
				"user_perm": user_perm,
			}

		if company and company in allowed_companies:
			filters["company"] = company
		else:
			if len(allowed_companies) == 1:
				filters["company"] = allowed_companies[0]
			else:
				filters["company"] = ["in", allowed_companies]
	else:
		if company and company != "All Companies":
			filters["company"] = company

	if from_date and to_date:
		filters["job_order_date"] = ["between", [from_date, to_date]]
	elif timespan == "Last 30 Days":
		filters["job_order_date"] = [">=", add_months(nowdate(), -1)]
	elif timespan == "This Year":
		filters["job_order_date"] = [">=", f"{getdate().year}-01-01"]

	job_orders = frappe.get_all(
		"Vehicle Job Order",
		filters=filters,
		fields=[
			"name",
			"company",
			"customer",
			"vehicle",
			"status",
			"payment_status",
			"total_labor",
			"total_parts",
			"discount_amount",
			"grand_total",
			"job_order_date",
		],
		order_by="job_order_date desc",
	)

	jo_names = [jo.name for jo in job_orders]

	# Summary KPIs
	total_revenue = sum(flt(jo.grand_total) for jo in job_orders)
	total_labor = sum(flt(jo.total_labor) for jo in job_orders)
	total_parts = sum(flt(jo.total_parts) for jo in job_orders)
	total_jos = len(job_orders)
	avg_ticket = (total_revenue / total_jos) if total_jos > 0 else 0.0
	unique_vehicles = len(set(jo.vehicle for jo in job_orders if jo.vehicle))

	# 1. Services Breakdown
	service_map = {}
	if jo_names:
		services = frappe.get_all(
			"Job Order Service Item",
			filters={"parent": ["in", jo_names]},
			fields=["service_item", "description", "hours", "rate", "discount_amount", "total_amount", "parent"],
		)
		for s in services:
			key = s.description or s.service_item or "General Service"
			if key not in service_map:
				service_map[key] = {
					"service_name": key,
					"item_code": s.service_item or "-",
					"count": 0,
					"total_hours": 0.0,
					"total_amount": 0.0,
				}
			service_map[key]["count"] += 1
			service_map[key]["total_hours"] += flt(s.hours) or 1.0
			service_map[key]["total_amount"] += flt(s.total_amount) or 0.0

	top_services = sorted(service_map.values(), key=lambda x: x["total_amount"], reverse=True)

	# 2. Parts, Tires & Mags Breakdown
	part_map = {}
	tires_mags_map = {}

	if jo_names:
		parts = frappe.get_all(
			"Job Order Part Item",
			filters={"parent": ["in", jo_names]},
			fields=["item_code", "item_name", "part_no", "qty", "uom", "rate", "discount_amount", "amount", "parent"],
		)
		for p in parts:
			name_key = p.item_name or p.item_code or "Generic Part"
			amount = flt(p.amount)
			qty = flt(p.qty) or 1.0

			# General Parts
			if name_key not in part_map:
				part_map[name_key] = {
					"item_name": name_key,
					"item_code": p.item_code or "-",
					"part_no": p.part_no or "-",
					"total_qty": 0.0,
					"uom": p.uom or "PC",
					"total_amount": 0.0,
				}
			part_map[name_key]["total_qty"] += qty
			part_map[name_key]["total_amount"] += amount

			# Categorize Tires, Mags & Wheels
			upper_name = name_key.upper()
			is_tire = any(k in upper_name for k in ["TIRE", "YOKOHAMA", "DUNLOP", "BRIDGESTONE", "MICHELIN", "SAILUN", "ROADCRUZA", "185/", "195/", "205/", "215/", "225/", "235/", "245/", "265/", "275/", "285/", "R14", "R15", "R16", "R17", "R18", "R20"])
			is_mag = any(k in upper_name for k in ["MAG", "TE37", "ROTA", "VOLK", "WHEEL", "RIMS", "ALLOY", "18X8.5", "18X9", "20X9.5", "17X8.5", "PM2"])

			if is_tire or is_mag:
				cat = "Mags / Wheels" if is_mag else "Tires"
				if name_key not in tires_mags_map:
					tires_mags_map[name_key] = {
						"item_name": name_key,
						"category": cat,
						"item_code": p.item_code or "-",
						"part_no": p.part_no or "-",
						"total_qty": 0.0,
						"uom": p.uom or "PC",
						"total_amount": 0.0,
					}
				tires_mags_map[name_key]["total_qty"] += qty
				tires_mags_map[name_key]["total_amount"] += amount

	top_parts = sorted(part_map.values(), key=lambda x: x["total_amount"], reverse=True)
	top_tires_mags = sorted(tires_mags_map.values(), key=lambda x: x["total_amount"], reverse=True)

	# 3. Company / Branch Performance
	company_map = {}
	all_companies = [c.name for c in frappe.get_all("Company", filters={"is_group": 0})]
	target_companies = all_companies if can_view_all else allowed_companies

	for comp in target_companies:
		if comp not in ["My Company"]:
			company_map[comp] = {
				"company": comp,
				"total_jos": 0,
				"total_labor": 0.0,
				"total_parts": 0.0,
				"total_revenue": 0.0,
				"completed_jos": 0,
			}

	for jo in job_orders:
		c = jo.company or "ULTRA MRF"
		if not can_view_all and c not in allowed_companies:
			continue
		if c not in company_map:
			company_map[c] = {
				"company": c,
				"total_jos": 0,
				"total_labor": 0.0,
				"total_parts": 0.0,
				"total_revenue": 0.0,
				"completed_jos": 0,
			}
		company_map[c]["total_jos"] += 1
		company_map[c]["total_labor"] += flt(jo.total_labor)
		company_map[c]["total_parts"] += flt(jo.total_parts)
		company_map[c]["total_revenue"] += flt(jo.grand_total)
		if jo.status in ["Completed", "Released", "Invoiced"]:
			company_map[c]["completed_jos"] += 1

	company_performance = sorted(
		[v for v in company_map.values() if v["total_jos"] > 0 or v["total_revenue"] > 0 or not can_view_all],
		key=lambda x: x["total_revenue"],
		reverse=True,
	)

	return {
		"summary": {
			"total_revenue": total_revenue,
			"total_labor": total_labor,
			"total_parts": total_parts,
			"total_jos": total_jos,
			"avg_ticket": avg_ticket,
			"unique_vehicles": unique_vehicles,
		},
		"top_services": top_services[:10],
		"top_parts": top_parts[:10],
		"top_tires_mags": top_tires_mags[:10],
		"company_performance": company_performance,
		"user_perm": user_perm,
	}
