# Inventory Audit filters - deployed

- Only items with stock: keeps positive on-hand quantity in any selected company.
- All items selected by default; item selector supports multiple selection, Select All Items, and Clear Selection.
- Search, item selection, and stock-only filters combine. Table totals and Excel export use the filtered rows.
- Removed the silent 2,000-item API cutoff. Live API returned 10,541 items.

Live UI verified: stock-only displayed 27 SKUs; Clear Selection displayed 0; Select All Items restored 27. Local checks covered positive, zero, negative stock, selection intersection, and recalculated totals.

Hermes regression: repeat with different companies and dates, choose individual items, verify search and stock-only intersections, and compare exported inventory rows and totals with the filtered table.
