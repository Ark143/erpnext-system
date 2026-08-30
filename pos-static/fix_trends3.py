import re
F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/trends.py"
t = open(F).read()

def to_case(m):
    # m.group(0) is SUM(IF(t1.X BETWEEN 'sd' AND 'ed', Y, NULL))
    inner = m.group(1)  # t1.X BETWEEN 'sd' AND 'ed'
    col = m.group(2)    # t2.stock_qty / t2.base_net_amount
    return f"SUM(CASE WHEN {inner} THEN {col} ELSE NULL END)"

pat = re.compile(r"SUM\(IF\(([^,]+?), ([^,]+?), NULL\)\)")
new = pat.sub(to_case, t)
n = len(pat.findall(t))
open(F,"w").write(new)
print("replaced SUM(IF...) occurrences:", n)
# show the result region
i = new.find("SUM(CASE")
print(new[i-60:i+160] if i>=0 else "no CASE found")
