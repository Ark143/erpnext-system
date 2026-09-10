# Copyright (c) 2026, Autometrik and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate


class InventoryCountSheet(Document):

	def validate(self):
		self.set_item_status()
		self.update_summary()

	def set_item_status(self):
		"""Compute variance_qty and count_status for each line."""
		for row in self.get("items", []):
			if row.physical_qty is None or row.physical_qty == "" or str(row.physical_qty) == "":
				# Not yet counted
				row.count_status = "Pending"
				row.variance_qty = 0
				continue

			physical = flt(row.physical_qty)
			system   = flt(row.system_qty)
			variance = physical - system
			row.variance_qty = variance

			if flt(row.system_qty) == 0 and physical > 0:
				row.count_status = "New Item"
			elif variance == 0:
				row.count_status = "Matched"
			elif variance > 0:
				row.count_status = "Over"
			else:
				row.count_status = "Short"

	def update_summary(self):
		"""Recalculate header KPI fields from items table."""
		items = self.get("items", [])
		total     = len(items)
		counted   = sum(1 for r in items if r.count_status != "Pending")
		matched   = sum(1 for r in items if r.count_status == "Matched")
		variance  = sum(1 for r in items if r.count_status in ("Over", "Short", "New Item"))
		uncounted = total - counted

		self.total_lines     = total
		self.counted_lines   = counted
		self.matched_lines   = matched
		self.variance_lines  = variance
		self.uncounted_lines = uncounted
		self.count_accuracy  = round((matched / counted * 100), 2) if counted else 0

		# Auto-set status
		if total > 0:
			if uncounted == total:
				self.status = "Draft"
			elif uncounted > 0:
				self.status = "In Progress"
			else:
				self.status = "Completed"

	def on_submit(self):
		self.status = "Submitted"
		self.db_set("status", "Submitted")

	def before_cancel(self):
		self.db_set("status", "Cancelled")


# ──────────────────────────────────────────────────────────────────────────────
# Whitelisted API methods for JS client
# ──────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_stock_qty(item_code, warehouse):
	"""Return the current system (ledger) quantity for an item in a warehouse."""
	qty = frappe.db.get_value(
		"Bin",
		{"item_code": item_code, "warehouse": warehouse},
		"actual_qty"
	) or 0
	return flt(qty)


@frappe.whitelist()
def get_warehouse_items(warehouse, bin_filter=None):
	"""
	Return all items that have stock in the given warehouse (from the Bin table).
	If bin_filter is provided, only items whose bin_location matches are returned.
	"""
	filters = {"warehouse": warehouse, "actual_qty": [">", 0]}
	bins = frappe.get_all(
		"Bin",
		filters=filters,
		fields=["item_code", "actual_qty"],
	)

	results = []
	for b in bins:
		item = frappe.db.get_value(
			"Item",
			b["item_code"],
			["item_name", "item_group", "stock_uom"],
			as_dict=True
		)
		if not item:
			continue
		results.append({
			"item_code":   b["item_code"],
			"item_name":   item.item_name,
			"item_group":  item.item_group,
			"uom":         item.stock_uom,
			"system_qty":  flt(b["actual_qty"]),
			"physical_qty": None,
			"variance_qty": 0,
			"count_status": "Pending",
			"bin_location": b.get("bin_location") or "",
		})

	return results
