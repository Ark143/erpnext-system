# -*- coding: utf-8 -*-
"""
Deploy the VM Per-Company Analytics Dashboard Server Script API.

Creates/updates a Server Script (script_type=API) named
"VM Company Dashboard API" with api_method "vm_company_dashboard_api".

RestrictedPython SAFE rules (verified this session):
  - NO `import`  (frappe is pre-bound)
  - NO int() / cint() / str.format()  -> use f-strings
  - NO augmented assignment on dict items (x = x + y)
  - NO leading-underscore names
  - NO `return` at module level; NO lambda; NO tuple unpacking
  - strftime / .format() blocked -> use fmt() f-string helper
  - str literals for dates in SQL (no %(...)s placeholders)
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

# date formatter (strftime + str.format blocked by sandbox guard)
def fmt(d):
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"

# ---- date range ----
today = frappe.utils.getdate(frappe.utils.nowdate())
if period == "this_month":
    from_d = fmt(today.replace(day=1))
    to_d = frappe.utils.nowdate()
elif period == "last_month":
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
    from_d = f"{ly:04d}-{lm:02d}-01"
    to_d = f"{ly:04d}-{lm:02d}-{lday:02d}"
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
co_filter_item = ""
co_filter_sle = ""
if company:
    co_filter = " AND company = %(company)s"
    co_filter_item = f" AND b.company = '{company}'"
    co_filter_sle = f" AND s.item_code IN (SELECT item_code FROM \"tabBin\" WHERE company = '{company}')"

def q(sql):
    p = {}
    if company:
        p["company"] = company
    return frappe.db.sql(sql, p, as_dict=True)

# ================= SALES =================
sales = q(f"""
    SELECT
        COUNT(name) AS invoice_count,
        COALESCE(SUM(grand_total), 0) AS revenue,
        COALESCE(SUM(outstanding_amount), 0) AS outstanding,
        COALESCE(SUM(base_grand_total), 0) AS base_revenue
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
""")[0]

# sales trend by month
sales_trend = q(f"""
    SELECT TO_CHAR(posting_date, 'Mon YY') AS label,
           TO_CHAR(posting_date, 'YYYY-MM') AS key,
           COALESCE(SUM(grand_total), 0) AS revenue,
           COUNT(name) AS count
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY TO_CHAR(posting_date, 'Mon YY'), TO_CHAR(posting_date, 'YYYY-MM')
    ORDER BY key
""")

# top sales reps (by document owner) — honest proxy for "sales employee"
top_sales_reps = q(f"""
    SELECT owner, COUNT(name) AS invoices, COALESCE(SUM(grand_total), 0) AS revenue
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY owner ORDER BY revenue DESC LIMIT 10
""")
for r in top_sales_reps:
    uname = r["owner"] or ""
    full = frappe.db.get_value("User", uname, "full_name") if uname else None
    r["rep"] = full or uname

# top products (by SI item amount)
top_products = q(f"""
    SELECT sii.item_code AS item, sii.item_name AS name,
           SUM(sii.qty) AS qty, COALESCE(SUM(sii.amount), 0) AS amount
    FROM "tabSales Invoice Item" sii
    JOIN "tabSales Invoice" si ON si.name = sii.parent
    WHERE si.docstatus = 1
      AND si.posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY sii.item_code, sii.item_name
    ORDER BY amount DESC LIMIT 10
""")

# top services (VM Job Order service items)
top_services = q(f"""
    SELECT sii.description AS name, COUNT(sii.name) AS count,
           COALESCE(SUM(sii.total_amount), 0) AS revenue
    FROM "tabJob Order Service Item" sii
    JOIN "tabVehicle Job Order" vjo ON vjo.name = sii.parent
    WHERE vjo.docstatus = 1
      AND vjo.job_order_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY sii.description ORDER BY revenue DESC LIMIT 10
""")

# top technicians (VM Job Order mechanic)
top_technicians = q(f"""
    SELECT sii.mechanic AS name, COUNT(DISTINCT sii.parent) AS jobs,
           COALESCE(SUM(sii.total_amount), 0) AS revenue
    FROM "tabJob Order Service Item" sii
    JOIN "tabVehicle Job Order" vjo ON vjo.name = sii.parent
    WHERE vjo.docstatus = 1
      AND vjo.job_order_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY sii.mechanic ORDER BY jobs DESC LIMIT 10
""")

# ================= COLLECTION / AGING =================
aging = q(f"""
    SELECT
        COUNT(CASE WHEN due_date >= '{to_d}' THEN 1 END) AS current_cnt,
        COALESCE(SUM(CASE WHEN due_date >= '{to_d}' THEN outstanding_amount ELSE 0 END), 0) AS current_amt,
        COUNT(CASE WHEN due_date < '{to_d}' AND due_date >= '{from_d}' THEN 1 END) AS d30_cnt,
        COALESCE(SUM(CASE WHEN due_date < '{to_d}' AND due_date >= '{from_d}' THEN outstanding_amount ELSE 0 END), 0) AS d30_amt,
        COUNT(CASE WHEN outstanding_amount > 0 AND due_date < '{from_d}' THEN 1 END) AS overdue_cnt,
        COALESCE(SUM(CASE WHEN outstanding_amount > 0 AND due_date < '{from_d}' THEN outstanding_amount ELSE 0 END), 0) AS overdue_amt
    FROM "tabSales Invoice"
    WHERE docstatus = 1 AND outstanding_amount > 0
      {co_filter}
""")[0]

top_customers = q(f"""
    SELECT customer, customer_name AS name,
           COUNT(name) AS invoices, COALESCE(SUM(grand_total), 0) AS revenue,
           COALESCE(SUM(outstanding_amount), 0) AS outstanding
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY customer, customer_name ORDER BY revenue DESC LIMIT 10
""")

# ================= EXPENSE / PURCHASE =================
expense = q(f"""
    SELECT COUNT(name) AS pi_count,
           COALESCE(SUM(grand_total), 0) AS expense_total,
           COALESCE(SUM(outstanding_amount), 0) AS outstanding
    FROM "tabPurchase Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
""")[0]

top_suppliers = q(f"""
    SELECT supplier, COUNT(name) AS bills, COALESCE(SUM(grand_total), 0) AS total
    FROM "tabPurchase Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    GROUP BY supplier ORDER BY total DESC LIMIT 10
""")

# ================= INVENTORY =================
# inventory balance: top items by qty * valuation_rate
inv_balance = q(f"""
    SELECT b.item_code AS item, i.item_name AS name, i.stock_uom AS uom,
           SUM(b.actual_qty) AS qty,
           COALESCE(i.valuation_rate, 0) AS rate,
           SUM(b.actual_qty) * COALESCE(i.valuation_rate, 0) AS value
    FROM "tabBin" b
    JOIN "tabItem" i ON i.name = b.item_code
    WHERE b.actual_qty > 0
      {co_filter_item}
    GROUP BY b.item_code, i.item_name, i.stock_uom, i.valuation_rate
    ORDER BY value DESC LIMIT 10
""")

# inventory movement (recent Stock Ledger Entries)
inv_movement = q(f"""
    SELECT item_code AS item, warehouse, voucher_type AS doctype, voucher_no AS name,
           actual_qty AS qty, posting_date AS date
    FROM "tabStock Ledger Entry" s
    WHERE is_cancelled = 0
      {co_filter_sle}
    ORDER BY posting_date DESC LIMIT 10
""")

# inventory aging: days since last movement per item
inv_aging = q(f"""
    SELECT s.item_code AS item, i.item_name AS name,
           MAX(s.posting_date) AS last_move,
           COUNT(s.name) AS moves
    FROM "tabStock Ledger Entry" s
    JOIN "tabItem" i ON i.name = s.item_code
    WHERE s.is_cancelled = 0
      {co_filter_sle}
    GROUP BY s.item_code, i.item_name
    ORDER BY MAX(s.posting_date) ASC LIMIT 10
""")

# bin locations (VM Bin Location doctype)
bin_locations = q(f"""
    SELECT bin_location_name AS name, warehouse, zone, rack, shelf, bin_no, description
    FROM "tabBin Location"
    WHERE 1=1
      {co_filter}
    ORDER BY warehouse, bin_location_name LIMIT 10
""")

# ================= APPROVALS =================
def approvals_for(doctype, pending_where, approved_where, date_col, party_col, amount_expr):
    party_expr = party_col if party_col else "''"
    pending = q(f"""
        SELECT name, {party_expr} AS party, {amount_expr} AS amount, {date_col} AS date, docstatus
        FROM "tab{doctype}"
        WHERE {pending_where}
          {co_filter}
        ORDER BY creation DESC LIMIT 10
    """)
    approved = q(f"""
        SELECT name, {party_expr} AS party, {amount_expr} AS amount, {date_col} AS date, docstatus
        FROM "tab{doctype}"
        WHERE {approved_where}
          {co_filter}
        ORDER BY modified DESC LIMIT 10
    """)
    pending_count = frappe.db.count(doctype, {"docstatus": 0}) if not company else frappe.db.count(doctype, {"docstatus": 0, "company": company})
    return {"pending": pending, "approved": approved, "pending_count": pending_count}

appr_po = approvals_for("Purchase Order", "docstatus = 0 AND status IN ('Draft','Submitted','Open','To Receive and Bill')", "docstatus = 1 AND status IN ('Completed','Closed','Received')", "transaction_date", "COALESCE(supplier,'')", "COALESCE(grand_total,0)")
appr_pi = approvals_for("Purchase Invoice", "docstatus = 0 AND status IN ('Draft','Submitted','Unpaid','Overdue','Partly Paid')", "docstatus = 1 AND status IN ('Paid','Unpaid')", "posting_date", "COALESCE(supplier,'')", "COALESCE(grand_total,0)")
appr_mr = approvals_for("Material Request", "docstatus = 0", "docstatus = 1", "transaction_date", "''", "0")
appr_se = approvals_for("Stock Entry", "docstatus = 0", "docstatus = 1", "posting_date", "''", "0")

# ================= MONTHLY / YEARLY VS INCOMING =================
def year_range(y):
    fy = f"{y:04d}-01-01"
    ty = f"{y:04d}-12-31"
    return fy, ty

ty_range = year_range(today.year)
ty_f = ty_range[0]
ty_t = ty_range[1]
ly_range = year_range(today.year - 1)
ly_f = ly_range[0]
ly_t = ly_range[1]

sales_this_year = frappe.db.sql(f"""
    SELECT COALESCE(SUM(grand_total),0) AS v FROM "tabSales Invoice"
    WHERE docstatus=1 AND posting_date BETWEEN '{ty_f}' AND '{ty_t}'
    {co_filter}""", {}, as_dict=True)[0]["v"]
sales_last_year = frappe.db.sql(f"""
    SELECT COALESCE(SUM(grand_total),0) AS v FROM "tabSales Invoice"
    WHERE docstatus=1 AND posting_date BETWEEN '{ly_f}' AND '{ly_t}'
    {co_filter}""", {}, as_dict=True)[0]["v"]
incoming_this_year = frappe.db.sql(f"""
    SELECT COALESCE(SUM(grand_total),0) AS v FROM "tabPurchase Invoice"
    WHERE docstatus=1 AND posting_date BETWEEN '{ty_f}' AND '{ty_t}'
    {co_filter}""", {}, as_dict=True)[0]["v"]

monthly_yearly = {
    "this_year_sales": sales_this_year,
    "last_year_sales": sales_last_year,
    "yoy_growth_pct": (sales_this_year - sales_last_year) if (sales_last_year > 0) else 0,
    "incoming_this_year": incoming_this_year,
    "net_position": sales_this_year - incoming_this_year,
}

# ================= SYNC / AUDIT TRAIL =================
sync_log = q(f"""
    SELECT 'Sales Invoice' AS doctype, name AS ref, customer AS party,
           grand_total AS amount, posting_date AS date, modified_by, creation
    FROM "tabSales Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    UNION ALL
    SELECT 'Purchase Invoice', name, supplier, COALESCE(grand_total,0), posting_date, modified_by, creation
    FROM "tabPurchase Invoice"
    WHERE docstatus = 1
      AND posting_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    UNION ALL
    SELECT 'Job Order', name, customer, COALESCE(grand_total,0), job_order_date, modified_by, creation
    FROM "tabVehicle Job Order"
    WHERE docstatus = 1
      AND job_order_date BETWEEN '{from_d}' AND '{to_d}'
      {co_filter}
    ORDER BY creation DESC LIMIT 30
""")

# ================= INSIGHTS / RECOMMENDATIONS =================
low_stock_count = frappe.db.count("Bin", {"actual_qty": ["<", 1]}) if not company else frappe.db.count("Bin", {"actual_qty": ["<", 1]})
insights = []
if aging and aging["overdue_amt"] > 0:
    insights.append({"type": "risk", "title": "Overdue receivables", "detail": f"{aging['overdue_cnt']} invoices overdue totalling {aging['overdue_amt']:.0f}"})
if expense and expense["outstanding"] > 0:
    insights.append({"type": "expense", "title": "Open payables", "detail": f"{expense['outstanding']:.0f} still payable to suppliers"})
if top_products:
    top1 = top_products[0]
    insights.append({"type": "top", "title": "Top product", "detail": f"{top1['name']} generated {top1['amount']:.0f}"})
if inv_aging:
    oldest = inv_aging[0]
    insights.append({"type": "inventory", "title": "Slowest mover", "detail": f"{oldest['name']} last moved {oldest['last_move']}"})
if monthly_yearly["yoy_growth_pct"] > 0:
    insights.append({"type": "growth", "title": "YoY growth", "detail": f"Sales up vs last year by {monthly_yearly['yoy_growth_pct']:.0f}"})

recommendations = [
    {"title": "Follow up overdue invoices", "detail": f"Collect {aging['overdue_amt']:.0f} across {aging['overdue_cnt']} invoices to improve cash flow"} if aging else {"title": "Collections", "detail": "No overdue receivables"},
    {"title": "Review slow movers", "detail": "Consider promotions for items with oldest last-movement dates"},
    {"title": "Approve pending documents", "detail": f"{appr_po['pending_count'] + appr_pi['pending_count'] + appr_mr['pending_count'] + appr_se['pending_count']} documents awaiting approval"},
]

# ================= COMPANY INFO =================
company_info = None
all_companies = []
if company:
    company_info = frappe.db.get_value("Company", company, ["name", "abbr", "default_currency", "company_logo", "phone_no", "email"], as_dict=True)
all_companies = frappe.db.sql("SELECT name, abbr, company_logo FROM \"tabCompany\" WHERE name != %(mc)s ORDER BY name", {"mc": "My Company"}, as_dict=True)

frappe.response["message"] = {
    "company": company or "All Companies",
    "company_info": company_info,
    "all_companies": all_companies,
    "period": period,
    "from_date": from_d,
    "to_date": to_d,
    "sales": sales,
    "sales_trend": sales_trend,
    "top_sales_reps": top_sales_reps,
    "top_products": top_products,
    "top_services": top_services,
    "top_technicians": top_technicians,
    "aging": aging,
    "top_customers": top_customers,
    "expense": expense,
    "top_suppliers": top_suppliers,
    "inv_balance": inv_balance,
    "inv_movement": inv_movement,
    "inv_aging": inv_aging,
    "bin_locations": bin_locations,
    "appr_po": appr_po,
    "appr_pi": appr_pi,
    "appr_mr": appr_mr,
    "appr_se": appr_se,
    "monthly_yearly": monthly_yearly,
    "sync_log": sync_log,
    "insights": insights,
    "recommendations": recommendations,
}
'''

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
if doc.is_new():
    doc.insert(ignore_permissions=True)
else:
    doc.save(ignore_permissions=True)
frappe.db.commit()
print("Deployed:", SCRIPT_NAME, "| api_method:", API_METHOD)
