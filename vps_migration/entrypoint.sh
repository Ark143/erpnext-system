#!/bin/bash
set -e

cd /workspace/frappe-bench/sites

# Ensure site dirs + symlinks for alias hosts (logo /files fix)
mkdir -p /workspace/frappe-bench/logs logs site1.local/logs
ln -sfn site1.local localhost
ln -sfn site1.local erp.localhost

echo "[entry] starting socketio (realtime)"
/usr/bin/node /workspace/frappe-bench/apps/frappe/socketio.js 0.0.0.0 9000 > /workspace/frappe-bench/sites/logs/realtime.log 2>&1 &

echo "[entry] starting frappe serve on :8000"
exec /usr/local/bin/python -m frappe.utils.bench_helper frappe --site site1.local serve --port 8000 --noreload
