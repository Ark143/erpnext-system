# -*- coding: utf-8 -*-
"""
Consolidated Multi-Company Financial & Inventory Audit Engine
Provides multi-column P&L, Balance Sheet, General Ledger Explorer, and Inventory Audit
across all companies with consolidated totals and drill-downs.
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
    """
    Main entry point for Consolidated Financials API.
    report_type: 'pnl' | 'balance_sheet' | 'general_ledger' | 'inventory_audit' | 'drilldown'
    """
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
    
    if selected_companies:
        if isinstance(selected_companies, str):
            import json
            try:
                selected_companies = json.loads(selected_companies)
            except Exception:
                selected_companies = [c.strip() for c in selected_companies.split(",") if c.strip()]
        if selected_companies and len(selected_companies) > 0:
            companies_records = [c for c in companies_records if c.name in selected_companies]

    companies = [c.name for c in companies_records]
    company_meta = {c.name: {"abbr": c.abbr, "currency": c.default_currency or "PHP"} for c in companies_records}

    if report_type == "pnl":
        return get_consolidated_pnl(companies, company_meta, from_date, to_date)
    elif report_type == "balance_sheet":
        return get_consolidated_balance_sheet(companies, company_meta, to_date)
    elif report_type == "general_ledger":
        return get_multi_company_gl(companies, from_date, to_date, voucher_type, search_text, page, page_length)
    elif report_type == "inventory_audit":
        return get_consolidated_inventory_audit(companies, company_meta, item_group, warehouse, search_text)
    elif report_type == "drilldown":
        account = frappe.form_dict.get("account")
        company = frappe.form_dict.get("company")
        return get_account_drilldown(company, account, from_date, to_date)
    else:
        frappe.throw(_("Invalid report type: {0}").format(report_type))


def get_consolidated_pnl(companies, company_meta, from_date, to_date):
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


def get_consolidated_balance_sheet(companies, company_meta, to_date):
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


def get_consolidated_inventory_audit(companies, company_meta, item_group=None, warehouse=None, search_text=None):
    conditions = ["(b.actual_qty != 0 OR b.stock_value != 0)"]
    values = []

    if search_text:
        conditions.append("(b.item_code LIKE %s OR item.item_name LIKE %s)")
        wildcard = f"%{search_text}%"
        values.extend([wildcard, wildcard])

    where_clause = " AND ".join(conditions)

    bins = frappe.db.sql(f"""
        SELECT 
            b.item_code,
            MAX(item.item_name) as item_name,
            MAX(item.item_group) as item_group,
            MAX(item.stock_uom) as stock_uom,
            wh.company,
            SUM(b.actual_qty) as actual_qty,
            AVG(b.valuation_rate) as valuation_rate,
            SUM(b.stock_value) as stock_value
        FROM `tabBin` b
        LEFT JOIN `tabItem` item ON item.name = b.item_code
        LEFT JOIN `tabWarehouse` wh ON wh.name = b.warehouse
        WHERE {where_clause}
        GROUP BY b.item_code, wh.company
        ORDER BY b.item_code asc
    """, values, as_dict=True)

    item_matrix = {}
    for row in bins:
        code = row.item_code
        co = row.company or "Other"
        if code not in item_matrix:
            item_matrix[code] = {
                "item_code": code,
                "item_name": row.item_name or code,
                "item_group": row.item_group or "Standard",
                "stock_uom": row.stock_uom or "Unit",
                "avg_valuation_rate": flt(row.valuation_rate),
                "companies_qty": {c: 0.0 for c in companies},
                "companies_val": {c: 0.0 for c in companies},
                "total_qty": 0.0,
                "total_val": 0.0
            }
        
        qty = flt(row.actual_qty)
        val = flt(row.stock_value)
        
        if co in item_matrix[code]["companies_qty"]:
            item_matrix[code]["companies_qty"][co] += qty
            item_matrix[code]["companies_val"][co] += val
        
        item_matrix[code]["total_qty"] += qty
        item_matrix[code]["total_val"] += val

    matrix_rows = list(item_matrix.values())

    company_qty_totals = {c: sum(r["companies_qty"].get(c, 0.0) for r in matrix_rows) for c in companies}
    company_val_totals = {c: sum(r["companies_val"].get(c, 0.0) for r in matrix_rows) for c in companies}

    return {
        "report": "Multi-Company Inventory Audit",
        "companies": companies,
        "company_meta": company_meta,
        "total_sku_count": len(matrix_rows),
        "total_qty": sum(r["total_qty"] for r in matrix_rows),
        "total_val": sum(r["total_val"] for r in matrix_rows),
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
