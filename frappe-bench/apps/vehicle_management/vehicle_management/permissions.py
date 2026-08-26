import frappe

def get_permission_query_conditions_for_doctype(doctype, user=None):
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return ""

	user_perms = frappe.get_all("User Permission", filters={"user": user, "allow": "Company"}, fields=["for_value"])
	if not user_perms:
		return ""

	allowed_companies = [frappe.db.escape(p.for_value) for p in user_perms]
	companies_str = ", ".join(allowed_companies)
	return f"(`tab{doctype}`.company IN ({companies_str}) OR `tab{doctype}`.company IS NULL OR `tab{doctype}`.company = '')"


def get_customer_vehicle_query_conditions(user=None):
	return get_permission_query_conditions_for_doctype("Customer Vehicle", user)


def get_vehicle_job_order_query_conditions(user=None):
	return get_permission_query_conditions_for_doctype("Vehicle Job Order", user)


def get_vehicle_inspection_query_conditions(user=None):
	return get_permission_query_conditions_for_doctype("Vehicle Inspection", user)


def get_vehicle_service_reminder_query_conditions(user=None):
	return get_permission_query_conditions_for_doctype("Vehicle Service Reminder", user)


def has_vehicle_permission(doc, ptype="read", user=None):
	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return True

	user_perms = frappe.get_all("User Permission", filters={"user": user, "allow": "Company"}, fields=["for_value"])
	if not user_perms:
		return True

	allowed_companies = {p.for_value for p in user_perms}
	doc_company = getattr(doc, "company", None)
	if not doc_company:
		return True

	return doc_company in allowed_companies
