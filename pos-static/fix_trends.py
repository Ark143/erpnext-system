F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()
old = '''\tquery_details += """SUM(IF(t1.{trans_date} BETWEEN '\\'{sd}\\' AND '\\'{ed}\\'', t2.stock_qty, NULL)),
\t\t\t\tSUM(IF(t1.{trans_date} BETWEEN '\\'{sd}\\' AND '\\'{ed}\\'', t2.base_net_amount, NULL)),
\t\t\t""".format(
\t\ttrans_date=trans_date,
\t\tsd=bet_dates[0],
\t\ted=bet_dates[1],
\t)
\treturn query_details'''
# Simpler: target the two SUM(IF lines precisely
old2 = '''\tquery_details += """SUM(IF(t1.{trans_date} BETWEEN '\\'{sd}\\' AND '\\'{ed}\\'', t2.stock_qty, NULL)),
\t\t\t\tSUM(IF(t1.{trans_date} BETWEEN '\\'{sd}\\' AND '\\'{ed}\\'', t2.base_net_amount, NULL)),'''
new = '''\tquery_details += """SUM(CASE WHEN t1.{trans_date} BETWEEN '\\'{sd}\\' AND '\\'{ed}\\'' THEN t2.stock_qty ELSE NULL END),
\t\t\t\tSUM(CASE WHEN t1.{trans_date} BETWEEN '\\'{sd}\\' AND '\\'{ed}\\'' THEN t2.base_net_amount ELSE NULL END),'''
if old2 in t:
    t = t.replace(old2, new)
    open(F,"w").write(t)
    print("patched trends.py SUM(IF -> CASE WHEN)")
else:
    print("PATTERN NOT FOUND; showing surrounding...")
    idx = t.find("SUM(IF(")
    print(repr(t[idx-50:idx+200]))
