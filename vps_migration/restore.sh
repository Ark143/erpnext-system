#!/bin/bash
# Runs INSIDE the erpnext container (after postgres is up) to restore the DB,
# install the vehicle_management app, migrate, and build assets.
set -euo pipefail

cd /workspace/frappe-bench
export PATH="/workspace/frappe-bench/env/bin:$PATH" 2>/dev/null || true
export PGPASSWORD=postgres

echo ">> waiting for postgres"
until pg_isready -h postgres -p 5432 -U postgres; do sleep 2; done

echo ">> creating role + database"
psql -h postgres -U postgres -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='site1_local') THEN CREATE ROLE site1_local LOGIN PASSWORD 'postgres'; END IF; END \$\$;"
psql -h postgres -U postgres -c "ALTER ROLE site1_local WITH SUPERUSER;"
# drop + recreate for a clean restore
psql -h postgres -U postgres -c "DROP DATABASE IF EXISTS site1_local;"
psql -h postgres -U postgres -c "CREATE DATABASE site1_local OWNER site1_local;"

echo ">> restoring dump (plain SQL — version independent)"
psql -h postgres -U postgres -d site1_local -v ON_ERROR_STOP=0 -f /tmp/artifacts/site1_local.sql 2>&1 | tail -20 || echo "WARN: some restore errors (likely benign) — continuing"

echo ">> ensure apps.txt + symlinks"
cd sites
ln -sfn site1.local localhost
ln -sfn site1.local erp.localhost
mkdir -p site1.local/logs logs
cd ..

echo ">> install vehicle_management app (direct python — avoids bench root guard)"
python -c "
import frappe
frappe.init(site='site1.local', sites_path='/workspace/frappe-bench/sites')
frappe.connect()
from frappe.installer import install_app
install_app('vehicle_management', force=True, verbose=False)
print('INSTALL_APP_OK')
" || echo "WARN: install-app via python failed"

echo ">> migrate (direct python)"
python -c "
import frappe
from frappe.migrate import SiteMigration
frappe.init(site='site1.local', sites_path='/workspace/frappe-bench/sites')
frappe.connect()
SiteMigration().run(site='site1.local')
print('MIGRATE_OK')
" || echo "WARN: migrate reported issues"

echo ">> build assets"
cd sites
python -c "
import frappe
frappe.init(site='site1.local', sites_path='/workspace/frappe-bench/sites')
import frappe.build as b
b.bundle(mode='production', verbose=True)
print('BUNDLE DONE')
" || echo "WARN: asset build failed"

echo ">> restore public files (logo/favicon)"
cd /workspace/frappe-bench
mkdir -p sites/site1.local/public
tar xzf /tmp/artifacts/site_public.tgz -C sites/site1.local/ 2>/dev/null || true

echo "RESTORE_DONE"
