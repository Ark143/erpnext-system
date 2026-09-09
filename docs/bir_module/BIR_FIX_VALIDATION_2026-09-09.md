# BIR fixes and live validation — 9 September 2026

Status: deployed and transaction-checked; PDF export and tax classification are still incomplete.

## Deployed changes

All nine BIR Client Scripts and all nine Print Formats were updated on the Frappe site at `38.247.138.224:10017`. Every update was read back and compared to the intended source. Original definitions are backed up locally under `backups/bir_fix_deploy_20260909_133037`. Subsequent label and wrapping changes have their previous definitions in that same folder. No Sales Invoice, Purchase Invoice, Payment Entry, Journal Entry, or saved BIR report was created or modified by this validation.

- Cash Receipt and Cash Disbursement journals now use actual non-cancelled Cash/Bank GL movements. Unpaid invoices do not become cash receipts/payments. Internal transfers netting to zero are excluded. Refunds appear in their actual cash-flow direction. Amounts use company currency.
- Source lists are paginated; stale detail rows are cleared at generation and when company/date scope changes. Cash journals also clear results when source loading fails.
- Sales/Purchases payment dates now require a submitted Payment Entry reference with a positive allocation. Invoice-origin Payment Ledger rows no longer manufacture payment dates. Other settlement types, such as Journal Entries and direct POS settlements, are not covered by this payment-date lookup.
- General Journal uses actual Account names/numbers and paginated invoice statuses. Unknown voucher statuses use POSTED rather than PAID. Cancelled GL entries are excluded.
- General Ledger includes opening balances from prior non-cancelled GL entries.
- Form 2307 enforces a single calendar quarter when generating and anchors monthly columns to the quarter. Its original background was recovered from Antigravity files, uploaded through Frappe's file API, and verified byte for byte. Previously saved reports are not rewritten by these changes.
- Print formats no longer invent fallback address/contact values. Company name/TIN come from Company. Other explicitly saved header values remain and require review. Cash references say Source Voucher; unknown tax/discount values display a dash. Wide tables wrap their cells and repeat headers in print CSS.

## Verified results

The deployed client scripts were fetched again and executed with live, read-only Frappe sources into in-memory forms. The test adapter rejects write methods and validates child-table field names against live DocTypes.

Scope: ULTRA MRF, 1 January–9 September 2026, except Form 2307 uses 1 July–9 September.

- All nine generators completed without runtime errors or unknown child fields.
- Cash Receipt: 46 vouchers, PHP 395,878.50, reconciled independently to cash/bank GL movements.
- Cash Disbursement: 7 vouchers, PHP 56,450.00, reconciled independently to cash/bank GL movements.
- Sales Journal: 148 invoices; Purchases Book: 8 invoices. Fully outstanding invoices have no invented payment date.
- General Journal: 633 rows including explanations; displayed invoice statuses match current source records.
- General Ledger: 457 rows including account totals; debits and credits reconcile to the source GL. A separate September run verifies opening balances for four accounts against prior posted GL.
- Empty-period tests remove transactional detail rows. VAT Summary retains its fixed two category and three total rows.
- Isolated fixtures cover partial/full payments, supplier payment, refund, unpaid invoice, cancelled entries, internal transfer, more than 500 source rows, empty periods and failed source reads. Both cash journals pass. These fixtures were never inserted into production.
- All nine generated documents render through the live HTML print endpoint (HTTP 200). The restored Form 2307 background is accessible (HTTP 200) and was visually inspected in the live print preview. Cash-journal preview was visually inspected with all columns fitting after wrapping.

## Remaining blockers and limitations

1. **PDF download still fails.** The live wkhtmltopdf download path returns HTTP 500 because the executable is missing. The alternate Chromium path also failed during the earlier audit. SSH at `administrator@38.247.138.224:10016` rejects the available key. Working OS access is required to repair and verify the renderer. No successful generated PDF or actual printed-page pagination is claimed.
2. **Tax classification is not certified.** Sales/Purchases/VAT and withholding generators still contain legacy tax-total/account-name heuristics and ATC assumptions. The tested Form 2307 and Withholding Summary produced no positive withholding rows. Approved VAT-account, zero-rated/exempt and ATC mappings are required before positive-tax transaction checks can establish correct tax treatment. Cash tax/discount columns are deliberately unclassified.
3. **Saved report headers and details may be old.** Reload the form, verify company/header fields, click Generate Report, and review before saving/printing. Scope-change clearing does not retroactively rewrite saved documents.
4. **Browser workflow and filing are not certified end to end.** Generator execution, independent reconciliations, HTML rendering and selected visual previews were tested. No accounting transaction was submitted and no tax return was filed.

## Reproduction

- `tools/bir_fixes/` contains the deployed scripts, print-format manifest, baseline hashes and restored image.
- Existing `tools/bir_export/client_scripts/` and `print_formats/` definitions were synchronized so a subsequent suite deployment retains these fixes. Use `tools/deploy_bir_fixes.py` for the repaired background and conflict-checked updates.
- Set `ERPNEXT_PASSWORD` in the environment. `ERPNEXT_URL` and `ERPNEXT_USER` are optional. No password is embedded in the new deployer or verifier.
- Run `node tools/test_bir_cash_transactions.mjs` for isolated transaction scenarios.
- Run `node tools/audit_bir_generators.mjs <snapshot-directory>` with current `Client_Script.json`, `*_meta.json` and `*_record.json` snapshots for read-only live generation. Optional `BIR_DOCTYPE`, `BIR_FROM_DATE`, `BIR_TO_DATE` select a focused run.
- Run `python tools/verify_bir_fixes.py` after generating the expected local candidate snapshots for independent live reconciliation and HTML/PDF status checks.
- `tools/prepare_bir_fixes.py` is the original preparation recipe and requires the private pre-fix backup. Normal deployment uses the committed prepared manifests and baseline hashes without that backup.

Private source records, generated transaction details and raw verification artifacts remain in local backup directories and are not part of this fix commit.
