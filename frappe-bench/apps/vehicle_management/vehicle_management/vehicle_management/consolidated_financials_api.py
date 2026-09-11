# -*- coding: utf-8 -*-
"""
Consolidated Multi-Company Financial & Inventory Audit Engine
Provides multi-column P&L, Balance Sheet, General Ledger Explorer, and Inventory Audit
across all companies with dynamic company column filtering, all-item running balances, and drill-downs.
"""

import frappe
from frappe import _
from frappe.utils import flt, cstr, getdate, nowdate, add_months

@frappe.whitelist(allow_guest=False)
def get_consolidated_financials(
    report_type="pnl",
    from_date=None,
    to_date=None,
    fiscal_year=None,
    selected_companies=None,
    item_group=None,
    warehouse=None,
    voucher_type=None,
    search_text=None,
    page=1,
    page_length=100
):
    if not to_date:
        to_date = nowdate()
    if not from_date:
        curr_year = getdate(to_date).year
        from_date = f"{curr_year}-01-01"

    # 1. Fetch active companies
    companies_records = frappe.get_all(
        "Company",
        fields=["name", "abbr", "default_currency", "country"],
        order_by="name asc"
    )
    all_companies = [c.name for c in companies_records]
    company_meta = {c.name: {"abbr": c.abbr, "currency": c.default_currency or "PHP"} for c in companies_records}

    companies = all_companies
    if selected_companies:
        if isinstance(selected_companies, str):
            clean_str = selected_companies.replace("[", "").replace("]", "").replace('"', '').replace("'", "")
            parts = [p.strip() for p in clean_str.split(",") if p.strip()]
            if parts:
                filtered = [c for c in all_companies if c in parts]
                if filtered:
                    companies = filtered

    if report_type == "pnl":
        return get_consolidated_pnl(companies, company_meta, all_companies, from_date, to_date)
    elif report_type == "balance_sheet":
        return get_consolidated_balance_sheet(companies, company_meta, all_companies, to_date)
    elif report_type == "cash_flow":
        period_type = frappe.form_dict.get("period") or "monthly"
        return get_consolidated_cash_flow(companies, company_meta, all_companies, from_date, to_date, period_type)
    elif report_type == "ar_aging":
        as_of_date = frappe.form_dict.get("as_of_date") or to_date or nowdate()
        customer = frappe.form_dict.get("customer")
        return get_ar_aging_report(companies, company_meta, all_companies, as_of_date, customer)
    elif report_type == "ap_aging":
        as_of_date = frappe.form_dict.get("as_of_date") or to_date or nowdate()
        supplier = frappe.form_dict.get("supplier")
        return get_ap_aging_report(companies, company_meta, all_companies, as_of_date, supplier)
    elif report_type == "general_ledger":
        return get_multi_company_gl(companies, from_date, to_date, voucher_type, search_text, page, page_length)
    elif report_type == "inventory_audit":
        return get_consolidated_inventory_audit(companies, company_meta, all_companies, from_date, to_date, search_text)
    elif report_type == "drilldown":
        account = frappe.form_dict.get("account")
        company = frappe.form_dict.get("company")
        return get_account_drilldown(company, account, from_date, to_date)
    elif report_type == "stock_ledger_drilldown":
        item_code = frappe.form_dict.get("item_code")
        company = frappe.form_dict.get("company")
        return get_stock_ledger_drilldown(item_code, company, from_date, to_date)
    else:
        frappe.throw(_("Invalid report type: {0}").format(report_type))


def get_consolidated_pnl(companies, company_meta, all_companies, from_date, to_date):
    placeholders = ", ".join(["%s"] * len(companies))
    query = f"""
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
          AND gle.company IN ({placeholders})
        GROUP BY gle.company, gle.account
        ORDER BY MAX(acc.root_type) desc, MAX(acc.account_name) asc
    """
    gl_entries = frappe.db.sql(query, [from_date, to_date] + companies, as_dict=True)

    income_accounts = {}
    cogs_accounts = {}
    expense_accounts = {}

    for row in gl_entries:
        co = row.company
        raw_name = row.account
        clean_name = row.account_name or raw_name.split(" - ")[0].strip()
        root_type = row.root_type
        acc_type = row.account_type or ""
        
        debit = flt(row.total_debit)
        credit = flt(row.total_credit)

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
        
        target_dict[clean_name]["companies"][co] += net_amt
        target_dict[clean_name]["total"] += net_amt

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


def get_consolidated_balance_sheet(companies, company_meta, all_companies, to_date):
    placeholders = ", ".join(["%s"] * len(companies))
    query = f"""
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
          AND gle.company IN ({placeholders})
        GROUP BY gle.company, gle.account
        ORDER BY MAX(acc.root_type) asc, MAX(acc.account_name) asc
    """
    gl_entries = frappe.db.sql(query, [to_date] + companies, as_dict=True)

    asset_accounts = {}
    liability_accounts = {}
    equity_accounts = {}
    period_pnl_per_company = {c: 0.0 for c in companies}

    for row in gl_entries:
        co = row.company
        raw_name = row.account
        clean_name = row.account_name or raw_name.split(" - ")[0].strip()
        root_type = row.root_type
        acc_type = row.account_type or ""
        
        debit = flt(row.total_debit)
        credit = flt(row.total_credit)

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
            period_pnl_per_company[co] += (credit - debit)
            continue
        elif root_type == "Expense":
            period_pnl_per_company[co] -= (debit - credit)
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
        
        target_dict[clean_name]["companies"][co] += net_amt
        target_dict[clean_name]["total"] += net_amt

    retained_row = {
        "account_name": "Current & Prior Period Earnings",
        "root_type": "Equity",
        "account_type": "Accumulated Profit",
        "companies": period_pnl_per_company,
        "total": sum(period_pnl_per_company.values())
    }
    equity_accounts["Current & Prior Period Earnings"] = retained_row

    asset_rows = list(asset_accounts.values())
    liability_rows = list(liability_accounts.values())
    equity_rows = list(equity_accounts.values())

    asset_totals = {c: sum(r["companies"][c] for r in asset_rows) for c in companies}
    asset_consolidated = sum(r["total"] for r in asset_rows)

    liability_totals = {c: sum(r["companies"][c] for r in liability_rows) for c in companies}
    liability_consolidated = sum(r["total"] for r in liability_rows)

    equity_totals = {c: sum(r["companies"][c] for r in equity_rows) for c in companies}
    equity_consolidated = sum(r["total"] for r in equity_rows)

    total_liab_equity_totals = {c: liability_totals[c] + equity_totals[c] for c in companies}
    total_liab_equity_consolidated = liability_consolidated + equity_consolidated

    balance_check_consolidated = round(asset_consolidated - total_liab_equity_consolidated, 2)

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
                "title": "Equity & Retained Reserves",
                "rows": equity_rows,
                "totals": equity_totals,
                "consolidated": equity_consolidated
            },
            "total_liabilities_equity": {
                "title": "Total Liabilities & Equity",
                "totals": total_liab_equity_totals,
                "consolidated": total_liab_equity_consolidated
            },
            "balance_check": {
                "title": "Out of Balance Difference",
                "consolidated": balance_check_consolidated,
                "is_balanced": balance_check_consolidated == 0
            }
        },
        "kpis": {
            "consolidated_assets": asset_consolidated,
            "consolidated_liabilities": liability_consolidated,
            "consolidated_equity": equity_consolidated,
            "is_balanced": balance_check_consolidated == 0
        }
    }


def get_multi_company_gl(companies, from_date, to_date, voucher_type=None, search_text=None, page=1, page_length=100):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    placeholders = ", ".join(["%s"] * len(companies))
    conditions.append(f"gle.company IN ({placeholders})")
    values = [from_date, to_date] + list(companies)

    if voucher_type:
        conditions.append("gle.voucher_type = %s")
        values.append(voucher_type)

    if search_text:
        conditions.append("(gle.voucher_no LIKE %s OR gle.account LIKE %s OR gle.remarks LIKE %s)")
        wildcard = f"%{search_text}%"
        values.extend([wildcard, wildcard, wildcard])

    where_clause = " AND ".join(conditions)

    count_res = frappe.db.sql(f"SELECT COUNT(*) as cnt FROM `tabGL Entry` gle WHERE {where_clause}", values, as_dict=True)
    total_count = count_res[0].cnt if count_res else 0

    limit_start = (int(page) - 1) * int(page_length)
    limit_clause = f"LIMIT {int(page_length)} OFFSET {int(limit_start)}"

    rows = frappe.db.sql(f"""
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
        WHERE {where_clause}
        ORDER BY gle.posting_date desc, gle.creation desc
        {limit_clause}
    """, values, as_dict=True)

    return {
        "report": "Multi-Company General Ledger",
        "total_records": total_count,
        "rows": rows
    }


def get_consolidated_inventory_audit(companies, company_meta, all_companies, from_date, to_date, search_text=None):
    items_all = frappe.get_all(
        "Item",
        fields=["name", "item_name", "item_group", "stock_uom", "valuation_rate", "is_stock_item"],
        order_by="name asc",
        limit_page_length=0
    )

    placeholders = ", ".join(["%s"] * len(companies))
    
    sle_query = f"""
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
          AND sle.company IN ({placeholders})
        GROUP BY sle.item_code, sle.company
    """
    sle_data = frappe.db.sql(sle_query, [to_date] + companies, as_dict=True)
    sle_map = {}
    for s in sle_data:
        sle_map[(s.get("item_code"), s.get("company"))] = s

    bin_query = f"""
        SELECT 
            b.item_code,
            wh.company,
            SUM(b.actual_qty) as actual_qty,
            AVG(b.valuation_rate) as valuation_rate,
            SUM(b.stock_value) as stock_value
        FROM `tabBin` b
        LEFT JOIN `tabWarehouse` wh ON wh.name = b.warehouse
        WHERE wh.company IN ({placeholders})
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
        def_rate = flt(it.get("valuation_rate"))

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
                in_q = flt(s.get("total_in_qty"))
                out_q = flt(s.get("total_out_qty"))
                end_q = flt(s.get("ending_balance_qty"))
                val = flt(s.get("total_stock_value"))
                v_rate = flt(s.get("avg_valuation_rate"))
                if v_rate > 0:
                    rates.append(v_rate)
                row_item["has_transactions"] = True

            if k in bin_map:
                b = bin_map[k]
                b_qty = flt(b.get("actual_qty"))
                b_val = flt(b.get("stock_value"))
                b_rate = flt(b.get("valuation_rate"))
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

            row_item["total_in"] += in_q
            row_item["total_out"] += out_q
            row_item["total_qty"] += end_q
            row_item["total_val"] += val

            company_in_totals[co] += in_q
            company_out_totals[co] += out_q
            company_qty_totals[co] += end_q
            company_val_totals[co] += val

        if rates:
            row_item["avg_valuation_rate"] = sum(rates) / len(rates)

        total_in_all += row_item["total_in"]
        total_out_all += row_item["total_out"]
        total_qty_all += row_item["total_qty"]
        total_val_all += row_item["total_val"]

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


def get_account_drilldown(company, account, from_date, to_date):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    values = [from_date, to_date]

    if company:
        conditions.append("gle.company = %s")
        values.append(company)
    
    if account:
        conditions.append("(gle.account = %s OR gle.account LIKE %s)")
        values.extend([account, f"{account} - %"])

    where_clause = " AND ".join(conditions)

    entries = frappe.db.sql(f"""
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
        WHERE {where_clause}
        ORDER BY gle.posting_date desc, gle.creation desc
        LIMIT 100
    """, values, as_dict=True)

    return {
        "entries": entries,
        "total_debit": sum(flt(e.debit) for e in entries),
        "total_credit": sum(flt(e.credit) for e in entries)
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

    entries = frappe.db.sql(f"""
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
        WHERE {where_clause}
        ORDER BY sle.posting_date asc, sle.posting_time asc, sle.creation asc
        LIMIT 200
    """, values, as_dict=True)

    return {
        "item_code": item_code,
        "company": company,
        "entries": entries,
        "total_in": sum(flt(e.actual_qty) for e in entries if flt(e.actual_qty) > 0),
        "total_out": sum(abs(flt(e.actual_qty)) for e in entries if flt(e.actual_qty) < 0),
        "ending_qty": entries[-1].get("qty_after_transaction") if entries else 0.0,
        "ending_value": entries[-1].get("stock_value") if entries else 0.0
    }


def get_consolidated_cash_flow(companies, company_meta, all_companies, from_date, to_date, period_type="monthly"):
    placeholders = ", ".join(["%s"] * len(companies))
    
    # 1. Opening cash balance as of from_date for each company
    opening_sql = f"""
        SELECT 
            gle.company,
            SUM(gle.debit - gle.credit) as opening_balance
        FROM `tabGL Entry` gle
        JOIN `tabAccount` acc ON acc.name = gle.account
        WHERE gle.posting_date < %s
          AND gle.is_cancelled = 0
          AND (acc.account_type IN ('Cash', 'Bank') OR (acc.root_type = 'Asset' AND (acc.account_name LIKE '%%Cash%%' OR acc.account_name LIKE '%%Bank%%')))
          AND gle.company IN ({placeholders})
        GROUP BY gle.company
    """
    opening_rows = frappe.db.sql(opening_sql, [from_date] + companies, as_dict=True)
    opening_by_company = {c: 0.0 for c in companies}
    for r in opening_rows:
        opening_by_company[r.company] = flt(r.opening_balance)
    total_opening_consolidated = sum(opening_by_company.values())

    # 2. Query all cash transactions in the period
    trx_sql = f"""
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
          AND gle.company IN ({placeholders})
        ORDER BY gle.posting_date ASC, gle.creation ASC
    """
    entries = frappe.db.sql(trx_sql, [from_date, to_date] + companies, as_dict=True)

    # Categories definitions
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

    # Grouping by period
    periods_map = {}

    for e in entries:
        p_date = getdate(e.posting_date)
        co = e.company
        debit = flt(e.debit)
        credit = flt(e.credit)
        against = (e.against or "").lower()
        v_type = e.voucher_type or ""

        month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_abbrs = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        m_str = str(p_date.month) if p_date.month >= 10 else "0" + str(p_date.month)
        d_str = str(p_date.day) if p_date.day >= 10 else "0" + str(p_date.day)

        if period_type == "daily":
            pkey = f"{p_date.year}-{m_str}-{d_str}"
            plabel = f"{month_abbrs[p_date.month]} {d_str}, {p_date.year}"
        elif period_type == "yearly":
            pkey = str(p_date.year)
            plabel = f"FY {p_date.year}"
        else:
            pkey = f"{p_date.year}-{m_str}"
            plabel = f"{month_names[p_date.month]} {p_date.year}"

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
        p_obj["entries_count"] += 1

        if debit > 0:
            if v_type in ("Sales Invoice", "POS Invoice") or "debtor" in against or "customer" in against:
                cat_key = "customer_collections"
            elif "income" in against or "sales" in against or "revenue" in against or "service" in against:
                cat_key = "operating_revenue"
            else:
                cat_key = "other_inflows"

            inflow_cats[cat_key]["companies"][co] += debit
            inflow_cats[cat_key]["total"] += debit

            p_obj["inflows"][co] += debit
            p_obj["inflow_total"] += debit
            p_obj["inflow_breakdown"][cat_key][co] += debit
            p_obj["net"][co] += debit
            p_obj["net_total"] += debit

        if credit > 0:
            if v_type in ("Purchase Invoice",) or "creditor" in against or "supplier" in against or "vendor" in against:
                cat_key = "supplier_payments"
            elif "expense" in against or "salary" in against or "payroll" in against or "rent" in against or "utility" in against:
                cat_key = "operating_expenses"
            elif "asset" in against or "stock" in against or "inventory" in against:
                cat_key = "stock_assets"
            else:
                cat_key = "other_outflows"

            outflow_cats[cat_key]["companies"][co] += credit
            outflow_cats[cat_key]["total"] += credit

            p_obj["outflows"][co] += credit
            p_obj["outflow_total"] += credit
            p_obj["outflow_breakdown"][cat_key][co] += credit
            p_obj["net"][co] -= credit
            p_obj["net_total"] -= credit

    sorted_pkeys = sorted(periods_map.keys())
    periods_list = []
    
    running_company_bal = {c: opening_by_company[c] for c in companies}
    running_total_bal = total_opening_consolidated

    for pk in sorted_pkeys:
        p = periods_map[pk]
        p_open_co = {c: running_company_bal[c] for c in companies}
        p_open_tot = running_total_bal

        for c in companies:
            running_company_bal[c] += p["net"][c]
        running_total_bal += p["net_total"]

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


def get_ar_aging_report(companies, company_meta, all_companies, as_of_date=None, customer=None):
    if not as_of_date:
        as_of_date = nowdate()
    as_of = getdate(as_of_date)

    placeholders = ", ".join(["%s"] * len(companies))
    params = list(companies)
    extra_cond = ""
    if customer:
        extra_cond += " AND (si.customer = %s OR si.customer_name LIKE %s)"
        params.extend([customer, f"%{customer}%"])

    query = f"""
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
          AND si.company IN ({placeholders})
          {extra_cond}
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
        cust_id = inv.customer or "Unknown"
        cust_name = inv.customer_name or cust_id
        co = inv.company
        post_date = getdate(inv.posting_date)
        due_date = getdate(inv.due_date or inv.posting_date)
        
        grand_total = flt(inv.grand_total)
        outstanding = flt(inv.outstanding_amount)
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
            "name": inv.name,
            "company": co,
            "company_abbr": company_meta.get(co, {}).get("abbr", co[:4]),
            "customer": cust_id,
            "customer_name": cust_name,
            "posting_date": str(post_date),
            "due_date": str(due_date),
            "terms": inv.payment_terms_template or inv.tc_name or "Standard Terms",
            "days_overdue": max(0, days_overdue),
            "is_overdue": days_overdue > 0,
            "bucket": bucket,
            "grand_total": grand_total,
            "outstanding_amount": outstanding,
            "amount_aged": amount_to_age,
            "status": inv.status
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
        c_entry[bucket] += amount_to_age
        c_entry["total_outstanding"] += amount_to_age
        c_entry["total_invoiced"] += grand_total
        c_entry["invoice_count"] += 1
        c_entry["companies"][co] += amount_to_age

        if co in company_map:
            co_entry = company_map[co]
            co_entry[bucket] += amount_to_age
            co_entry["total_outstanding"] += amount_to_age
            co_entry["total_invoiced"] += grand_total
            co_entry["invoice_count"] += 1

        bucket_totals[bucket] += amount_to_age
        bucket_totals["total_outstanding"] += amount_to_age
        bucket_totals["total_invoiced"] += grand_total
        bucket_totals["invoice_count"] += 1

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


def get_ap_aging_report(companies, company_meta, all_companies, as_of_date=None, supplier=None):
    if not as_of_date:
        as_of_date = nowdate()
    as_of = getdate(as_of_date)

    placeholders = ", ".join(["%s"] * len(companies))
    params = list(companies)
    extra_cond = ""
    if supplier:
        extra_cond += " AND (pi.supplier = %s OR pi.supplier_name LIKE %s)"
        params.extend([supplier, f"%{supplier}%"])

    query = f"""
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
          AND pi.company IN ({placeholders})
          {extra_cond}
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
        supp_id = bill.supplier or "Unknown"
        supp_name = bill.supplier_name or supp_id
        co = bill.company
        post_date = getdate(bill.posting_date)
        due_date = getdate(bill.due_date or bill.posting_date)
        
        grand_total = flt(bill.grand_total)
        outstanding = flt(bill.outstanding_amount)
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
            "name": bill.name,
            "company": co,
            "company_abbr": company_meta.get(co, {}).get("abbr", co[:4]),
            "supplier": supp_id,
            "supplier_name": supp_name,
            "bill_no": bill.bill_no or bill.name,
            "bill_date": str(bill.bill_date or post_date),
            "posting_date": str(post_date),
            "due_date": str(due_date),
            "terms": bill.payment_terms_template or bill.tc_name or "Standard Terms",
            "days_overdue": max(0, days_overdue),
            "is_overdue": days_overdue > 0,
            "bucket": bucket,
            "grand_total": grand_total,
            "outstanding_amount": outstanding,
            "amount_aged": amount_to_age,
            "status": bill.status
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
        s_entry[bucket] += amount_to_age
        s_entry["total_outstanding"] += amount_to_age
        s_entry["total_billed"] += grand_total
        s_entry["bill_count"] += 1
        s_entry["companies"][co] += amount_to_age

        if co in company_map:
            co_entry = company_map[co]
            co_entry[bucket] += amount_to_age
            co_entry["total_outstanding"] += amount_to_age
            co_entry["total_billed"] += grand_total
            co_entry["bill_count"] += 1

        bucket_totals[bucket] += amount_to_age
        bucket_totals["total_outstanding"] += amount_to_age
        bucket_totals["total_billed"] += grand_total
        bucket_totals["bill_count"] += 1

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
