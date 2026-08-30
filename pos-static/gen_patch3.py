import subprocess
# 1) fresh diff of erpnext working tree -> container /tmp, then cp to host
gen = 'cd /workspace/frappe-bench/apps/erpnext && git --no-pager diff HEAD > /tmp/erpnext_pg_fixes.patch && wc -l /tmp/erpnext_pg_fixes.patch'
r = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",gen], capture_output=True, text=True, timeout=120)
print("gen:", (r.stdout or r.stderr).strip()[:120])
cp = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","cp","erp-frappe:/tmp/erpnext_pg_fixes.patch",
                     "/mnt/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch"], capture_output=True, text=True, timeout=60)
print("cp:", (cp.stdout or cp.stderr).strip()[:120])
import os
p = "/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch"
print("exists:", os.path.exists(p), "size:", os.path.getsize(p) if os.path.exists(p) else 0)
