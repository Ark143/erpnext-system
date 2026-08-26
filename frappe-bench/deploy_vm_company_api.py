# -*- coding: utf-8 -*-
"""
Deploy the VM Per-Company Analytics Dashboard Server Script API.

Creates/updates a Server Script (script_type=API) named
"VM Company Dashboard API" with api_method "vm_company_dashboard_api".

RestrictedPython SAFE rules observed:
  - NO `import`  (frappe is pre-bound in the sandbox globals)
  - NO int() / cint() / str.format()  -> use f-strings
  - NO augmented assignment on dict items (x = x + y)
  - NO leading-underscore names
  - NO `return` at module level; NO lambda; NO tuple unpacking
"""

import sys, os
sys.path.insert(0, "apps/frappe")
os.chdir("sites")
import frappe

frappe.init(site="site1.local")
frappe.connect()
frappe.set_user("Administrator")

SCRIPT = r'''
# VM Company Dashboard API — runs inside the RestrictedPython sandbox.
# frappe is pre-bound; do NOT import it.

fd = frappe.form_dict or {}
company = fd.get("company") or ""
period = fd.get("period") or "this_year"

# date formatter (strftime + str.format are blocked by the sandbox guard)
def fmt(d):
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"

# ---- date range ----
# NOTE: RestrictedPython blocks all `import`/`from ... import`; use frappe.utils.* directly.
today = frappe.utils.getdate(frappe.utils.nowdate())
if period == "this_month":
    from_d = fmt(today.replace(day=1))
    to_d = frappe.utils.nowdate()
elif period == "last_month":
    # avoid datetime.timedelta (RestrictedPython blocks __import__ in frappe.utils.datetime)
    if today.month == 1:
        ly = today.year - 1
        lm = 12
    else:
        ly = today.year
        lm = today.month - 1
    if lm in (1, 3, 5, 7, 8, 10, 12):
        lday = 31
    elif lm == 2:
        if (ly % 4 == 0 and ly % 100 != 0) or (ly % 400 == 0):
            lday = 29
        else:
            lday = 28
    else:
        lday = 30
    from_d = "{0:04d}-{1:02d}-01".format(ly, lm)
    to_d = "{0:04d}-{1:02d}-{2:02d}".format(ly, lm, lday)
elif period == "this_year":
    from_d = fmt(today.replace(month=1, day=1))
    to_d = frappe.utils.nowdate()
elif period == "last_year":
    from_d = fmt(today.replace(year=today.year - 1, month=1, day=1))
    to_d = fmt(today.replace(year=today.year - 1, month=12, day=31))
else:
    from_d = "2020-01-01"
    to_d = frappe.utils.nowdate()

co_filter = ""
co_params = {"from_d": from_d, "to_d": to_d}
if company:
    co_filter = " AND company = %(company)s"
    co_params["company"] = company

# ---- helper for safe execution ----
def q(sql, params=None):
    p = params or co_params
    return frappe.db.sql(sql, p, as_dict=True)

# ---- KPI: Vehicle Job Orders ----
jo = q(f"""
    SELECT
        COUNT(name) AS total_jo,
        COALESCE(SUM(grand_total), 0) AS jo_revenue,
        COUNT(CASE WHEN status = 'Completed' THEN 1 END) AS completed,
        COUNT(CASE WHEN status = 'In Progress' THEN 1 END) AS in_progress,
        COUNT(CASE WHEN status = 'Released' THEN 1 END) AS released,
        COUNT(CASE WHEN payment_status = 'Paid' THEN 1 END) AS paid,
        COALESCE(SUM(outstanding_amount), 0) AS outstanding
    FROM "tabVehicle Job Order"
    WHERE docstatus = 1
      AND job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
""")[0]

# ---- KPI: Estimates ----
est = q(f"""
    SELECT COUNT(name) AS total_est, COALESCE(SUM(grand_total), 0) AS est_value
    FROM "tabVehicle Estimate"
    WHERE docstatus = 1
      AND estimate_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
""")[0]

# ---- KPI: Inspections ----
insp = q(f"""
    SELECT COUNT(name) AS total_insp
    FROM "tabVehicle Inspection"
    WHERE docstatus = 1
      AND inspection_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
""")[0]

# ---- KPI: Sales Invoice revenue for the company ----
rev = q(f"""
    SELECT COALESCE(SUM(grand_total), 0) AS total_revenue,
           COUNT(name) AS invoice_count
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
""")[0]

# ---- Monthly Job Order trend ----
jo_trend = q(f"""
    SELECT TO_CHAR(job_order_date, 'Mon YY') AS label,
           TO_CHAR(job_order_date, 'YYYY-MM') AS key,
           COUNT(name) AS jo_count,
           COALESCE(SUM(grand_total), 0) AS revenue
    FROM "tabVehicle Job Order"
    WHERE docstatus = 1
      AND job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY TO_CHAR(job_order_date, 'Mon YY'), TO_CHAR(job_order_date, 'YYYY-MM')
    ORDER BY key
""")

# ---- Monthly Revenue trend (Sales Invoice) ----
rev_trend = q(f"""
    SELECT TO_CHAR(posting_date, 'Mon YY') AS label,
           TO_CHAR(posting_date, 'YYYY-MM') AS key,
           COALESCE(SUM(grand_total), 0) AS revenue
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY TO_CHAR(posting_date, 'Mon YY'), TO_CHAR(posting_date, 'YYYY-MM')
    ORDER BY key
""")

# ---- Top services (from Job Order service items) ----
top_services = q(f"""
    SELECT sii.item_name AS name,
           COUNT(sii.name) AS count,
           COALESCE(SUM(sii.amount), 0) AS revenue
    FROM "tabVehicle Job Order Item" sii
    JOIN "tabVehicle Job Order" vjo ON vjo.name = sii.parent
    WHERE vjo.docstatus = 1
      AND vjo.job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY sii.item_name
    ORDER BY revenue DESC
    LIMIT 10
""")

# ---- Top customers (by Job Order) ----
top_customers = q(f"""
    SELECT customer, customer_name,
           COUNT(name) AS visits,
           COALESCE(SUM(grand_total), 0) AS total_spent
    FROM "tabVehicle Job Order"
    WHERE docstatus = 1
      AND job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY customer, customer_name
    ORDER BY total_spent DESC
    LIMIT 10
""")

# ---- Vehicle mix (make distribution) ----
vehicle_mix = q(f"""
    SELECT COALESCE(make, 'Unknown') AS make, COUNT(name) AS count
    FROM "tabVehicle Job Order"
    WHERE docstatus = 1
      AND job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    GROUP BY make
    ORDER BY count DESC
    LIMIT 8
""")

# ---- Audit trail: recent synced transactions across doctypes ----
audit_trail = q(f"""
    SELECT 'Job Order' AS doc_type, name AS ref, customer AS party,
           grand_total AS amount, job_order_date AS date, modified_by, creation
    FROM "tabVehicle Job Order"
    WHERE docstatus = 1
      AND job_order_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    UNION ALL
    SELECT 'Estimate', name, customer, COALESCE(grand_total, 0), estimate_date, modified_by, creation
    FROM "tabVehicle Estimate"
    WHERE docstatus = 1
      AND estimate_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    UNION ALL
    SELECT 'Inspection', name, customer, 0, inspection_date, modified_by, creation
    FROM "tabVehicle Inspection"
    WHERE docstatus = 1
      AND inspection_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    UNION ALL
    SELECT 'Invoice', name, customer, COALESCE(grand_total, 0), posting_date, modified_by, creation
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN %(from_d)s AND %(to_d)s
      {co_filter}
    ORDER BY creation DESC
    LIMIT 30
""")

# ---- Company info + logo ----
company_info = None
if company:
    company_info = frappe.db.get_value(
        "Company", company,
        ["name", "abbr", "default_currency", "company_logo", "phone_no", "email"],
        as_dict=True,
    )

# ---- All companies (for switcher) ----
all_companies = frappe.db.sql(
    "SELECT name, abbr, company_logo FROM \"tabCompany\" WHERE name != %(mc)s ORDER BY name",
    {"mc": "My Company"},
    as_dict=True,
)

kpis = {
    "total_jo": jo.total_jo,
    "jo_revenue": jo.jo_revenue,
    "completed_jo": jo.completed,
    "in_progress_jo": jo.in_progress,
    "released_jo": jo.released,
    "paid_jo": jo.paid,
    "outstanding": jo.outstanding,
    "total_est": est.total_est,
    "est_value": est.est_value,
    "total_insp": insp.total_insp,
    "total_revenue": rev.total_revenue,
    "invoice_count": rev.invoice_count,
}

frappe.response["message"] = {
    "company": company or "All Companies",
    "company_info": company_info,
    "all_companies": all_companies,
    "period": period,
    "from_date": from_d,
    "to_date": to_d,
    "kpis": kpis,
    "jo_trend": jo_trend,
    "rev_trend": rev_trend,
    "top_services": top_services,
    "top_customers": top_customers,
    "vehicle_mix": vehicle_mix,
    "audit_trail": audit_trail,
}
'''

# ---- create / update the Server Script via ORM ----
SCRIPT_NAME = "VM Company Dashboard API"
API_METHOD = "vm_company_dashboard_api"

if frappe.db.exists("Server Script", SCRIPT_NAME):
    doc = frappe.get_doc("Server Script", SCRIPT_NAME)
    print("Updating existing Server Script:", SCRIPT_NAME)
else:
    doc = frappe.new_doc("Server Script")
    doc.name = SCRIPT_NAME
    print("Creating new Server Script:", SCRIPT_NAME)

doc.script_type = "API"
doc.api_method = API_METHOD
doc.allow_guest = 1
doc.enabled = 1
doc.script = SCRIPT
doc.insert(ignore_permissions=True) if doc.is_new() else doc.save(ignore_permissions=True)
frappe.db.commit()
print("Deployed:", SCRIPT_NAME, "| api_method:", API_METHOD)
