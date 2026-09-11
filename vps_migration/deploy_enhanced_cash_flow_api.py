# Deploy enhanced Consolidated Financials API with Hierarchical Year/Month/Day Cash Flow & Anti-Overlap Engine

import requests, json

BASE_URL = 'http://38.247.138.224:10017'

SERVER_SCRIPT_CODE = '''
# Server Script: VM Consolidated Financials API
# DocType: Server Script | Script Type: API
# Method: vm_consolidated_financials


def get_companies():
    all_companies_raw = frappe.get_all("Company", fields=["name", "abbr", "default_currency", "country"], order_by="name asc")
    all_companies = [c["name"] for c in all_companies_raw]
    company_meta = {c["name"]: {"abbr": c.get("abbr") or c["name"][:4].upper(), "currency": c.get("default_currency") or "PHP"} for c in all_companies_raw}
    
    req_co = frappe.form_dict.get("selected_companies")
    if req_co:
        if isinstance(req_co, str):
            selected = [x.strip() for x in req_co.split(",") if x.strip() in all_companies]
        else:
            selected = [x for x in req_co if x in all_companies]
        companies = selected if selected else all_companies
    else:
        companies = all_companies
    return companies, company_meta, all_companies

def execute():
    report_type = frappe.form_dict.get("report_type") or "pnl"
    from_date = frappe.form_dict.get("from_date") or (str(frappe.utils.getdate().year) + "-01-01")
    to_date = frappe.form_dict.get("to_date") or frappe.utils.nowdate()
    voucher_type = frappe.form_dict.get("voucher_type")
    search_text = frappe.form_dict.get("search_text")
    page = int(frappe.form_dict.get("page") or 1)
    page_length = int(frappe.form_dict.get("page_length") or 100)

    co_info = get_companies()
    companies = co_info[0]
    company_meta = co_info[1]
    all_companies = co_info[2]

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
          AND acc.root_type IN ('Asset', 'Liability', 'Equity', 'Income', 'Expense')
          AND gle.company IN (""" + placeholders + """)
        GROUP BY gle.company, gle.account
        ORDER BY MAX(acc.root_type) asc, MAX(acc.account_name) asc
    """
    gl_entries = frappe.db.sql(query, [to_date] + companies, as_dict=True)

    asset_accounts = {}
    liability_accounts = {}
    equity_accounts = {}
    period_pnl_per_company = {c: 0.0 for c in companies}

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
            target_dict = asset_accounts
        elif root_type == "Liability":
            net_amt = credit - debit
            target_dict = liability_accounts
        elif root_type == "Equity":
            net_amt = credit - debit
            target_dict = equity_accounts
        elif root_type == "Income":
            period_pnl_per_company[co] = period_pnl_per_company[co] + (credit - debit)
            continue
        elif root_type == "Expense":
            period_pnl_per_company[co] = period_pnl_per_company[co] - (debit - credit)
            continue
        else:
            continue

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

    retained_earnings_name = "Current Period Net Earnings"
    if retained_earnings_name not in equity_accounts:
        equity_accounts[retained_earnings_name] = {
            "account_name": retained_earnings_name,
            "root_type": "Equity",
            "account_type": "Equity",
            "companies": {c: 0.0 for c in companies},
            "total": 0.0
        }
    for c in companies:
        pnl_val = period_pnl_per_company[c]
        equity_accounts[retained_earnings_name]["companies"][c] = equity_accounts[retained_earnings_name]["companies"][c] + pnl_val
        equity_accounts[retained_earnings_name]["total"] = equity_accounts[retained_earnings_name]["total"] + pnl_val

    asset_rows = list(asset_accounts.values())
    liability_rows = list(liability_accounts.values())
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

    # Maps for daily, monthly, and yearly aggregation
    daily_map = {}
    monthly_map = {}
    yearly_map = {}

    month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_abbrs = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for e in entries:
        p_date = frappe.utils.getdate(e.get("posting_date"))
        co = e.get("company")
        debit = float(e.get("debit") or 0)
        credit = float(e.get("credit") or 0)
        against = (e.get("against") or "").lower()
        v_type = e.get("voucher_type") or ""

        m_str = str(p_date.month) if p_date.month >= 10 else "0" + str(p_date.month)
        d_str = str(p_date.day) if p_date.day >= 10 else "0" + str(p_date.day)
        y_str = str(p_date.year)

        day_key = y_str + "-" + m_str + "-" + d_str
        month_key = y_str + "-" + m_str
        year_key = y_str

        day_label = month_abbrs[p_date.month] + " " + d_str
        month_label = month_names[p_date.month] + " " + y_str
        year_label = "FY " + y_str

        # Initialize maps if not present
        if day_key not in daily_map:
            daily_map[day_key] = {
                "period_key": day_key,
                "period_label": day_label,
                "full_label": month_abbrs[p_date.month] + " " + d_str + ", " + y_str,
                "year_key": year_key,
                "month_key": month_key,
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
        if month_key not in monthly_map:
            monthly_map[month_key] = {
                "period_key": month_key,
                "period_label": month_label,
                "month_abbr": month_abbrs[p_date.month] + " " + y_str,
                "year_key": year_key,
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
        if year_key not in yearly_map:
            yearly_map[year_key] = {
                "period_key": year_key,
                "period_label": year_label,
                "year_key": year_key,
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

        daily_map[day_key]["entries_count"] = daily_map[day_key]["entries_count"] + 1
        monthly_map[month_key]["entries_count"] = monthly_map[month_key]["entries_count"] + 1
        yearly_map[year_key]["entries_count"] = yearly_map[year_key]["entries_count"] + 1

        if debit > 0:
            if v_type in ("Sales Invoice", "POS Invoice") or "debtor" in against or "customer" in against:
                cat_key = "customer_collections"
            elif "income" in against or "sales" in against or "revenue" in against or "service" in against:
                cat_key = "operating_revenue"
            else:
                cat_key = "other_inflows"

            inflow_cats[cat_key]["companies"][co] = inflow_cats[cat_key]["companies"][co] + debit
            inflow_cats[cat_key]["total"] = inflow_cats[cat_key]["total"] + debit

            for m_obj in [daily_map[day_key], monthly_map[month_key], yearly_map[year_key]]:
                m_obj["inflows"][co] = m_obj["inflows"][co] + debit
                m_obj["inflow_total"] = m_obj["inflow_total"] + debit
                m_obj["inflow_breakdown"][cat_key][co] = m_obj["inflow_breakdown"][cat_key][co] + debit
                m_obj["net"][co] = m_obj["net"][co] + debit
                m_obj["net_total"] = m_obj["net_total"] + debit

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

            for m_obj in [daily_map[day_key], monthly_map[month_key], yearly_map[year_key]]:
                m_obj["outflows"][co] = m_obj["outflows"][co] + credit
                m_obj["outflow_total"] = m_obj["outflow_total"] + credit
                m_obj["outflow_breakdown"][cat_key][co] = m_obj["outflow_breakdown"][cat_key][co] + credit
                m_obj["net"][co] = m_obj["net"][co] - credit
                m_obj["net_total"] = m_obj["net_total"] - credit

    # Compute running balances for daily
    sorted_days = sorted(daily_map.keys())
    running_day_co = {c: opening_by_company[c] for c in companies}
    running_day_tot = total_opening_consolidated
    daily_list = []
    for dk in sorted_days:
        d = daily_map[dk]
        d["opening_balance"] = {c: running_day_co[c] for c in companies}
        d["opening_total"] = running_day_tot
        for c in companies:
            running_day_co[c] = running_day_co[c] + d["net"][c]
        running_day_tot = running_day_tot + d["net_total"]
        d["ending_balance"] = {c: running_day_co[c] for c in companies}
        d["ending_total"] = running_day_tot
        daily_list.append(d)

    # Compute running balances for monthly
    sorted_months = sorted(monthly_map.keys())
    running_mo_co = {c: opening_by_company[c] for c in companies}
    running_mo_tot = total_opening_consolidated
    monthly_list = []
    for mk in sorted_months:
        m = monthly_map[mk]
        m["opening_balance"] = {c: running_mo_co[c] for c in companies}
        m["opening_total"] = running_mo_tot
        for c in companies:
            running_mo_co[c] = running_mo_co[c] + m["net"][c]
        running_mo_tot = running_mo_tot + m["net_total"]
        m["ending_balance"] = {c: running_mo_co[c] for c in companies}
        m["ending_total"] = running_mo_tot
        m["days"] = [d for d in daily_list if d["month_key"] == mk]
        monthly_list.append(m)

    # Compute running balances for yearly
    sorted_years = sorted(yearly_map.keys())
    running_yr_co = {c: opening_by_company[c] for c in companies}
    running_yr_tot = total_opening_consolidated
    yearly_list = []
    for yk in sorted_years:
        y = yearly_map[yk]
        y["opening_balance"] = {c: running_yr_co[c] for c in companies}
        y["opening_total"] = running_yr_tot
        for c in companies:
            running_yr_co[c] = running_yr_co[c] + y["net"][c]
        running_yr_tot = running_yr_tot + y["net_total"]
        y["ending_balance"] = {c: running_yr_co[c] for c in companies}
        y["ending_total"] = running_yr_tot
        y["months"] = [m for m in monthly_list if m["year_key"] == yk]
        yearly_list.append(y)

    # Select periods based on requested period_type
    if period_type == "daily":
        active_periods = daily_list
    elif period_type == "yearly":
        active_periods = yearly_list
    else:
        active_periods = monthly_list

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
        "periods": active_periods,
        "hierarchy": {
            "years": yearly_list,
            "months": monthly_list,
            "days": daily_list
        },
        "entries_count": len(entries)
    }

def get_ar_aging_data(companies, company_meta, all_companies, as_of_date, customer=None):
    as_of = frappe.utils.getdate(as_of_date)
    placeholders = ", ".join(["%s"] * len(companies))
    params = list(companies)

    query = """
        SELECT 
            si.name,
            si.customer,
            si.customer_name,
            si.company,
            si.posting_date,
            si.due_date,
            si.payment_terms_template,
            si.grand_total,
            si.outstanding_amount,
            si.status,
            si.currency
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.outstanding_amount > 0
          AND si.company IN (""" + placeholders + """)
    """
    if customer:
        query = query + " AND (si.customer = %s OR si.customer_name LIKE %s)"
        params.extend([customer, "%" + customer + "%"])
    query = query + " ORDER BY si.due_date ASC, si.posting_date ASC"

    invoices = frappe.db.sql(query, params, as_dict=True)

    bucket_totals = {
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "invoice_count": len(invoices)
    }

    customer_map = {}
    company_map = {c: {
        "company": c,
        "abbr": company_meta.get(c, {}).get("abbr", c[:4]),
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "invoice_count": 0
    } for c in companies}

    invoice_list = []

    for inv in invoices:
        due = frappe.utils.getdate(inv.get("due_date") or inv.get("posting_date"))
        post = frappe.utils.getdate(inv.get("posting_date"))
        out_amt = float(inv.get("outstanding_amount") or 0)
        tot_amt = float(inv.get("grand_total") or 0)
        co = inv.get("company")
        cust = inv.get("customer_name") or inv.get("customer") or "Unknown"

        days_overdue = (as_of - due).days

        if days_overdue <= 0:
            b_key = "current"
        elif days_overdue <= 30:
            b_key = "range_1_30"
        elif days_overdue <= 60:
            b_key = "range_31_60"
        elif days_overdue <= 90:
            b_key = "range_61_90"
        else:
            b_key = "range_90_plus"

        bucket_totals[b_key] = bucket_totals[b_key] + out_amt
        bucket_totals["total_outstanding"] = bucket_totals["total_outstanding"] + out_amt

        if co in company_map:
            company_map[co][b_key] = company_map[co][b_key] + out_amt
            company_map[co]["total_outstanding"] = company_map[co]["total_outstanding"] + out_amt
            company_map[co]["invoice_count"] = company_map[co]["invoice_count"] + 1

        if cust not in customer_map:
            customer_map[cust] = {
                "customer_name": cust,
                "company": co,
                "current": 0.0,
                "range_1_30": 0.0,
                "range_31_60": 0.0,
                "range_61_90": 0.0,
                "range_90_plus": 0.0,
                "total_outstanding": 0.0,
                "invoice_count": 0
            }
        customer_map[cust][b_key] = customer_map[cust][b_key] + out_amt
        customer_map[cust]["total_outstanding"] = customer_map[cust]["total_outstanding"] + out_amt
        customer_map[cust]["invoice_count"] = customer_map[cust]["invoice_count"] + 1

        terms_label = inv.get("payment_terms_template") or ((due - post).days if (due - post).days > 0 else "Due on Receipt")
        if isinstance(terms_label, int):
            terms_label = str(terms_label) + " Days Credit"

        invoice_list.append({
            "name": inv.get("name"),
            "customer_name": cust,
            "company": co,
            "company_abbr": company_meta.get(co, {}).get("abbr", co[:4]),
            "posting_date": str(post),
            "due_date": str(due),
            "terms": terms_label,
            "days_overdue": days_overdue,
            "bucket": b_key,
            "grand_total": tot_amt,
            "outstanding_amount": out_amt,
            "amount_aged": out_amt,
            "status": inv.get("status")
        })

    sorted_cust = sorted(list(customer_map.values()), key=lambda x: x["total_outstanding"], reverse=True)

    return {
        "report": "Accounts Receivable (AR) Aging Analysis",
        "as_of_date": as_of_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "totals": bucket_totals,
        "customer_summary": sorted_cust,
        "company_summary": list(company_map.values()),
        "invoices": invoice_list,
        "invoice_count": len(invoice_list)
    }

def get_ap_aging_data(companies, company_meta, all_companies, as_of_date, supplier=None):
    as_of = frappe.utils.getdate(as_of_date)
    placeholders = ", ".join(["%s"] * len(companies))
    params = list(companies)

    query = """
        SELECT 
            pi.name,
            pi.supplier,
            pi.supplier_name,
            pi.company,
            pi.posting_date,
            pi.due_date,
            pi.payment_terms_template,
            pi.grand_total,
            pi.outstanding_amount,
            pi.status,
            pi.currency
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1
          AND pi.outstanding_amount > 0
          AND pi.company IN (""" + placeholders + """)
    """
    if supplier:
        query = query + " AND (pi.supplier = %s OR pi.supplier_name LIKE %s)"
        params.extend([supplier, "%" + supplier + "%"])
    query = query + " ORDER BY pi.due_date ASC, pi.posting_date ASC"

    bills = frappe.db.sql(query, params, as_dict=True)

    bucket_totals = {
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "bill_count": len(bills)
    }

    supplier_map = {}
    company_map = {c: {
        "company": c,
        "abbr": company_meta.get(c, {}).get("abbr", c[:4]),
        "current": 0.0,
        "range_1_30": 0.0,
        "range_31_60": 0.0,
        "range_61_90": 0.0,
        "range_90_plus": 0.0,
        "total_outstanding": 0.0,
        "bill_count": 0
    } for c in companies}

    bill_list = []

    for b in bills:
        due = frappe.utils.getdate(b.get("due_date") or b.get("posting_date"))
        post = frappe.utils.getdate(b.get("posting_date"))
        out_amt = float(b.get("outstanding_amount") or 0)
        tot_amt = float(b.get("grand_total") or 0)
        co = b.get("company")
        supp = b.get("supplier_name") or b.get("supplier") or "Unknown"

        days_overdue = (as_of - due).days

        if days_overdue <= 0:
            b_key = "current"
        elif days_overdue <= 30:
            b_key = "range_1_30"
        elif days_overdue <= 60:
            b_key = "range_31_60"
        elif days_overdue <= 90:
            b_key = "range_61_90"
        else:
            b_key = "range_90_plus"

        bucket_totals[b_key] = bucket_totals[b_key] + out_amt
        bucket_totals["total_outstanding"] = bucket_totals["total_outstanding"] + out_amt

        if co in company_map:
            company_map[co][b_key] = company_map[co][b_key] + out_amt
            company_map[co]["total_outstanding"] = company_map[co]["total_outstanding"] + out_amt
            company_map[co]["bill_count"] = company_map[co]["bill_count"] + 1

        if supp not in supplier_map:
            supplier_map[supp] = {
                "supplier_name": supp,
                "company": co,
                "current": 0.0,
                "range_1_30": 0.0,
                "range_31_60": 0.0,
                "range_61_90": 0.0,
                "range_90_plus": 0.0,
                "total_outstanding": 0.0,
                "bill_count": 0
            }
        supplier_map[supp][b_key] = supplier_map[supp][b_key] + out_amt
        supplier_map[supp]["total_outstanding"] = supplier_map[supp]["total_outstanding"] + out_amt
        supplier_map[supp]["bill_count"] = supplier_map[supp]["bill_count"] + 1

        terms_label = b.get("payment_terms_template") or ((due - post).days if (due - post).days > 0 else "Due on Receipt")
        if isinstance(terms_label, int):
            terms_label = str(terms_label) + " Days Credit"

        bill_list.append({
            "name": b.get("name"),
            "supplier_name": supp,
            "company": co,
            "company_abbr": company_meta.get(co, {}).get("abbr", co[:4]),
            "posting_date": str(post),
            "due_date": str(due),
            "terms": terms_label,
            "days_overdue": days_overdue,
            "bucket": b_key,
            "grand_total": tot_amt,
            "outstanding_amount": out_amt,
            "amount_aged": out_amt,
            "status": b.get("status")
        })

    sorted_supp = sorted(list(supplier_map.values()), key=lambda x: x["total_outstanding"], reverse=True)

    return {
        "report": "Accounts Payable (AP) Aging Analysis",
        "as_of_date": as_of_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "totals": bucket_totals,
        "supplier_summary": sorted_supp,
        "company_summary": list(company_map.values()),
        "bills": bill_list,
        "bill_count": len(bill_list)
    }

def get_gl_data(companies, from_date, to_date, voucher_type, search_text, page, page_length):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    placeholders = ", ".join(["%s"] * len(companies))
    conditions.append("gle.company IN (" + placeholders + ")")
    values = [from_date, to_date] + list(companies)

    if voucher_type:
        conditions.append("gle.voucher_type = %s")
        values.append(voucher_type)

    if search_text:
        conditions.append("(gle.voucher_no LIKE %s OR gle.account LIKE %s OR gle.remarks LIKE %s)")
        wildcard = "%" + search_text + "%"
        values.extend([wildcard, wildcard, wildcard])

    where_clause = " AND ".join(conditions)

    count_res = frappe.db.sql("SELECT COUNT(*) as cnt FROM `tabGL Entry` gle WHERE " + where_clause, values, as_dict=True)
    total_count = count_res[0].get("cnt") if count_res else 0

    limit_start = (page - 1) * page_length
    limit_clause = "LIMIT " + str(page_length) + " OFFSET " + str(limit_start)

    rows = frappe.db.sql("""
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
        """ + limit_clause, values, as_dict=True)

    return {
        "report": "Multi-Company General Ledger",
        "total_records": total_count,
        "page": page,
        "page_length": page_length,
        "rows": rows
    }

def get_inventory_data(companies, company_meta, all_companies, from_date, to_date, search_text=None):
    items_all = frappe.get_all(
        "Item",
        fields=["name", "item_name", "item_group", "stock_uom", "valuation_rate", "is_stock_item"],
        order_by="name asc",
        limit_page_length=0
    )

    placeholders = ", ".join(["%s"] * len(companies))
    
    sle_query = """
        SELECT 
            sle.item_code,
            sle.company,
            SUM(CASE WHEN sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) as total_in_qty,
            SUM(CASE WHEN sle.actual_qty < 0 THEN ABS(sle.actual_qty) ELSE 0 END) as total_out_qty,
            SUM(sle.actual_qty) as ending_balance_qty,
            AVG(sle.valuation_rate) as avg_valuation_rate,
            SUM(sle.stock_value_difference) as total_stock_value
        FROM `tabStock Ledger Entry` sle
        WHERE sle.is_cancelled = 0
          AND sle.posting_date <= %s
          AND sle.company IN (""" + placeholders + """)
        GROUP BY sle.item_code, sle.company
    """
    sle_data = frappe.db.sql(sle_query, [to_date] + companies, as_dict=True)
    sle_map = {}
    for s in sle_data:
        sle_map[(s.get("item_code"), s.get("company"))] = s

    bin_query = """
        SELECT 
            b.item_code,
            wh.company,
            SUM(b.actual_qty) as actual_qty,
            AVG(b.valuation_rate) as valuation_rate,
            SUM(b.stock_value) as stock_value
        FROM `tabBin` b
        LEFT JOIN `tabWarehouse` wh ON wh.name = b.warehouse
        WHERE wh.company IN (""" + placeholders + """)
        GROUP BY b.item_code, wh.company
    """
    bin_data = frappe.db.sql(bin_query, companies, as_dict=True)
    bin_map = {}
    for b in bin_data:
        bin_map[(b.get("item_code"), b.get("company"))] = b

    matrix_rows = []
    total_qty_all = 0.0
    total_val_all = 0.0
    total_in_all = 0.0
    total_out_all = 0.0

    company_qty_totals = {c: 0.0 for c in companies}
    company_val_totals = {c: 0.0 for c in companies}
    company_in_totals = {c: 0.0 for c in companies}
    company_out_totals = {c: 0.0 for c in companies}

    search_lower = str(search_text).lower() if search_text else None

    for it in items_all:
        code = it.get("name")
        name = it.get("item_name") or code
        group = it.get("item_group") or "Standard"
        uom = it.get("stock_uom") or "Unit"
        def_rate = float(it.get("valuation_rate") or 0)

        if search_lower and (search_lower not in code.lower() and search_lower not in name.lower() and search_lower not in group.lower()):
            continue

        row_item = {
            "item_code": code,
            "item_name": name,
            "item_group": group,
            "stock_uom": uom,
            "is_stock_item": it.get("is_stock_item"),
            "avg_valuation_rate": def_rate,
            "companies_qty": {c: 0.0 for c in companies},
            "companies_in": {c: 0.0 for c in companies},
            "companies_out": {c: 0.0 for c in companies},
            "companies_val": {c: 0.0 for c in companies},
            "total_in": 0.0,
            "total_out": 0.0,
            "total_qty": 0.0,
            "total_val": 0.0,
            "has_transactions": False
        }

        rates = []
        for co in companies:
            k = (code, co)
            in_q = 0.0
            out_q = 0.0
            end_q = 0.0
            val = 0.0

            if k in sle_map:
                s = sle_map[k]
                in_q = float(s.get("total_in_qty") or 0)
                out_q = float(s.get("total_out_qty") or 0)
                end_q = float(s.get("ending_balance_qty") or 0)
                val = float(s.get("total_stock_value") or 0)
                v_rate = float(s.get("avg_valuation_rate") or 0)
                if v_rate > 0:
                    rates.append(v_rate)
                row_item["has_transactions"] = True

            if k in bin_map:
                b = bin_map[k]
                b_qty = float(b.get("actual_qty") or 0)
                b_val = float(b.get("stock_value") or 0)
                b_rate = float(b.get("valuation_rate") or 0)
                if b_qty != 0 or end_q == 0:
                    end_q = b_qty
                    val = b_val
                if b_rate > 0:
                    rates.append(b_rate)
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
        "report": "Consolidated Inventory & Stock Valuation Audit",
        "as_of_date": to_date,
        "companies": companies,
        "all_companies": all_companies,
        "company_meta": company_meta,
        "rows": matrix_rows,
        "totals": {
            "total_in_qty": total_in_all,
            "total_out_qty": total_out_all,
            "total_qty": total_qty_all,
            "total_val": total_val_all,
            "company_in": company_in_totals,
            "company_out": company_out_totals,
            "company_qty": company_qty_totals,
            "company_val": company_val_totals
        }
    }

def get_drilldown_data(company, account, from_date, to_date):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    values = [from_date, to_date]
    if company:
        conditions.append("gle.company = %s")
        values.append(company)
    if account:
        conditions.append("(gle.account LIKE %s OR acc.account_name = %s)")
        values.extend(["%" + account + "%", account])
    
    where_clause = " AND ".join(conditions)
    entries = frappe.db.sql("""
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
        JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE """ + where_clause + """
        ORDER BY gle.posting_date desc
        LIMIT 200
    """, values, as_dict=True)
    return {"entries": entries}

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
            sle.name,
            sle.posting_date,
            sle.posting_time,
            sle.company,
            sle.warehouse,
            sle.voucher_type,
            sle.voucher_no,
            sle.actual_qty,
            sle.qty_after_transaction,
            sle.valuation_rate,
            sle.stock_value_difference
        FROM `tabStock Ledger Entry` sle
        WHERE """ + where_clause + """
        ORDER BY sle.posting_date desc, sle.posting_time desc
        LIMIT 200
    """, values, as_dict=True)
    return {"entries": entries}

response = execute()
frappe.response["message"] = response
'''

def main():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
    if r.status_code != 200:
        print("Login failed:", r.status_code)
        return

    print("Logged in successfully!")

    # 1. Update Server Script on VPS
    ss_payload = {
        "doctype": "Server Script",
        "name": "VM Consolidated Financials API",
        "script_type": "API",
        "api_method": "vm_consolidated_financials",
        "allow_guest": 1,
        "disabled": 0,
        "script": SERVER_SCRIPT_CODE
    }

    check = s.get(f"{BASE_URL}/api/resource/Server%20Script/VM%20Consolidated%20Financials%20API")
    if check.status_code == 200:
        print("Updating existing Server Script...")
        res = s.put(f"{BASE_URL}/api/resource/Server%20Script/VM%20Consolidated%20Financials%20API", json=ss_payload)
    else:
        print("Creating Server Script...")
        res = s.post(f"{BASE_URL}/api/resource/Server%20Script", json=ss_payload)

    print("Server Script status:", res.status_code)

if __name__ == '__main__':
    main()
