import sys, os, subprocess, gzip

sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
from frappe.utils import nowdate, flt

print("=== 1. Restoring Full Backup ===")
backup_path = "/workspace/frappe-bench/sites/site1.local/private/backups/20260826_002914-site1.local-POST-CANCELFIX-database.sql.gz"

# Run pg_restore via subprocess into site1_local
# Note: PGDMP archive format
cmd = f"gunzip -c {backup_path} | pg_restore -h 127.0.0.1 -p 5432 -U postgres -d site1_local --clean --if-exists --no-owner --no-privileges"
print("Executing restore command:", cmd)
p = subprocess.run(cmd, shell=True, env=dict(os.environ, PGPASSWORD="admin"), capture_output=True, text=True)
print("Restore exit code:", p.returncode)
if p.stderr:
    print("Stderr (first 500 chars):", p.stderr[:500])

frappe.init('site1.local')
frappe.connect()

print("\n=== 2. Checking Restored Counts ===")
print("Companies:", frappe.db.count("Company"))
print("Customers:", frappe.db.count("Customer"))
print("Customer Vehicles:", frappe.db.count("Customer Vehicle"))
print("Vehicle Job Orders:", frappe.db.count("Vehicle Job Order"))
print("Sales Invoices:", frappe.db.count("Sales Invoice"))
print("Purchase Invoices:", frappe.db.count("Purchase Invoice"))

print("\n=== 3. Schema Updates & Patches ===")
# Ensure schema columns exist
frappe.db.sql('ALTER TABLE "tabContact" ADD COLUMN IF NOT EXISTS is_billing_contact integer DEFAULT 0;')
frappe.db.sql('ALTER TABLE "tabContact" ADD COLUMN IF NOT EXISTS is_primary_contact integer DEFAULT 0;')
frappe.db.sql('ALTER TABLE "tabVehicle Job Order" ADD COLUMN IF NOT EXISTS company varchar(140) DEFAULT \'ULTRA MRF\';')
frappe.db.sql('ALTER TABLE "tabVehicle Job Order" ADD COLUMN IF NOT EXISTS cost_center varchar(140);')
frappe.db.sql('ALTER TABLE "tabVehicle Job Order" ADD COLUMN IF NOT EXISTS estimate varchar(140);')
frappe.db.sql('ALTER TABLE "tabVehicle Inspection" ADD COLUMN IF NOT EXISTS company varchar(140) DEFAULT \'ULTRA MRF\';')
frappe.db.sql('ALTER TABLE "tabVehicle Inspection" ADD COLUMN IF NOT EXISTS cost_center varchar(140);')
frappe.db.sql('ALTER TABLE "tabVehicle Inspection" ADD COLUMN IF NOT EXISTS job_order varchar(140);')
frappe.db.sql('ALTER TABLE "tabJob Order Part Item" ADD COLUMN IF NOT EXISTS uom varchar(140) DEFAULT \'PC\';')

frappe.db.sql("UPDATE \"tabVehicle Job Order\" SET company = 'ULTRA MRF' WHERE company IS NULL OR company = '';")
frappe.db.sql("UPDATE \"tabVehicle Inspection\" SET company = 'ULTRA MRF' WHERE company IS NULL OR company = '';")
frappe.db.sql("UPDATE \"tabJob Order Part Item\" SET uom = 'PC' WHERE uom IS NULL OR uom = '';")
frappe.db.commit()

print("\n=== 4. Setting Currency to PHP (Philippine Peso) ===")
# Ensure PHP currency exists and is enabled
if not frappe.db.exists("Currency", "PHP"):
    curr = frappe.get_doc({
        "doctype": "Currency",
        "currency_name": "PHP",
        "enabled": 1,
        "fraction": "Centavo",
        "fraction_units": 100,
        "smallest_currency_fraction_value": 0.01,
        "symbol": "₱",
        "symbol_on_right": 0
    })
    curr.insert(ignore_permissions=True)
    print("Created Currency PHP")
else:
    frappe.db.set_value("Currency", "PHP", {
        "enabled": 1,
        "fraction": "Centavo",
        "fraction_units": 100,
        "smallest_currency_fraction_value": 0.01,
        "symbol": "₱",
        "symbol_on_right": 0
    })
    print("Updated Currency PHP")

# Set Global Defaults
frappe.db.set_default("currency", "PHP")
frappe.db.set_default("default_currency", "PHP")

# Update all companies default_currency to PHP
frappe.db.sql("UPDATE \"tabCompany\" SET default_currency = 'PHP' WHERE default_currency != 'PHP' OR default_currency IS NULL;")
print("Updated all Company records to default_currency = PHP")

# Currency Exchange USD -> PHP
if not frappe.db.exists("Currency Exchange", {"from_currency": "USD", "to_currency": "PHP", "date": nowdate()}):
    ce = frappe.get_doc({
        "doctype": "Currency Exchange",
        "from_currency": "USD",
        "to_currency": "PHP",
        "exchange_rate": 57.5,
        "for_buying": 1,
        "for_selling": 1,
        "date": nowdate()
    })
    ce.insert(ignore_permissions=True)
    print("Created USD -> PHP Currency Exchange rate 57.5")

if not frappe.db.exists("Currency Exchange", {"from_currency": "PHP", "to_currency": "USD", "date": nowdate()}):
    ce2 = frappe.get_doc({
        "doctype": "Currency Exchange",
        "from_currency": "PHP",
        "to_currency": "USD",
        "exchange_rate": 1.0 / 57.5,
        "for_buying": 1,
        "for_selling": 1,
        "date": nowdate()
    })
    ce2.insert(ignore_permissions=True)
    print("Created PHP -> USD Currency Exchange rate")

frappe.db.commit()

print("\n=== 5. Reloading Doctypes ===")
for dt in ["vehicle_job_order", "vehicle_estimate", "vehicle_inspection", "job_order_part_item", "job_order_service_item"]:
    try:
        frappe.reload_doc("vehicle_management", "doctype", dt, force=True)
    except Exception as e:
        print(f"Reload {dt}: {e}")
frappe.db.commit()

print("\n=== Restoration & PHP Currency Migration Complete! ===")
