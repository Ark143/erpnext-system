import urllib.request
import urllib.parse
import json
import http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

patch_code = '''
def apply_goal_fix():
    goal_mod = frappe.get_module("frappe.utils.goal")
    
    # 1. Update on disk in frappe/utils/goal.py
    try:
        filepath = goal_mod.__file__
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        old_code = """\treturn dict(
\t\tfrappe.qb.get_query(
\t\t\ttable=goal_doctype,
\t\t\tfields=[
\t\t\t\tDateFormat(Table[date_col], date_format).as_("month_year"),
\t\t\t\tFunction(aggregation, Table[goal_field]),
\t\t\t],
\t\t\tfilters=filters,
\t\t\tignore_permissions=False,
\t\t)
\t\t.groupby("month_year")
\t\t.run()
\t)"""

        new_code = """\tagg_map = {
\t\t"sum": Sum,
\t\t"avg": Avg,
\t\t"count": Count,
\t\t"min": Min,
\t\t"max": Max,
\t}
\tagg_func = agg_map.get(aggregation.lower(), Sum)

\treturn dict(
\t\tfrappe.qb.get_query(
\t\t\ttable=goal_doctype,
\t\t\tfields=[
\t\t\t\tDateFormat(Table[date_col], date_format).as_("month_year"),
\t\t\t\tagg_func(Table[goal_field]),
\t\t\t],
\t\t\tfilters=filters,
\t\t\tgroup_by="month_year",
\t\t\tignore_permissions=False,
\t\t)
\t\t.run()
\t)"""

        if 'from frappe.query_builder.functions import DateFormat, Function' in content:
            content = content.replace(
                'from frappe.query_builder.functions import DateFormat, Function',
                'from frappe.query_builder.functions import Avg, Count, DateFormat, Max, Min, Sum'
            )
            
        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
        # Also in-memory patch
        from_qb = frappe.get_module("frappe.query_builder.functions")
        from_qb_utils = frappe.get_module("frappe.query_builder.utils")
        
        def patched_get_monthly_results(
            goal_doctype,
            goal_field,
            date_col,
            filters,
            aggregation = "sum",
        ):
            if aggregation.lower() not in {"sum", "avg", "count", "min", "max"}:
                frappe.throw(f"Invalid aggregation type: {aggregation}")

            valid_fields = frappe.get_meta(goal_doctype).get_valid_fields()
            if goal_field not in valid_fields:
                frappe.throw(f"Invalid goal field: {goal_field}")
            if date_col not in valid_fields:
                frappe.throw(f"Invalid date field: {date_col}")

            Table = from_qb_utils.DocType(goal_doctype)
            date_format = "%m-%Y" if frappe.db.db_type != "postgres" else "MM-YYYY"

            agg_map = {
                "sum": from_qb.Sum,
                "avg": from_qb.Avg,
                "count": from_qb.Count,
                "min": from_qb.Min,
                "max": from_qb.Max,
            }
            agg_func = agg_map.get(aggregation.lower(), from_qb.Sum)

            return dict(
                frappe.qb.get_query(
                    table=goal_doctype,
                    fields=[
                        from_qb.DateFormat(Table[date_col], date_format).as_("month_year"),
                        agg_func(Table[goal_field]),
                    ],
                    filters=filters,
                    group_by="month_year",
                    ignore_permissions=False,
                )
                .run()
            )
            
        goal_mod.get_monthly_results = patched_get_monthly_results
        frappe.response["message"] = {"status": "success", "message": "Patched frappe.utils.goal on disk and in memory!"}
    except Exception as e:
        frappe.response["message"] = {"status": "error", "error": str(e)}

apply_goal_fix()
'''

server_script_payload = {
    'doctype': 'Server Script',
    'name': 'VM Patch Goal Aggregation',
    'script_type': 'API',
    'api_method': 'vm_patch_goal_aggregation',
    'allow_guest': 1,
    'disabled': 0,
    'script': patch_code
}

try:
    check = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Patch%20Goal%20Aggregation', headers=H))
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Patch%20Goal%20Aggregation',
        data=urllib.parse.urlencode({'data': json.dumps(server_script_payload)}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    op.open(req)
except Exception:
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script',
        data=urllib.parse.urlencode({'data': json.dumps(server_script_payload)}).encode(),
        headers=H
    )
    op.open(req)

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_patch_goal_aggregation', headers=H))
print("Patch Response:", r_call.read().decode())
