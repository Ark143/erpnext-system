import frappe
from frappe.query_builder.functions import DateFormat, Function
from frappe.query_builder.utils import DocType
from pypika import PostgreSQLQuery, Field

# Let's inspect what pypika generates
Table = DocType("Sales Invoice")
date_format = "MM-YYYY"

q = frappe.qb.get_query(
    table="Sales Invoice",
    fields=[
        DateFormat(Table["posting_date"], date_format).as_("month_year"),
        Function("sum", Table["base_grand_total"]),
    ],
    filters={"docstatus": 1},
    ignore_permissions=False,
).groupby("month_year")

print("Generated SQL (str):", str(q))
print("Generated SQL (get_sql):", q.get_sql())
