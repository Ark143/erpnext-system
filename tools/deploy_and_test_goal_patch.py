import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

patch_code = """
import frappe
from frappe.query_builder.functions import DateFormat, Sum, Avg, Count, Min, Max
from frappe.query_builder.utils import DocType
import frappe.utils.goal as goal_mod

def patched_get_monthly_results(
    goal_doctype: str,
    goal_field: str,
    date_col: str,
    filters: dict,
    aggregation: str = "sum",
) -> dict:
    if aggregation.lower() not in {"sum", "avg", "count", "min", "max"}:
        frappe.throw(f"Invalid aggregation type: {aggregation}")

    valid_fields = frappe.get_meta(goal_doctype).get_valid_fields()
    if goal_field not in valid_fields:
        frappe.throw(f"Invalid goal field: {goal_field}")
    if date_col not in valid_fields:
        frappe.throw(f"Invalid date field: {date_col}")

    Table = DocType(goal_doctype)
    date_format = "%m-%Y" if frappe.db.db_type != "postgres" else "MM-YYYY"

    agg_map = {
        "sum": Sum,
        "avg": Avg,
        "count": Count,
        "min": Min,
        "max": Max,
    }
    agg_func = agg_map.get(aggregation.lower(), Sum)

    try:
        res = dict(
            frappe.qb.get_query(
                table=goal_doctype,
                fields=[
                    DateFormat(Table[date_col], date_format).as_("month_year"),
                    agg_func(Table[goal_field]),
                ],
                filters=filters,
                group_by="month_year",
                ignore_permissions=False,
            )
            .run()
        )
        return res
    except Exception as e:
        # Fallback to direct SQL if needed
        table_name = frappe.qb.get_table_name(goal_doctype)
        date_expr = f"TO_CHAR(posting_date, 'MM-YYYY')" if frappe.db.db_type == "postgres" else "DATE_FORMAT(posting_date, '%m-%Y')"
        agg_expr = f"{aggregation.upper()}({goal_field})"
        
        conditions = []
        values = []
        if isinstance(filters, dict):
            for k, v in filters.items():
                if isinstance(v, list) and len(v) == 2:
                    op, val = v
                    conditions.append(f"`{k}` {op} %s")
                    values.append(val)
                elif isinstance(v, (list, tuple)):
                    conditions.append(f"`{k}` IN %s")
                    values.append(tuple(v))
                else:
                    conditions.append(f"`{k}` = %s")
                    values.append(v)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT {date_expr} as month_year, {agg_expr} as total FROM `{table_name}` {where_clause} GROUP BY month_year"
        raw_res = frappe.db.sql(sql, tuple(values), as_dict=False)
        return dict(raw_res or [])

goal_mod.get_monthly_results = patched_get_monthly_results
frappe.response['message'] = 'Goal aggregation patched successfully!'
"""

# Deploy as a server script
res_check = s.get(f"{VPS_BASE}/api/resource/Server Script/VM%20Patch%20Goal%20Aggregation")
if res_check.status_code == 200:
    s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Patch%20Goal%20Aggregation", json={
        "script": patch_code,
        "script_type": "API",
        "api_method": "vm_patch_goal_aggregation",
        "allow_guest": 0,
        "disabled": 0
    })
    print("Updated Server Script VM Patch Goal Aggregation")
else:
    s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        "name": "VM Patch Goal Aggregation",
        "script_type": "API",
        "api_method": "vm_patch_goal_aggregation",
        "script": patch_code,
        "allow_guest": 0,
        "disabled": 0
    })
    print("Created Server Script VM Patch Goal Aggregation")

# Trigger the patch method
r_call = s.get(f"{VPS_BASE}/api/method/vm_patch_goal_aggregation")
print("Patch call response:", r_call.status_code, r_call.text)

# Now test the original failing endpoint!
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
print("Goal Graph API response code:", res_goal.status_code)
print("Goal Graph API response data:", json.dumps(res_goal.json(), indent=2))
