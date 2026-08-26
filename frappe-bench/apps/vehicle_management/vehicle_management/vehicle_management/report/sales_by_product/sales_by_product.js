frappe.query_reports["Sales by Product"] = {
	filters: [
  {
    "fieldname": "company",
    "label": "Company",
    "fieldtype": "Link",
    "options": "Company",
    "width": "200"
  },
  {
    "fieldname": "from_date",
    "label": "From Date",
    "fieldtype": "Date",
    "default": "Today",
    "width": "100"
  },
  {
    "fieldname": "to_date",
    "label": "To Date",
    "fieldtype": "Date",
    "default": "Today",
    "width": "100"
  },
  {
    "fieldname": "item",
    "label": "Product",
    "fieldtype": "Link",
    "options": "Item"
  },
  {
    "fieldname": "item_group",
    "label": "Item Group",
    "fieldtype": "Link",
    "options": "Item Group"
  }
]
};
