frappe.query_reports["Top Vehicles Served"] = {
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
    "fieldname": "make",
    "label": "Vehicle Make",
    "fieldtype": "Link",
    "options": "Vehicle Make"
  },
  {
    "fieldname": "sort_by",
    "label": "Sort By",
    "fieldtype": "Select",
    "options": "Total Amount\nCount"
  }
]
};
