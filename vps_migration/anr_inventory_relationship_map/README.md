# ANR Inventory Relationship Map

Deployed 2026-09-09 to http://134.199.177.169/inventory-relationship-map for
A&R Craft Philippines Inc. Open from Home or Stock, or the View menu on saved
Item, Warehouse, Stock Entry, Stock Reconciliation, Purchase Receipt, Delivery
Note, Purchase Invoice, Sales Invoice, and POS Invoice forms.

Adapted from ../inventory_relationship_map. ANR has no Bin Location DocType or
ledger bin_location field: this version uses warehouse nodes, omits the bin
selector/ledger column, and uses /app document routes. The authenticated API
uses permission-aware reads and makes no stock/accounting changes.

Filters: item, company, warehouse, posting date range. Tabs: relationship map,
movement ledger, current warehouse balances, upstream document references.
Latest 120 movements load by default; graph initially draws 36. Both limits
are disclosed in the UI. Dates filter movements, not current stock balances.

Deployment: set ERPNEXT_URL to the ANR origin, ERPNEXT_USER and ERPNEXT_PASSWORD,
then run python vps_migration/deploy_anr_inventory_map.py. No credentials are
stored in the source. The deployer also repairs the pre-existing Stock shortcut
to missing Global Stock Balance by pointing it to the verified Stock Balance
report, retaining its existing label.

Before-images: ../backups/inventory_map_20260909_145102/before.json and
../backups/inventory_map_20260909_145211/before.json. Roll back in reverse order
using deploy_inventory_relationship_map.py --rollback with ANR environment
variables set. These backups cover feature configuration, not the full database.

Verified: independent stock-ledger IDs and signed quantities; company/warehouse
isolation and Bin balance reconciliation; empty date ranges preserving current
balances; truncation and invalid dates; unknown item and unsupported source
rejection; guest denial; saved Home/Stock shortcuts and content; JavaScript
syntax. Browser verified graph and movement-ledger tab with real ANR data.
Restricted staff accounts were not separately tested.
