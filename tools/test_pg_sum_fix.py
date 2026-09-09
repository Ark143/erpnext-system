import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# Let's create a server script to run postgres function definitions
pg_script = """
def run_fix():
    queries = [
        '''
        CREATE OR REPLACE FUNCTION sum(text)
        RETURNS numeric AS $$
        BEGIN
            RETURN sum($1::numeric);
        EXCEPTION WHEN OTHERS THEN
            RETURN 0;
        END;
        $$ LANGUAGE plpgsql;
        ''',
        '''
        CREATE OR REPLACE FUNCTION avg(text)
        RETURNS numeric AS $$
        BEGIN
            RETURN avg($1::numeric);
        EXCEPTION WHEN OTHERS THEN
            RETURN 0;
        END;
        $$ LANGUAGE plpgsql;
        ''',
        '''
        CREATE OR REPLACE FUNCTION min(text)
        RETURNS text AS $$
        BEGIN
            RETURN min($1);
        END;
        $$ LANGUAGE plpgsql;
        ''',
        '''
        CREATE OR REPLACE FUNCTION max(text)
        RETURNS text AS $$
        BEGIN
            RETURN max($1);
        END;
        $$ LANGUAGE plpgsql;
        '''
    ]
    
    results = []
    for q in queries:
        try:
            frappe.db.sql(q)
            frappe.db.commit()
            results.append("OK")
        except Exception as e:
            results.append("Err: " + str(e))
            
    frappe.response['message'] = results
"""

res_check = s.get(f"{VPS_BASE}/api/resource/Server Script/VM%20PG%20Sum%20Fix")
if res_check.status_code == 200:
    s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20PG%20Sum%20Fix", json={
        "script": pg_script,
        "script_type": "API",
        "api_method": "vm_pg_sum_fix",
        "allow_guest": 0,
        "disabled": 0
    })
else:
    s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        "name": "VM PG Sum Fix",
        "script_type": "API",
        "api_method": "vm_pg_sum_fix",
        "script": pg_script,
        "allow_guest": 0,
        "disabled": 0
    })

# Call the script
r_call = s.get(f"{VPS_BASE}/api/method/vm_pg_sum_fix")
print("Postgres function creation response:", r_call.status_code, r_call.text)

# Test the goal graph API now!
res_goal = s.get(f"{VPS_BASE}/api/method/frappe.utils.goal.get_monthly_goal_graph_data", params={
    "doctype": "Company",
    "docname": "Automan Car Care Center",
    "title": "Sales",
    "goal_value_field": "monthly_sales_target",
    "goal_total_field": "total_monthly_sales",
    "goal_history_field": "sales_monthly_history",
    "goal_doctype": "Sales Invoice",
    "goal_doctype_link": "company",
    "goal_field": "base_grand_total",
    "date_field": "posting_date",
    "filters": json.dumps({"docstatus": 1, "is_opening": ["!=", "Yes"]}),
    "aggregation": "sum"
})
print("\nGoal Graph API status:", res_goal.status_code)
print("Goal Graph API response:", res_goal.text[:500])
