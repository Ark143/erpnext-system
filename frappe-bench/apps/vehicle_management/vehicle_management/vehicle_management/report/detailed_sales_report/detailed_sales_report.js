frappe.query_reports["Detailed Sales Report"] = {
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
    "fieldname": "customer",
    "label": "Customer",
    "fieldtype": "Link",
    "options": "Customer"
  },
  {
    "fieldname": "sales_person",
    "label": "Sales Person",
    "fieldtype": "Link",
    "options": "Sales Person"
  }
]
};
