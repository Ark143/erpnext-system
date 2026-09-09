# BIR functional and print audit — 2026-09-09

This is the pre-fix audit. See [deployed fixes and validation](BIR_FIX_VALIDATION_2026-09-09.md) for the subsequent repairs, transaction checks and remaining blockers.

**Result: the BIR suite is not working end to end and is not ready for operational sign-off.**

Target: `http://38.247.138.224:10017`. Tested as Administrator. Main populated
generation test: ULTRA MRF, 2026-01-01 through 2026-09-09. Empty-period regression
test: 1900-01-01 through 1900-01-02. Existing saved examples were also inspected.

## What was tested

- All nine installed BIR parent DocTypes, enabled Client Scripts, named Print
  Formats and default print-format assignments were found.
- Executed all nine live `generate_report` handlers in an in-memory form adapter
  using authenticated, read-only requests to the actual VPS. Child-table names
  and assigned fields were checked against live schemas. No forms were saved.
- All nine handlers completed without runtime errors. Seven produced populated
  output; Form 2307 and Withholding Summary returned zero detail rows. Those two
  positive withholding-data paths remain unverified.
- Rendered all nine existing examples and all nine freshly generated documents
  through the live `frappe.www.printview.get_html_and_style` endpoint: HTTP 200.
- Requested all nine default server PDF downloads: **nine HTTP 500 failures**.
  Missing `wkhtmltopdf` is the common error. An explicit Chrome PDF test also
  failed with `TimeoutError: Chromium took too long to start`.
- Visually inspected the nine generated HTML print layouts in the browser.
  These are the live renderer's HTML/style outputs, served locally for review.
  Also exercised the live Sales Journal form's Generate Report button without
  saving. This is not nine separate full browser-form walkthroughs.

## Blocking findings

### P1 — PDF export fails for every module

Every format selects `wkhtmltopdf`, but that executable is unavailable on the
VPS. The alternative Chrome renderer did not start. Successful HTML rendering
does not establish that PDF export works. No successful production PDF could be
examined, so final pagination, repeated page headings and physical paper output
are **not validated**. The in-app browser's print-to-PDF capability was also
unavailable; it was not used as a substitute for a working server export.

### P1 — Cash journals report unpaid invoices as cash

Cash Receipt Journal builds from submitted Sales Invoices and assigns invoice
grand total directly to `net_cash`. In the selected company and period, **111
fully outstanding invoices totaling PHP 798,992.50** were included as net cash.
Their outstanding amounts equal their grand totals in the source records.

Cash Disbursement Journal builds from submitted Purchase Invoices and calculates
`net_paid` from grand total less deducted taxes, without actual payment allocation.
**Three fully outstanding invoices totaling PHP 200.00** were shown as net paid.
The generated print even labels these rows UNPAID while showing positive NET PAID.

These are reproduced software/data errors, not a review of tax treatment. Repair
should reconcile payment dates and allocations, including partial payments,
returns, cancellations and POS payments, before cash-journal sign-off.

### P1 — Form 2307 background is unavailable

The template depends on `/files/bir_2307_page1.png`. That asset returned HTTP 500.
The preview displays floating text without the form's boxes, headings or labels.
The generator also contains hard-coded fallback TIN/address/ZIP values. Missing
taxpayer details must not silently become fabricated certificate information.

### P1 — Six generators retain old rows after an empty-period query

After generating populated reports, changing the dates to an empty period leaves
previous rows intact in Cash Receipt Journal, Cash Disbursement Journal, Sales
Journal, Purchases Book, General Journal and General Ledger. The handlers show
a no-records message, but the form can still display/print the previous data
under the newly selected period. This was reproduced in the in-memory adapter.

### P1 — General Journal mislabels accounts and payment status

The code splits account names on ` - ` and uses the company abbreviation as the
account title. The preview shows entries such as code `Cash`, title `UM` instead
of a correctly resolved account code/title.

Invoice-status lookups lack explicit pagination, and missing statuses default
to PAID. **111 fully outstanding Sales Invoices were labeled PAID** in generated
General Journal transaction headers. Source debit/credit totals did reconcile:
PHP 17,672,007.00 on each side. Balanced totals do not correct those label errors.

### P2 — Payment dates and report metadata are unreliable

Sales Journal and Purchases Book take posting dates from any matching Payment
Ledger Entry without establishing that the row represents a payment. All 111
unpaid Sales Invoices and all three unpaid Purchase Invoices received a payment
date in these reports.

Multiple templates use a fallback Davao address and ZIP, and can reuse unrelated
header/contact values from the saved sample. Metadata should be resolved and
validated for the selected company. Sensitive sample contact details are omitted
from this audit report.

Cash Receipt Journal assigns `payment_date`, which does not exist in its live
child-table schema. It is not reliable persisted report data.

### P2 — Tax classification and positive withholding cases need further tests

Sales/Purchases/VAT generators use aggregate `total_taxes_and_charges` as VAT,
and infer classifications from its sign. This does not identify the tax accounts
or distinguish VAT from other charges/deductions. The current ULTRA MRF test
records do not exercise populated VAT and withholding cases sufficiently to
approve that logic. Form 2307 and Withholding Summary generated zero detail rows;
zero rows plus a success notification is not a successful positive-case test.

Form 2307 accepts arbitrary date ranges, while its monthly breakdown only handles
the first three relative months. Quarter validation and a known withholding case
are needed before certificate testing can be completed.

## Module-by-module result

- **BIR Cash Receipt Journal — FAIL.** Generated 148 detail and five summary
  rows. HTML layout renders; unpaid invoices become cash, a generated field is
  missing from the schema, empty-period output is stale, and PDF download fails.
- **BIR Cash Disbursement Journal — FAIL.** Generated eight detail and five
  summary rows. HTML layout renders; unpaid invoices become disbursements,
  empty-period output is stale, and PDF download fails.
- **BIR Form 2307 — FAIL / positive case unverified.** No detail rows for the
  selected live party. Background asset fails, fallback identity data exists,
  and PDF download fails.
- **BIR Sales Journal — FAIL.** Generated 148 detail and four summary rows.
  False payment dates and stale empty-period rows are reproduced. The wide
  preview overflows at 1265px: its table measures approximately 1575px. Print CSS
  reduces the size, but actual paginated output remains unverified. PDF fails.
- **BIR Purchases Book — FAIL.** Generated eight detail rows. Table renders,
  but unpaid invoices receive payment dates, empty-period output is stale,
  and PDF download fails.
- **BIR General Journal — FAIL.** Generated 633 rows including explanations.
  Debit/credit totals reconcile to 448 source GL entries, but account titles
  and payment statuses are wrong; empty-period rows persist; PDF fails.
- **BIR General Ledger — PARTIAL, end-to-end FAIL.** Generated 457 rows,
  comprising 448 GL postings and nine account-total rows. Grouped HTML layout
  renders. Balances start at zero at the selected period, so they are period
  movements rather than opening-inclusive account balances. Empty-period rows
  persist and PDF download fails. Cancellation handling remains a code concern;
  this source set contained no cancelled GL rows.
- **BIR VAT Summary — PARTIAL, end-to-end FAIL.** Two category and three
  summary rows render. Counts match 148 sales and eight purchase invoices.
  Empty-period values reset, but nonzero VAT classifications are not validated,
  template metadata needs correction, and PDF download fails.
- **BIR Withholding Summary — UNVERIFIED positive case, end-to-end FAIL.**
  Empty HTML layout renders and the empty-period path clears rows. No positive
  withholding details were produced in the selected data; PDF download fails.

## Repair order and acceptance checks

1. Restore a supported server PDF engine and the authoritative Form 2307
   background. Verify actual downloaded PDFs for each format.
2. Correct cash journals and payment-date lookups against actual payment
   allocations. Use known unpaid, partly paid, fully paid, returned and cancelled
   examples, and reconcile totals independently.
3. Clear/rebuild report tables on every generation; prevent stale data after
   errors or empty results. Fix General Journal account/status resolution and
   missing schema fields.
4. Resolve report headers from the selected company; remove fabricated defaults.
   Validate the intended tax-account mappings and positive VAT/withholding cases
   with the responsible accounting owner.
5. Recheck letter/landscape sizing, all rightmost columns, long names, multi-page
   tables, repeated headings and final totals using the repaired production PDF
   engine. Then test Accounts User/Manager permissions; this audit used Administrator.

## Evidence and changes

Raw source snapshots, generated documents, renderer HTML, and machine-readable
results are local in `backups/bir_audit_20260909/`. They contain business data and
must not be published to the repository. The read-only generator adapter is
`tools/audit_bir_generators.mjs`; run with `ERPNEXT_PASSWORD` supplied through the
environment and the snapshot directory as its argument.

No business records, tax calculations, report templates or VPS configuration were
changed during the audit. Existing sample reports were not overwritten. The live
browser form was modified only in memory and was not saved. This audit establishes
software defects and test gaps; it does not certify regulatory compliance.
