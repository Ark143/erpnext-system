"""
Vehicle Management - Company Dashboard API
Provides aggregated analytics endpoints for the per-company web dashboard.
"""

import frappe
from frappe.utils import nowdate, getdate, flt, cint
import datetime


def _get_date_range(period: str):
    today = getdate(nowdate())
    if period == "this_month":
        return today.replace(day=1).strftime("%Y-%m-%d"), nowdate()
    if period == "last_month":
        first_this = today.replace(day=1)
        end = first_this - datetime.timedelta(days=1)
        return end.replace(day=1).strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    if period == "this_year":
        return today.replace(month=1, day=1).strftime("%Y-%m-%d"), nowdate()
    if period == "last_year":
        y = today.year - 1
        return f"{y}-01-01", f"{y}-12-31"
    # all_time
    return "2020-01-01", nowdate()


@frappe.whitelist(allow_guest=True)
def get_company_dashboard(company=None, period="this_year"):
    """
    Returns aggregated analytics for the given company.
    company=None → all companies combined.
    """
    from_date, to_date = _get_date_range(period)

    base_params = {"from_date": from_date, "to_date": to_date}
    si_where = "si.docstatus = 1 AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    vjo_where = "vjo.docstatus = 1 AND vjo.job_order_date BETWEEN %(from_date)s AND %(to_date)s"
    pe_where = "pe.docstatus = 1 AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    po_where = "po.docstatus = 1 AND po.transaction_date BETWEEN %(from_date)s AND %(to_date)s"

    if company:
        base_params["company"] = company
        si_where += " AND si.company = %(company)s"
        vjo_where += " AND vjo.company = %(company)s"
        pe_where += " AND pe.company = %(company)s"
        po_where += " AND po.company = %(company)s"

    def q(sql, params=None):
        return frappe.db.sql(sql, params or base_params, as_dict=True)

    # ── KPIs ─────────────────────────────────────────────────
    rev = q(f"""
        SELECT COALESCE(SUM(grand_total),0) AS total_revenue,
               COALESCE(SUM(total_taxes_and_charges),0) AS total_tax,
               COALESCE(SUM(discount_amount),0) AS total_discount,
               COUNT(name) AS invoice_count
        FROM "tabSales Invoice" si WHERE {si_where}
    """)[0]

    jos = q(f"""
        SELECT COUNT(name) AS total_jo,
               COALESCE(SUM(grand_total),0) AS jo_revenue,
               COUNT(CASE WHEN status='Completed' THEN 1 END) AS completed,
               COUNT(CASE WHEN status='In Progress' THEN 1 END) AS in_progress,
               COUNT(CASE WHEN status='Released' THEN 1 END) AS released
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
    """)[0]

    pl = q(f"""
        SELECT
            COALESCE(SUM(CASE WHEN sii.item_group IN ('Services','Labor','Service')
                THEN sii.amount ELSE 0 END),0) AS labor_revenue,
            COALESCE(SUM(CASE WHEN sii.item_group NOT IN ('Services','Labor','Service')
                THEN sii.amount ELSE 0 END),0) AS parts_revenue
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name=sii.parent
        WHERE {si_where}
    """)[0]

    purch = q(f"""
        SELECT COALESCE(SUM(grand_total),0) AS total_purchases, COUNT(name) AS po_count
        FROM "tabPurchase Order" po WHERE {po_where}
    """)[0]

    cust_v = q(f"""
        SELECT COUNT(DISTINCT customer) AS unique_customers,
               COUNT(DISTINCT plate_no) AS unique_vehicles
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
    """)[0]

    comm = q(f"""
        SELECT COALESCE(SUM(si.grand_total * COALESCE(st.commission_rate::numeric,0)/100),0)
               AS total_commissions
        FROM "tabSales Team" st
        JOIN "tabSales Invoice" si ON si.name=st.parent AND st.parenttype='Sales Invoice'
        WHERE {si_where}
    """)[0]

    payments = q(f"""
        SELECT COALESCE(SUM(paid_amount),0) AS total_collected, COUNT(name) AS payment_count
        FROM "tabPayment Entry" pe WHERE {pe_where} AND payment_type='Receive'
    """)[0]

    # ── Trends ───────────────────────────────────────────────
    rev_trend = q(f"""
        SELECT TO_CHAR(posting_date,'Mon YY') AS label,
               TO_CHAR(posting_date,'YYYY-MM') AS key,
               COALESCE(SUM(grand_total),0) AS revenue,
               COUNT(name) AS count
        FROM "tabSales Invoice" si WHERE {si_where}
        GROUP BY TO_CHAR(posting_date,'Mon YY'), TO_CHAR(posting_date,'YYYY-MM')
        ORDER BY key
    """)

    jo_trend = q(f"""
        SELECT TO_CHAR(job_order_date,'Mon YY') AS label,
               TO_CHAR(job_order_date,'YYYY-MM') AS key,
               COUNT(name) AS jo_count,
               COALESCE(SUM(grand_total),0) AS revenue
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
        GROUP BY TO_CHAR(job_order_date,'Mon YY'), TO_CHAR(job_order_date,'YYYY-MM')
        ORDER BY key
    """)

    # ── Top Lists ─────────────────────────────────────────────
    top_customers = q(f"""
        SELECT customer, COUNT(name) AS visits,
               COALESCE(SUM(grand_total),0) AS total_spent
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
        GROUP BY customer ORDER BY total_spent DESC LIMIT 10
    """)

    top_vehicles = q(f"""
        SELECT COALESCE(vehicle,'Unknown') AS vehicle,
               COUNT(name) AS visits,
               COALESCE(SUM(grand_total),0) AS revenue
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
        GROUP BY COALESCE(vehicle,'Unknown') ORDER BY visits DESC LIMIT 10
    """)

    top_services = q(f"""
        SELECT sii.item_name AS name,
               COUNT(sii.name) AS count,
               COALESCE(SUM(sii.amount),0) AS revenue
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name=sii.parent
        WHERE {si_where} AND sii.item_group IN ('Services','Labor','Service')
        GROUP BY sii.item_name ORDER BY revenue DESC LIMIT 10
    """)

    top_products = q(f"""
        SELECT sii.item_name AS name,
               COUNT(sii.name) AS count,
               COALESCE(SUM(sii.qty),0) AS qty,
               COALESCE(SUM(sii.amount),0) AS revenue
        FROM "tabSales Invoice Item" sii
        JOIN "tabSales Invoice" si ON si.name=sii.parent
        WHERE {si_where} AND sii.item_group NOT IN ('Services','Labor','Service')
        GROUP BY sii.item_name ORDER BY revenue DESC LIMIT 10
    """)

    # ── Audit Trail ───────────────────────────────────────────
    audit = q(f"""
        SELECT 'Sales Invoice' AS doc_type, name AS ref, customer AS party,
               grand_total AS amount, posting_date AS date,
               owner AS created_by, modified_by, creation
        FROM "tabSales Invoice" si WHERE {si_where}
        UNION ALL
        SELECT 'Job Order', name, customer, COALESCE(grand_total,0),
               job_order_date, owner, modified_by, creation
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
        UNION ALL
        SELECT 'Payment', name, party, paid_amount,
               posting_date, owner, modified_by, creation
        FROM "tabPayment Entry" pe
        WHERE {pe_where} AND payment_type='Receive'
        ORDER BY creation DESC LIMIT 30
    """)

    # ── Due for Service ───────────────────────────────────────
    due = q(f"""
        SELECT customer, vehicle, plate_no,
               MAX(job_order_date) AS last_visit,
               MAX(job_order_date) + INTERVAL '90 days' AS next_due,
               (MAX(job_order_date) + INTERVAL '90 days' - CURRENT_DATE) AS days_left
        FROM "tabVehicle Job Order" vjo WHERE {vjo_where}
        GROUP BY customer, vehicle, plate_no
        HAVING (MAX(job_order_date) + INTERVAL '90 days') >= CURRENT_DATE
        ORDER BY next_due LIMIT 15
    """)

    # ── Company Info ──────────────────────────────────────────
    co_info = None
    if company and frappe.db.exists("Company", company):
        co_info = frappe.db.get_value(
            "Company", company,
            ["name", "abbr", "default_currency", "company_logo", "phone_no", "email"],
            as_dict=True,
        )

    all_companies = frappe.db.sql(
        'SELECT name, abbr, company_logo FROM "tabCompany" WHERE name!=%(mc)s ORDER BY name',
        {"mc": "My Company"},
        as_dict=True,
    )

    return {
        "company": company or "All Companies",
        "company_info": co_info,
        "all_companies": all_companies,
        "period": period,
        "from_date": from_date,
        "to_date": to_date,
        "kpis": {
            "total_revenue": flt(rev.total_revenue, 2),
            "invoice_count": cint(rev.invoice_count),
            "total_tax": flt(rev.total_tax, 2),
            "total_discount": flt(rev.total_discount, 2),
            "total_jo": cint(jos.total_jo),
            "jo_revenue": flt(jos.jo_revenue, 2),
            "completed_jo": cint(jos.completed),
            "in_progress_jo": cint(jos.in_progress),
            "released_jo": cint(jos.released),
            "labor_revenue": flt(pl.labor_revenue, 2),
            "parts_revenue": flt(pl.parts_revenue, 2),
            "total_purchases": flt(purch.total_purchases, 2),
            "po_count": cint(purch.po_count),
            "unique_customers": cint(cust_v.unique_customers),
            "unique_vehicles": cint(cust_v.unique_vehicles),
            "total_commissions": flt(comm.total_commissions, 2),
            "total_collected": flt(payments.total_collected, 2),
            "payment_count": cint(payments.payment_count),
        },
        "revenue_trend": rev_trend,
        "jo_trend": jo_trend,
        "top_customers": top_customers,
        "top_vehicles": top_vehicles,
        "top_services": top_services,
        "top_products": top_products,
        "audit_trail": audit,
        "due_for_service": due,
    }


@frappe.whitelist(allow_guest=True)
def get_all_companies_summary():
    """YTD summary card for each company — used on the hub page."""
    companies = frappe.db.sql(
        'SELECT name, abbr, company_logo FROM "tabCompany" WHERE name!=%(mc)s ORDER BY name',
        {"mc": "My Company"},
        as_dict=True,
    )
    out = []
    for co in companies:
        kpi = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total),0) AS revenue,
                   COUNT(name) AS invoices
            FROM "tabSales Invoice"
            WHERE docstatus=1 AND company=%(co)s
              AND posting_date >= DATE_TRUNC('year', CURRENT_DATE)
        """, {"co": co.name}, as_dict=True)[0]

        jos = frappe.db.sql("""
            SELECT COUNT(name) AS jo_count
            FROM "tabVehicle Job Order"
            WHERE docstatus=1 AND company=%(co)s
              AND job_order_date >= DATE_TRUNC('year', CURRENT_DATE)
        """, {"co": co.name}, as_dict=True)[0]

        out.append({
            "name": co.name,
            "abbr": co.abbr,
            "logo": co.company_logo,
            "ytd_revenue": flt(kpi.revenue, 2),
            "ytd_invoices": cint(kpi.invoices),
            "ytd_jo_count": cint(jos.jo_count),
        })
    return out


@frappe.whitelist()
def get_inventory_logistics(company=None, limit=10):
    """
    Resolve Stock Ledger transactions along with their bin locations.
    Returns the most recent stock movements for the given company,
    newest first, capped at `limit` rows.
    """
    if not company:
        company = frappe.defaults.get_user_default("Company")
    if not company:
        frappe.throw("Company not found. Pass a `company` or set a default Company.")

    entries = frappe.db.sql(
        """
        SELECT
            sle.name,
            sle.item_code,
            sle.actual_qty,
            sle.warehouse,
            sle.voucher_type,
            sle.voucher_no,
            sle.posting_date,
            sle.posting_time,
            sle.bin_location
        FROM "tabStock Ledger Entry" sle
        WHERE sle.company = %(company)s
        ORDER BY sle.posting_date DESC, sle.posting_time DESC
        LIMIT %(limit)s
        """,
        {"company": company, "limit": cint(limit)},
        as_dict=True,
    )
    return entries


@frappe.whitelist(allow_guest=True)
def get_dashboard_cards(company=None, limit=10):
    """
    One call that returns the four live card lists for the operations
    dashboard: sales pipeline, inventory movement, action approvals,
    and expense velocity. Each list is real ERPNext data (no fabricated
    values).
    """
    if not company:
        company = frappe.defaults.get_user_default("Company")
    if not company:
        row = frappe.db.sql(
            'SELECT name FROM "tabCompany" WHERE name!=%(mc)s ORDER BY name LIMIT 1',
            {"mc": "My Company"},
            as_dict=True,
        )
        company = row[0]["name"] if row else None
    if not company:
        frappe.throw("No Company found.")

    lim = cint(limit)

    sales = frappe.db.sql(
        """
        SELECT name, customer, customer_name, grand_total, posting_date, status
        FROM "tabSales Invoice"
        WHERE docstatus = 1 AND company = %(company)s
        ORDER BY posting_date DESC, creation DESC
        LIMIT %(lim)s
        """,
        {"company": company, "lim": lim},
        as_dict=True,
    )

    inventory = get_inventory_logistics(company=company, limit=lim)

    approvals = frappe.db.sql(
        """
        SELECT name, supplier, grand_total, transaction_date, status
        FROM "tabPurchase Order"
        WHERE docstatus = 0 AND company = %(company)s
        ORDER BY transaction_date DESC, creation DESC
        LIMIT %(lim)s
        """,
        {"company": company, "lim": lim},
        as_dict=True,
    )

    expenses = frappe.db.sql(
        """
        SELECT name, supplier, grand_total, posting_date, status
        FROM "tabPurchase Invoice"
        WHERE docstatus = 1 AND company = %(company)s
        ORDER BY posting_date DESC, creation DESC
        LIMIT %(lim)s
        """,
        {"company": company, "lim": lim},
        as_dict=True,
    )

    currency = frappe.db.get_value("Company", company, "default_currency") or ""

    return {
        "company": company,
        "currency": currency,
        "sales": sales,
        "inventory": inventory,
        "approvals": approvals,
        "expenses": expenses,
    }
