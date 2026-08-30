import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
from erpnext.controllers.trends import get_columns
filters = frappe._dict({"company":"ULTRA MRF","based_on":"Item","period":"Monthly","period_based_on":"transaction_date","fiscal_year":frappe.defaults.get_global_default("fiscal_year"),"from_date":"2026-01-01","to_date":"2026-12-31"})
conditions = get_columns(filters, "Sales Order")
print("conditions keys:", list(conditions.keys()))
# build the exact data1 query like the report
query_details = conditions["based_on_select"] + conditions["period_wise_select"]
posting_date = "t1.transaction_date"
year_start_date, year_end_date = frappe.get_cached_value("Fiscal Year", filters.fiscal_year, ["year_start_date","year_end_date"])
sql = """ select {} from `tab{}` t1, `tab{} Item` t2 {}
        where t2.parent = t1.name and t1.company = {} and {} between {} and {} and
        t1.docstatus = 1 {}
        group by {}
    """.format(
        query_details,
        conditions["trans"],
        conditions["trans"],
        conditions["addl_tables"],
        "%s",
        posting_date,
        "%s",
        "%s",
        conditions.get("addl_tables_relational_cond"),
        "",
        conditions["group_by"],
    )
print("SQL (modified will show):")
try:
    frappe.db.rollback()
    rows = frappe.db.sql(sql, (filters.company, year_start_date, year_end_date), as_list=1)
    print("OK rows:", len(rows))
except Exception as e:
    print("REAL SQL ERROR:", type(e).__name__)
    print(str(e)[:400])
    traceback.print_exc(limit=3)
