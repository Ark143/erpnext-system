f = "/workspace/frappe-bench/apps/frappe/frappe/public/js/bootstrap-4-web.bundle.js"
s = open(f).read()
if "jquery-bootstrap" not in s:
    s = 'import "./jquery-bootstrap.js";\n' + s
    open(f, "w").write(s)
    print("ADDED import ./jquery-bootstrap.js")
else:
    print("already present")
print("FIRST LINE:", s.splitlines()[0])
