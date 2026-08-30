import subprocess
# Generate diff inside container AND write straight to the Windows mount (container sees /mnt/c)
cmd = ('cd /workspace/frappe-bench/apps/erpnext && git --no-pager diff HEAD > '
       '/mnt/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch && '
       'echo LINES=$(wc -l < /mnt/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch)')
r = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",cmd], capture_output=True, text=True, timeout=120)
print("gen:", (r.stdout or r.stderr).strip()[:150])
import os
p = "/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch"
print("exists:", os.path.exists(p), "size:", os.path.getsize(p) if os.path.exists(p) else 0)
