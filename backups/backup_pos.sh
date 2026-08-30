#!/usr/bin/env bash
# POS / ERPNext backup: full DB dump + POS record export, timestamped into backups/
set -e
REPO="/workspace/frappe-bench"
WINREPO="C:/Users/josem/erpnext-system"
TS=$(date +%Y%m%d_%H%M%S)
DEST="$WINREPO/backups"
mkdir -p "$DEST"
# 1) full DB dump of site1_local (captures Web Page, Server Scripts, Cashier Profiles, all doctype data)
wsl -d podman-machine-default sudo podman exec erp-postgres bash -c "pg_dump -U postgres site1_local" | gzip > "$DEST/erpnext-site1_local-$TS.sql.gz"
# 2) export POS-critical records as JSON, captured on the Windows side from container stdout
#    NOTE: bare `python` inside the container is the system interpreter (no frappe on path).
#    Use the bench virtualenv at /workspace/frappe-bench/env/bin/python. The exporter is piped
#    in via stdin (pos_export_job.py alongside this script) to avoid passing a multi-line script
#    through `wsl` argv. frappe.connect() writes a log under /workspace/logs, which must exist.
wsl -d podman-machine-default sudo podman exec -i -w /workspace/frappe-bench erp-frappe bash -c "mkdir -p /workspace/logs && /workspace/frappe-bench/env/bin/python -" < "$WINREPO/backups/pos_export_job.py" > "$DEST/pos_export-$TS.json"
echo "exported pos_export-$TS.json ($(wc -c < "$DEST/pos_export-$TS.json") bytes)"
# keep only last 20 dumps
ls -tp "$DEST"/erpnext-site1_local-*.sql.gz | tail -n +21 | xargs -r rm -f
ls -tp "$DEST"/pos_export-*.json | tail -n +21 | xargs -r rm -f
echo "BACKUP DONE $TS -> $(ls -la "$DEST/erpnext-site1_local-$TS.sql.gz" | awk '{print $5}') bytes"
