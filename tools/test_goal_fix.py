import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# Let's inspect what happens if we patch or test frappe.utils.goal on VPS
# Let's write a small script to test via python API
test_code = """
import frappe
from frappe.query_builder.functions import DateFormat, Sum, Avg, Count, Min, Max, Function
from frappe.query_builder.utils import DocType

goal_doctype = "Sales Invoice"
goal_field = "base_grand_total"
date_col = "posting_date"
filters = {"company": "Automan Car Care Center", "docstatus": 1}
aggregation = "sum"

Table = DocType(goal_doctype)
date_format = "%m-%Y" if frappe.db.db_type != "postgres" else "MM-YYYY"

# Option 1: Using Sum from pypika / frappe.query_builder.functions
func_map = {
    "sum": Sum,
    "avg": Avg,
    "count": Count,
    "min": Min,
    "max": Max
}
agg_func = func_map.get(aggregation.lower(), Sum)

# Test 1: with get_query and agg_func
try:
    q1 = frappe.qb.get_query(
        table=goal_doctype,
        fields=[
            DateFormat(Table[date_col], date_format).as_("month_year"),
            agg_func(Table[goal_field]),
        ],
        filters=filters,
        ignore_permissions=False,
    ).groupby("month_year")
    print("Option 1 SQL:", str(q1))
    res1 = dict(q1.run())
    print("Option 1 result:", res1)
except Exception as e:
    print("Option 1 failed:", e)

# Test 2: with frappe.qb.from_(Table)
try:
    q2 = (
        frappe.qb.from_(Table)
        .select(
            DateFormat(Table[date_col], date_format).as_("month_year"),
            agg_func(Table[goal_field]).as_("val")
        )
        .where(Table.company == "Automan Car Care Center")
        .where(Table.docstatus == 1)
        .groupby("month_year")
    )
    print("Option 2 SQL:", str(q2))
    res2 = dict(q2.run())
    print("Option 2 result:", res2)
except Exception as e:
    print("Option 2 failed:", e)
"""

print(test_code)
