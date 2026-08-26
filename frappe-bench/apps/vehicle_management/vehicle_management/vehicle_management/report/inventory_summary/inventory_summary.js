frappe.query_reports["Inventory Summary"] = {
	filters: [
  {
    "fieldname": "company",
    "label": "Company",
    "fieldtype": "Link",
    "options": "Company",
    "width": "200"
  },
  {
    "fieldname": "to_date",
    "label": "To Date",
    "fieldtype": "Date",
    "default": "Today",
    "width": "100"
  },
  {
    "fieldname": "item_group",
    "label": "Item Group",
    "fieldtype": "Link",
    "options": "Item Group"
  }
]
};
