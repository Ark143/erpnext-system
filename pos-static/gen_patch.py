import subprocess
# Generate a full git diff of erpnext working-tree changes from the container,
# save to the Windows host repo as a patch file.
out = "/mnt/c/Users/josem/erpnext-system/frappe-bench/erpnext_pg_fixes.patch"
cmd = f'cd /workspace/frappe-bench/apps/erpnext && git --no-pager diff > {out} && echo LINES=$(wc -l < {out})'
r = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",cmd],
                    capture_output=True, text=True, timeout=120)
print(r.stdout.strip() or r.stderr.strip())
# also capture untracked new files (e.g. none expected, but list them)
ls = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",
    'cd /workspace/frappe-bench/apps/erpnext && git status --short | head -40'],
    capture_output=True, text=True, timeout=60)
print("STATUS:\n"+ls.stdout.strip())
