frappe.query_reports["Vehicle Transactions"] = {
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
    "fieldname": "plate_no",
    "label": "Plate No",
    "fieldtype": "Data"
  }
]
};
