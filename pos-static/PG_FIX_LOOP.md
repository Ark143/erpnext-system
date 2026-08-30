# ERPNext v16 on PostgreSQL — MySQL-ism Fix Loop (Subagent-Driven)

## Problem
The bench runs ERPNext 16.33 on **PostgreSQL** (not its native MariaDB). ERPNext's
queries/reports are written in MySQL dialect, so they 500 when run. Confirmed classes of breakage:

1. `if(cond, a, b)` — MySQL control-flow function. PostgreSQL has no `if()`. → must become `CASE WHEN cond THEN a ELSE b END`.
2. `ifnull(a, b)` — MySQL. PostgreSQL → `coalesce(a, b)`.
3. Loose `GROUP BY` — MySQL allows non-aggregated SELECT columns not in GROUP BY; PostgreSQL forbids it. → extend GROUP BY with the extra non-aggregate columns.
4. Zero-dates `'0000-00-00'` — PostgreSQL rejects. → use a sentinel like `'0001-01-01'`.
5. Backtick-quoted identifiers `` `tabX` `` — frappe's `modify_query` already converts these to `"tabX"`, so usually safe; only fix if a query still 500s.
6. `locate(a, b)` — PostgreSQL → `strpos(b, a)` (arg order swapped). frappe's `modify_query` converts `locate(`→`strpos(` but does NOT swap args, so double-check.

## KEY FINDING (verified)
frappe's PostgreSQL `modify_query` (`apps/frappe/frappe/database/postgres/database.py`)
does NOT auto-convert `ifnull(`, `locate(`, or `if()`. It only handles backtick→quote
and numeric literal quoting. So `ifnull(` / `locate(` / `if()` inside raw SQL ARE genuine
PostgreSQL-breaking bugs and must be fixed in the ERPNext source.

Precise scan (no-space `if(` = MySQL fn; Python `if (cond):` excluded): remaining real
SQL-isms are dominated by `ifnull(` (→ `coalesce`) and zero-dates (`'0000-00-00'` →
`'0001-01-01'`). True `if(` and `locate(` are rare after prior fixes.

## Already Fixed (this session)
- `erpnext/controllers/trends.py` — `SUM(IF(...))` → `SUM(CASE...)`; GROUP BY augmentation helper. (Sales/Purchase/Delivery/Receipt Trends reports) — VERIFIED runs.
- `erpnext/controllers/queries.py` — full `item_query` rewrite (ifnull→coalesce, backticks→quotes, if()→case, zero-date).
- `erpnext/stock/stock_balance.py` — `if(dont_reserve_qty_on_return, ..., 0)` → CASE.
- `erpnext/accounts/doctype/payment_entry/payment_entry.py` — `if(rounded, rounded, grand)` → CASE.

## Loop Plan (subagent-driven)
For each high-traffic ERPNext module file, a subagent:
  1. Scans the file for MySQL-isms (if(, ifnull(, loose GROUP BY, zero-dates, locate().
  2. Rewrites ONLY the broken SQL, preserving all other behavior (match existing style).
  3. Verifies the file still imports (py_compile) and the affected report/query runs against PostgreSQL in the bench.
  4. Reports exactly what changed.

### Tasks (batched by file group)
- T1: `erpnext/accounts/report/*` (all script reports with raw SQL)
- T2: `erpnext/stock/report/*`
- T3: `erpnext/selling/report/*` + `erpnext/buying/report/*`
- T4: `erpnext/controllers/queries.py` remaining (other query fns) + `taxes.py` + `status_updater.py`
- T5: `erpnext/accounts/utils.py` + `general_ledger.py` + `stock_ledger.py`
- T6: `erpnext/manufacturing/report/*` + `erpnext/projects/report/*`
- T7: Final integration sweep — run a smoke test that opens each fixed report via the bench API and confirms 200/no SQL error.

## Verification standard (every subagent MUST do)
- `python -m py_compile <file>` → no syntax error.
- Run the affected report/query inside the container with `frappe` against `site1.local` and confirm it returns rows (not a PostgreSQL error).
- Do NOT change Python logic, only SQL-string dialect.
- Do NOT touch files already fixed.

## Execution Log
- [x] Plan written (PG_FIX_LOOP.md)
- [x] Precise scan: identified `ifnull(` + zero-date as the dominant remaining SQL-isms; confirmed `modify_query` does NOT auto-convert them.
- [x] Dispatched 4 parallel subagents (accounts / stock / selling-buying-controllers / manufacturing-assets-projects-setup) to convert `ifnull(`→`coalesce(`, zero-date→`'0001-01-01'`, SQL `if()`→`CASE`, `locate`→`strpos` and py_compile-verify each file.
- [x] Subagents done: ~30 files patched (ifnull→coalesce + zero-date). test_loyalty_program.py reverted (tests not patched).
- [x] NEW MySQL-ism class found: **double-quoted string literals** in raw SQL (`case add_deduct_tax when "Add"`) — PostgreSQL treats `"Add"` as a COLUMN, not a string. Fixed purchase_register.py `"Add"`→`'Add'`. Sales Register / others verified.
- [x] Restarted erp-frappe; smoke test (isolated subprocess per report):
  - WORKING: Sales Order Trends, Purchase Order Trends, Delivery Note Trends, Purchase Receipt Trends, Sales Register (14 rows), Accounts Receivable, Stock Ledger (4 rows), Gross Profit (41 rows), Purchase Register (6 rows after fix).
  - REMAINING REAL BUGS (not MySQL-isms, dispatched focused subagent): Sales Analytics (`'Analytics' object has no attribute 'data'`), Cash Flow (SQL/Python error in financial_statements.py get_accounting_entries). Both use frappe.qb (backend-agnostic) → likely genuine v16 code bugs, under investigation.
- [x] Collect focused subagent result for Sales Analytics + Cash Flow
- [x] FINAL SMOKE TEST (all 13 reports, fresh subprocess each, correct filters): ALL PASS
  - Sales Order Trends ✓ Purchase Order Trends ✓ Delivery Note Trends ✓ Purchase Receipt Trends ✓
  - Sales Analytics ✓ (12 rows) Sales Register ✓ (14) Purchase Register ✓ (6)
  - Cash Flow ✓ (17) Gross Profit ✓ (41) Accounts Receivable ✓ Stock Ledger ✓ (4)
  - Profit and Loss Statement ✓ (6) Balance Sheet ✓ (16)
  - Bonus fixed: financial_statements.py `FORCE INDEX` MySQL hint gated behind `db.db_type=="mariadb"` (was breaking P&L/Balance Sheet/Cash Flow + Consolidated on PostgreSQL).
- [x] Back up erp_bench + erp_pg volumes to data_backup/ (erp_pg_20260830_220941.tar.gz, erp_bench_20260830_220941.tar.gz)
- [x] Generated complete patch of all 38 erpnext file changes -> frappe-bench/erpnext_pg_fixes.patch (44KB, saved in host repo)
- [x] Committed + PUSHED to GitHub Ark143/erpnext-system (branch main, commit bc2a24f): PG-fix patch + Caddyfile + vehicle_management analytics + backup script.
- [x] Restarted containers; full stack verified: login 200, logo 200, socket.io 200 (socketio restarted manually — start.sh nohup doesn't survive serve exec; known quirk).

## RESULT
All 13 dashboard/reports run on PostgreSQL. ~30 files patched for MySQL-isms + double-quoted literals + FORCE INDEX gating. Loop engineering methodology (subagent-driven, isolated verification) applied and documented. Backup + push complete per standing instruction.

## Risk guardrails
- Each subagent edits its OWN file set (no two subagents touch the same file) to avoid conflicts.
- Backtick conversion is handled by frappe core — subagents must NOT blindly wrap every backtick; only fix if the query 500s.
- After all tasks: restart `erp-frappe` container so the running serve reloads modules, then run the smoke test.
