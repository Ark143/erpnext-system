import frappe, traceback
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
inv = frappe.db.sql("select name from `tabPurchase Invoice` limit 1", as_dict=1)
if not inv:
    print("no purchase invoice"); raise SystemExit
nm = inv[0]["name"]
q = """select parent, account_head, case add_deduct_tax when 'Add' then sum(base_tax_amount_after_discount_amount)
else sum(base_tax_amount_after_discount_amount) * -1 end as tax_amount
from `tabPurchase Taxes and Charges`
where parent in (%s) and category in ('Total', 'Valuation and Total')
and base_tax_amount_after_discount_amount != 0 and parenttype='Purchase Invoice'
group by parent, account_head, add_deduct_tax"""
try:
    r = frappe.db.sql(q, (nm,), as_dict=1)
    print("QUERY OK rows=", len(r))
except Exception as e:
    print("REAL SQL ERROR:", type(e).__name__)
    print(str(e)[:300])
