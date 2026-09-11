import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    with op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
            method="POST",
        ),
        timeout=30,
    ) as r:
        raw = r.read().decode()
        if "message" in raw and "Logged In" in raw:
            print("[OK] Logged into VPS as Administrator")

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body[:400]}")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body}

report_script_code = """
def run_trial_balance(filters):
    def prepare_net_row(row):
        dr_or_cr = "debit" if row.get("root_type") in ["Asset", "Equity", "Expense"] else "credit"
        rev_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"
        
        for prefix in ["opening", "closing"]:
            v_col = prefix + "_" + dr_or_cr
            r_col = prefix + "_" + rev_dr_or_cr
            row[v_col] = row[v_col] - row[r_col]
            if row[v_col] < 0:
                row[r_col] = abs(row[v_col])
                row[v_col] = 0.0
            else:
                row[r_col] = 0.0

    def get_columns():
        return [
            {"fieldname": "account", "label": "Account", "fieldtype": "Link", "options": "Account", "width": 300},
            {"fieldname": "acc_name", "label": "Account Name", "fieldtype": "Data", "hidden": 1, "width": 250},
            {"fieldname": "acc_number", "label": "Account Number", "fieldtype": "Data", "hidden": 1, "width": 120},
            {"fieldname": "currency", "label": "Currency", "fieldtype": "Link", "options": "Currency", "hidden": 1},
            {"fieldname": "opening_debit", "label": "Opening (Dr)", "fieldtype": "Currency", "options": "currency", "width": 120},
            {"fieldname": "opening_credit", "label": "Opening (Cr)", "fieldtype": "Currency", "options": "currency", "width": 120},
            {"fieldname": "debit", "label": "Debit", "fieldtype": "Currency", "options": "currency", "width": 120},
            {"fieldname": "credit", "label": "Credit", "fieldtype": "Currency", "options": "currency", "width": 120},
            {"fieldname": "closing_debit", "label": "Closing (Dr)", "fieldtype": "Currency", "options": "currency", "width": 120},
            {"fieldname": "closing_credit", "label": "Closing (Cr)", "fieldtype": "Currency", "options": "currency", "width": 120}
        ]

    if not filters:
        filters = {}
    if not filters.get("fiscal_year"):
        frappe.throw("Fiscal Year is required")
        
    fy = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
    if not fy:
        frappe.throw("Fiscal Year " + str(filters.fiscal_year) + " does not exist")
        
    year_start_date = frappe.utils.getdate(fy.year_start_date)
    year_end_date = frappe.utils.getdate(fy.year_end_date)
    
    from_date = frappe.utils.getdate(filters.get("from_date") or year_start_date)
    to_date = frappe.utils.getdate(filters.get("to_date") or year_end_date)
    
    company = filters.get("company")
    if not company:
        frappe.throw("Company is required")
        
    company_currency = filters.get("presentation_currency") or frappe.db.get_value("Company", company, "default_currency") or "PHP"
    
    accounts = frappe.db.sql('''
        select name, account_number, parent_account, account_name, root_type, report_type, is_group, lft, rgt
        from `tabAccount`
        where company = %s
        order by lft
    ''', (company,), as_dict=True)
    
    if not accounts:
        return get_columns(), []
        
    parent_children_map = {}
    accounts_by_name = {}
    for d in accounts:
        accounts_by_name[d.name] = d
        p = d.parent_account or None
        if p not in parent_children_map:
            parent_children_map[p] = []
        parent_children_map[p].append(d)
        
    filtered_accounts = []
    def add_to_list(parent, level):
        if level < 20:
            children = parent_children_map.get(parent) or []
            for child in children:
                child.indent = level
                filtered_accounts.append(child)
                add_to_list(child.name, level + 1)
                
    add_to_list(None, 0)
    
    # 3. Calculate Opening Balances
    cost_center_cond = ""
    cost_center_param = []
    if filters.get("cost_center"):
        cc_list = filters.get("cost_center")
        if isinstance(cc_list, list) and cc_list:
            cost_center_cond = " and cost_center in (%s)" % ", ".join(["%s"] * len(cc_list))
            cost_center_param = cc_list
            
    proj_cond = ""
    proj_param = []
    if filters.get("project"):
        p_list = filters.get("project")
        if isinstance(p_list, list) and p_list:
            proj_cond = " and project in (%s)" % ", ".join(["%s"] * len(p_list))
            proj_param = p_list
    
    opening_sql = '''
        select 
            account, 
            coalesce(sum(debit), 0.0) as debit, 
            coalesce(sum(credit), 0.0) as credit
        from `tabGL Entry`
        where company = %s
          and is_cancelled = 0
          and (posting_date < %s or is_opening = 'Yes')
    ''' + cost_center_cond + proj_cond + '''
        group by account
    '''
    params_op = [company, from_date] + cost_center_param + proj_param
    opening_rows = frappe.db.sql(opening_sql, tuple(params_op), as_dict=True)
    opening_map = {}
    for r in opening_rows:
        opening_map[r.account] = {
            "opening_debit": float(r.debit or 0.0),
            "opening_credit": float(r.credit or 0.0)
        }
        
    # 4. Period Movement
    period_sql = '''
        select 
            account, 
            coalesce(sum(debit), 0.0) as debit, 
            coalesce(sum(credit), 0.0) as credit
        from `tabGL Entry`
        where company = %s
          and is_cancelled = 0
          and posting_date >= %s
          and posting_date <= %s
          and is_opening = 'No'
    ''' + cost_center_cond + proj_cond + '''
        group by account
    '''
    params_pm = [company, from_date, to_date] + cost_center_param + proj_param
    period_rows = frappe.db.sql(period_sql, tuple(params_pm), as_dict=True)
    period_map = {}
    for r in period_rows:
        period_map[r.account] = {
            "debit": float(r.debit or 0.0),
            "credit": float(r.credit or 0.0)
        }
        
    value_fields = ["opening_debit", "opening_credit", "debit", "credit", "closing_debit", "closing_credit"]
    
    for d in filtered_accounts:
        for vf in value_fields:
            d[vf] = 0.0
            
        op = opening_map.get(d.name, {})
        d["opening_debit"] = float(op.get("opening_debit", 0.0))
        d["opening_credit"] = float(op.get("opening_credit", 0.0))
        
        pm = period_map.get(d.name, {})
        d["debit"] = float(pm.get("debit", 0.0))
        d["credit"] = float(pm.get("credit", 0.0))
        
        d["closing_debit"] = d["opening_debit"] + d["debit"]
        d["closing_credit"] = d["opening_credit"] + d["credit"]
        
        if filters.get("show_net_values"):
            prepare_net_row(d)
            
    for d in filtered_accounts[::-1]:
        if d.parent_account and d.parent_account in accounts_by_name:
            p = accounts_by_name[d.parent_account]
            for vf in value_fields:
                p[vf] = p[vf] + d[vf]
                
    data = []
    for d in filtered_accounts:
        if parent_children_map.get(d.name) and filters.get("show_net_values"):
            prepare_net_row(d)
            
        has_val = False
        row = {
            "account": d.name,
            "parent_account": d.parent_account,
            "indent": d.indent,
            "from_date": str(from_date),
            "to_date": str(to_date),
            "currency": company_currency,
            "is_group_account": d.is_group,
            "acc_name": d.account_name,
            "acc_number": d.account_number,
            "account_name": (str(d.account_number) + " - " + str(d.account_name)) if d.account_number else d.account_name
        }
        for vf in value_fields:
            row[vf] = round(float(d.get(vf, 0.0)), 2)
            if abs(row[vf]) > 0.001:
                has_val = True
                
        row["has_value"] = has_val
        data.append(row)
        
    if not filters.get("show_group_accounts"):
        data = [r for r in data if not r.get("is_group_account")]
        for r in data:
            r["indent"] = 0
            
    total_row = {
        "account": "'Total'",
        "account_name": "'Total'",
        "warn_if_negative": True,
        "opening_debit": 0.0,
        "opening_credit": 0.0,
        "debit": 0.0,
        "credit": 0.0,
        "closing_debit": 0.0,
        "closing_credit": 0.0,
        "parent_account": None,
        "indent": 0,
        "has_value": True,
        "currency": company_currency
    }
    for d in data:
        if not filters.get("show_group_accounts") or not d.get("parent_account"):
            for vf in value_fields:
                total_row[vf] = total_row[vf] + d.get(vf, 0.0)
                
    for vf in value_fields:
        total_row[vf] = round(total_row[vf], 2)
        
    data.extend([{}, total_row])
    
    if not filters.get("show_zero_values"):
        data = [r for r in data if r.get("has_value") or r.get("account") == "'Total'" or not r]
        
    return get_columns(), data

data = run_trial_balance(filters)
"""

login()

# Deploy server script that updates Report in DB
update_script = """
report_script = frappe.form_dict.get("report_script")
frappe.db.set_value("Report", "Trial Balance", {
    "is_standard": "No",
    "report_type": "Script Report",
    "report_script": report_script
})
frappe.response["message"] = {"status": "success", "updated": True}
"""

ss_doc = {
    'name': 'VM Update Standard Report',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_update_standard_report',
    'allow_guest': 0,
    'disabled': 0,
    'script': update_script
}

# Update or create Server Script
call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Update Standard Report')}", "PUT", {"script": update_script})
# Trigger update
res_up = call("/api/method/vm_update_standard_report", "POST", {"report_script": report_script_code})
print("[OK] Update report response:", res_up)

# Test Trial Balance via desk query report run
test_payload = {
    'report_name': 'Trial Balance',
    'filters': json.dumps({
        'company': 'Automan Car Care Center',
        'fiscal_year': '2026',
        'from_date': '2026-01-01',
        'to_date': '2026-12-31',
        'cost_center': [],
        'project': [],
        'branch': [],
        'with_period_closing_entry_for_opening': 1,
        'with_period_closing_entry_for_current_period': 1,
        'include_default_book_entries': 1,
        'show_net_values': 1,
        'show_group_accounts': 1
    }),
    'ignore_prepared_report': 1
}

res_test = call("/api/method/frappe.desk.query_report.run", "GET", None)
# Try GET with query params
qs = urllib.parse.urlencode(test_payload)
res_test = call(f"/api/method/frappe.desk.query_report.run?{qs}", "GET")
rep = res_test.get('message', {})
print(f"[OK] Report executed successfully! Columns: {len(rep.get('columns', []))}, Rows: {len(rep.get('result', []))}")
if rep.get('result'):
    print("Sample rows:")
    for r in rep['result'][:8]:
        print(" ", r)
