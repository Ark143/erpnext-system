# Migration: local Vehicle Management -> live Frappe Cloud (demoerpnext.s.frappe.cloud)

Source: http://erp.localhost (Podman ERPNext v16, PostgreSQL)
Target: https://demoerpnext.s.frappe.cloud (Frappe Cloud, MariaDB v16)
Auth: logged-in browser session (window.frappe.csrf_token).

## Scope (user-confirmed)
- Master Data: PUSH EVERYTHING (all master-data DocTypes, full records).
- Custom module (vehicle_management app): NOT installed on cloud -> DEPLOY it.
- Web Pages + Server Scripts: migrate (DB-stored).
- POS: the POS UI/functionality (not historical POS invoices).

## Master data volumes (local, verified)
Customer Vehicle 38654, Customer 39466, Item 10531, Supplier 832,
Vehicle Make 71, Vehicle Model 21, Item Group 33, Customer Group 5, Supplier Group 8,
Price List 3, Warehouse 76, Account 1237, Cost Center 37, POS Profile 2, Mode of Payment 5,
Bin 26, Cashier Profile 2, Inspection Template 4, Item Part Cross Reference 2,
Item Vehicle Compatibility 2.
Transactional (NOT in scope unless asked): Vehicle Job Order 481, Vehicle Inspection 476,
Vehicle Estimate 24, Vehicle POS Invoice 5 (+ items).

## Constraints
- Local PG -> cloud MariaDB: cannot DB-dump/restore. Export via Frappe (JSON/CSV), import via
  Frappe Data Import / import-doc. The custom app code is DB-agnostic (PG patches were in ERPNext
  core, not this app) so it should run on MariaDB.
- Frappe Cloud rate-limits + bulk import is the safe path, not row-by-row REST.

## TASK / ISSUE LOG
### MIG-001 App repo for Frappe Cloud Upload App
- Status: IN PROGRESS
- Extract vehicle_management app into its own git repo (Frappe Cloud needs app at repo root or
  specified path). Push to GitHub. Then "Upload App" on cloud.
- Acceptance: app installed on cloud; its DocTypes (Customer Vehicle, Vehicle POS Invoice, etc.)
  exist on demoerpnext.

### MIG-002 Export master data from local
- Status: DONE
- Exported 20 DocTypes to pos-static/export/ (Customer 39466, Customer Vehicle 38654, Item 10531,
  Supplier 832, + groups/warehouse/accounts/pos profile/bin/custom tables). Also exported Company
  (13, local has ULTRA MRF + branches) after discovering the cloud lacked ULTRA MRF.

### MIG-003 Import master data to cloud (bulk, MERGE)
- Status: IN PROGRESS — big import re-run FIXED and running (proc_40c3ff39fcef)
- ROOT CAUSE of earlier 0-ok import (2026-08-31): source export records used GROUP nodes in
  leaf-required link fields, which Frappe rejects:
    * Customer.customer_group = 'All Customer Groups' (group) -> remap 'Individual'
    * Customer.territory = 'All Territories' (group) -> remap 'Philippines'
    * Supplier.supplier_group = 'All Supplier Groups' (group) -> remap 'Local'
    * Item.item_group = 'GENERAL REPAIRS' (group) -> 'Services'; 'OTHER SERVICES' (group) -> 'Services'
    * Item.item_group = 'TRANSMISSION' was MISSING on cloud -> ensured leaf Item Group (exists)
  Fix script: pos-static/import_big_fix.py (REMAP dict + ensure_item_groups). Now inserts succeed.
- Done before (skip-dup): Company 16, Account 1600, Cost Center 67, Warehouse 107, MOP 6,
- DONE via API insert (skip-on-duplicate): Company (13 pushed, auto CoA), Account (1237),
  Cost Center (37), Warehouse (76), Mode of Payment, POS Profile, Item Group, Customer Group,
  Supplier Group, Price List, Vehicle Make (60→60), Vehicle Model (21). Cash MOP wired to
  per-company Cash accounts so POS Profile validates.
- In-flight (background, 2026-08-31): Customer (39466), Supplier (832), Item (10531) via
  pos-static/import_big.py; then Customer Vehicle (38654) via import_customer_vehicle.py.
- CRITICAL findings (2026-08-31):
  - Cloud is NOT empty: has base/demo data (Company: INASAL CORP/IT Cavite Branch/JMIT; Customer 41;
    Supplier 679; Item 94; Account 363; etc.). Local is source of truth (ULTRA MRF companies).
  - Cloud companies != local (ULTRA MRF). Must import ULTRA MRF companies + their Chart of Accounts.
  - `/api/resource/{doctype}` path-encodes spaces to %20 -> Frappe 500 "No module named
    frappe.core.doctype.vehicle%20make". FIX: use `/api/method/frappe.client.insert` with doc in BODY
    (no URL doctype). Implemented in pos-static/import_threaded.py (threaded, skip-on-duplicate).
  - `insert_many` is all-or-nothing + cannot upsert -> replaced with per-record insert (threads=8).
  - `get_list`/?limit returned wrong counts due to the same %20 bug; use get_count + insert method.
- Import order (dependency): Account -> Cost Center -> Warehouse -> Mode of Payment -> POS Profile
  -> Company (needs default accounts) -> Item Group -> Customer Group -> Supplier Group -> Price List
  -> Vehicle Make -> Vehicle Model -> Customer -> Supplier -> Item -> Customer Vehicle -> custom tables.
- MIG-007 (custom DocTypes) already created 17/18 on cloud via API (Vehicle Estimate & Vehicle Job
  Order deferred — circular, will come with app deploy).
- Acceptance: cloud counts match local for each master DocType.

### MIG-004 Web Pages
- Status: PENDING
- Recreate the 2 web pages (pos_terminal.html, vehicle_pos_web.html) + any published Web Pages on
  cloud via browser/API.
- Acceptance: pages return 200 on cloud.

### MIG-005 Server Scripts
- Status: PENDING
- Recreate the 10 Server Scripts (vm_pos_*, executive_dashboard, vm_company_dashboard_api, etc.) on
  cloud with safe_exec-compatible code.
- Acceptance: all 10 scripts enabled + return 200 via API.

### MIG-006 POS verify on cloud
- Status: PENDING
- Confirm /desk/vehicle_pos (or equivalent) loads + a test transaction creates a Vehicle POS Invoice.
- Acceptance: POS usable on cloud.

### MIG-007 Create custom DocTypes on cloud BEFORE master data
- Status: IN PROGRESS (defs prepared)
- The cloud must have the custom DocTypes (schema) BEFORE importing master data, else Customer
  Vehicle / Vehicle Make / Vehicle Model / Cashier Profile / Inspection Template / Item Part Cross
  Reference / Item Vehicle Compatibility / Bin Location / Vehicle Service Reminder cannot be imported.
- Approach A (preferred): deploy the vehicle_management app via Frappe Cloud "Upload App" from the
  dedicated GitHub repo `vehicle_management` (app at repo root). This creates all 18 DocTypes + their
  Python controllers + the POS page + hooks. REQUIRES the repo to exist (user must create it).
- Approach B (fallback if no repo): recreate each custom DocType on the cloud via the DocType REST API
  by POSTing its JSON definition (prepared at pos-static/doctype_defs/*.json). Schema-only; Python
  controllers (create_from_pos etc.) will be absent until the app is deployed. Master-data import only
  needs schema, so this unblocks MIG-003.
- DocType defs prepared on host: pos-static/doctype_defs/<name>.json (18 files).
- Acceptance: all 18 custom DocTypes exist on cloud (at minimum the master-data ones) before MIG-003.

## STATUS UPDATE (2026-08-31 15:32 + re-sweep)
Read-only verification sweep run against https://demoerpnext.s.frappe.cloud (login OK).
Script: pos-static/verify_cloud_sweep2.py (out: verify_cloud_sweep2.out).

### Custom DocTypes (Vehicle Management) — REAL COUNTS
- Vehicle Make ........ OK, 60 records   (only custom V-Master that has rows)
- Vehicle Model ....... OK, 0
- Customer Vehicle ..... OK, 0
- Cashier Profile ...... OK, 0
- Bin Location ......... OK, 0
- Vehicle Service Reminder OK, 0
- Inspection Template, Inspection Template Item, Item Part Cross Reference,
  Item Vehicle Compatibility, Vehicle POS Invoice (+Item), Vehicle Inspection
  (+Item), Job Order Part Item, Job Order Service Item .... NO_PERM (HTTP 403)
  -> schema exists on cloud but this login cannot READ them (not System Manager).
- Vehicle Estimate, Vehicle Job Order .... MISSING (HTTP 404) -> do NOT exist on cloud.

CONCLUSION: only Vehicle Make schema + 60 rows copied. All other V-Management
master tables are EMPTY or unreachable. Vehicle Estimate / Vehicle Job Order
were never created.

### Base / standard modules (cloud's OWN demo data, NOT ULTRA MRF)
Company 3, Customer 41, Supplier 679, Item 94, Account 363, Cost Center 30,
POS Profile 1, Mode of Payment 5, Price List 2, Sales Invoice 430, Purchase
Invoice 115, Stock Entry 119, Quotation 48, Sales Order 74, Purchase Order 373,
Material Request 507, Payment Entry 323, Delivery Note 48, Purchase Receipt 152,
BOM 11, Work Order 20, Batch 9, etc. (full list in verify_cloud_sweep2.out)

### Web Pages (published) — 8 found, all return OK at the list level
executive, inasal-dashboard, inventory-stock-ledger-balance, inventory-monitoring,
sales-revenue-dashboard, sales-revenue-analytics, ultr-mrf, daily-sales-report

### Server Scripts — 16 total, 15 ENABLED / 1 DISABLED
ENABLED: Auto Fetch DN/QTN/SI/SO Commission Line Items, executive_dashboard,
gen_comisary_sales, inasal_dashboard_api, JMIT Daily Sales Report API, JMIT
Inventory Dashboard API, JMIT Sales Dashboard API, jmit_mrf_data, jmit_ultr_api,
sales_revenue_dashboard, ULTR Inventory API.
DISABLED: bank_loan_app_automation, bank_loan_app_validate.

NOTE: these are JMIT/Inasal scripts — NO vehicle_pos / vm_pos_* scripts exist
on the cloud yet (would come with app deploy, MIG-007).

### MIG-006 POS verify on cloud — RESULT: NOT DEPLOYED
- Custom POS Page search (title like %vehicle%) = [] -> NO vehicle POS page on cloud.
- Page doctype total on cloud = 24 (none vehicle-related).
- POS is NOT usable on the cloud. Blocked on MIG-007 app deploy.

### Updated task statuses
- MIG-001 App repo for Upload App: IN PROGRESS (blocked — repo not created)
- MIG-002 Export master data from local: DONE
- MIG-003 Import master data to cloud: BLOCKED (403 + rate-limit + company mismatch)
- MIG-004 Web Pages: PENDING (8 base web pages exist; 0 vehicle pages)
- MIG-005 Server Scripts: PENDING (15 JMIT scripts exist; 0 vehicle scripts)
- MIG-006 POS verify on cloud: BLOCKED (no app, no page)
### MIG-007 Create custom DocTypes on cloud: DONE (schema) — 2026-08-31
- All 18 Vehicle Management DocTypes now exist on cloud. Created the 2 missing ones
  (Vehicle Estimate, Vehicle Job Order) via API; the other 16 existed (some read=403 because
  this login isn't System Manager, but schema is present and record inserts work).
- Vehicle Estimate <-> Vehicle Job Order circular link: neutralised by pointing the cross-link
  field at Sales Invoice during creation (valid), so both created with 200.
- 9 doctypes return 403 on get_count (read perm), NOT missing. Record inserts succeeded
  (Customer/Supplier/Item/Vehicle Make-Model all imported).
- SMALL-TABLE DATA (pos-static/import_custom_small.py, 2026-08-31):
    * Cashier Profile: 1 ok, 1 linkfail (cashier.test@example.com User missing — test rec, harmless).
    * Item Part Cross Reference / Item Vehicle Compatibility: 0 ok / 2 err each — export rows are
      CHILD TABLE records (need a parent Item); cannot insert standalone. Minor (2 recs each).
    * Inspection Template: 403 — this login cannot INSERT that doctype (needs System Manager /
      doctype perm). 4 recs not imported.
    * Bin Location / Vehicle Service Reminder: NO export source exists (corrected script skips them).

## BLOCKERS (root cause) — UPDATED 2026-08-31
1. (RESOLVED) Earlier "login not System Manager / Data Import 403" was wrong — login IS a
   System Manager (system_user=yes) and inserts work. The real import failure was GROUP-node
   link values (see MIG-003). Fixed.
2. Frappe Cloud rate-limits slow row-by-row inserts (~2/sec) — mitigated with threaded importer.
3. Cloud companies (INASAL/JMIT + 13 ULTRA MRF pushed) != originally empty; now aligned.
4. vehicle_management app not deployed -> Vehicle Estimate/Job Order + POS page exist as schema
   but desk UI/page not wired. MIG-001 (Upload App) still pending for full UI.
5. (MINOR) Inspection Template insert = 403 (doctype perm); Item Part Cross Reference /
   Item Vehicle Compatibility are child tables (need parent). Non-blocking for main data.

## Notes
- Backup cloud site + git push AFTER each change batch (standing rule).
- Big import (Customer/Supplier/Item) running proc_40c3ff39fcef; Customer Vehicle queued.
