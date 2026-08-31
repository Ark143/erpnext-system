# Vehicle POS — Top Nav + Customer Vehicle Details (Loop-Engineer Task)

Target URL: http://erp.localhost/desk/vehicle_pos
File: /workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/page/vehicle_pos/vehicle_pos.js
DocType backend: vehicle_management/.../doctype/vehicle_pos_invoice/vehicle_pos_invoice.py (create_from_pos)

## Goal (user request)
1. Move the LEFT SIDE nav (Dashboard / Workspace / Vehicles / POS Invoices) to a TOP navigation bar.
2. Move the category FILTER button(s) into the TOP nav bar.
3. In the Current Ticket, the Customer Vehicle details are missing from the UI — that is why the
   customer↔vehicle link is not visible/verifiable. Add the missing vehicle + customer details so the
   operator can see and confirm the link, and make sure the link is correctly fetched and passed to
   create_from_pos.
4. Test that the transaction works end-to-end (vehicle + customer link -> Vehicle POS Invoice created).

## Current layout (as built)
- `.vpos-app` = CSS grid `220px 1fr 1fr` (side | items | order).
- `.vpos-side` = brand + `.vpos-nav` (Dashboard, Workspace, Vehicles, POS Invoices) + foot.
- `.vpos-main` = `.vpos-topbar` (search + branch select) > `.vpos-cats` (category filter buttons) > `.vpos-products`.
- `.vpos-order` = Current Ticket: Vehicle link control + Customer display + cart + totals + tender + actions.
- `on_vehicle_change()` fetches only `["customer","customer_name","plate_no"]` and writes to
  `.vpos-customer` / `.vpos-customer-display`. No vehicle details panel is rendered.

## Customer Vehicle DocType fields available (verified)
company, plate_no, customer, customer_name, contact_no, email, status, make, model,
year_model, color, vin, engine_no, transmission, cylinders, fuel_type, current_mileage,
mileage_unit, last_service_date, registration_type, insurance_company, insurance_expiry_date,
notes, total_visits, latest_odometer.

## TASK / ISSUE LOG (VMS-015..)

### VMS-015 — Move side nav to TOP nav bar
- Status: DONE (2026-08-31, loop-engineer subagent)
- Type: UI restructure (CSS + DOM)
- Result: `.vpos-side` replaced by `<header class="vpos-topnav">`; `.vpos-app` grid areas "topnav topnav" / "main order" (50/50 body). Verified in container.
- Detail: Convert `.vpos-app` from 3-col grid (side|main|order) to a layout where the nav becomes a
  horizontal top bar spanning full width, and the body below is items (left) + order (right) at 50/50.
  .vpos-nav-item links keep `data-route` behavior (frappe.set_route).
- Acceptance: nav is a top bar (not a left column); items/order still 50/50; responsive on tablet/phone.

### VMS-016 — Move category Filter button into top nav
- Status: DONE (2026-08-31, loop-engineer subagent)
- Type: UI restructure
- Result: `.vpos-cats` (id preserved) now lives inside `.vpos-topnav-cats` within the top nav; filter still works (load_categories populates #vpos-cats, click handler intact).
- Detail: `.vpos-cats` filter buttons ("All" + item groups) should render inside the top nav bar
  (e.g. a horizontally scrollable filter row) instead of sitting above the product grid.
- Acceptance: selecting a category still filters products; filter row is in the top nav area.

### VMS-017 — Add Customer Vehicle details panel (fix the link visibility bug)
- Status: DONE (2026-08-31, loop-engineer subagent)
- Type: Bug fix + feature (data fetch + render)
- Root cause: `on_vehicle_change()` only fetched customer/customer_name/plate_no and wrote a single hidden input + display line. No vehicle details card => operator couldn't see/confirm the link. Backend create_from_pos already resolves customer from vehicle (server-side correct); the UI gap made it look unlinked.
- Fix: added `<div class="vpos-vehicle-details" id="vpos-vehicle-details">` in Current Ticket; `on_vehicle_change()` now fetches plate_no, customer, customer_name, contact_no, email, make, model, year_model, color, vin, transmission, fuel_type, status; new `render_vehicle_details(r, linked)` renders a card (plate + status badge, make/model/year, color, VIN, transmission, fuel, customer, contact, email) plus an explicit "Linked to customer: <customer>" line. `.vpos-customer` hidden input still populated for submit.
- Verified: source markers present; in-container fetch proves fields resolve.
- Root cause: `on_vehicle_change()` only fetches customer/customer_name/plate_no and writes a hidden
  input + a single display line. There is NO vehicle details card, so the operator cannot see/confirm
  the vehicle↔customer link. (Backend create_from_pos already resolves customer from vehicle, so the
  link is correct server-side; the UI gap makes it look "not linking".)
- Fix:
  - Fetch a richer field set on vehicle change: plate_no, customer, customer_name, contact_no, email,
    make, model, year_model, color, vin, transmission, fuel_type, status.
  - Render a `.vpos-vehicle-details` card in the Current Ticket (plate, make/model/year, color, VIN,
    transmission, fuel, customer name, contact, email, status badge).
  - Keep populating `.vpos-customer` hidden input (so submit_invoice passes it) and set `self.customer`.
  - Show a clear "linked to: <customer>" confirmation so the operator sees the link.
- Acceptance: on selecting a vehicle, the details card populates with make/model/plate/customer; the
  submit_invoice payload still sends both `customer` and `vehicle`.

### VMS-018 — Verify transaction end-to-end
- Status: DONE (2026-08-31)
- Type: Verification
- Detail: drove create_from_pos with real vehicle NDB-3344 (Mitsubishi Strada/Triton 2023) -> customer NELSON L. CASTILLO, company Ultra MRF Dau Main, item, paid=200.
- Result: Vehicle POS Invoice **VMSPOS-2026-00005** created (docstatus=1), `vehicle: NDB-3344` correctly captured on the invoice (LINK WORKS), customer NELSON L. CASTILLO. Page http://erp.localhost/desk/vehicle_pos returns 200 (subagent-confirmed); new UI markers (.vpos-topnav, #vpos-vehicle-details, .vpos-cats in top nav) present in served source.
- Acceptance: VMSPOS-#### created (docstatus=1), vehicle link persisted. ✅

## Process note
Loop-engineer: fresh subagent per task, two-stage review (spec compliance then code quality),
verify in a fresh frappe process, then update this log. Backup erp_pg + erp_bench and push to
GitHub Ark143/erpnext-system after all tasks pass.
