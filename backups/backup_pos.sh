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
wsl -d podman-machine-default sudo podman exec -e FRAPPE_STREAM_LOGGING=1 -w /workspace/frappe-bench erp-frappe bash -c 'cat > /tmp/exp_cron.py <<PY
import frappe, json, sys
try:
    frappe.init(site="erp.localhost", sites_path="/workspace/frappe-bench/sites")
except Exception:
    frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect(); frappe.set_user("Administrator")
out={}
for dt,names in [("Web Page",["vehicle-pos-terminal"]),("Server Script",["VM POS Items","VM POS Meta","VM POS Vehicles","VM POS Vehicle Customer","VM POS Cashier","VM POS History"]),("Cashier Profile",None)]:
    if names is None:
        names=[d.name for d in frappe.get_all(dt,filters={},limit_page_length=200)]
    out[dt]=[frappe.get_doc(dt,n).as_dict() for n in names]
sys.stdout.write(json.dumps(out,default=str))
PY
python /tmp/exp_cron.py' > "$DEST/pos_export-$TS.json"
echo "exported pos_export-$TS.json ($(wc -c < "$DEST/pos_export-$TS.json") bytes)"
# keep only last 20 dumps
ls -tp "$DEST"/erpnext-site1_local-*.sql.gz | tail -n +21 | xargs -r rm -f
ls -tp "$DEST"/pos_export-*.json | tail -n +21 | xargs -r rm -f
echo "BACKUP DONE $TS -> $(ls -la "$DEST/erpnext-site1_local-$TS.sql.gz" | awk '{print $5}') bytes"
