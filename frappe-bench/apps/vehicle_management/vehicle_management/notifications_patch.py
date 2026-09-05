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


def patch_query_payment_ledger():
	try:
		import erpnext.accounts.utils
		from frappe import qb
		from frappe.query_builder import AliasedQuery, Case, Criterion, Table
		from pypika.terms import Max, Sum

		def query_for_outstanding(self):
			ple = self.ple

			filter_on_voucher_no = []
			filter_on_against_voucher_no = []

			if self.vouchers:
				voucher_types = set([x.voucher_type for x in self.vouchers])
				voucher_nos = set([x.voucher_no for x in self.vouchers])

				filter_on_voucher_no.append(ple.voucher_type.isin(voucher_types))
				filter_on_voucher_no.append(ple.voucher_no.isin(voucher_nos))

				filter_on_against_voucher_no.append(ple.against_voucher_type.isin(voucher_types))
				filter_on_against_voucher_no.append(ple.against_voucher_no.isin(voucher_nos))

			if self.voucher_no:
				filter_on_voucher_no.append(ple.voucher_no.like(f"%{self.voucher_no}%"))
				filter_on_against_voucher_no.append(ple.against_voucher_no.like(f"%{self.voucher_no}%"))

			# build outstanding amount filter
			filter_on_outstanding_amount = []
			if self.min_outstanding:
				if self.min_outstanding > 0:
					filter_on_outstanding_amount.append(
						Table("outstanding").amount_in_account_currency >= self.min_outstanding
					)
				else:
					filter_on_outstanding_amount.append(
						Table("outstanding").amount_in_account_currency <= self.min_outstanding
					)
			if self.max_outstanding:
				if self.max_outstanding > 0:
					filter_on_outstanding_amount.append(
						Table("outstanding").amount_in_account_currency <= self.max_outstanding
					)
				else:
					filter_on_outstanding_amount.append(
						Table("outstanding").amount_in_account_currency >= self.max_outstanding
					)

			if self.limit and self.get_invoices:
				outstanding_vouchers = (
					qb.from_(ple)
					.select(
						ple.against_voucher_no.as_("voucher_no"),
						Sum(ple.amount_in_account_currency).as_("amount_in_account_currency"),
						Max(
							Case().when(
								(
									(ple.voucher_no == ple.against_voucher_no)
									& (ple.voucher_type == ple.against_voucher_type)
								),
								(ple.posting_date),
							)
						).as_("invoice_date"),
					)
					.where(ple.delinked == 0)
					.where(Criterion.all(filter_on_against_voucher_no))
					.where(Criterion.all(self.common_filter))
					.where(Criterion.all(self.dimensions_filter))
					.where(Criterion.all(self.voucher_posting_date))
					.groupby(ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party)
					.orderby(ple.invoice_date, ple.voucher_no)
					.having(qb.Field("amount_in_account_currency") > 0)
					.limit(self.limit)
					.run()
				)
				if outstanding_vouchers:
					filter_on_voucher_no.append(ple.voucher_no.isin([x[0] for x in outstanding_vouchers]))
					filter_on_against_voucher_no.append(
						ple.against_voucher_no.isin([x[0] for x in outstanding_vouchers])
					)

			# build query for voucher amount
			query_voucher_amount = (
				qb.from_(ple)
				.select(
					ple.account,
					ple.voucher_type,
					ple.voucher_no,
					ple.party_type,
					ple.party,
					Max(ple.posting_date).as_("posting_date"),
					Max(ple.due_date).as_("due_date"),
					Max(ple.account_currency).as_("currency"),
					Max(ple.cost_center).as_("cost_center"),
					Sum(ple.amount).as_("amount"),
					Sum(ple.amount_in_account_currency).as_("amount_in_account_currency"),
					Max(ple.remarks).as_("remarks"),
				)
				.where(ple.delinked == 0)
				.where(Criterion.all(filter_on_voucher_no))
				.where(Criterion.all(self.common_filter))
				.where(Criterion.all(self.dimensions_filter))
				.groupby(
					ple.account,
					ple.voucher_type,
					ple.voucher_no,
					ple.party_type,
					ple.party,
				)
			)

			# build query for voucher outstanding
			query_voucher_outstanding = (
				qb.from_(ple)
				.select(
					ple.account,
					ple.against_voucher_type.as_("voucher_type"),
					ple.against_voucher_no.as_("voucher_no"),
					ple.party_type,
					ple.party,
					Sum(ple.amount).as_("amount"),
					Sum(ple.amount_in_account_currency).as_("amount_in_account_currency"),
				)
				.where(ple.delinked == 0)
				.where(Criterion.all(filter_on_against_voucher_no))
				.where(Criterion.all(self.common_filter))
				.groupby(
					ple.account,
					ple.against_voucher_type,
					ple.against_voucher_no,
					ple.party_type,
					ple.party,
				)
			)

			if self.get_invoices:
				query_voucher_outstanding = query_voucher_outstanding.having(
					Sum(ple.amount_in_account_currency) > 0
				)
			elif self.get_payments:
				query_voucher_outstanding = query_voucher_outstanding.having(
					Sum(ple.amount_in_account_currency) < 0
				)

			# build CTE for combining voucher amount and outstanding
			self.cte_query_voucher_amount_and_outstanding = (
				qb.with_(query_voucher_amount, "vouchers")
				.with_(query_voucher_outstanding, "outstanding")
				.from_(AliasedQuery("vouchers"))
				.left_join(AliasedQuery("outstanding"))
				.on(
					(AliasedQuery("vouchers").account == AliasedQuery("outstanding").account)
					& (AliasedQuery("vouchers").voucher_type == AliasedQuery("outstanding").voucher_type)
					& (AliasedQuery("vouchers").voucher_no == AliasedQuery("outstanding").voucher_no)
					& (AliasedQuery("vouchers").party_type == AliasedQuery("outstanding").party_type)
					& (AliasedQuery("vouchers").party == AliasedQuery("outstanding").party)
				)
				.select(
					Table("vouchers").account,
					Table("vouchers").voucher_type,
					Table("vouchers").voucher_no,
					Table("vouchers").party_type,
					Table("vouchers").party,
					Table("vouchers").posting_date,
					Table("vouchers").amount.as_("invoice_amount"),
					Table("vouchers").amount_in_account_currency.as_("invoice_amount_in_account_currency"),
					Table("outstanding").amount.as_("outstanding"),
					Table("outstanding").amount_in_account_currency.as_("outstanding_in_account_currency"),
					(Table("vouchers").amount - Table("outstanding").amount).as_("paid_amount"),
					(
						Table("vouchers").amount_in_account_currency
						- Table("outstanding").amount_in_account_currency
					).as_("paid_amount_in_account_currency"),
					Table("vouchers").due_date,
					Table("vouchers").currency,
					Table("vouchers").cost_center.as_("cost_center"),
					Table("vouchers").remarks,
				)
				.where(Criterion.all(filter_on_outstanding_amount))
			)

			if self.limit:
				self.cte_query_voucher_amount_and_outstanding = (
					self.cte_query_voucher_amount_and_outstanding.limit(self.limit)
				)

			# Clear any PyPika mistaken _havings on outer query to prevent PostgreSQL syntax errors
			if hasattr(self.cte_query_voucher_amount_and_outstanding, "_havings"):
				self.cte_query_voucher_amount_and_outstanding._havings.clear()

			# execute SQL
			self.voucher_outstandings = self.cte_query_voucher_amount_and_outstanding.run(as_dict=True)

		# Also patch get_matched_payment_request_of_references
		import erpnext.accounts.doctype.payment_entry.payment_entry as pe_module

		def get_matched_payment_request_of_references(references):
			if not references:
				return

			refs = {
				(row.reference_doctype, row.reference_name, row.allocated_amount)
				for row in references
				if row.reference_doctype and row.reference_name and row.allocated_amount
			}

			if not refs:
				return

			PR = frappe.qb.DocType("Payment Request")
			from frappe.query_builder.functions import Count
			from frappe.query_builder import Tuple

			subquery = (
				frappe.qb.from_(PR)
				.select(
					PR.reference_doctype,
					PR.reference_name,
					PR.outstanding_amount.as_("allocated_amount"),
					Max(PR.name).as_("payment_request"),
					Count("*").as_("count"),
				)
				.where(Tuple(PR.reference_doctype, PR.reference_name, PR.outstanding_amount).isin(refs))
				.where(PR.status != "Paid")
				.where(PR.docstatus == 1)
				.groupby(PR.reference_doctype, PR.reference_name, PR.outstanding_amount)
			)

			matched_prs = (
				frappe.qb.from_(subquery)
				.select(
					subquery.reference_doctype,
					subquery.reference_name,
					subquery.allocated_amount,
					subquery.payment_request,
				)
				.where(subquery.count == 1)
				.run()
			)

			return matched_prs if matched_prs else None

		pe_module.get_matched_payment_request_of_references = get_matched_payment_request_of_references

		erpnext.accounts.utils.QueryPaymentLedger.query_for_outstanding = query_for_outstanding
	except Exception:
		pass

def patch_get_mode_of_payments_info():
	try:
		import erpnext.accounts.doctype.sales_invoice.sales_invoice as si_module

		def safe_get_mode_of_payments_info(mode_of_payments, company):
			data = frappe.db.sql(
				"""
				select
					mpa.default_account, mpa.parent as mop, mp.type as type
				from
					`tabMode of Payment Account` mpa,`tabMode of Payment` mp
				where
					mpa.parent = mp.name and
					mpa.company = %s and
					mp.enabled = 1 and
					mp.name in %s
				group by
					mp.name, mpa.default_account, mpa.parent, mp.type
				""",
				(company, mode_of_payments),
				as_dict=1,
			)
			return {row.get("mop"): row for row in data}

		si_module.get_mode_of_payments_info = safe_get_mode_of_payments_info
	except Exception:
		pass

# Apply PostgreSQL compatibility patches
patch_query_payment_ledger()
patch_get_mode_of_payments_info()




