import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
login_res.raise_for_status()
print("[OK] Logged in to VPS as Administrator")

SERVER_SCRIPT_CODE = '''# Server Script: VM Consolidated Financials API
# Method: vm_consolidated_financials

def get_data():
    report_type = frappe.form_dict.get("report_type") or "pnl"
    from_date = frappe.form_dict.get("from_date") or "2026-01-01"
    to_date = frappe.form_dict.get("to_date") or "2026-12-31"
    voucher_type = frappe.form_dict.get("voucher_type")
    search_text = frappe.form_dict.get("search_text")
    selected_companies_raw = frappe.form_dict.get("selected_companies")
    page = int(frappe.form_dict.get("page") or 1)
    page_length = int(frappe.form_dict.get("page_length") or 100)

    # 1. Fetch all companies
    companies_records = frappe.get_all(
        "Company",
        fields=["name", "abbr", "default_currency"],
        order_by="name asc"
    )
    all_companies = [c.get("name") for c in companies_records]
    company_meta = {c.get("name"): {"abbr": c.get("abbr"), "currency": c.get("default_currency") or "PHP"} for c in companies_records}

    # Filter companies if selected_companies passed
    companies = all_companies
    if selected_companies_raw:
        if isinstance(selected_companies_raw, str):
            clean_str = selected_companies_raw.replace("[", "").replace("]", "").replace("\\"", "").replace("'", "")
            parts = [p.strip() for p in clean_str.split(",") if p.strip()]
            if parts:
                filtered = [c for c in all_companies if c in parts]
                if filtered:
                    companies = filtered

    if not companies:
        companies = all_companies

    if report_type == "pnl":
        return get_pnl_data(companies, company_meta, all_companies, from_date, to_date)
    elif report_type == "balance_sheet":
        return get_balance_sheet_data(companies, company_meta, all_companies, to_date)
    elif report_type == "cash_flow":
        period_type = frappe.form_dict.get("period") or "monthly"
        return get_cash_flow_data(companies, company_meta, all_companies, from_date, to_date, period_type)
    elif report_type == "ar_aging":
        as_of_date = frappe.form_dict.get("as_of_date") or to_date or frappe.utils.nowdate()
        customer = frappe.form_dict.get("customer")
        return get_ar_aging_data(companies, company_meta, all_companies, as_of_date, customer)
    elif report_type == "ap_aging":
        as_of_date = frappe.form_dict.get("as_of_date") or to_date or frappe.utils.nowdate()
        supplier = frappe.form_dict.get("supplier")
        return get_ap_aging_data(companies, company_meta, all_companies, as_of_date, supplier)
    elif report_type == "general_ledger":
        return get_gl_data(companies, from_date, to_date, voucher_type, search_text, page, page_length)
    elif report_type == "inventory_audit":
        return get_inventory_data(companies, company_meta, all_companies, from_date, to_date, search_text)
    elif report_type == "drilldown":
        company = frappe.form_dict.get("company")
        account = frappe.form_dict.get("account")
        return get_drilldown_data(company, account, from_date, to_date)
    elif report_type == "stock_ledger_drilldown":
        item_code = frappe.form_dict.get("item_code")
        company = frappe.form_dict.get("company")
        return get_stock_ledger_drilldown(item_code, company, from_date, to_date)
    else:
        return {"error": "Invalid report_type: " + str(report_type)}

def get_pnl_data(companies, company_meta, all_companies, from_date, to_date):
    placeholders = ", ".join(["%s"] * len(companies))
    query = """
        SELECT 
            gle.company,
            gle.account,
            MAX(acc.account_name) as account_name,
            MAX(acc.root_type) as root_type,
            MAX(acc.account_type) as account_type,
            SUM(gle.debit) as total_debit,
            SUM(gle.credit) as total_credit
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.posting_date BETWEEN %s AND %s
          AND gle.is_cancelled = 0
          AND acc.root_type IN ('Income', 'Expense')
          AND gle.company IN (""" + placeholders + """)
        GROUP BY gle.company, gle.account
        ORDER BY MAX(acc.root_type) desc, MAX(acc.account_name) asc
    """
    gl_entries = frappe.db.sql(query, [from_date, to_date] + companies, as_dict=True)

    income_accounts = {}
    cogs_accounts = {}
    expense_accounts = {}

    for row in gl_entries:
        co = row.get("company")
        raw_name = row.get("account") or ""
        clean_name = row.get("account_name") or raw_name.split(" - ")[0].strip()
        root_type = row.get("root_type") or ""
        acc_type = row.get("account_type") or ""
        
        debit = float(row.get("total_debit") or 0)
        credit = float(row.get("total_credit") or 0)

        if root_type == "Income":
            net_amt = credit - debit
            target_dict = income_accounts
        else:
            net_amt = debit - credit
            if "cost of" in clean_name.lower() or "cogs" in clean_name.lower() or acc_type in ("Cost of Goods Sold", "Direct Expense"):
                target_dict = cogs_accounts
            else:
                target_dict = expense_accounts

        if clean_name not in target_dict:
            target_dict[clean_name] = {
                "account_name": clean_name,
                "root_type": root_type,
                "account_type": acc_type,
                "companies": {c: 0.0 for c in companies},
                "total": 0.0
            }
        
        target_dict[clean_name]["companies"][co] = target_dict[clean_name]["companies"][co] + net_amt
        target_dict[clean_name]["total"] = target_dict[clean_name]["total"] + net_amt

    income_rows = list(income_accounts.values())
    cogs_rows = list(cogs_accounts.values())
    expense_rows = list(expense_accounts.values())

    revenue_totals = {c: sum(r["companies"][c] for r in income_rows) for c in companies}
    revenue_consolidated = sum(r["total"] for r in income_rows)

    cogs_totals = {c: sum(r["companies"][c] for r in cogs_rows) for c in companies}
    cogs_consolidated = sum(r["total"] for r in cogs_rows)

    gross_profit_totals = {c: revenue_totals[c] - cogs_totals[c] for c in companies}
    gross_profit_consolidated = revenue_consolidated - cogs_consolidated

    expense_totals = {c: sum(r["companies"][c] for r in expense_rows) for c in companies}
    expense_consolidated = sum(r["total"] for r in expense_rows)

    net_profit_totals = {c: gross_profit_totals[c] - expense_totals[c] for c in companies}
    net_profit_consolidated = gross_profit_consolidated - expense_consolidated

    gross_margin_consolidated = round((gross_profit_consolidated / revenue_consolidated * 100), 1) if revenue_consolidated > 0 else 0.0
    net_margin_consolidated = round((net_profit_consolidated / revenue_consolidated * 100), 1) if revenue_consolidated > 0 else 0.0

    return {
        "report": "Consolidated Profit & Loss",
        "from_date": from_date,
        "to_date": to_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "sections": {
            "income": {
                "title": "Operating Revenue",
                "rows": income_rows,
                "totals": revenue_totals,
                "consolidated": revenue_consolidated
            },
            "cogs": {
                "title": "Cost of Goods Sold & Direct Expenses",
                "rows": cogs_rows,
                "totals": cogs_totals,
                "consolidated": cogs_consolidated
            },
            "gross_profit": {
                "title": "Gross Profit",
                "totals": gross_profit_totals,
                "consolidated": gross_profit_consolidated,
                "consolidated_margin_pct": gross_margin_consolidated
            },
            "operating_expenses": {
                "title": "Operating Expenses",
                "rows": expense_rows,
                "totals": expense_totals,
                "consolidated": expense_consolidated
            },
            "net_profit": {
                "title": "Net Operating Income / (Loss)",
                "totals": net_profit_totals,
                "consolidated": net_profit_consolidated,
                "consolidated_margin_pct": net_margin_consolidated
            }
        },
        "kpis": {
            "consolidated_revenue": revenue_consolidated,
            "consolidated_cogs": cogs_consolidated,
            "consolidated_gross_profit": gross_profit_consolidated,
            "consolidated_expenses": expense_consolidated,
            "consolidated_net_profit": net_profit_consolidated,
            "consolidated_net_margin": net_margin_consolidated
        }
    }

def get_balance_sheet_data(companies, company_meta, all_companies, to_date):
    placeholders = ", ".join(["%s"] * len(companies))
    query = """
        SELECT 
            gle.company,
            gle.account,
            MAX(acc.account_name) as account_name,
            MAX(acc.root_type) as root_type,
            MAX(acc.account_type) as account_type,
            SUM(gle.debit) as total_debit,
            SUM(gle.credit) as total_credit
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.posting_date <= %s
          AND gle.is_cancelled = 0
          AND acc.root_type IN ('Asset', 'Liability', 'Equity')
          AND gle.company IN (""" + placeholders + """)
        GROUP BY gle.company, gle.account
        ORDER BY MAX(acc.root_type) asc, MAX(acc.account_name) asc
    """
    gl_entries = frappe.db.sql(query, [to_date] + companies, as_dict=True)

    assets_accounts = {}
    liabilities_accounts = {}
    equity_accounts = {}

    for row in gl_entries:
        co = row.get("company")
        raw_name = row.get("account") or ""
        clean_name = row.get("account_name") or raw_name.split(" - ")[0].strip()
        root_type = row.get("root_type") or ""
        acc_type = row.get("account_type") or ""
        
        debit = float(row.get("total_debit") or 0)
        credit = float(row.get("total_credit") or 0)

        if root_type == "Asset":
            net_amt = debit - credit
            target_dict = assets_accounts
        elif root_type == "Liability":
            net_amt = credit - debit
            target_dict = liabilities_accounts
        else: # Equity
            net_amt = credit - debit
            target_dict = equity_accounts

        if clean_name not in target_dict:
            target_dict[clean_name] = {
                "account_name": clean_name,
                "root_type": root_type,
                "account_type": acc_type,
                "companies": {c: 0.0 for c in companies},
                "total": 0.0
            }
        
        target_dict[clean_name]["companies"][co] = target_dict[clean_name]["companies"][co] + net_amt
        target_dict[clean_name]["total"] = target_dict[clean_name]["total"] + net_amt

    asset_rows = list(assets_accounts.values())
    liability_rows = list(liabilities_accounts.values())
    equity_rows = list(equity_accounts.values())

    asset_totals = {c: sum(r["companies"][c] for r in asset_rows) for c in companies}
    asset_consolidated = sum(r["total"] for r in asset_rows)

    liability_totals = {c: sum(r["companies"][c] for r in liability_rows) for c in companies}
    liability_consolidated = sum(r["total"] for r in liability_rows)

    equity_totals = {c: sum(r["companies"][c] for r in equity_rows) for c in companies}
    equity_consolidated = sum(r["total"] for r in equity_rows)

    total_liab_equity = {c: liability_totals[c] + equity_totals[c] for c in companies}
    total_liab_equity_consolidated = liability_consolidated + equity_consolidated

    return {
        "report": "Consolidated Balance Sheet",
        "as_of_date": to_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "sections": {
            "assets": {
                "title": "Assets",
                "rows": asset_rows,
                "totals": asset_totals,
                "consolidated": asset_consolidated
            },
            "liabilities": {
                "title": "Liabilities",
                "rows": liability_rows,
                "totals": liability_totals,
                "consolidated": liability_consolidated
            },
            "equity": {
                "title": "Equity",
                "rows": equity_rows,
                "totals": equity_totals,
                "consolidated": equity_consolidated
            },
            "total_liab_equity": {
                "title": "Total Liabilities & Equity",
                "totals": total_liab_equity,
                "consolidated": total_liab_equity_consolidated
            }
        },
        "kpis": {
            "consolidated_assets": asset_consolidated,
            "consolidated_liabilities": liability_consolidated,
            "consolidated_equity": equity_consolidated,
            "is_balanced": abs(asset_consolidated - total_liab_equity_consolidated) < 1.0
        }
    }

def get_cash_flow_data(companies, company_meta, all_companies, from_date, to_date, period_type="monthly"):
    placeholders = ", ".join(["%s"] * len(companies))
    
    # 1. Opening cash balance as of from_date
    opening_sql = """
        SELECT 
            gle.company,
            SUM(gle.debit - gle.credit) as opening_balance
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.posting_date < %s
          AND gle.is_cancelled = 0
          AND (acc.account_type IN ('Cash', 'Bank') OR (acc.root_type = 'Asset' AND (acc.account_name LIKE '%%Cash%%' OR acc.account_name LIKE '%%Bank%%')))
          AND gle.company IN (""" + placeholders + """)
        GROUP BY gle.company
    """
    opening_rows = frappe.db.sql(opening_sql, [from_date] + companies, as_dict=True)
    opening_by_company = {c: 0.0 for c in companies}
    for r in opening_rows:
        opening_by_company[r.get("company")] = float(r.get("opening_balance") or 0)
    total_opening_consolidated = sum(opening_by_company.values())

    # 2. Query all cash transactions in the period
    trx_sql = """
        SELECT 
            gle.name,
            gle.company,
            gle.posting_date,
            gle.voucher_type,
            gle.voucher_no,
            gle.against,
            gle.account,
            acc.account_name,
            gle.debit,
            gle.credit,
            gle.remarks
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.posting_date BETWEEN %s AND %s
          AND gle.is_cancelled = 0
          AND (acc.account_type IN ('Cash', 'Bank') OR (acc.root_type = 'Asset' AND (acc.account_name LIKE '%%Cash%%' OR acc.account_name LIKE '%%Bank%%')))
          AND gle.company IN (""" + placeholders + """)
        ORDER BY gle.posting_date ASC, gle.creation ASC
    """
    entries = frappe.db.sql(trx_sql, [from_date, to_date] + companies, as_dict=True)

    inflow_cats = {
        "customer_collections": {"label": "Customer Receipts & POS Collections", "companies": {c: 0.0 for c in companies}, "total": 0.0},
        "operating_revenue": {"label": "Direct Sales & Service Income", "companies": {c: 0.0 for c in companies}, "total": 0.0},
        "other_inflows": {"label": "Other Inflows & Capital Deposits", "companies": {c: 0.0 for c in companies}, "total": 0.0},
    }
    outflow_cats = {
        "supplier_payments": {"label": "Vendor & Supplier Disbursements", "companies": {c: 0.0 for c in companies}, "total": 0.0},
        "operating_expenses": {"label": "Operating & Administrative Expenses", "companies": {c: 0.0 for c in companies}, "total": 0.0},
        "stock_assets": {"label": "Inventory & Capital Expenditures", "companies": {c: 0.0 for c in companies}, "total": 0.0},
        "other_outflows": {"label": "Other Cash Outflows & Transfers", "companies": {c: 0.0 for c in companies}, "total": 0.0},
    }

    periods_map = {}

    for e in entries:
        p_date = frappe.utils.getdate(e.get("posting_date"))
        co = e.get("company")
        debit = float(e.get("debit") or 0)
        credit = float(e.get("credit") or 0)
        against = (e.get("against") or "").lower()
        v_type = e.get("voucher_type") or ""

        month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_abbrs = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        m_str = str(p_date.month) if p_date.month >= 10 else "0" + str(p_date.month)
        d_str = str(p_date.day) if p_date.day >= 10 else "0" + str(p_date.day)

        if period_type == "daily":
            pkey = str(p_date.year) + "-" + m_str + "-" + d_str
            plabel = month_abbrs[p_date.month] + " " + d_str + ", " + str(p_date.year)
        elif period_type == "yearly":
            pkey = str(p_date.year)
            plabel = "FY " + str(p_date.year)
        else:
            pkey = str(p_date.year) + "-" + m_str
            plabel = month_names[p_date.month] + " " + str(p_date.year)

        if pkey not in periods_map:
            periods_map[pkey] = {
                "period_key": pkey,
                "period_label": plabel,
                "inflows": {c: 0.0 for c in companies},
                "outflows": {c: 0.0 for c in companies},
                "inflow_total": 0.0,
                "outflow_total": 0.0,
                "net": {c: 0.0 for c in companies},
                "net_total": 0.0,
                "inflow_breakdown": {k: {c: 0.0 for c in companies} for k in inflow_cats},
                "outflow_breakdown": {k: {c: 0.0 for c in companies} for k in outflow_cats},
                "entries_count": 0
            }
        
        p_obj = periods_map[pkey]
        p_obj["entries_count"] = p_obj["entries_count"] + 1

        if debit > 0:
            if v_type in ("Sales Invoice", "POS Invoice") or "debtor" in against or "customer" in against:
                cat_key = "customer_collections"
            elif "income" in against or "sales" in against or "revenue" in against or "service" in against:
                cat_key = "operating_revenue"
            else:
                cat_key = "other_inflows"

            inflow_cats[cat_key]["companies"][co] = inflow_cats[cat_key]["companies"][co] + debit
            inflow_cats[cat_key]["total"] = inflow_cats[cat_key]["total"] + debit

            p_obj["inflows"][co] = p_obj["inflows"][co] + debit
            p_obj["inflow_total"] = p_obj["inflow_total"] + debit
            p_obj["inflow_breakdown"][cat_key][co] = p_obj["inflow_breakdown"][cat_key][co] + debit
            p_obj["net"][co] = p_obj["net"][co] + debit
            p_obj["net_total"] = p_obj["net_total"] + debit

        if credit > 0:
            if v_type in ("Purchase Invoice",) or "creditor" in against or "supplier" in against or "vendor" in against:
                cat_key = "supplier_payments"
            elif "expense" in against or "salary" in against or "payroll" in against or "rent" in against or "utility" in against:
                cat_key = "operating_expenses"
            elif "asset" in against or "stock" in against or "inventory" in against:
                cat_key = "stock_assets"
            else:
                cat_key = "other_outflows"

            outflow_cats[cat_key]["companies"][co] = outflow_cats[cat_key]["companies"][co] + credit
            outflow_cats[cat_key]["total"] = outflow_cats[cat_key]["total"] + credit

            p_obj["outflows"][co] = p_obj["outflows"][co] + credit
            p_obj["outflow_total"] = p_obj["outflow_total"] + credit
            p_obj["outflow_breakdown"][cat_key][co] = p_obj["outflow_breakdown"][cat_key][co] + credit
            p_obj["net"][co] = p_obj["net"][co] - credit
            p_obj["net_total"] = p_obj["net_total"] - credit

    sorted_pkeys = sorted(periods_map.keys())
    periods_list = []
    
    running_company_bal = {c: opening_by_company[c] for c in companies}
    running_total_bal = total_opening_consolidated

    for pk in sorted_pkeys:
        p = periods_map[pk]
        p_open_co = {c: running_company_bal[c] for c in companies}
        p_open_tot = running_total_bal

        for c in companies:
            running_company_bal[c] = running_company_bal[c] + p["net"][c]
        running_total_bal = running_total_bal + p["net_total"]

        p_end_co = {c: running_company_bal[c] for c in companies}
        p_end_tot = running_total_bal

        p["opening_balance"] = p_open_co
        p["opening_total"] = p_open_tot
        p["ending_balance"] = p_end_co
        p["ending_total"] = p_end_tot
        periods_list.append(p)

    total_inflows_by_company = {c: sum(inflow_cats[k]["companies"][c] for k in inflow_cats) for c in companies}
    total_inflows_consolidated = sum(inflow_cats[k]["total"] for k in inflow_cats)

    total_outflows_by_company = {c: sum(outflow_cats[k]["companies"][c] for k in outflow_cats) for c in companies}
    total_outflows_consolidated = sum(outflow_cats[k]["total"] for k in outflow_cats)

    net_cash_by_company = {c: total_inflows_by_company[c] - total_outflows_by_company[c] for c in companies}
    net_cash_consolidated = total_inflows_consolidated - total_outflows_consolidated

    ending_by_company = {c: opening_by_company[c] + net_cash_by_company[c] for c in companies}
    total_ending_consolidated = total_opening_consolidated + net_cash_consolidated

    return {
        "report": "Consolidated Cash Flow Statement",
        "period_type": period_type,
        "from_date": from_date,
        "to_date": to_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "summary": {
            "opening_balance": opening_by_company,
            "opening_consolidated": total_opening_consolidated,
            "inflows_total": total_inflows_by_company,
            "inflows_consolidated": total_inflows_consolidated,
            "outflows_total": total_outflows_by_company,
            "outflows_consolidated": total_outflows_consolidated,
            "net_cash_flow": net_cash_by_company,
            "net_consolidated": net_cash_consolidated,
            "ending_balance": ending_by_company,
            "ending_consolidated": total_ending_consolidated
        },
        "inflow_categories": inflow_cats,
        "outflow_categories": outflow_cats,
        "periods": periods_list,
        "entries_count": len(entries)
    }

def get_ar_aging_data(companies, company_meta, all_companies, as_of_date, customer=None):
    as_of = frappe.utils.getdate(as_of_date)
    placeholders = ", ".join(["%s"] * len(companies))
    params = list(companies)
    extra_cond = ""
    if customer:
        extra_cond = " AND (si.customer = %s OR si.customer_name LIKE %s)"
        params.extend([customer, "%" + customer + "%"])

    query = """
        SELECT 
            si.name,
            si.company,
            si.customer,
            si.customer_name,
            si.posting_date,
            si.due_date,
            si.grand_total,
            si.outstanding_amount,
            si.currency,
            si.payment_terms_template,
            si.tc_name,
            si.terms,
            si.status
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.company IN (""" + placeholders + """)
          """ + extra_cond + """
        ORDER BY si.customer_name ASC, si.posting_date ASC
    """
    invoices = frappe.db.sql(query, params, as_dict=True)

    customer_map = {}
    company_map = {c: {
        "company": c,
        "abbr": company_meta.get(c, {}).get("abbr", c[:4]),
        "currency": company_meta.get(c, {}).get("currency", "PHP"),
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "total_invoiced": 0.0,
        "invoice_count": 0
    } for c in companies}

    bucket_totals = {
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "total_invoiced": 0.0,
        "invoice_count": 0
    }

    processed_invoices = []

    for inv in invoices:
        cust_id = inv.get("customer") or "Unknown"
        cust_name = inv.get("customer_name") or cust_id
        co = inv.get("company")
        post_date = frappe.utils.getdate(inv.get("posting_date"))
        due_date = frappe.utils.getdate(inv.get("due_date") or inv.get("posting_date"))
        
        grand_total = float(inv.get("grand_total") or 0)
        outstanding = float(inv.get("outstanding_amount") or 0)
        amount_to_age = outstanding if outstanding > 0 else grand_total

        days_overdue = (as_of - due_date).days
        bucket = "current"
        if days_overdue > 90:
            bucket = "range_90_plus"
        elif days_overdue >= 61:
            bucket = "range_61_90"
        elif days_overdue >= 31:
            bucket = "range_31_60"
        elif days_overdue >= 1:
            bucket = "range_1_30"
        else:
            bucket = "current"

        inv_item = {
            "name": inv.get("name"),
            "company": co,
            "company_abbr": company_meta.get(co, {}).get("abbr", co[:4]),
            "customer": cust_id,
            "customer_name": cust_name,
            "posting_date": str(post_date),
            "due_date": str(due_date),
            "terms": inv.get("payment_terms_template") or inv.get("tc_name") or "Standard Terms",
            "days_overdue": max(0, days_overdue),
            "is_overdue": days_overdue > 0,
            "bucket": bucket,
            "grand_total": grand_total,
            "outstanding_amount": outstanding,
            "amount_aged": amount_to_age,
            "status": inv.get("status")
        }
        processed_invoices.append(inv_item)

        if cust_id not in customer_map:
            customer_map[cust_id] = {
                "customer": cust_id,
                "customer_name": cust_name,
                "company": co,
                "current": 0.0,
                "range_1_30": 0.0,
                "range_31_60": 0.0,
                "range_61_90": 0.0,
                "range_90_plus": 0.0,
                "total_outstanding": 0.0,
                "total_invoiced": 0.0,
                "invoice_count": 0,
                "companies": {c: 0.0 for c in companies}
            }
        c_entry = customer_map[cust_id]
        c_entry[bucket] = c_entry[bucket] + amount_to_age
        c_entry["total_outstanding"] = c_entry["total_outstanding"] + amount_to_age
        c_entry["total_invoiced"] = c_entry["total_invoiced"] + grand_total
        c_entry["invoice_count"] = c_entry["invoice_count"] + 1
        if co in c_entry["companies"]:
            c_entry["companies"][co] = c_entry["companies"][co] + amount_to_age

        if co in company_map:
            co_entry = company_map[co]
            co_entry[bucket] = co_entry[bucket] + amount_to_age
            co_entry["total_outstanding"] = co_entry["total_outstanding"] + amount_to_age
            co_entry["total_invoiced"] = co_entry["total_invoiced"] + grand_total
            co_entry["invoice_count"] = co_entry["invoice_count"] + 1

        bucket_totals[bucket] = bucket_totals[bucket] + amount_to_age
        bucket_totals["total_outstanding"] = bucket_totals["total_outstanding"] + amount_to_age
        bucket_totals["total_invoiced"] = bucket_totals["total_invoiced"] + grand_total
        bucket_totals["invoice_count"] = bucket_totals["invoice_count"] + 1

    return {
        "report": "Accounts Receivable (AR) Aging Analysis",
        "as_of_date": str(as_of),
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "buckets": ["current", "range_1_30", "range_31_60", "range_61_90", "range_90_plus"],
        "bucket_labels": {
            "current": "Current / Not Due",
            "range_1_30": "1 - 30 Days",
            "range_31_60": "31 - 60 Days",
            "range_61_90": "61 - 90 Days",
            "range_90_plus": "90+ Days"
        },
        "totals": bucket_totals,
        "company_summary": list(company_map.values()),
        "customer_summary": list(customer_map.values()),
        "invoices": processed_invoices,
        "invoice_count": len(processed_invoices)
    }

def get_ap_aging_data(companies, company_meta, all_companies, as_of_date, supplier=None):
    as_of = frappe.utils.getdate(as_of_date)
    placeholders = ", ".join(["%s"] * len(companies))
    params = list(companies)
    extra_cond = ""
    if supplier:
        extra_cond = " AND (pi.supplier = %s OR pi.supplier_name LIKE %s)"
        params.extend([supplier, "%" + supplier + "%"])

    query = """
        SELECT 
            pi.name,
            pi.company,
            pi.supplier,
            pi.supplier_name,
            pi.bill_no,
            pi.bill_date,
            pi.posting_date,
            pi.due_date,
            pi.grand_total,
            pi.outstanding_amount,
            pi.currency,
            pi.payment_terms_template,
            pi.tc_name,
            pi.terms,
            pi.status
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1
          AND pi.company IN (""" + placeholders + """)
          """ + extra_cond + """
        ORDER BY pi.supplier_name ASC, pi.posting_date ASC
    """
    bills = frappe.db.sql(query, params, as_dict=True)

    supplier_map = {}
    company_map = {c: {
        "company": c,
        "abbr": company_meta.get(c, {}).get("abbr", c[:4]),
        "currency": company_meta.get(c, {}).get("currency", "PHP"),
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "total_billed": 0.0,
        "bill_count": 0
    } for c in companies}

    bucket_totals = {
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "total_billed": 0.0,
        "bill_count": 0
    }

    processed_bills = []

    for bill in bills:
        supp_id = bill.get("supplier") or "Unknown"
        supp_name = bill.get("supplier_name") or supp_id
        co = bill.get("company")
        post_date = frappe.utils.getdate(bill.get("posting_date"))
        due_date = frappe.utils.getdate(bill.get("due_date") or bill.get("posting_date"))
        
        grand_total = float(bill.get("grand_total") or 0)
        outstanding = float(bill.get("outstanding_amount") or 0)
        amount_to_age = outstanding if outstanding > 0 else grand_total

        days_overdue = (as_of - due_date).days
        bucket = "current"
        if days_overdue > 90:
            bucket = "range_90_plus"
        elif days_overdue >= 61:
            bucket = "range_61_90"
        elif days_overdue >= 31:
            bucket = "range_31_60"
        elif days_overdue >= 1:
            bucket = "range_1_30"
        else:
            bucket = "current"

        bill_item = {
            "name": bill.get("name"),
            "company": co,
            "company_abbr": company_meta.get(co, {}).get("abbr", co[:4]),
            "supplier": supp_id,
            "supplier_name": supp_name,
            "bill_no": bill.get("bill_no") or bill.get("name"),
            "bill_date": str(bill.get("bill_date") or post_date),
            "posting_date": str(post_date),
            "due_date": str(due_date),
            "terms": bill.get("payment_terms_template") or bill.get("tc_name") or "Standard Terms",
            "days_overdue": max(0, days_overdue),
            "is_overdue": days_overdue > 0,
            "bucket": bucket,
            "grand_total": grand_total,
            "outstanding_amount": outstanding,
            "amount_aged": amount_to_age,
            "status": bill.get("status")
        }
        processed_bills.append(bill_item)

        if supp_id not in supplier_map:
            supplier_map[supp_id] = {
                "supplier": supp_id,
                "supplier_name": supp_name,
                "company": co,
                "current": 0.0,
                "range_1_30": 0.0,
                "range_31_60": 0.0,
                "range_61_90": 0.0,
                "range_90_plus": 0.0,
                "total_outstanding": 0.0,
                "total_billed": 0.0,
                "bill_count": 0,
                "companies": {c: 0.0 for c in companies}
            }
        s_entry = supplier_map[supp_id]
        s_entry[bucket] = s_entry[bucket] + amount_to_age
        s_entry["total_outstanding"] = s_entry["total_outstanding"] + amount_to_age
        s_entry["total_billed"] = s_entry["total_billed"] + grand_total
        s_entry["bill_count"] = s_entry["bill_count"] + 1
        if co in s_entry["companies"]:
            s_entry["companies"][co] = s_entry["companies"][co] + amount_to_age

        if co in company_map:
            co_entry = company_map[co]
            co_entry[bucket] = co_entry[bucket] + amount_to_age
            co_entry["total_outstanding"] = co_entry["total_outstanding"] + amount_to_age
            co_entry["total_billed"] = co_entry["total_billed"] + grand_total
            co_entry["bill_count"] = co_entry["bill_count"] + 1

        bucket_totals[bucket] = bucket_totals[bucket] + amount_to_age
        bucket_totals["total_outstanding"] = bucket_totals["total_outstanding"] + amount_to_age
        bucket_totals["total_billed"] = bucket_totals["total_billed"] + grand_total
        bucket_totals["bill_count"] = bucket_totals["bill_count"] + 1

    return {
        "report": "Accounts Payable (AP) Aging Analysis",
        "as_of_date": str(as_of),
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "buckets": ["current", "range_1_30", "range_31_60", "range_61_90", "range_90_plus"],
        "bucket_labels": {
            "current": "Current / Not Due",
            "range_1_30": "1 - 30 Days",
            "range_31_60": "31 - 60 Days",
            "range_61_90": "61 - 90 Days",
            "range_90_plus": "90+ Days"
        },
        "totals": bucket_totals,
        "company_summary": list(company_map.values()),
        "supplier_summary": list(supplier_map.values()),
        "bills": processed_bills,
        "bill_count": len(processed_bills)
    }

def get_gl_data(companies, from_date, to_date, voucher_type, search_text, page, page_length):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    values = [from_date, to_date]

    placeholders = ", ".join(["%s"] * len(companies))
    conditions.append("gle.company IN (" + placeholders + ")")
    values.extend(companies)

    if voucher_type:
        conditions.append("gle.voucher_type = %s")
        values.append(voucher_type)

    if search_text:
        conditions.append("(gle.voucher_no LIKE %s OR gle.account LIKE %s OR gle.remarks LIKE %s OR gle.against LIKE %s)")
        wild = "%" + search_text + "%"
        values.extend([wild, wild, wild, wild])

    where_clause = " AND ".join(conditions)
    offset = (page - 1) * page_length

    query = """
        SELECT 
            gle.name,
            gle.posting_date,
            gle.company,
            gle.account,
            gle.voucher_type,
            gle.voucher_no,
            gle.against,
            gle.debit,
            gle.credit,
            gle.remarks
        FROM `tabGL Entry` gle
        WHERE """ + where_clause + """
        ORDER BY gle.posting_date desc, gle.creation desc
        LIMIT %s OFFSET %s
    """
    entries = frappe.db.sql(query, values + [page_length, offset], as_dict=True)

    count_query = "SELECT COUNT(*) as cnt FROM `tabGL Entry` gle WHERE " + where_clause
    total_count = frappe.db.sql(count_query, values, as_dict=True)[0].get("cnt") or 0

    return {
        "report": "Multi-Company General Ledger",
        "from_date": from_date,
        "to_date": to_date,
        "companies": companies,
        "page": page,
        "page_length": page_length,
        "total_records": total_count,
        "entries": entries
    }

def get_inventory_data(companies, company_meta, all_companies, from_date, to_date, search_text):
    cond = ["item.disabled = 0"]
    params = []
    if search_text:
        cond.append("(item.item_code LIKE %s OR item.item_name LIKE %s OR item.item_group LIKE %s)")
        w = "%" + search_text + "%"
        params.extend([w, w, w])

    where_str = " AND ".join(cond)
    items = frappe.db.sql("""
        SELECT item_code, item_name, item_group, stock_uom
        FROM `tabItem` item
        WHERE """ + where_str + """
        ORDER BY item.item_group asc, item.item_code asc
    """, params, as_dict=True)

    placeholders = ", ".join(["%s"] * len(companies))
    sle_query = """
        SELECT 
            sle.item_code,
            sle.company,
            SUM(CASE WHEN sle.actual_qty > 0 AND sle.posting_date BETWEEN %s AND %s THEN sle.actual_qty ELSE 0 END) as in_qty,
            SUM(CASE WHEN sle.actual_qty < 0 AND sle.posting_date BETWEEN %s AND %s THEN ABS(sle.actual_qty) ELSE 0 END) as out_qty,
            SUBSTRING_INDEX(GROUP_CONCAT(sle.qty_after_transaction ORDER BY sle.posting_date desc, sle.posting_time desc, sle.creation desc), ',', 1) as ending_qty,
            SUBSTRING_INDEX(GROUP_CONCAT(sle.stock_value ORDER BY sle.posting_date desc, sle.posting_time desc, sle.creation desc), ',', 1) as ending_val,
            SUBSTRING_INDEX(GROUP_CONCAT(sle.valuation_rate ORDER BY sle.posting_date desc, sle.posting_time desc, sle.creation desc), ',', 1) as last_val_rate,
            COUNT(sle.name) as tx_count
        FROM `tabStock Ledger Entry` sle
        WHERE sle.is_cancelled = 0
          AND sle.posting_date <= %s
          AND sle.company IN (""" + placeholders + """)
        GROUP BY sle.item_code, sle.company
    """
    sle_params = [from_date, to_date, from_date, to_date, to_date] + companies
    sle_records = frappe.db.sql(sle_query, sle_params, as_dict=True)

    sle_map = {}
    for r in sle_records:
        icode = r.get("item_code")
        co = r.get("company")
        if icode not in sle_map:
            sle_map[icode] = {}
        sle_map[icode][co] = {
            "in_qty": float(r.get("in_qty") or 0),
            "out_qty": float(r.get("out_qty") or 0),
            "ending_qty": float(r.get("ending_qty") or 0),
            "ending_val": float(r.get("ending_val") or 0),
            "val_rate": float(r.get("last_val_rate") or 0),
            "tx_count": int(r.get("tx_count") or 0)
        }

    matrix_rows = []
    total_in_all = 0.0
    total_out_all = 0.0
    total_qty_all = 0.0
    total_val_all = 0.0

    company_in_totals = {c: 0.0 for c in companies}
    company_out_totals = {c: 0.0 for c in companies}
    company_qty_totals = {c: 0.0 for c in companies}
    company_val_totals = {c: 0.0 for c in companies}

    for it in items:
        icode = it.get("item_code")
        row_item = {
            "item_code": icode,
            "item_name": it.get("item_name") or icode,
            "item_group": it.get("item_group") or "Standard",
            "stock_uom": it.get("stock_uom") or "Nos",
            "avg_valuation_rate": 0.0,
            "companies_in": {},
            "companies_out": {},
            "companies_qty": {},
            "companies_val": {},
            "total_in": 0.0,
            "total_out": 0.0,
            "total_qty": 0.0,
            "total_val": 0.0,
            "has_transactions": False
        }

        rates = []
        for co in companies:
            in_q = 0.0
            out_q = 0.0
            end_q = 0.0
            val = 0.0

            if icode in sle_map and co in sle_map[icode]:
                cdata = sle_map[icode][co]
                in_q = cdata["in_qty"]
                out_q = cdata["out_qty"]
                end_q = cdata["ending_qty"]
                val = cdata["ending_val"]
                if cdata["val_rate"] > 0:
                    rates.append(cdata["val_rate"])
                if cdata["tx_count"] > 0:
                    row_item["has_transactions"] = True

            row_item["companies_in"][co] = in_q
            row_item["companies_out"][co] = out_q
            row_item["companies_qty"][co] = end_q
            row_item["companies_val"][co] = val

            row_item["total_in"] = row_item["total_in"] + in_q
            row_item["total_out"] = row_item["total_out"] + out_q
            row_item["total_qty"] = row_item["total_qty"] + end_q
            row_item["total_val"] = row_item["total_val"] + val

            company_in_totals[co] = company_in_totals[co] + in_q
            company_out_totals[co] = company_out_totals[co] + out_q
            company_qty_totals[co] = company_qty_totals[co] + end_q
            company_val_totals[co] = company_val_totals[co] + val

        if rates:
            row_item["avg_valuation_rate"] = sum(rates) / len(rates)

        total_in_all = total_in_all + row_item["total_in"]
        total_out_all = total_out_all + row_item["total_out"]
        total_qty_all = total_qty_all + row_item["total_qty"]
        total_val_all = total_val_all + row_item["total_val"]

        matrix_rows.append(row_item)

    return {
        "report": "Multi-Company Inventory Audit",
        "from_date": from_date,
        "to_date": to_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "total_sku_count": len(matrix_rows),
        "total_in_qty": total_in_all,
        "total_out_qty": total_out_all,
        "total_qty": total_qty_all,
        "total_val": total_val_all,
        "company_in_totals": company_in_totals,
        "company_out_totals": company_out_totals,
        "company_qty_totals": company_qty_totals,
        "company_val_totals": company_val_totals,
        "rows": matrix_rows
    }

def get_drilldown_data(company, account, from_date, to_date):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    values = [from_date, to_date]

    if company:
        conditions.append("gle.company = %s")
        values.append(company)
    
    if account:
        conditions.append("(gle.account = %s OR gle.account LIKE %s)")
        values.extend([account, account + " - %"])

    where_clause = " AND ".join(conditions)

    entries = frappe.db.sql("""
        SELECT 
            gle.posting_date,
            gle.company,
            gle.account,
            gle.voucher_type,
            gle.voucher_no,
            gle.debit,
            gle.credit,
            gle.remarks
        FROM `tabGL Entry` gle
        WHERE """ + where_clause + """
        ORDER BY gle.posting_date desc, gle.creation desc
        LIMIT 100
    """, values, as_dict=True)

    return {
        "entries": entries,
        "total_debit": sum(float(e.get("debit") or 0) for e in entries),
        "total_credit": sum(float(e.get("credit") or 0) for e in entries)
    }

def get_stock_ledger_drilldown(item_code, company, from_date, to_date):
    conditions = ["sle.is_cancelled = 0"]
    values = []

    if item_code:
        conditions.append("sle.item_code = %s")
        values.append(item_code)

    if company:
        conditions.append("sle.company = %s")
        values.append(company)

    if to_date:
        conditions.append("sle.posting_date <= %s")
        values.append(to_date)

    where_clause = " AND ".join(conditions)

    entries = frappe.db.sql("""
        SELECT 
            sle.posting_date,
            sle.posting_time,
            sle.company,
            sle.warehouse,
            sle.voucher_type,
            sle.voucher_no,
            sle.actual_qty,
            sle.qty_after_transaction,
            sle.incoming_rate,
            sle.valuation_rate,
            sle.stock_value,
            sle.stock_value_difference
        FROM `tabStock Ledger Entry` sle
        WHERE """ + where_clause + """
        ORDER BY sle.posting_date asc, sle.posting_time asc, sle.creation asc
        LIMIT 200
    """, values, as_dict=True)

    return {
        "item_code": item_code,
        "company": company,
        "entries": entries,
        "total_in": sum(float(e.get("actual_qty") or 0) for e in entries if float(e.get("actual_qty") or 0) > 0),
        "total_out": sum(abs(float(e.get("actual_qty") or 0)) for e in entries if float(e.get("actual_qty") or 0) < 0),
        "ending_qty": entries[-1].get("qty_after_transaction") if entries else 0.0,
        "ending_value": entries[-1].get("stock_value") if entries else 0.0
    }

frappe.response["message"] = get_data()
'''

def deploy_server_script():
    print("\n--- Deploying Server Script 'VM Consolidated Financials API' ---")
    ss_doc = {
        "doctype": "Server Script",
        "name": "VM Consolidated Financials API",
        "script_type": "API",
        "api_method": "vm_consolidated_financials",
        "allow_guest": 0,
        "disabled": 0,
        "script": SERVER_SCRIPT_CODE
    }

    chk = session.get(f"{BASE_URL}/api/resource/Server%20Script/VM%20Consolidated%20Financials%20API")
    if chk.status_code == 200:
        res = session.put(f"{BASE_URL}/api/resource/Server%20Script/VM%20Consolidated%20Financials%20API", json=ss_doc)
        print("Updated Server Script:", res.status_code)
    else:
        res = session.post(f"{BASE_URL}/api/resource/Server%20Script", json=ss_doc)
        print("Created Server Script:", res.status_code)
    
    if res.status_code not in (200, 201):
        print("Error deploying server script:", res.text)
    else:
        print("[OK] Server Script successfully deployed!")

def test_api():
    print("\n--- Testing API Endpoints (Cash Flow, AR Aging, AP Aging, P&L, BS, Inv) ---")
    
    # 1. Cash Flow - Monthly
    cf_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&from_date=2026-01-01&to_date=2026-12-31&period=monthly")
    print(f"\nCash Flow (Monthly) Status: {cf_res.status_code}")
    cf_data = cf_res.json().get("message", {})
    print(f" - Opening Bal: PHP {cf_data.get('summary', {}).get('opening_consolidated', 0):,.2f}")
    print(f" - Inflows Total: PHP {cf_data.get('summary', {}).get('inflows_consolidated', 0):,.2f}")
    print(f" - Outflows Total: PHP {cf_data.get('summary', {}).get('outflows_consolidated', 0):,.2f}")
    print(f" - Net Cash Flow: PHP {cf_data.get('summary', {}).get('net_consolidated', 0):,.2f}")
    print(f" - Ending Bal: PHP {cf_data.get('summary', {}).get('ending_consolidated', 0):,.2f}")
    print(f" - Periods count: {len(cf_data.get('periods', []))}")
    print(f" - Sample Period: {cf_data.get('periods', [{}])[0].get('period_label') if cf_data.get('periods') else 'None'}")

    # 2. Cash Flow - Daily
    cf_daily_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&from_date=2026-08-01&to_date=2026-08-31&period=daily")
    print(f"\nCash Flow (Daily) Status: {cf_daily_res.status_code}")
    cf_daily_data = cf_daily_res.json().get("message", {})
    print(f" - Daily Periods count: {len(cf_daily_data.get('periods', []))}")

    # 3. Cash Flow - Yearly
    cf_yr_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=cash_flow&from_date=2024-01-01&to_date=2026-12-31&period=yearly")
    print(f"\nCash Flow (Yearly) Status: {cf_yr_res.status_code}")
    cf_yr_data = cf_yr_res.json().get("message", {})
    print(f" - Yearly Periods count: {len(cf_yr_data.get('periods', []))}")

    # 4. AR Aging
    ar_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=ar_aging&as_of_date=2026-09-11")
    print(f"\nAR Aging Status: {ar_res.status_code}")
    ar_data = ar_res.json().get("message", {})
    ar_totals = ar_data.get("totals", {})
    print(f" - Invoices Count: {ar_data.get('invoice_count')}")
    print(f" - Current: PHP {ar_totals.get('current', 0):,.2f}")
    print(f" - 1-30 Days: PHP {ar_totals.get('range_1_30', 0):,.2f}")
    print(f" - 31-60 Days: PHP {ar_totals.get('range_31_60', 0):,.2f}")
    print(f" - 61-90 Days: PHP {ar_totals.get('range_61_90', 0):,.2f}")
    print(f" - 90+ Days: PHP {ar_totals.get('range_90_plus', 0):,.2f}")
    print(f" - Total Outstanding: PHP {ar_totals.get('total_outstanding', 0):,.2f}")
    print(f" - Customer summaries count: {len(ar_data.get('customer_summary', []))}")

    # 5. AP Aging
    ap_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=ap_aging&as_of_date=2026-09-11")
    print(f"\nAP Aging Status: {ap_res.status_code}")
    ap_data = ap_res.json().get("message", {})
    ap_totals = ap_data.get("totals", {})
    print(f" - Bills Count: {ap_data.get('bill_count')}")
    print(f" - Current: PHP {ap_totals.get('current', 0):,.2f}")
    print(f" - 1-30 Days: PHP {ap_totals.get('range_1_30', 0):,.2f}")
    print(f" - 31-60 Days: PHP {ap_totals.get('range_31_60', 0):,.2f}")
    print(f" - 61-90 Days: PHP {ap_totals.get('range_61_90', 0):,.2f}")
    print(f" - 90+ Days: PHP {ap_totals.get('range_90_plus', 0):,.2f}")
    print(f" - Total Outstanding: PHP {ap_totals.get('total_outstanding', 0):,.2f}")
    print(f" - Supplier summaries count: {len(ap_data.get('supplier_summary', []))}")

if __name__ == "__main__":
    deploy_server_script()
    test_api()
