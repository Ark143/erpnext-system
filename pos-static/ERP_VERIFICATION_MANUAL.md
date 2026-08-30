# ERPNext v16 + Vehicle Management — System Documentation & Loop-Engineering Issue Log
# Local deployment: http://erp.localhost  (Podman: erp-frappe / erp-postgres / erp-redis / erp-caddy)
# Generated: 2026-08-31 — for future AI agents maintaining this system

================================================================================
0. EXECUTIVE SUMMARY
================================================================================
This is a LOCAL-ONLY ERPNext v16.33 / Frappe 16.32 deployment running on
**PostgreSQL** (NOT MariaDB). The `vehicle_management` custom app adds a tire/mag
(POS + service) business layer on top of ERPNext.

CRITICAL CONSTRAINT: ERPNext is written in MySQL dialect. Running it on
PostgreSQL REQUIRES manual SQL-porting fixes. frappe's `modify_query()` does
NOT auto-convert `ifnull(`, `if(`, `locate(`, zero-dates, double-quoted string
literals, or `FORCE INDEX` hints. Every one of those is a real bug that 500s.

All known MySQL-ism bugs have been fixed (see §6). The remaining historical
blinders (server scripts disabled, safe_exec violations, wrong table name) are
documented in §6 TASK/ISSUE LOG.

VERIFIED WORKING (this session):
- Login 200, ULTRA MRF logo 200, socket.io 200
- 18 Web Pages render 200
- 10 POS/Dashboard Server-Script APIs (8 + 2 dashboards after fix)
- 13 accounting/financial reports run on PostgreSQL
- 33 ERPNext modules present; 18 Vehicle Management doctypes present

================================================================================
1. ARCHITECTURE & ACCESS
================================================================================
Containers (Podman, static IPs):
  erp-postgres  10.88.0.3:5432   PostgreSQL  (volume: erp_pg)
  erp-redis     10.88.0.2:6379   Redis
  erp-frappe    10.88.0.50:8000  Frappe serve + :9000 socketio (volume: erp_bench)
  erp-caddy     :80 -> :8000, :9000 socket.io proxy

Commands from Windows host:
  wsl -d podman-machine-default sudo podman exec erp-frappe bash -c '...'
  wsl -d podman-machine-default sudo podman restart erp-frappe
  wsl -d podman-machine-default sudo podman cp <host> erp-frappe:/tmp/<x>

Python in container: /workspace/frappe-bench/env/bin/python
Site: site1.local   sites_path: /workspace/frappe-bench/sites

KNOWN QUIRK: after `podman restart`, the socketio process does NOT auto-start
(the start.sh nohup background process dies when the serve `exec` replaces the
shell). Restart socketio manually:
  wsl -d podman-machine-default sudo podman exec -d erp-frappe bash -c \
    'nohup /usr/local/bin/node /workspace/frappe-bench/apps/frappe/socketio.js 10.88.0.50 9000 > /workspace/frappe-bench/sites/logs/realtime.log 2>&1 &'

Company: "ULTRA MRF"  (default company). Admin login: administrator / admin
(cleartext in site_config.json admin_password — local only).

================================================================================
2. MODULE DOCUMENTATION
================================================================================
ERPNext ships 33 modules. The business-specific one is **Vehicle Management**
(custom app). Below are the modules and the Vehicle Management doctype map.

2.1 ERPNext core modules (33)
  Accounts, Assets, Automation, Bulk Transaction, Buying, CRM, Communication,
  Contacts, Core, Custom, Desk, EDI, ERPNext Integrations, Email, Geo,
  Integrations, Maintenance, Manufacturing, Portal, Printing, Projects,
  Quality Management, Regional, Selling, Setup, Stock, Subcontracting,
  Support, Telephony, Utilities, Vehicle Management, Website, Workflow.

2.2 Vehicle Management doctypes (18) — the custom business layer
  Master / Setup:
    Vehicle Make            - car brands (Toyota, Honda, ...)
    Vehicle Model           - model per make
    Inspection Template     - checklist template for inspections
    Inspection Template Item- line item of an inspection template
    Cashier Profile         - POS cashier config (employee, store, payment modes)
    Bin Location            - physical bin/shelf location within a warehouse
  Transactions:
    Customer Vehicle        - a customer's vehicle (plate, VIN, make/model, odometer)
    Vehicle Job Order       - service job order (parent of service + part items)
    Job Order Service Item  - service line (mechanic, hours, rate, total)
    Job Order Part Item     - parts used line
    Vehicle Estimate        - quote/estimate
    Vehicle Inspection      - inspection result (uses Inspection Template)
    Vehicle Inspection Item - inspection line
    Vehicle POS Invoice     - the POS sale (cashier, customer, vehicle, payments)
    Vehicle POS Invoice Item- POS line item
    Vehicle Service Reminder- scheduled service reminder
  Cross-reference:
    Item Vehicle Compatibility - which Items fit which Vehicle Make/Model
    Item Part Cross Reference  - OEM/aftermarket part cross-reference

NOTE for future agents: a stale name "Vehicle Job Order Item" is referenced by
legacy code/scripts but the real child tables are "Job Order Service Item" and
"Job Order Part Item". Do NOT create a "Vehicle Job Order Item" doctype — fix
the reference instead (see ISSUE VMS-014).

================================================================================
3. WEB PAGES (18 published) — routes & purpose
================================================================================
All render HTTP 200. Public pages are reachable without login.

POS terminals:
  /pos-terminal        - full Vehicle POS SPA (373 KB HTML+JS bundle)
  /vehicle-pos        - secondary POS entry

Vehicle Management dashboards:
  /vm-dashboard        - main VM dashboard (calls vm_pos_* + vm_company_dashboard_api)
  /vm-company-dashboard - per-company dashboard (calls vm_company_dashboard_api)

Executive dashboards (14 — one per branch/warehouse):
  /executive, /executive-dashboard,
  /executive-ultra-mrf, /executive-ultra-mrf-dau-annex, /executive-ultra-mrf-dau-main,
  /executive-ultra-mrf-warehouse-dau, /executive-ultra-mrf-mexico-warehouse,
  /executive-ultra-mrf-san-fernando, /executive-ultra-mrf-telebastagan,
  /executive-ultra-mrf-telebastagan-2, /executive-automan-car-care-center,
  /executive-san-fernando-warehouse, /executive-the-wheelhub, /executive-wheel-core
  (all call the "Executive Dashboard API" server script = executive_dashboard)

VERIFY: curl -s -o /dev/null -w "%{http_code}" http://localhost/<route>

================================================================================
4. POS / DASHBOARD APIS (10 Server Scripts, api_method names)
================================================================================
All are API-type Server Scripts (safe_exec sandbox). Enabled via
common_site_config.json: "server_script_enabled": true.

  vm_pos_meta            - companies + item categories (no args)
  vm_pos_items           - item search (args: txt, category, company)
  vm_pos_vehicles        - vehicle search (arg: txt)
  vm_pos_vehicle_customer- customer+vehicle by vehicle (arg: vehicle)
  vm_pos_stock           - bin qty + bin locations for item codes (arg: codes)
  vm_pos_history         - cashier's past POS invoices (uses session user)
  vm_pos_cashier         - cashier profile for current user
  vm_probe_api           - health/liveness probe
  executive_dashboard    - executive KPI dashboard (no args; reads all companies)
  vm_company_dashboard_api - per-company KPIs (args: company, period)

VERIFY (from host, with login session):
  POST /api/method/login {usr:administrator,pwd:admin}
  GET  /api/method/<api_method>[?company=ULTRA MRF&period=this_year]
  Expect HTTP 200 with non-empty message.

================================================================================
5. POS TRANSACTION FLOW (how a sale is created)
================================================================================
1. Cashier opens /pos-terminal. Page calls vm_pos_meta (companies/categories)
   and vm_pos_cashier (current user's cashier profile: store, payment modes).
2. Cashier searches items via vm_pos_items(txt=...) — returns code,name,rate,uom.
3. Cashier searches customer vehicle via vm_pos_vehicles(txt=...) or
   vm_pos_vehicle_customer(vehicle=...).
4. Stock check via vm_pos_stock(codes=...) shows bin qty + bin locations.
5. Cashier adds line items, applies payment method(s) (Cash/Card/etc).
6. Save -> creates a **Vehicle POS Invoice** (docstatus 0 -> 1 submit).
   Payment entries posted against company "ULTRA MRF".
7. vm_pos_history shows the cashier's saved invoices.
8. The Invoice also feeds accounting (Sales Invoice style) and the executive/
   company dashboards aggregate from Vehicle Job Order / Sales Invoice / etc.

Known test invoices created earlier: VMSPOS-2026-00001 (₱9,045, Paid),
VMSPOS-2026-00002 (₱70, Paid).

================================================================================
6. TASK / ISSUE LOG  (loop-engineering — for future AI agents)
================================================================================
Each entry: ID | Severity | Symptom | Root Cause | Fix | Status

--- VMS-001 [CRIT] Reports 500: column "X" does not exist (ifnull) -----------
Symptom : Purchase Register /趋势 / financial reports 500 on PostgreSQL.
Root    : Raw SQL used MySQL `ifnull(a,b)`. PG has no ifnull.
Fix     : Converted `ifnull(` -> `coalesce(` across ~30 files
          (accounts, stock, selling, buying, controllers, manufacturing,
          assets, projects, setup, utilities, startup).
Status  : DONE. Verified 9+ reports run.

--- VMS-002 [CRIT] Trends report: function if(boolean,...) does not exist ----
Symptom : Sales/Purchase Order Trends 500.
Root    : trends.py used `SUM(IF(cond,x,NULL))` — PG has no IF().
Fix     : `SUM(IF(cond,x,NULL))` -> `SUM(CASE WHEN cond THEN x ELSE NULL END)`
          + added get_group_by_augmented() to extend GROUP BY with non-agg
          SELECT columns. Patched controllers/trends.py.
Status  : DONE. 4 trend reports verified.

--- VMS-003 [CRIT] Purchase Register: column "Add" does not exist -----------
Symptom : Purchase Register 500, error masked as InFailedSqlTransaction.
Root    : `case add_deduct_tax when "Add" then ...` — PG reads "Add" as a
          COLUMN (double-quoted = identifier in PG). MySQL reads it as string.
Fix     : `"Add"` -> `'Add'` (single quotes) in purchase_register.py.
Status  : DONE.

--- VMS-004 [CRIT] Cash Flow / P&L / Balance Sheet: syntax error at "INDEX" -
Symptom : Cash Flow 500; P&L/Balance Sheet cascade.
Root    : financial_statements.py emitted `FORCE INDEX (idx)` MySQL hint,
          which PG rejects.
Fix     : Gated the hint behind `if frappe.db.db_type == "mariadb":` so PG
          omits it. Patched accounts/report/financial_statements.py.
Status  : DONE. Cash Flow 17 rows, P&L 6, Balance Sheet 16 verified.

--- VMS-005 [CRIT] Server Scripts disabled -> POS + all dashboards dead -----
Symptom : ALL vm_pos_* and dashboard APIs return HTTP 403
          "Server Scripts are disabled. Please enable server scripts from bench".
Root    : common_site_config.json lacked the enable flag. (Wrong key
          `enable_server_scripts` was tried first and IGNORED — frappe uses
          `server_script_enabled`.)
Fix     : Added `"server_script_enabled": true` to common_site_config.json
          and restarted container.
Status  : DONE. After this, 8/10 APIs returned 200 immediately.

--- VMS-006 [HIGH] Executive Dashboard: safe_exec violations -----------------
Symptom : executive_dashboard 500 (SyntaxError then NameError).
Root    : (a) `zone_map[z]["bins_count"] += 1` — augmented assignment on dict
          items is FORBIDDEN in frappe safe_exec sandbox.
          (b) uses `cint()` which is NOT pre-bound in safe_exec (only `flt`).
Fix     : (a) `obj[k] += v` -> `obj[k] = obj[k] + v`.
          (b) add `def cint(v): return int(flt(v) or 0)` helper at top, revert
          `int(` back to `cint(` where None can occur.
Status  : DONE + VERIFIED (HTTP 200, size=4). Helper added; augmented
          assignments converted; int()->cint() None-safe.

--- VMS-007 [HIGH] Company Dashboard: date.replace + wrong table/columns ----
Symptom : vm_company_dashboard_api 500 (KeyError __import__ then
          UndefinedTable then UndefinedColumn then AmbiguousColumn).
Root    : (a) `today.replace(day=1)` — datetime.date.replace triggers blocked
          `__import__` in safe_exec.
          (b) Query referenced `tabVehicle Job Order Item` (does NOT exist).
              Real table is `tabJob Order Service Item`.
          (c) `GROUP BY sii.item_name` — column is `service_item`.
          (d) `vehicle_mix` used `make` from tabVehicle Job Order — but Job Order
              has NO `make` column (make lives on linked Customer Vehicle).
          (e) After JOIN fix, `company` filter became AMBIGUOUS (both tables have it).
Fix     : (a) date math via f-string (no .replace()).
          (b) FROM `tabJob Order Service Item`, SELECT `service_item`,
              GROUP BY `sii.service_item`, total via `total_amount`.
          (d) vehicle_mix now LEFT JOIN tabCustomer Vehicle ON cv.name=vjo.vehicle
              and GROUP BY cv.make.
          (e) co_filter_vjo = " AND vjo.company = %(company)s" in the JOIN query.
Status  : DONE + VERIFIED (HTTP 200, size=13).

--- VMS-008 [MED] Double-quoted string literals in raw SQL -------------------
Symptom : Various `column "X" does not exist` in reports using
          `case col when "Value"`.
Root    : PG interprets "Value" as identifier.
Fix     : Scan + convert value literals to single quotes. (purchase_register
          fixed in VMS-003; sales_analytics "Order Types" fixed by subagent.)
Status  : DONE for known cases; scan pattern = `when "X"` in SQL strings.

--- VMS-009 [MED] zero-date '0000-00-00' ------------------------------------
Symptom : PG rejects MySQL zero-date.
Root    : Default date values '0000-00-00'.
Fix     : -> '0001-01-01' where present.
Status  : DONE in converted files.

--- VMS-010 [LOW] socket.io 502 / Invalid origin -----------------------------
Symptom : realtime 502, "Invalid origin".
Root    : socketio bound to wrong host / CORS.
Fix     : start.sh launches socketio on 10.88.0.50:9000; site_config
          allow_cors:['*']. WS upgrade returns 101.
Status  : DONE (but socketio needs manual restart after container restart).

--- VMS-011 [LOW] Logo 404 / workspace "Icon not configured" ----------------
Symptom : app logo 500/404; workspace icon error.
Root    : missing app_icon + logo path.
Fix     : app_logo /files/ultra_mrf_logo.png; hooks.py app_icon="fa fa-car".
Status  : DONE.

--- VMS-012 [WARN] "Company is mandatory" on dashboard charts ---------------
Symptom : trend Dashboard Charts 500 without company.
Root    : charts lacked company filter; default company not injected.
Fix     : added "company":"ULTRA MRF" to Sales/Purchase Order Trends,
          Top Customers, Top Suppliers filters_json.
Status  : DONE.

--- VMS-013 [INFO] Server Script field names differ from v15 -----------------
Symptom : my discovery queries failed (column "method"/"enabled"/"doc_type"
          does not exist on Server Script).
Root    : v16 Server Script doctype uses `api_method` (not `method`),
          `disabled` (not `enabled`). Just a query-field mismatch, not a bug.
Status  : INFO only.

--- VMS-014 [INFO] Stale "Vehicle Job Order Item" reference -----------------
Symptom : UndefinedTable on company dashboard.
Root    : legacy name; real child tables are Job Order Service Item / Part Item.
Fix     : reference real tables; do NOT recreate the stale doctype.
Status  : DONE (VMS-007).

================================================================================
7. HOW TO VERIFY / RE-RUN THE LOOP
================================================================================
Smoke tests (host, Python 3.11):
  pos-static/test_apis_proc.py   - tests all 10 APIs in separate subprocesses
  pos-static/test_pages.py       - curl all 18 web page routes
  pos-static/smoke_sub.py        - runs 13 financial reports (fresh proc each)

Re-run loop methodology (subagent-driven-development skill):
  1. Precise scan for MySQL-isms: `ifnull(`, `if(`, `locate(`, `'0000-00-00'`,
     `when "X"` (double-quoted value), `FORCE INDEX`, `USE INDEX`.
  2. Confirm frappe modify_query does NOT convert them (it doesn't).
  3. Dispatch one leaf subagent per directory subtree (no shared files).
  4. Each subagent: edit + py_compile (from neutral CWD) + verify in fresh
     PostgreSQL process (a failed txn poisons the shared connection).
  5. Record every fix in §6 issue log.

================================================================================
8. BACKUP / RESTORE NOTES (PROTECT THE DATA)
================================================================================
This user is PROTECTIVE of his data. Before ANY destructive op, back up FIRST.
  Volumes: erp_pg (live records), erp_bench (bench + all code).
  Backup dir: C:\Users\josem\erpnext-system\data_backup\
  Command (stop containers, tar volumes, restart):
    wsl -d podman-machine-default sudo podman stop erp-frappe erp-postgres erp-redis erp-caddy
    wsl -d podman-machine-default sudo podman volume inspect erp_pg  (find Mountpoint)
    sudo tar czf <backup>/erp_pg_<date>.tar.gz -C <mountpoint> .
    ... same for erp_bench ...
    wsl -d podman-machine-default sudo podman start erp-frappe erp-postgres erp-redis erp-caddy

GitHub: changes pushed to Ark143/erpnext-system (main). Full erpnext patch:
  frappe-bench/erpnext_pg_fixes.patch (38 files).

================================================================================
9. STANDING USER INSTRUCTIONS (do not forget)
================================================================================
- LOCAL ONLY. No Cloudflare/hosting sites. Access = http://localhost / erp.localhost.
- After every feature session: BACK UP volumes + PUSH to GitHub. No questions.
- The user judges by what RENDERS. After editing a custom app Page/JS, confirm
  the /assets/...js returns 200 + hard-refresh before claiming done.
- Preserve ALL UI columns/cards/panels 1:1 when refactoring — dropping a
  feature is a regression he flags tersely.
