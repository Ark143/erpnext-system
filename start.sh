#!/bin/bash
ln -sf /workspace/frappe-bench /workspace/bench
cd /workspace/frappe-bench/sites
mkdir -p logs
# Start realtime/socketio server (binds 0.0.0.0:9000 by default)
nohup /usr/local/bin/node /workspace/frappe-bench/apps/frappe/socketio.js 10.88.0.50 9000 > /workspace/frappe-bench/sites/logs/realtime.log 2>&1 &
echo "starting frappe serve + socketio..."
exec /workspace/frappe-bench/env/bin/python -m frappe.utils.bench_helper frappe --site site1.local serve --port 8000 --noreload
