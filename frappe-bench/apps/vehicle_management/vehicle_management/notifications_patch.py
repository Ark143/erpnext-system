import json
from typing import Literal
import frappe
from frappe import _


@frappe.whitelist()
def get_open_count(doctype: str, name: str, items=None):
	"""
	Safe implementation of get_open_count with PostgreSQL resilience.
	Prevents non-existent column queries from aborting PostgreSQL transactions.
	"""
	if frappe.flags.in_migrate or frappe.flags.in_install:
		return {"count": []}

	# None of the count queries should take more than 1s individually
	try:
		frappe.db.set_execution_timeout(1)
	except Exception:
		pass

	try:
		return _get_linked_document_counts(doctype, name, items)
	except Exception as e:
		if frappe.db.is_statement_timeout(e):
			return {"count": []}
		raise


def _get_linked_document_counts(doctype: str, name: str, items=None):
	doc = frappe.get_lazy_doc(doctype, name, check_permission=True)
	meta = doc.meta
	links = meta.get_dashboard_data()

	# compile all items in a list
	if items is None:
		items = []
		for group in links.transactions:
			items.extend(group.get("items"))

	if not isinstance(items, list):
		items = json.loads(items)

	out = {
		"external_links_found": [],
		"internal_links_found": [],
	}

	for d in items:
		internal_link_for_doctype = links.get("internal_links", {}).get(d) or links.get(
			"internal_and_external_links", {}
		).get(d)
		if internal_link_for_doctype:
			internal_links_data_for_d = get_internal_links(doc, internal_link_for_doctype, d)
			if internal_links_data_for_d["count"]:
				out["internal_links_found"].append(internal_links_data_for_d)
			elif d in links.get("internal_and_external_links", {}):
				try:
					external_links_data_for_d = get_external_links(d, name, links)
					out["external_links_found"].append(external_links_data_for_d)
				except Exception:
					out["external_links_found"].append({"doctype": d, "open_count": 0, "count": 0})
			else:
				out["internal_links_found"].append(internal_links_data_for_d)
		else:
			try:
				external_links_data_for_d = get_external_links(d, name, links)
				out["external_links_found"].append(external_links_data_for_d)
			except Exception:
				out["external_links_found"].append({"doctype": d, "open_count": 0, "count": 0})

	out = {
		"count": out,
	}

	if not meta.custom:
		try:
			module = frappe.get_meta_module(doctype)
			if hasattr(module, "get_timeline_data"):
				out["timeline_data"] = module.get_timeline_data(doctype, name)
		except Exception:
			pass

	return out


def get_internal_links(doc, link, link_doctype):
	names = []
	data = {"doctype": link_doctype}

	if isinstance(link, str):
		value = doc.get(link)
		if value and value not in names:
			names.append(value)
	elif isinstance(link, list):
		table_fieldname, link_fieldname = link
		for row in doc.get(table_fieldname) or []:
			value = row.get(link_fieldname)
			if value and value not in names:
				names.append(value)

	data["open_count"] = 0
	data["count"] = len(names)
	data["names"] = names

	return data


def get_external_links(doctype, name, links):
	fieldname = links.get("non_standard_fieldnames", {}).get(doctype, links.get("fieldname"))
	if not fieldname:
		return {"doctype": doctype, "count": 0, "open_count": 0}

	meta = frappe.get_meta(doctype)
	if not meta.has_field(fieldname) and fieldname not in ("name", "owner", "creation", "modified"):
		return {"doctype": doctype, "count": 0, "open_count": 0}

	filters = {fieldname: name}

	# updating filters based on dynamic_links
	try:
		from frappe.desk.notifications import get_dynamic_link_filters, get_filters_for
		if dynamic_link_filters := get_dynamic_link_filters(doctype, links, fieldname):
			filters.update(dynamic_link_filters)

		total_count = get_doc_count(doctype, filters)

		open_count = 0
		if open_count_filters := get_filters_for(doctype):
			filters.update(open_count_filters)
			open_count = get_doc_count(doctype, filters)

		return {"doctype": doctype, "count": total_count, "open_count": open_count}
	except Exception:
		return {"doctype": doctype, "count": 0, "open_count": 0}


def get_doc_count(doctype, filters) -> int | Literal["?"]:
	try:
		docs = frappe.get_all(
			doctype, filters=filters, limit=100, distinct=True, ignore_ifnull=True, order_by=None
		)
		return len(docs)
	except Exception as e:
		if frappe.db.is_statement_timeout(e):
			return "?"
		return 0
