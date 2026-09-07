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
    page = int(frappe.form_dict.get("page") or 1)
    page_length = int(frappe.form_dict.get("page_length") or 100)

    # 1. Fetch all companies
    companies_records = frappe.get_all(
        "Company",
        fields=["name", "abbr", "default_currency"],
        order_by="name asc"
    )
    companies = [c.get("name") for c in companies_records]
    company_meta = {c.get("name"): {"abbr": c.get("abbr"), "currency": c.get("default_currency") or "PHP"} for c in companies_records}

    if report_type == "pnl":
        return get_pnl_data(companies, company_meta, from_date, to_date)
    elif report_type == "balance_sheet":
        return get_balance_sheet_data(companies, company_meta, to_date)
    elif report_type == "general_ledger":
        return get_gl_data(companies, from_date, to_date, voucher_type, search_text, page, page_length)
    elif report_type == "inventory_audit":
        return get_inventory_data(companies, company_meta, search_text)
    elif report_type == "drilldown":
        company = frappe.form_dict.get("company")
        account = frappe.form_dict.get("account")
        return get_drilldown_data(company, account, from_date, to_date)
    else:
        return {"error": "Invalid report_type: " + str(report_type)}

def get_pnl_data(companies, company_meta, from_date, to_date):
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
        raw_name = row.get("account")
        clean_name = row.get("account_name") or raw_name.split(" - ")[0].strip()
        root_type = row.get("root_type")
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

def get_balance_sheet_data(companies, company_meta, to_date):
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
        raw_name = row.get("account")
        clean_name = row.get("account_name") or raw_name.split(" - ")[0].strip()
        root_type = row.get("root_type")
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

def get_gl_data(companies, from_date, to_date, voucher_type, search_text, page, page_length):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    placeholders = ", ".join(["%s"] * len(companies))
    conditions.append("gle.company IN (" + placeholders + ")")
    values = [from_date, to_date] + list(companies)

    if voucher_type:
        conditions.append("gle.voucher_type = %s")
        values = values + [voucher_type]

    if search_text:
        conditions.append("(gle.voucher_no LIKE %s OR gle.account LIKE %s OR gle.remarks LIKE %s)")
        wildcard = "%" + str(search_text) + "%"
        values = values + [wildcard, wildcard, wildcard]

    where_clause = " AND ".join(conditions)

    count_res = frappe.db.sql("SELECT COUNT(*) as cnt FROM `tabGL Entry` gle WHERE " + where_clause, values, as_dict=True)
    total_count = count_res[0].get("cnt") if count_res else 0

    limit_start = (int(page) - 1) * int(page_length)
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
        "rows": rows
    }

def get_inventory_data(companies, company_meta, search_text):
    conditions = ["(b.actual_qty != 0 OR b.stock_value != 0)"]
    values = []

    if search_text:
        conditions.append("(b.item_code LIKE %s OR item.item_name LIKE %s)")
        wildcard = "%" + str(search_text) + "%"
        values = values + [wildcard, wildcard]

    where_clause = " AND ".join(conditions)

    bins = frappe.db.sql("""
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
        WHERE """ + where_clause + """
        GROUP BY b.item_code, wh.company
        ORDER BY b.item_code asc
    """, values, as_dict=True)

    item_matrix = {}
    for row in bins:
        code = row.get("item_code")
        co = row.get("company") or "Other"
        if code not in item_matrix:
            item_matrix[code] = {
                "item_code": code,
                "item_name": row.get("item_name") or code,
                "item_group": row.get("item_group") or "Standard",
                "stock_uom": row.get("stock_uom") or "Unit",
                "avg_valuation_rate": float(row.get("valuation_rate") or 0),
                "companies_qty": {c: 0.0 for c in companies},
                "companies_val": {c: 0.0 for c in companies},
                "total_qty": 0.0,
                "total_val": 0.0
            }
        
        qty = float(row.get("actual_qty") or 0)
        val = float(row.get("stock_value") or 0)
        
        if co in item_matrix[code]["companies_qty"]:
            item_matrix[code]["companies_qty"][co] = item_matrix[code]["companies_qty"][co] + qty
            item_matrix[code]["companies_val"][co] = item_matrix[code]["companies_val"][co] + val
        
        item_matrix[code]["total_qty"] = item_matrix[code]["total_qty"] + qty
        item_matrix[code]["total_val"] = item_matrix[code]["total_val"] + val

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

def get_drilldown_data(company, account, from_date, to_date):
    conditions = ["gle.posting_date BETWEEN %s AND %s", "gle.is_cancelled = 0"]
    values = [from_date, to_date]

    if company:
        conditions.append("gle.company = %s")
        values = values + [company]
    
    if account:
        conditions.append("(gle.account = %s OR gle.account LIKE %s)")
        values = values + [account, account + " - %"]

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
    print("\n--- Testing API Endpoints ---")
    # 1. Test P&L
    pnl_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=pnl&from_date=2026-01-01&to_date=2026-12-31")
    print(f"P&L Status: {pnl_res.status_code}")
    pnl_data = pnl_res.json().get("message", {})
    kpis = pnl_data.get("kpis", {})
    print(f" - Consolidated Revenue: PHP {kpis.get('consolidated_revenue', 0):,.2f}")
    print(f" - Consolidated Gross Profit: PHP {kpis.get('consolidated_gross_profit', 0):,.2f}")
    print(f" - Consolidated Net Profit: PHP {kpis.get('consolidated_net_profit', 0):,.2f}")
    print(f" - Total Companies: {len(pnl_data.get('companies', []))}")

    # 2. Test Balance Sheet
    bs_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=balance_sheet&to_date=2026-12-31")
    print(f"\nBalance Sheet Status: {bs_res.status_code}")
    bs_data = bs_res.json().get("message", {})
    bs_kpis = bs_data.get("kpis", {})
    print(f" - Consolidated Assets: PHP {bs_kpis.get('consolidated_assets', 0):,.2f}")
    print(f" - Consolidated Liabilities: PHP {bs_kpis.get('consolidated_liabilities', 0):,.2f}")
    print(f" - Consolidated Equity: PHP {bs_kpis.get('consolidated_equity', 0):,.2f}")
    print(f" - Is Balanced: {bs_kpis.get('is_balanced')}")

    # 3. Test General Ledger
    gl_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=general_ledger&from_date=2026-01-01&to_date=2026-12-31&page_length=5")
    print(f"\nGeneral Ledger Status: {gl_res.status_code}")
    gl_data = gl_res.json().get("message", {})
    print(f" - Total Records: {gl_data.get('total_records')}")
    print(f" - Sample Rows: {len(gl_data.get('rows', []))}")

    # 4. Test Inventory Audit
    inv_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=inventory_audit")
    print(f"\nInventory Audit Status: {inv_res.status_code}")
    inv_data = inv_res.json().get("message", {})
    print(f" - Total SKUs: {inv_data.get('total_sku_count')}")
    print(f" - Total Units: {inv_data.get('total_qty')}")
    print(f" - Total Stock Valuation: PHP {inv_data.get('total_val', 0):,.2f}")

    # 5. Test Drill-Down
    dd_res = session.get(f"{BASE_URL}/api/method/vm_consolidated_financials?report_type=drilldown&account=Debtors&from_date=2026-01-01&to_date=2026-12-31")
    print(f"\nDrilldown Status: {dd_res.status_code}")
    dd_data = dd_res.json().get("message", {})
    print(f" - Drilldown Entries for Debtors: {len(dd_data.get('entries', []))}")

if __name__ == "__main__":
    deploy_server_script()
    test_api()
