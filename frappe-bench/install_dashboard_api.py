"""
Vehicle Management Company Dashboard API
Server Script (whitelisted API) for ERPNext

Install via: python install_dashboard_api.py
"""
import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

# ─────────────────────────────────────────────
# 1.  Server Script (API)
# ─────────────────────────────────────────────
API_SCRIPT = '''
import frappe
from frappe.utils import nowdate, add_months, add_days, getdate, flt, cint
import json

@frappe.whitelist(allow_guest=True)
def get_company_dashboard(company=None, period="this_year"):
    """
    Returns aggregated analytics for the given company.
    If company is None, returns data for ALL companies (group).
    """
    today = getdate(nowdate())
    
    if period == "this_month":
        from_date = today.replace(day=1).strftime("%Y-%m-%d")
        to_date = nowdate()
    elif period == "last_month":
        first_this = today.replace(day=1)
        last_month_end = (first_this - frappe.utils.datetime.timedelta(days=1))
        from_date = last_month_end.replace(day=1).strftime("%Y-%m-%d")
        to_date = last_month_end.strftime("%Y-%m-%d")
    elif period == "this_year":
        from_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        to_date = nowdate()
    elif period == "last_year":
        from_date = today.replace(year=today.year-1, month=1, day=1).strftime("%Y-%m-%d")
        to_date = today.replace(year=today.year-1, month=12, day=31).strftime("%Y-%m-%d")
    else:  # all_time
        from_date = "2020-01-01"
        to_date = nowdate()

    co_filter = ""
    co_params = {"from_date": from_date, "to_date": to_date}
    if company:
        co_filter = " AND company = %(company)s"
        co_params["company"] = company

    vjo_filter = co_filter
    si_filter = co_filter

    # ── KPI Cards ──────────────────────────────────────────────
    # Revenue
    rev = frappe.db.sql("""
        SELECT
            COALESCE(SUM(grand_total), 0) AS total_revenue,
            COALESCE(SUM(total_taxes_and_charges), 0) AS total_tax,
            COALESCE(SUM(discount_amount), 0) AS total_discount,
            COUNT(name) AS invoice_count
        FROM "tabSales Invoice"
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + si_filter, co_params, as_dict=True)[0]

    # Job Orders
    jos = frappe.db.sql("""
        SELECT
            COUNT(name) AS total_jo,
            COALESCE(SUM(grand_total), 0) AS jo_revenue,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) AS completed,
            COUNT(CASE WHEN status = 'In Progress' THEN 1 END) AS in_progress,
            COUNT(CASE WHEN status = 'Released' THEN 1 END) AS released
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter, co_params, as_dict=True)[0]

    # Parts vs Labor
    parts_labor = frappe.db.sql("""
        SELECT
            COALESCE(SUM(CASE WHEN sii.item_group IN ('Services','Labor','Service')
                THEN sii.amount ELSE 0 END), 0) AS labor_revenue,
            COALESCE(SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor','Service')
                THEN sii.amount ELSE 0 END), 0) AS parts_revenue
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + ("AND si.company = %(company)s" if company else ""),
        co_params, as_dict=True)[0]

    # Purchase
    purchases = frappe.db.sql("""
        SELECT
            COALESCE(SUM(grand_total), 0) AS total_purchases,
            COUNT(name) AS po_count
        FROM "tabPurchase Order"
        WHERE docstatus = 1
          AND transaction_date BETWEEN %(from_date)s AND %(to_date)s
          """ + co_filter, co_params, as_dict=True)[0]

    # Unique customers served
    customers = frappe.db.sql("""
        SELECT COUNT(DISTINCT customer) AS unique_customers
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter, co_params, as_dict=True)[0]

    # Unique vehicles served
    vehicles = frappe.db.sql("""
        SELECT COUNT(DISTINCT plate_no) AS unique_vehicles
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter, co_params, as_dict=True)[0]

    # Commission / Sales Incentives
    commissions = frappe.db.sql("""
        SELECT COALESCE(SUM(si.grand_total * COALESCE(st.commission_rate::numeric, 0) / 100), 0) AS total_commissions
        FROM "tabSales Team" st
        JOIN "tabSales Invoice" si ON si.name = st.parent AND st.parenttype = 'Sales Invoice'
        WHERE si.docstatus = 1
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + ("AND si.company = %(company)s" if company else ""),
        co_params, as_dict=True)[0]

    # ── Monthly Revenue Trend ──────────────────────────────────
    monthly_trend = frappe.db.sql("""
        SELECT
            TO_CHAR(posting_date, 'Mon YY') AS month_label,
            TO_CHAR(posting_date, 'YYYY-MM') AS month_key,
            COALESCE(SUM(grand_total), 0) AS revenue,
            COUNT(name) AS invoices
        FROM "tabSales Invoice"
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + si_filter + """
        GROUP BY TO_CHAR(posting_date, 'Mon YY'), TO_CHAR(posting_date, 'YYYY-MM')
        ORDER BY month_key
    """, co_params, as_dict=True)

    # ── Monthly JO Trend ──────────────────────────────────────
    jo_trend = frappe.db.sql("""
        SELECT
            TO_CHAR(job_order_date, 'Mon YY') AS month_label,
            TO_CHAR(job_order_date, 'YYYY-MM') AS month_key,
            COUNT(name) AS jo_count,
            COALESCE(SUM(grand_total), 0) AS jo_revenue
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter + """
        GROUP BY TO_CHAR(job_order_date, 'Mon YY'), TO_CHAR(job_order_date, 'YYYY-MM')
        ORDER BY month_key
    """, co_params, as_dict=True)

    # ── Top Customers ─────────────────────────────────────────
    top_customers = frappe.db.sql("""
        SELECT
            customer,
            COUNT(name) AS visit_count,
            COALESCE(SUM(grand_total), 0) AS total_spent
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter + """
        GROUP BY customer
        ORDER BY total_spent DESC
        LIMIT 10
    """, co_params, as_dict=True)

    # ── Top Vehicles ──────────────────────────────────────────
    top_vehicles = frappe.db.sql("""
        SELECT
            COALESCE(vehicle, 'Unknown') AS vehicle,
            COUNT(name) AS visit_count,
            COALESCE(SUM(grand_total), 0) AS total_revenue
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter + """
        GROUP BY COALESCE(vehicle, 'Unknown')
        ORDER BY visit_count DESC
        LIMIT 10
    """, co_params, as_dict=True)

    # ── Top Services ──────────────────────────────────────────
    top_services = frappe.db.sql("""
        SELECT
            sii.item_name AS service,
            COUNT(sii.name) AS usage_count,
            COALESCE(SUM(sii.amount), 0) AS total_revenue
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND sii.item_group IN ('Services','Labor','Service')
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + ("AND si.company = %(company)s" if company else "") + """
        GROUP BY sii.item_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """, co_params, as_dict=True)

    # ── Top Products (Parts) ──────────────────────────────────
    top_products = frappe.db.sql("""
        SELECT
            sii.item_name AS product,
            COUNT(sii.name) AS usage_count,
            COALESCE(SUM(sii.qty), 0) AS total_qty,
            COALESCE(SUM(sii.amount), 0) AS total_revenue
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name = sii.parent
        WHERE si.docstatus = 1
          AND sii.item_group NOT IN ('Services','Labor','Service')
          AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + ("AND si.company = %(company)s" if company else "") + """
        GROUP BY sii.item_name
        ORDER BY total_revenue DESC
        LIMIT 10
    """, co_params, as_dict=True)

    # ── Audit Trail (recent transactions) ──────────────────────
    audit_trail = frappe.db.sql("""
        SELECT
            'Sales Invoice' AS doc_type,
            name AS reference,
            customer AS party,
            grand_total AS amount,
            posting_date AS date,
            creation,
            modified_by
        FROM "tabSales Invoice"
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + si_filter + """
        UNION ALL
        SELECT
            'Vehicle Job Order' AS doc_type,
            name AS reference,
            customer AS party,
            COALESCE(grand_total, 0) AS amount,
            job_order_date AS date,
            creation,
            modified_by
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          AND job_order_date BETWEEN %(from_date)s AND %(to_date)s
          """ + vjo_filter + """
        UNION ALL
        SELECT
            'Payment Entry' AS doc_type,
            name AS reference,
            party AS party,
            paid_amount AS amount,
            posting_date AS date,
            creation,
            modified_by
        FROM "tabPayment Entry"
        WHERE docstatus = 1
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
          """ + co_filter + """
        ORDER BY creation DESC
        LIMIT 30
    """, co_params, as_dict=True)

    # ── Due for Service ───────────────────────────────────────
    due_service = frappe.db.sql("""
        SELECT
            customer,
            vehicle,
            plate_no,
            MAX(job_order_date) AS last_visit,
            MAX(job_order_date) + INTERVAL '90 days' AS next_due,
            (MAX(job_order_date) + INTERVAL '90 days' - CURRENT_DATE) AS days_until_due
        FROM "tabVehicle Job Order"
        WHERE docstatus = 1
          """ + vjo_filter + """
        GROUP BY customer, vehicle, plate_no
        HAVING (MAX(job_order_date) + INTERVAL '90 days') >= CURRENT_DATE
        ORDER BY next_due ASC
        LIMIT 15
    """, co_params, as_dict=True)

    # ── Company Info ──────────────────────────────────────────
    company_info = None
    if company:
        company_info = frappe.db.get_value(
            "Company", company,
            ["name", "abbr", "default_currency", "company_logo", "phone_no", "email"],
            as_dict=True
        )

    # ── All Companies list (for switcher) ─────────────────────
    all_companies = frappe.db.sql(
        'SELECT name, abbr, company_logo FROM "tabCompany" WHERE name != %(mc)s ORDER BY name',
        {"mc": "My Company"},
        as_dict=True
    )

    return {
        "company": company or "All Companies",
        "company_info": company_info,
        "all_companies": all_companies,
        "period": period,
        "from_date": from_date,
        "to_date": to_date,
        "kpis": {
            "total_revenue": flt(rev.total_revenue, 2),
            "total_tax": flt(rev.total_tax, 2),
            "total_discount": flt(rev.total_discount, 2),
            "invoice_count": cint(rev.invoice_count),
            "total_jo": cint(jos.total_jo),
            "jo_revenue": flt(jos.jo_revenue, 2),
            "completed_jo": cint(jos.completed),
            "in_progress_jo": cint(jos.in_progress),
            "released_jo": cint(jos.released),
            "labor_revenue": flt(parts_labor.labor_revenue, 2),
            "parts_revenue": flt(parts_labor.parts_revenue, 2),
            "total_purchases": flt(purchases.total_purchases, 2),
            "po_count": cint(purchases.po_count),
            "unique_customers": cint(customers.unique_customers),
            "unique_vehicles": cint(vehicles.unique_vehicles),
            "total_commissions": flt(commissions.total_commissions, 2),
        },
        "monthly_revenue_trend": monthly_trend,
        "monthly_jo_trend": jo_trend,
        "top_customers": top_customers,
        "top_vehicles": top_vehicles,
        "top_services": top_services,
        "top_products": top_products,
        "audit_trail": audit_trail,
        "due_for_service": due_service,
    }


@frappe.whitelist(allow_guest=True)
def get_all_companies_summary():
    """Returns per-company KPI summary for the company switcher."""
    companies = frappe.db.sql(
        'SELECT name, abbr, company_logo FROM "tabCompany" WHERE name != %(mc)s ORDER BY name',
        {"mc": "My Company"},
        as_dict=True
    )
    result = []
    for co in companies:
        kpi = frappe.db.sql("""
            SELECT
                COALESCE(SUM(grand_total), 0) AS revenue,
                COUNT(name) AS invoices
            FROM "tabSales Invoice"
            WHERE docstatus = 1
              AND company = %(co)s
              AND posting_date >= DATE_TRUNC('year', CURRENT_DATE)
        """, {"co": co.name}, as_dict=True)[0]
        
        jos = frappe.db.sql("""
            SELECT COUNT(name) AS jo_count
            FROM "tabVehicle Job Order"
            WHERE docstatus = 1
              AND company = %(co)s
              AND job_order_date >= DATE_TRUNC('year', CURRENT_DATE)
        """, {"co": co.name}, as_dict=True)[0]
        
        result.append({
            "name": co.name,
            "abbr": co.abbr,
            "logo": co.company_logo,
            "ytd_revenue": flt(kpi.revenue, 2),
            "ytd_invoices": cint(kpi.invoices),
            "ytd_jo_count": cint(jos.jo_count),
        })
    return result
'''

# ─────────────────────────────────────────────
# Install the Server Script
# ─────────────────────────────────────────────
from frappe.utils import now_datetime
now = now_datetime()

script_name = "VM Dashboard API"
exists = frappe.db.exists("Server Script", script_name)

if exists:
    frappe.db.sql(
        'UPDATE "tabServer Script" SET script=%s, modified=%s, modified_by=%s WHERE name=%s',
        (API_SCRIPT, now, 'Administrator', script_name)
    )
    print(f"UPDATED: {script_name}")
else:
    frappe.db.sql(
        '''INSERT INTO "tabServer Script"
           (name, script_type, api_method, allow_guest, script, enabled, creation, modified, modified_by, owner, docstatus)
           VALUES (%s, %s, %s, %s, %s, 1, %s, %s, %s, %s, 0)''',
        (script_name, 'API', 'vehicle_management_dashboard_api', 1,
         API_SCRIPT, now, now, 'Administrator', 'Administrator')
    )
    print(f"CREATED: {script_name}")

frappe.db.commit()
print("Server Script installed!")
