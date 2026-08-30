# Vehicle POS — Debugging & Issue Log
# Module: Vehicle POS  (routes: /vehicle-pos , /pos-terminal ; file: pos_terminal.html)
# App: vehicle_management  |  Served from: apps/vehicle_management/.../www/pos_terminal.html
# Generated: 2026-08-31 — loop-engineering task

================================================================================
1. MODULE OVERVIEW
================================================================================
Vehicle POS is a single-file SPA (pos_terminal.html, ~13,500 lines: inlined CSS
+ JS, plus bundled QR/qrcode libs). It is NOT a Frappe Desk form — it is a
custom www page rendered standalone.

Layout (desktop/tablet, current):
  CSS grid:  grid-template-columns: 68px 1fr 380px
             [rail] [main = item catalog] [ticket = cart/checkout]
  - rail (68px): nav icons (catalog, customers, history, logout)
  - main (1fr): search bar + category chips + product grid (.vpos-grid)
  - ticket (380px fixed): customer vehicle, linked customer, cart rows,
    tender/paid keypad, totals, Charge&Pay button

JS class `POS` (assigned to global `POS`):
  - search()      -> api vm_pos_items
  - card(it)      -> renders product card; onclick -> add()
  - add()         -> push to this.cart; cartRender(); totals(); search()
  - cartRender()  -> render cart rows
  - totals()      -> compute; ENABLE charge btn ONLY if
                     (cart.length && vehicle && customer && company && paid>=total)
  - charge()      -> guards (cart/vehicle/customer/company/paid); confirm(); submit()
  - submit(tot,paid) -> api vehicle_pos_invoice.create_from_pos({...})
                        -> alert success; clear(); open POS Invoice

================================================================================
2. REPORTED BUGS (from user)
================================================================================
U1. UI overlap: "POS UI overlaps the item selection when I select item / add to
    POS" — the ticket/cart panel visually covers the product grid.
U2. Item wrap: items should wrap cleanly; currently wraps but layout shifts/
    overlaps when items are added.
U3. 50/50 ratio: user wants item UI and POS (ticket) UI to be 50% / 50%, not
    the current 1fr + fixed 380px (ticket too narrow, items take the rest).
U4. Responsive: must be usable on mobile (phone), tablet, and PC.
U5. Transaction not working: clicking Charge & Pay does nothing / no invoice
    is created.

================================================================================
3. ROOT-CAUSE ANALYSIS (evidence from source)
================================================================================
[U3 / U1] Layout is fixed 3-col grid with ticket width 380px (desktop) / 340px
   (tablet 769-1024). Not 50/50. See line 44:
     .vpos-app { display:grid; grid-template-columns:68px 1fr 380px; ... }
   At tablet (line 209): 60px 1fr 340px.
   The product grid (.vpos-grid, line 77) uses
     grid-template-columns: repeat(auto-fill, minmax(170px,1fr))
   which is fine, but the PARENT column is 1fr while ticket is fixed -> unequal.

[U1] Overlap cause candidates:
   - On <768px the ticket becomes position:fixed; inset:54px 0 0 0; z-index:50
     and is toggled by .mobile-active (lines 295-306). If toggle logic is off,
     it covers the catalog. Floating cart bar (.vpos-mobile-cart-bar) also
     position:fixed at bottom.
   - The .vpos-tip tooltip is position:fixed and may render over content.
   - On desktop the grid columns should NOT overlap (grid isolates them), so the
     reported overlap is most likely at TABLET/MOBILE widths OR when the ticket
     panel's internal content overflows without its own scroll containment.

[U5] Charge button enable gate (line 13437):
     chargeBtn.disabled = !(cart.length && this.vehicle && this.customer &&
                           this.company && paid >= tot)
   If the Company <select> (.vpos-company, line 13030) is never populated or the
   user does not pick a company, the button stays DISABLED -> "transaction does
   nothing". Also `submit()` calls create_from_pos; if that doctype method throws
   on PostgreSQL, the alert says "Failed to create invoice. See console."

[U5] The submit endpoint:
     api("vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.
         vehicle_pos_invoice.create_from_pos", {...})
   Must be verified to actually create a Vehicle POS Invoice on PostgreSQL.

================================================================================
4. REPRODUCTION STEPS
================================================================================
1. Open http://erp.localhost/vehicle-pos (or /pos-terminal) in a browser.
2. Desktop: observe item grid (left, wide) vs ticket (right, 380px). Confirm
   NOT 50/50 and check if adding items causes visual overlap.
3. Resize to tablet (~900px) and phone (~390px); confirm ticket overlap /
   unusable layout.
4. Select a Customer Vehicle (populates customer), pick Company, add items,
   enter paid amount >= total, click Charge & Pay. Observe whether an invoice
   is created (alert + new tab /desk#Form/POS Invoice/...).

================================================================================
5. FIX PLAN (to be executed by loop-engineer subagent)
================================================================================
F1. 50/50 layout (desktop + tablet): change grid to give items and ticket equal
    share:
      .vpos-app { grid-template-columns: 64px 1fr 1fr; }   /* rail | items | ticket */
    Keep rail slim. Ensure .vpos-main and .vpos-ticket each have
    min-width:0 and their own overflow-y:auto so content never escapes/overlaps.
F2. Overlap-proof: guarantee ticket is a real grid column (not absolute) on
    desktop/tablet; on mobile keep it a full-screen overlay toggled by
    .mobile-active and ensure the floating cart bar does not cover catalog
    (give catalog bottom padding).
F3. Item wrap: keep .vpos-grid auto-fill minmax but raise min card width on
    large screens and ensure cards never overflow the column (min-width:0 on
    grid items).
F4. Responsive breakpoints:
      >1024px : 64px 1fr 1fr (50/50)
      769-1024 : 60px 1fr 1fr (50/50, smaller cards)
      <=768px  : stacked; ticket full-screen overlay; 2-col product grid.
F5. Transaction: verify create_from_pos works on PostgreSQL. If the Company
    <select> is not auto-populated, populate it from vm_pos_meta.companies on
    init so the charge button can enable. Test end-to-end: create a Vehicle POS
    Invoice via the API and confirm a record is created.

================================================================================
6. VERIFICATION
================================================================================
- Visual: load /vehicle-pos at 1440px, 900px, 390px; confirm no overlap, 50/50
  on desktop/tablet, usable on mobile.
- Functional: programmatically (or via UI) run a full POS transaction and assert
  a Vehicle POS Invoice doc is created (check via frappe.get_all).
- Regression: other web pages and APIs still 200 (see ERP_VERIFICATION_MANUAL.md).
