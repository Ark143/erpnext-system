# Consolidated Financials export - fixed, Hermes testing required

The previous export crashed with an undefined `fromDate` variable before reaching the download. The corrected export reads the date inputs and produces native XLSX files, one worksheet for the active tab. The General Ledger loader now records its loaded state for export.

Implemented on the VPS and mirrored in both local HTML files. Handler tests for all four tabs triggered a download with the correct filename. Generated workbooks passed ZIP integrity and openpyxl checks for sheet names, numeric values, Unicode, and literal text beginning with `=`.

Hermes acceptance test: reload `/consolidated-financials`, wait for the report to load, and click Export Excel for P&L, Balance Sheet, General Ledger, and Inventory Audit. Confirm each file actually lands in the download folder, opens as XLSX, has the correct worksheet title, and matches the displayed table. Check accounting-style negative amounts remain negative numbers. General Ledger exports the currently loaded table (currently limited to 100 records by the existing report query).

Browser download confirmation remains pending: the Codex in-app browser download-event check timed out; it reported no page JavaScript errors. Do not mark end-to-end browser testing PASS until a downloaded file is observed.

## Follow-up: live button output tested in Microsoft Excel

Captured the exact Blob produced by clicking Export Excel on each loaded VPS tab, saved those bytes locally, and opened each file read-only using installed Microsoft Excel 16.0 with macros disabled. Excel recognized all four as file format 51 (XLSX):

- Profit and Loss: 16 rows, 15 columns; revenue 2644071 and expenses -46736415 read as numbers.
- Balance Sheet: 18 rows, 15 columns.
- General Ledger: 104 rows, 9 columns (100 displayed records plus metadata/header).
- Inventory Audit: 2005 rows, 18 columns.

This verifies the live workbook content with Microsoft Excel itself. The user's saved copy and browser download handling remain to be compared; no unsupported claim of a confirmed browser-saved file is made.
