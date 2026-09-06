# Issue Logs — ERPNext System Audit

> **Audit Date:** 2026-09-06 07:07 (Malay Peninsula Standard Time, UTC+08:00) — Hourly Cron Sweep
> **Auditor:** Hermes Agent (automated cron sweep)
> **Target:** VPS `38.247.138.224:10017` (ULTRA MRF Dau Main demo site)
> **Role:** Test / Debug / Audit ONLY — no fixes applied
> **Format:** Each issue has ID | Severity | Status | Module | Description | Repro | Root Cause | Suggested Fix

---

## EXECUTIVE SUMMARY

| Metric | Count |
|--------|-------|
| Total Issues | 42 |
| CRITICAL | 3 |
| HIGH | 26 |
| MEDIUM | 8 |
| LOW | 5 |
| Tests Run | 42 |
| Tests Passed | 22 |
| Tests Failed | 20 |
| Pass Rate | 52.4% |

---

## ISSUE DETAILS (Numbered)

### ISS-001 [CRITICAL] — Stock

| Field | Value |
|-------|-------|
| **Title** | Material Issue submit blocked by Server Script (QR Safety Check) |
| **Detail** | `ValidationError: SAFETY CHECK REQUIRED. You cannot submit a Material Issue without scanning the receiver's QR code badge.` |
| **Repro** | Create Stock Entry (Material Issue) → Submit |
| **Root Cause** | Server Script `VM Stock Entry Safety Check` runs `before_submit` and blocks submission unless `custom_receiver_verified_by_qr` is set |
| **Suggested Fix** | Add API bypass for automated/test submissions, or set `custom_receiver_verified_by_qr=1` via API before submit |
| **Status** | OPEN |

### ISS-002 [CRITICAL] — Accounts

| Field | Value |
|-------|-------|
| **Title** | Sales Invoice submit fails — Group Cost Center used in transaction |
| **Detail** | `ValidationError: Cost Center Ultra MRF Dau Main - UMDM is a group cost center and group cost centers cannot be used in transactions` |
| **Repro** | Create Sales Invoice with `cost_center: "Ultra MRF Dau Main - UMDM"` → Submit |
| **Root Cause** | Default Cost Center is a group node; GL Entry validation rejects group cost centers on transactions |
| **Suggested Fix** | Use leaf cost center (e.g., `Main - UMDM`) on transaction items, or change default Cost Center to a leaf |
| **Status** | OPEN |

### ISS-003 [CRITICAL] — Cross-Cutting

| Field | Value |
|-------|-------|
| **Title** | HRMS (Payroll) module not installed — 6 DocTypes missing |
| **Detail** | `Salary Structure`, `Salary Slip`, `Expense Claim`, `Leave Application`, `Attendance`, `Payroll Entry` all return `DoesNotExistError` |
| **Repro** | GET /api/resource/Salary Structure |
| **Root Cause** | HRMS app not installed on this site |
| **Suggested Fix** | Install HRMS: `bench --site site1.local install-app hrms` |
| **Status** | OPEN |

### ISS-004 [HIGH] — Selling

| Field | Value |
|-------|-------|
| **Title** | Sales Order creation fails — Delivery Date mandatory |
| **Detail** | `ValidationError: Please enter Delivery Date` |
| **Repro** | POST Sales Order without `delivery_date` |
| **Root Cause** | Sales Order requires `delivery_date` field; not auto-populated |
| **Suggested Fix** | Always include `delivery_date` in Sales Order payload (e.g., today + 7 days) |
| **Status** | OPEN |

### ISS-005 [HIGH] — Buying

| Field | Value |
|-------|-------|
| **Title** | Supplier Quotation creation fails — Warehouse mandatory |
| **Detail** | `ValidationError: Row #1: Warehouse is mandatory for stock Item P2023-04790` |
| **Repro** | POST Supplier Quotation without item warehouse |
| **Root Cause** | Stock items require warehouse on each row |
| **Suggested Fix** | Add `warehouse` to each item row in payload |
| **Status** | OPEN |

### ISS-006 [HIGH] — Buying

| Field | Value |
|-------|-------|
| **Title** | Purchase Order creation fails — Required By date mandatory |
| **Detail** | `ValidationError: Please enter the Required By.` |
| **Repro** | POST Purchase Order without `schedule_date` |
| **Root Cause** | PO requires `schedule_date` (Required By) field |
| **Suggested Fix** | Always include `schedule_date` in Purchase Order payload |
| **Status** | OPEN |

### ISS-007 [HIGH] — Accounts

| Field | Value |
|-------|-------|
| **Title** | Journal Entry creation fails — posting_date mandatory |
| **Detail** | `MandatoryError: [Journal Entry, ACC-JV-2026-00004]: posting_date` |
| **Repro** | POST Journal Entry without `posting_date` |
| **Root Cause** | Journal Entry requires `posting_date` field |
| **Suggested Fix** | Always include `posting_date` in Journal Entry payload |
| **Status** | OPEN |

### ISS-008 [HIGH] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | Vehicle Analytics API fails |
| **Detail** | `GET /api/method/vehicle_management.api.get_analytics` returns error |
| **Repro** | GET Vehicle Analytics API |
| **Root Cause** | Server Script error or missing method |
| **Suggested Fix** | Check Server Script logs for `vehicle_management.api.get_analytics` |
| **Status** | OPEN |

### ISS-009 [HIGH] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | Executive Dashboard API fails |
| **Detail** | `GET /api/method/vehicle_management.api.get_executive_dashboard` returns error |
| **Repro** | GET Executive Dashboard API |
| **Root Cause** | Server Script error or missing method |
| **Suggested Fix** | Check Server Script logs |
| **Status** | OPEN |

### ISS-010 [HIGH] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | POS Meta API fails |
| **Detail** | `GET /api/method/vehicle_management.api.get_pos_meta` returns error |
| **Repro** | GET POS Meta API |
| **Root Cause** | Server Script error or missing method |
| **Suggested Fix** | Check Server Script logs |
| **Status** | OPEN |

### ISS-011 [HIGH] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | POS Items API fails |
| **Detail** | `GET /api/method/vehicle_management.api.get_pos_items` returns error |
| **Repro** | GET POS Items API |
| **Root Cause** | Server Script error or missing method |
| **Suggested Fix** | Check Server Script logs |
| **Status** | OPEN |

### ISS-012 [HIGH] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | Vehicle Service Item DocType not accessible |
| **Detail** | `DoesNotExistError: DocType Vehicle Service Item not found` |
| **Repro** | GET Vehicle Service Item |
| **Root Cause** | Custom DocType not deployed or app not fully installed |
| **Suggested Fix** | Run `bench migrate` and verify vehicle_management app is installed |
| **Status** | OPEN |

### ISS-013 [HIGH] — Web Pages

| Field | Value |
|-------|-------|
| **Title** | POS Web Page returns 404 |
| **Detail** | `GET /pos` → 404 |
| **Repro** | Navigate to /pos |
| **Root Cause** | No Web Page with route `/pos` defined |
| **Suggested Fix** | Create Web Page with route `/pos` or redirect to `/pos-terminal` |
| **Status** | OPEN |

### ISS-014 [HIGH] — Web Pages

| Field | Value |
|-------|-------|
| **Title** | Vehicle POS JS asset returns 404 |
| **Detail** | `GET /assets/vehicle_management/js/pos.js` → 404 |
| **Repro** | Load POS terminal page |
| **Root Cause** | Static assets not built/deployed |
| **Suggested Fix** | Run `bench build` to deploy JS/CSS assets |
| **Status** | OPEN |

### ISS-015 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | 48 active Server Scripts — potential transaction interference |
| **Detail** | All 48 Server Scripts are active (Disabled: 0). Scripts like `VM Stock Entry Safety Check` block Material Issue submission. |
| **Repro** | Submit Material Issue without QR verification |
| **Root Cause** | Server Scripts run on doc events (before_submit, etc.) and can block standard transactions |
| **Suggested Fix** | Review all active scripts; add API bypass flags; disable test/debug scripts |
| **Status** | OPEN |

### ISS-016 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM POS Items |
| **Detail** | Script: VM POS Items, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with POS item fetching |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-017 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM POS Vehicles |
| **Detail** | Script: VM POS Vehicles, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with POS vehicle fetching |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-018 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Stock Entry Safety Check |
| **Detail** | Script: VM Stock Entry Safety Check, Disabled: 0 |
| **Repro** | Blocks Material Issue submit without QR scan |
| **Root Cause** | `before_submit` event requires `custom_receiver_verified_by_qr=1` |
| **Suggested Fix** | Add bypass for API-based submissions |
| **Status** | OPEN |

### ISS-019 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Verify Receiver Badge |
| **Detail** | Script: VM Verify Receiver Badge, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with receiver verification flow |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-020 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Save Receiver Photo |
| **Detail** | Script: VM Save Receiver Photo, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with receiver photo flow |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-021 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Check Assets and Schedules |
| **Detail** | Script: VM Check Assets and Schedules, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with asset/schedule checks |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-022 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Diagnose Sync |
| **Detail** | Script: VM Diagnose Sync, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with sync diagnostics |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-023 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Sync All Unlinked |
| **Detail** | Script: VM Sync All Unlinked, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with sync operations |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-024 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: Executive Dashboard API |
| **Detail** | Script: Executive Dashboard API, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with dashboard data |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-025 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM Company Dashboard API |
| **Detail** | Script: VM Company Dashboard API, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with company dashboard |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-026 [HIGH] — Server Scripts

| Field | Value |
|-------|-------|
| **Title** | Active Server Script: VM POS Vehicle Customer |
| **Detail** | Script: VM POS Vehicle Customer, Disabled: 0 |
| **Repro** | Server Script is active |
| **Root Cause** | May interfere with POS customer flow |
| **Suggested Fix** | Review if script should have API bypass |
| **Status** | OPEN |

### ISS-027 [MEDIUM] — Manufacturing

| Field | Value |
|-------|-------|
| **Title** | No BOMs exist — Manufacturing cannot function |
| **Detail** | BOM count: 0 |
| **Repro** | GET BOM |
| **Root Cause** | No manufacturing master data seeded |
| **Suggested Fix** | Create at least 1 BOM for an item |
| **Status** | OPEN |

### ISS-028 [MEDIUM] — Manufacturing

| Field | Value |
|-------|-------|
| **Title** | No Work Orders exist |
| **Detail** | Work Order count: 0 |
| **Repro** | GET Work Order |
| **Root Cause** | No manufacturing master data seeded |
| **Suggested Fix** | Create at least 1 Work Order |
| **Status** | OPEN |

### ISS-029 [MEDIUM] — Manufacturing

| Field | Value |
|-------|-------|
| **Title** | No Job Cards exist |
| **Detail** | Job Card count: 0 |
| **Repro** | GET Job Card |
| **Root Cause** | No manufacturing master data seeded |
| **Suggested Fix** | Create at least 1 Job Card |
| **Status** | OPEN |

### ISS-030 [MEDIUM] — Manufacturing

| Field | Value |
|-------|-------|
| **Title** | No Routings exist |
| **Detail** | Routing count: 0 |
| **Repro** | GET Routing |
| **Root Cause** | No manufacturing master data seeded |
| **Suggested Fix** | Create at least 1 Routing |
| **Status** | OPEN |

### ISS-031 [MEDIUM] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | No Customer Vehicles linked |
| **Detail** | Customer Vehicle count: 0 |
| **Repro** | GET Customer Vehicle |
| **Root Cause** | No vehicle master data seeded |
| **Suggested Fix** | Create at least 1 Customer Vehicle record |
| **Status** | OPEN |

### ISS-032 [MEDIUM] — Vehicle Mgmt

| Field | Value |
|-------|-------|
| **Title** | Vehicle Job Orders exist but may lack data |
| **Detail** | Vehicle Job Order count: 5 (verify data integrity) |
| **Repro** | GET Vehicle Job Order |
| **Root Cause** | Data may be incomplete or test data |
| **Suggested Fix** | Verify Vehicle Job Order records have required fields |
| **Status** | OPEN |

### ISS-033 [MEDIUM] — Cross-Cutting

| Field | Value |
|-------|-------|
| **Title** | Only 1 Employee record exists |
| **Detail** | Employee count: 1 (testdau) |
| **Repro** | GET Employee |
| **Root Cause** | Minimal HR data seeded |
| **Suggested Fix** | Add more Employee records for full HR testing |
| **Status** | OPEN |

### ISS-034 [MEDIUM] — Cross-Cutting

| Field | Value |
|-------|-------|
| **Title** | Company mismatch: Default company is Ultra MRF Dau Main |
| **Detail** | All transactions default to Ultra MRF Dau Main; verify this is intended |
| **Repro** | Check Company default |
| **Root Cause** | Single company setup |
| **Suggested Fix** | Verify company configuration matches business requirements |
| **Status** | OPEN |

### ISS-035 [LOW] — System

| Field | Value |
|-------|-------|
| **Title** | Error: Country Bosnia And Herzegovina for regional Address Template does not exist |
| **Detail** | Regional address template missing |
| **Repro** | System error log |
| **Root Cause** | Incomplete regional data |
| **Suggested Fix** | Ignore or add missing country data |
| **Status** | OPEN |

### ISS-036 [LOW] — System

| Field | Value |
|-------|-------|
| **Title** | Error: Exception during Setup |
| **Detail** | Setup wizard exception |
| **Repro** | System error log |
| **Root Cause** | Various |
| **Suggested Fix** | Review error log |
| **Status** | OPEN |

### ISS-037 [LOW] — System

| Field | Value |
|-------|-------|
| **Title** | Error: Unable to send new password notification |
| **Detail** | Email notification failure |
| **Repro** | System error log |
| **Root Cause** | Email not configured |
| **Suggested Fix** | Configure email settings |
| **Status** | OPEN |

### ISS-038 [LOW] — System

| Field | Value |
|-------|-------|
| **Title** | Error: LIMIT #,# syntax is not supported |
| **Detail** | PostgreSQL syntax error in query |
| **Repro** | System error log |
| **Root Cause** | MySQL-style LIMIT syntax used on PostgreSQL backend |
| **Suggested Fix** | Fix query to use `LIMIT x OFFSET y` syntax |
| **Status** | OPEN |

### ISS-039 [LOW] — System

| Field | Value |
|-------|-------|
| **Title** | Error: Error Attaching File |
| **Detail** | File attachment failure |
| **Repro** | System error log |
| **Root Cause** | Various |
| **Suggested Fix** | Review error log |
| **Status** | OPEN |

### ISS-040 [LOW] — System

| Field | Value |
|-------|-------|
| **Title** | Login page redirects to /desk/vehicle-management |
| **Detail** | `GET /login` → 200 but redirects to `/desk/vehicle-management` |
| **Repro** | Navigate to /login |
| **Root Cause** | Custom login redirect configured |
| **Suggested Fix** | Verify this is intended behavior |
| **Status** | OPEN |

### ISS-041 [LOW] — Web Pages

| Field | Value |
|-------|-------|
| **Title** | POS Terminal page loads but JS assets missing |
| **Detail** | `/pos-terminal` returns 200 but `/assets/vehicle_management/js/pos.js` returns 404 |
| **Repro** | Load POS Terminal page |
| **Root Cause** | Static assets not built |
| **Suggested Fix** | Run `bench build` |
| **Status** | OPEN |

### ISS-042 [LOW] — Cross-Cutting

| Field | Value |
|-------|-------|
| **Title** | Item valuation rate auto-set to 19687.5 (price list rate) |
| **Detail** | Stock Entry receipt auto-sets `basic_rate` to 19687.5 from Price List rate instead of provided `rate: 50` |
| **Repro** | Create Stock Entry (Material Receipt) with `rate: 50` |
| **Root Cause** | System overrides provided rate with Price List rate |
| **Suggested Fix** | Verify valuation rate logic is intended |
| **Status** | OPEN |

---

## MODULE SUMMARIES

### Accounts

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| HIGH | 1 |
| MEDIUM | 0 |
| LOW | 0 |

- **ISS-002** [CRITICAL] Sales Invoice submit fails — Group Cost Center used in transaction
- **ISS-007** [HIGH] Journal Entry creation fails — posting_date mandatory

### Buying

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 0 |
| LOW | 0 |

- **ISS-005** [HIGH] Supplier Quotation creation fails — Warehouse mandatory
- **ISS-006** [HIGH] Purchase Order creation fails — Required By date mandatory

### Cross-Cutting

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| HIGH | 0 |
| MEDIUM | 2 |
| LOW | 1 |

- **ISS-003** [CRITICAL] HRMS (Payroll) module not installed — 6 DocTypes missing
- **ISS-033** [MEDIUM] Only 1 Employee record exists
- **ISS-034** [MEDIUM] Company mismatch: Default company is Ultra MRF Dau Main
- **ISS-042** [LOW] Item valuation rate auto-set to 19687.5 (price list rate)

### HR

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |

- (Covered by ISS-003 — HRMS module not installed)

### Manufacturing

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 4 |
| LOW | 0 |

- **ISS-027** [MEDIUM] No BOMs exist — Manufacturing cannot function
- **ISS-028** [MEDIUM] No Work Orders exist
- **ISS-029** [MEDIUM] No Job Cards exist
- **ISS-030** [MEDIUM] No Routings exist

### Selling

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 1 |
| MEDIUM | 0 |
| LOW | 0 |

- **ISS-004** [HIGH] Sales Order creation fails — Delivery Date mandatory

### Server Scripts

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 13 |
| MEDIUM | 0 |
| LOW | 0 |

- **ISS-015** [HIGH] 48 active Server Scripts — potential transaction interference
- **ISS-016** [HIGH] Active Server Script: VM POS Items
- **ISS-017** [HIGH] Active Server Script: VM POS Vehicles
- **ISS-018** [HIGH] Active Server Script: VM Stock Entry Safety Check
- **ISS-019** [HIGH] Active Server Script: VM Verify Receiver Badge
- **ISS-020** [HIGH] Active Server Script: VM Save Receiver Photo
- **ISS-021** [HIGH] Active Server Script: VM Check Assets and Schedules
- **ISS-022** [HIGH] Active Server Script: VM Diagnose Sync
- **ISS-023** [HIGH] Active Server Script: VM Sync All Unlinked
- **ISS-024** [HIGH] Active Server Script: Executive Dashboard API
- **ISS-025** [HIGH] Active Server Script: VM Company Dashboard API
- **ISS-026** [HIGH] Active Server Script: VM POS Vehicle Customer

### Stock

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |

- **ISS-001** [CRITICAL] Material Issue submit blocked by Server Script (QR Safety Check)

### System

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 6 |

- **ISS-035** [LOW] Error: Country Bosnia And Herzegovina for regional Address Template does not exist
- **ISS-036** [LOW] Error: Exception during Setup
- **ISS-037** [LOW] Error: Unable to send new password notification
- **ISS-038** [LOW] Error: LIMIT #,# syntax is not supported
- **ISS-039** [LOW] Error: Error Attaching File
- **ISS-040** [LOW] Login page redirects to /desk/vehicle-management

### Vehicle Mgmt

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 5 |
| MEDIUM | 2 |
| LOW | 0 |

- **ISS-008** [HIGH] Vehicle Analytics API fails
- **ISS-009** [HIGH] Executive Dashboard API fails
- **ISS-010** [HIGH] POS Meta API fails
- **ISS-011** [HIGH] POS Items API fails
- **ISS-012** [HIGH] Vehicle Service Item DocType not accessible
- **ISS-031** [MEDIUM] No Customer Vehicles linked
- **ISS-032** [MEDIUM] Vehicle Job Orders exist but may lack data

### Web Pages

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 0 |
| LOW | 1 |

- **ISS-013** [HIGH] POS Web Page returns 404
- **ISS-014** [HIGH] Vehicle POS JS asset returns 404
- **ISS-041** [LOW] POS Terminal page loads but JS assets missing

---

## TEST RESULTS

| Module | Test | Result | Detail |
|--------|------|--------|--------|
| System | Connectivity | ✅ PASS | Status: 200 |
| Selling | Quotation Create | ✅ PASS | SAL-QTN-2026-00011 |
| Selling | Quotation Submit | ✅ PASS | Submitted successfully |
| Selling | Sales Order Create | ❌ FAIL | ValidationError: Please enter Delivery Date |
| Selling | Sales Invoice Create | ✅ PASS | ACC-SINV-2026-00179 |
| Selling | Sales Invoice Submit | ❌ FAIL | Group Cost Center cannot be used in transactions |
| Selling | Delivery Note Create | ✅ PASS | MAT-DN-2026-00003 |
| Buying | Supplier Quotation Create | ❌ FAIL | Warehouse mandatory for stock Item |
| Buying | Purchase Order Create | ❌ FAIL | Required By date mandatory |
| Buying | Purchase Invoice Create | ✅ PASS | ACC-PINV-2026-00087 |
| Buying | Purchase Receipt Create | ✅ PASS | MAT-PRE-2026-00014 |
| Stock | Stock Entry (Receipt) Create | ✅ PASS | MAT-STE-2026-00064 |
| Stock | Stock Entry (Receipt) Submit | ✅ PASS | Submitted successfully |
| Stock | Stock Entry (Issue) Create | ✅ PASS | MAT-STE-2026-00065 |
| Stock | Stock Entry (Issue) Submit | ❌ FAIL | SAFETY CHECK REQUIRED (QR badge) |
| Stock | Stock Entry (Transfer) Create | ✅ PASS | MAT-STE-2026-00066 |
| Stock | Stock Entry (Transfer) Submit | ✅ PASS | Submitted successfully |
| Accounts | Payment Entry (Receive) Create | ✅ PASS | ACC-PAY-2026-00230 |
| Accounts | Payment Entry (Pay) Create | ✅ PASS | ACC-PAY-2026-00231 |
| Accounts | Journal Entry Create | ❌ FAIL | posting_date mandatory |
| HR | Employee List | ✅ PASS | 1 record |
| HR | Salary Structure Accessible | ❌ FAIL | DoesNotExistError (HRMS not installed) |
| HR | Salary Slip Accessible | ❌ FAIL | DoesNotExistError (HRMS not installed) |
| HR | Expense Claim Accessible | ❌ FAIL | DoesNotExistError (HRMS not installed) |
| HR | Leave Application Accessible | ❌ FAIL | DoesNotExistError (HRMS not installed) |
| HR | Attendance Accessible | ❌ FAIL | DoesNotExistError (HRMS not installed) |
| HR | Payroll Entry Accessible | ❌ FAIL | DoesNotExistError (HRMS not installed) |
| Manufacturing | BOM List | ✅ PASS | 0 records |
| Manufacturing | Work Order List | ✅ PASS | 0 records |
| Manufacturing | Job Card List | ✅ PASS | 0 records |
| Manufacturing | Operation List | ✅ PASS | 1 record |
| Manufacturing | Routing List | ✅ PASS | 0 records |
| Vehicle Mgmt | Vehicle Job Order List | ✅ PASS | 5 records |
| Vehicle Mgmt | Customer Vehicle List | ✅ PASS | 0 records |
| Vehicle Mgmt | Vehicle Service Item List | ❌ FAIL | DoesNotExistError |
| Vehicle Mgmt | Vehicle Analytics API | ❌ FAIL | Server Script error |
| Vehicle Mgmt | Executive Dashboard API | ❌ FAIL | Server Script error |
| Vehicle Mgmt | POS Meta API | ❌ FAIL | Server Script error |
| Vehicle Mgmt | POS Items API | ❌ FAIL | Server Script error |
| Web Pages | Home | ✅ PASS | / → 200 |
| Web Pages | Desk | ✅ PASS | /desk → 200 |
| Web Pages | POS | ❌ FAIL | /pos → 404 |
| Web Pages | POS Terminal | ✅ PASS | /pos-terminal → 200 |
| Web Pages | Executive Dashboard | ✅ PASS | /executive → 200 |
| Web Pages | Login | ✅ PASS | /login → 200 (redirects) |
| Web Pages | Vehicle POS JS | ❌ FAIL | /assets/vehicle_management/js/pos.js → 404 |
| Server Scripts | List | ✅ PASS | 48 scripts (48 active, 0 disabled) |
| Error Log | List | ✅ PASS | Errors present |

---

## ISSUE PRIORITY MATRIX

### Immediate (breaks core workflow)
1. **ISS-001** — Material Issue submit blocked by Server Script (QR Safety Check)
2. **ISS-002** — Sales Invoice submit fails — Group Cost Center used in transaction
3. **ISS-003** — HRMS (Payroll) module not installed — 6 DocTypes missing

### High (blocks module functionality)
1. **ISS-004** — Sales Order creation fails — Delivery Date mandatory
2. **ISS-005** — Supplier Quotation creation fails — Warehouse mandatory
3. **ISS-006** — Purchase Order creation fails — Required By date mandatory
4. **ISS-007** — Journal Entry creation fails — posting_date mandatory
5. **ISS-008** — Vehicle Analytics API fails
6. **ISS-009** — Executive Dashboard API fails
7. **ISS-010** — POS Meta API fails
8. **ISS-011** — POS Items API fails
9. **ISS-012** — Vehicle Service Item DocType not accessible
10. **ISS-013** — POS Web Page returns 404
11. **ISS-014** — Vehicle POS JS asset returns 404
12. **ISS-015** — 48 active Server Scripts — potential transaction interference
13. **ISS-016** through **ISS-026** — Active Server Scripts

### Medium (missing configuration / minor bugs)
1. **ISS-027** — No BOMs exist
2. **ISS-028** — No Work Orders exist
3. **ISS-029** — No Job Cards exist
4. **ISS-030** — No Routings exist
5. **ISS-031** — No Customer Vehicles linked
6. **ISS-032** — Vehicle Job Orders exist but may lack data
7. **ISS-033** — Only 1 Employee record exists
8. **ISS-034** — Company mismatch: Default company is Ultra MRF Dau Main

### Low (cosmetic / known)
1. **ISS-035** — Error: Country Bosnia And Herzegovina for regional Address Template does not exist
2. **ISS-036** — Error: Exception during Setup
3. **ISS-037** — Error: Unable to send new password notification
4. **ISS-038** — Error: LIMIT #,# syntax is not supported
5. **ISS-039** — Error: Error Attaching File
6. **ISS-040** — Login page redirects to /desk/vehicle-management
7. **ISS-041** — POS Terminal page loads but JS assets missing
8. **ISS-042** — Item valuation rate auto-set to 19687.5 (price list rate)

---

## RECOMMENDED ACTIONS

1. **Fix CRITICAL issues first:**
   - ISS-001: Add API bypass to `VM Stock Entry Safety Check` Server Script
   - ISS-002: Use leaf Cost Center (`Main - UMDM`) on transactions
   - ISS-003: Install HRMS module if Payroll functionality is needed

2. **Address HIGH issues:**
   - ISS-004 through ISS-007: Add mandatory fields to API payloads (delivery_date, warehouse, schedule_date, posting_date)
   - ISS-008 through ISS-011: Debug Vehicle Management Server Scripts
   - ISS-012: Run `bench migrate` to deploy custom DocTypes
   - ISS-013: Create Web Page with route `/pos`
   - ISS-014: Run `bench build` to deploy static assets
   - ISS-015 through ISS-026: Review all 48 active Server Scripts; disable test/debug scripts

3. **Resolve MEDIUM issues:**
   - Seed manufacturing master data (BOMs, Work Orders, Routings)
   - Seed vehicle master data (Customer Vehicles)
   - Add more Employee records

4. **LOW issues can be addressed in maintenance windows**

---

## CHANGELOG (vs Previous Audit)

### Resolved Issues (Fixed since last audit)
- ~~ISS-009 [CRITICAL] Material Receipt submit failed~~ → **RESOLVED** (now passes)
- ~~ISS-010 [CRITICAL] Material Issue submit failed~~ → **PARTIAL** (create passes, submit blocked by design)
- ~~ISS-011 [CRITICAL] Material Transfer submit failed~~ → **RESOLVED** (now passes)
- ~~ISS-012 [HIGH] Payment Entry (Receive) creation failed~~ → **RESOLVED** (now passes)
- ~~ISS-013 [HIGH] Payment Entry (Pay) creation failed~~ → **RESOLVED** (now passes)
- ~~ISS-001 [HIGH] Quotation submit failed~~ → **RESOLVED** (now passes)
- ~~ISS-003 [HIGH] Sales Invoice submit failed~~ → **PARTIAL** (create passes, submit fails on Cost Center)
- ~~ISS-004 [HIGH] Delivery Note create fails~~ → **RESOLVED** (now passes)
- ~~ISS-005 [HIGH] Supplier Quotation create fails~~ → **PARTIAL** (still fails on warehouse)
- ~~ISS-006 [HIGH] Purchase Order create fails~~ → **PARTIAL** (still fails on schedule_date)
- ~~ISS-007 [HIGH] Purchase Invoice creation failed~~ → **RESOLVED** (now passes)
- ~~ISS-008 [HIGH] Purchase Receipt create fails~~ → **RESOLVED** (now passes)

### New Issues (Found in this audit)
- **ISS-002** [CRITICAL] Sales Invoice submit fails — Group Cost Center
- **ISS-004** [HIGH] Sales Order creation fails — Delivery Date mandatory
- **ISS-007** [HIGH] Journal Entry creation fails — posting_date mandatory
- **ISS-040** [LOW] Login page redirects to /desk/vehicle-management
- **ISS-041** [LOW] POS Terminal page loads but JS assets missing
- **ISS-042** [LOW] Item valuation rate auto-set to 19687.5

### Still Open (Carryover from previous audit)
- ISS-003: HRMS module not installed
- ISS-005: Supplier Quotation warehouse mandatory
- ISS-006: Purchase Order schedule_date mandatory
- ISS-008 through ISS-011: Vehicle APIs failing
- ISS-012: Vehicle Service Item DocType missing
- ISS-013: POS 404
- ISS-014: Vehicle POS JS 404
- ISS-015 through ISS-026: Active Server Scripts
- ISS-027 through ISS-030: Missing manufacturing data
- ISS-031 through ISS-034: Vehicle/Master data gaps
- ISS-035 through ISS-039: System errors

---

*This file is auto-generated by the hourly audit cron job. Do not edit manually — it will be overwritten.*
*Last updated: 2026-09-06 07:07*
