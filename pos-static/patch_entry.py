p="/var/lib/containers/storage/overlay/55f7b335bc784b4684053ff45d51c6b815aa53c07f2d0ecfe7ed92e22873c14b/merged/entrypoint.sh"
content='''#!/bin/bash
exec > /workspace/frappe-bench/entry.log 2>&1
set -x
echo "[entry] starting at $(date)"
cd /workspace/frappe-bench || { echo "cd bench failed"; exit 1; }
echo "[entry] in bench dir"
cd /workspace/frappe-bench/sites || { echo "cd sites failed"; exit 1; }
echo "[entry] starting node realtime"
node /workspace/frappe-bench/apps/frappe/realtime/index.js &
echo "[entry] node started pid $!"
echo "[entry] starting bench serve foreground"
python -m frappe.utils.bench_helper frappe --site site1.local serve --port 8000 --noreload
echo "[entry] bench serve exited code $?"
'''
open(p,"w").write(content)
print("entrypoint fully rewritten with tracing")
