# Inventory Relationship Map

Live page: http://38.247.138.224:10017/inventory-relationship-map

Open **Stock → Inventory Relationship Map**, or open a saved Item, Warehouse,
Stock Entry, Stock Reconciliation, Purchase Receipt, Delivery Note, Purchase
Invoice, Sales Invoice, or POS Invoice and choose
**View → Inventory Relationship Map**.

## Behaviour

- Search an item by code or name; filter by company, warehouse and posting dates.
- Form launch preselects the document's first item and company. The item input
  offers the document's other item codes. The view traces that item's history,
  not just the source document's movements.
- Receipt/issue cards connect to warehouses using actual, non-cancelled Stock
  Ledger Entries. Positive entries appear on the left; negative and zero-quantity
  adjustments appear on the right. Cards open the underlying records.
- Stock transfers appear on both sides. Inward/outward totals include transfers
  and must not be interpreted as purchases/sales totals.
- The movement ledger includes quantities, warehouse balance after each entry,
  company, document, dates and recorded batch/serial/bundle references.
- Warehouse balances come from current Bin records. Dates filter movements,
  never the current stock snapshot. Quantities use the item's stock UOM.
- Document references show explicit item-row links to purchase/sales orders,
  material requests, receipts and delivery notes, plus return-against links.
  Reference documents do not add to movement totals.
- The API loads the latest 120 entries by default, bounded to 300 when called
  directly. Truncation is prominently indicated; narrow date/warehouse filters
  to inspect older history. The graph starts with 36 entries; select **All loaded
  entries** to draw every entry returned. Zoom and scrolling support large maps.

## Deployment

The feature uses supported Frappe REST document updates. SSH on port 22 was
unreachable during deployment; no server filesystem access or restart is needed.

Set `ERPNEXT_PASSWORD` in your shell (or inject it through your secret manager).
Optional settings are `ERPNEXT_URL` and `ERPNEXT_USER`; the defaults are the VPS
above and Administrator. Passwords are never embedded in these feature files.

```powershell
python vps_migration/deploy_inventory_relationship_map.py
python vps_migration/inventory_relationship_map/test_live.py
```

The deployer installs its own API Server Script, Web Page and nine Client
Scripts, then appends one Stock workspace shortcut. Existing vehicle/P2P maps
and unrelated workspace entries are preserved. It reads each changed document
back and checks stored scalar fields against the source. The API smoke check
runs before publishing the page and navigation.

`api.py` is the canonical server implementation. The deployer extracts its
`build_map` function into the API Server Script; its imports and native Frappe
decorator are not included in restricted execution. HTML, CSS and JavaScript
are deployed verbatim from this directory.

## Access and safety

The API disallows guests and uses permission-aware `frappe.get_list` for items,
warehouses, ledger entries, balances and document checks. It does not use SQL,
`get_all`, or permission bypasses. Related documents are fetched only after an
explicit readable-name query. A missing permission may fail the request rather
than return a misleading empty map. Users need read access to the relevant
inventory and referenced document types. No stock or accounting records are
created, changed or submitted by this feature.

The page shell is public, but it contains no inventory data. Data is fetched only
through the authenticated endpoint; guests see a sign-in action.

## Rollback

Every deployment saves before-images in the git-ignored directory
`vps_migration/backups/inventory_map_<timestamp>/before.json` before each update.
Use the backup for the deployment to undo:

```powershell
python vps_migration/deploy_inventory_relationship_map.py --rollback "vps_migration/backups/inventory_map_<timestamp>/before.json"
```

Rollback restores updated fields and removes records newly created by that
deployment. It also restores the Stock workspace's previous shortcut/content
fields; review concurrent workspace edits before rolling back. For complete
removal of the initial installation on 2026-09-08, the first backup is
`inventory_map_20260908_230140`.

## Verified on 2026-09-08

Eight read-only integration checks passed against the VPS: ledger IDs and signed
quantity reconciliation, company/warehouse isolation and Bin reconciliation,
empty date periods with unchanged current balances, truncation and invalid date
rejection, form source context with upstream PO links, unsupported/missing input
rejection, unauthenticated access denial, and page/shortcut installation.

Browser checks verified item selection, company filtering, reference-tab
navigation, real graph rendering, and opening the map from a Purchase Receipt's
View menu with the expected item/company. No browser console errors were captured
on the map. Python compilation and JavaScript syntax checks passed. Restricted
staff-role combinations were not separately exercised through a logged-in staff
browser session.
