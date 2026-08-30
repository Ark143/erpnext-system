import subprocess
# 1) write diff inside container
cmd = 'cd /workspace/frappe-bench/apps/erpnext && git --no-pager diff HEAD > /tmp/erpnext_pg_fixes.patch && echo LINES=$(wc -l < /tmp/erpnext_pg_fixes.patch)'
r = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",cmd],
                    capture_output=True, text=True, timeout=120)
print("gen:", r.stdout.strip() or r.stderr.strip())
# 2) copy to host via podman cp (container path -> /mnt/c windows mount)
out_host = "/mnt/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch"
cp = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","cp","erp-frappe:/tmp/erpnext_pg_fixes.patch", out_host],
                    capture_output=True, text=True, timeout=60)
print("cp:", cp.stdout.strip() or cp.stderr.strip())
