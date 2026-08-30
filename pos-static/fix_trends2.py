F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
old = "SUM(IF(t1.{trans_date} BETWEEN '{sd}' AND '{ed}', t2.stock_qty, NULL)),\n\t\t\t\tSUM(IF(t1.{trans_date} BETWEEN '{sd}' AND '{ed}', t2.base_net_amount, NULL)),"
new = "SUM(CASE WHEN t1.{trans_date} BETWEEN '{sd}' AND '{ed}' THEN t2.stock_qty ELSE NULL END),\n\t\t\t\tSUM(CASE WHEN t1.{trans_date} BETWEEN '{sd}' AND '{ed}' THEN t2.base_net_amount ELSE NULL END),"
if old in t:
    t = t.replace(old, new)
    open(F,"w").write(t)
    print("patched trends.py: SUM(IF -> CASE WHEN)")
else:
    print("NOT FOUND")
