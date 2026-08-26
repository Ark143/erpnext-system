frappe.query_reports["Top Selling Services"] = {
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
    "fieldname": "item_group",
    "label": "Item Group",
    "fieldtype": "Link",
    "options": "Item Group"
  },
  {
    "fieldname": "sort_by",
    "label": "Sort By",
    "fieldtype": "Select",
    "options": "Total Amount\nCount"
  }
]
};
