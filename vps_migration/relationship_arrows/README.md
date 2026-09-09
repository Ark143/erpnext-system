# VMS and P2P document arrows

Deployed 9 September 2026 to `http://38.247.138.224:10017`.

The previous renderer passed SVG markup strings to jQuery `append`. Live inspection confirmed that the resulting connector paths had the HTML namespace (`http://www.w3.org/1999/xhtml`), so the browser did not draw them. The replacement creates SVG elements with `createElementNS` and uses explicit arrowhead polygons without shared marker IDs.

The renderer shows directional source-to-target links, labels, dashed references and colored payment/conversion links. Same-column connections curve around the cards; links skipping a stage travel below the cards. Actual card heights determine the attachment points. Native text nodes prevent relationship labels being interpreted as HTML. Arrows share the canvas transform for zoom/pan and replace previous connectors on refresh.

## Deployment

`draw_edges.js` is the common renderer fragment. The canonical app source is `frappe-bench/apps/vehicle_management/vehicle_management/public/js/vehicle_relationship_map.js`.

Set `ERPNEXT_PASSWORD`, then run `python vps_migration/relationship_arrows/deploy.py` from the repository. Optional `ERPNEXT_URL` and `ERPNEXT_USER` override the target. The deployer patches only the renderer in each enabled `SAP Relationship Map - ...` and `VM SAP Relationship Map Client...` script, retaining their distinct map UI and backend API. It backs up existing definitions, checks for concurrent modifications and verifies every write by readback. Unrecognized renderer versions stop deployment before writes.

28 live Client Scripts verified. Rollback definitions are local in `backups/relationship_arrows_deploy_20260909_183137/`. No business documents or API relationship logic were changed.

## Validation

- `node vps_migration/relationship_arrows/test_edges.mjs`: native SVG, forward/reverse/same-column/skip-stage connectors, arrowheads, text-safe labels, missing/self links and repeat rendering pass.
- Canonical JavaScript passes `node --check`.
- Live P2P: Purchase Receipt `MAT-PRE-2026-00002`, 5 cards / 4 SVG arrows. Purchase Order → Purchase Receipt → Purchase Invoice → Payment Entry and Supplier → Purchase Receipt verified. Fit-to-screen reviewed visually.
- Live VMS: Job Order `JO-2026-00028`, 7 cards / 7 SVG arrows. Customer/vehicle, estimate/inspection, job order, invoice and payment relationships verified. Same-column and skip-stage routes reviewed visually. Zoom preserves arrows; clicking the Sales Invoice opens its correct document details.
- Both maps refresh without duplicate connectors.

Reload existing Desk forms to load the updated Client Scripts. Open **View → VMS Relationship Map** or **View → VMS / P2P Relationship Map**, then use **Fit to Screen** for the complete flow.
