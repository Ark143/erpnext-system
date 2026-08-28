#!/bin/bash
set -e

cd /workspace/frappe-bench

echo "[Entrypoint] Linking apps in editable mode..."
pip install --no-deps -e ./apps/frappe -e ./apps/erpnext -e ./apps/vehicle_management

echo "[Entrypoint] Ensuring asset symlinks are active..."
python fix_asset_symlinks.py

cd /workspace/frappe-bench/sites

echo "[Entrypoint] Starting Node.js Realtime Socket.IO service..."
node /workspace/frappe-bench/apps/frappe/realtime/index.js &
SOCKETIO_PID=$!

echo "[Entrypoint] Starting Frappe Web Server..."
python -m frappe.utils.bench_helper frappe --site site1.local serve --port 8000 --noreload &
FRAPPE_PID=$!

trap "kill -TERM $SOCKETIO_PID $FRAPPE_PID 2>/dev/null; exit 0" SIGINT SIGTERM

echo "[Entrypoint] Services started (SocketIO PID: $SOCKETIO_PID, Frappe PID: $FRAPPE_PID). Monitoring..."
wait -n $SOCKETIO_PID $FRAPPE_PID
