# ERPNext & VMS Multi-Branch Enterprise Implementation Plan
## Scope of Work: 7 Service Branches & 3 Central Warehouses
### *Phase 1 Focus: Automan Car Care Center Prototype Pilot*

---

## Executive Presentation Deck Summary

The executive presentation file has been generated and is ready for executive review:
- **PowerPoint File (Root)**: [`ERPNEXT_VMS_IMPLEMENTATION_PLAN_DECK.pptx`](file:///c:/Users/josem/erpnext-system/ERPNEXT_VMS_IMPLEMENTATION_PLAN_DECK.pptx)
- **PowerPoint File (Docs)**: [`docs/ERPNEXT_VMS_IMPLEMENTATION_PLAN_DECK.pptx`](file:///c:/Users/josem/erpnext-system/docs/ERPNEXT_VMS_IMPLEMENTATION_PLAN_DECK.pptx)

---

## Slide-by-Slide Content & Executive Summary

### Slide 1: Title Slide (Modern Dark Navy Theme)
- **Title**: ERPNext & Vehicle Management System (VMS)
- **Subtitle**: Comprehensive Network Implementation Plan & Scope of Work
- **Target Scope**: 7 Service Branches & 3 Central Warehouses
- **Phase 1 Pilot**: **Automan Car Care Center** Prototype Implementation

---

### Slide 2: Strategic Objectives & Value Proposition
1. **Unified Multi-Branch Operations**: Consolidates 7 branches and 3 warehouses under a single core with standardized pricing, vehicle history, and service catalogs.
2. **Real-Time Inventory & ₱47M Stock Control**: Live bin-level tracking, automated intercompany supply chain from Dau/Mexico central warehouses, and mobile barcode put-away & picking.
3. **100% BIR CAS Tax & Audit Compliance**: Built-in Philippine BIR CAS modules: Form 2307, Sales Journal, Purchases Book, Cash Receipts (CRJ), Cash Disbursement (CDJ), and General Ledger.
4. **Role-Based Branch Security & Analytics**: Branch staff are strictly scoped to their assigned company while Executives (CEO, COO, CFO, Auditor) maintain full consolidated performance visibility.

---

### Slide 3: Network Scope & Topology (7 Branches & 3 Warehouses)
```
                          [CENTRAL SUPPLY CHAIN HUBS]
               ┌───────────────────────┼───────────────────────┐
      [Ultra MRF Warehouse Dau]  [San Fernando Warehouse]  [Mexico Warehouse]
               └───────────────────────┬───────────────────────┘
                                       │ (Automated Intercompany Orders)
       ┌────────────────┬──────────────┼──────────────┬────────────────┐
  [Automan Center]  [Dau Main]   [Dau Annex]    [San Fernando]    [Wheel Core]
  (PROTOTYPE HUB)                                       [The Wheelhub] [Telebastagan]
```
- **3 Central Warehouses**:
  - `Ultra MRF Warehouse Dau` (Main Central Distribution Hub)
  - `San Fernando Warehouse` (Pampanga South & Regional Hub)
  - `Ultra MRF Mexico Warehouse` (Bulk Tires, Rims & Alloy Wheels Storage)
- **7 Service Branches**:
  - `Automan Car Care Center` (Phase 1 Prototype Pilot)
  - `Ultra MRF Dau Main`
  - `Ultra MRF Dau Annex`
  - `Ultra MRF San Fernando`
  - `Wheel Core`
  - `The Wheelhub`
  - `Ultra MRF Telebastagan`

---

### Slide 4: Phased Rollout Strategy (Prototype-First Approach)
| Phase | Duration | Scope | Key Focus / Milestone |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Weeks 1 – 4** | **Automan Car Care Center** | Complete pilot of Front Desk, POS, Job Orders, Bin barcodes, BIR invoicing & staff sign-off. |
| **Phase 2** | **Weeks 5 – 7** | **3 Central Warehouses** | Dau, San Fernando, Mexico warehouse bins, bulk inventory count & automated intercompany supply flow. |
| **Phase 3** | **Weeks 8 – 10** | **Cluster 1 Branches** | Rollout to Dau Main, Dau Annex, and San Fernando service branches. |
| **Phase 4** | **Weeks 11 – 12** | **Cluster 2 & Go-Live** | Onboard Wheel Core, The Wheelhub, and Telebastagan + Consolidated Executive BI Launch. |

---

### Slide 5: Live Highlight 1 — Vehicle Management Operations Control Center
- **Live Metrics**: **38,654** Registered Vehicles | **₱2.22M+** Tracked Lifetime Revenue | **₱46.99M** Total Stock Valuation | **481+** Job Orders.
- **Workflow Modules**: Front Desk, Vehicle Estimates, Vehicle Inspections, Job Orders, Stock Requisitions, and Vehicle History Cards.

---

### Slide 6: Live Highlight 2 — Vehicle Analytics & Role-Based Branch Scoping
- **Executive View**: Consolidated performance across all 11 companies.
- **Branch Scoping**: Automatic branch-level restriction (e.g. Automan staff only view Automan transactions).
- **KPI Visualizations**: Labor vs. Parts split (₱104.7k Labor vs. ₱2.11M Parts/Tires), top services ranking, and top tire sizes.

---

### Slide 7: Live Highlight 3 — Vehicle POS Terminal & Multi-Payment Checkout
- **Cashier Features**: Quick barcode scanning, vehicle plate lookup, quick cash denomination shortcuts (+100, +200, +500, +1000).
- **Payment Channels**: Cash, Credit/Debit Card, GCash, Maya, BDO Bank Transfer.
- **Thermal Receipts**: 80mm/58mm thermal receipts with official BIR numbers.

---

### Slide 8: Live Highlight 4 — Triple Enterprise Relationship Maps (SAP-Style Visual Traceability)
- **1. 🚗 VMS Operations Relationship Map**:
  - *Lineage Flow*: `Vehicle Master` $\rightarrow$ `Estimate / Quote` $\rightarrow$ `Pre-Service Inspection` $\rightarrow$ `Job Order` $\rightarrow$ `POS Invoice` $\rightarrow$ `Payment Entry`
  - *Governance*: Complete service and warranty history tied to the vehicle plate number. Eliminates unbilled technician labor and unrecorded parts consumption.
- **2. 📦 Inventory & Stock Movement Relationship Map**:
  - *Lineage Flow*: `Material Request` $\rightarrow$ `Intercompany Transfer (Dau/Mexico Hubs)` $\rightarrow$ `In-Transit Tracking` $\rightarrow$ `Branch Receipt` $\rightarrow$ `Bin QR Location`
  - *Governance*: Full visibility across ₱47M stock across 3 central warehouses and 7 branch service bays with bin putaway and serial/batch tracking.
- **3. 🔄 Procure-to-Pay (P2P) & Intercompany Map**:
  - *Lineage Flow*: `Purchase Requisition` $\rightarrow$ `Branch PO` $\rightarrow$ `Central SO` $\rightarrow$ `Delivery Note` $\rightarrow$ `Goods Receipt` $\rightarrow$ `BIR 2307 Withholding` $\rightarrow$ `Payment Entry`
  - *Governance*: 100% audit-proof document lineage with automated cross-company reconciliation and Philippine tax audit trail.

---

### Slide 9: Live Highlight 5 — 100% BIR CAS Philippine Tax & Accounting Suite
- **Compliance Books**: BIR Form 2307 Withholding Certificates, Sales Journal, Purchases Book, Cash Receipts Journal (CRJ), Cash Disbursements Journal (CDJ), General Journal (GJ), and General Ledger (GL).
- **Live Financials**: Real-time Profit & Loss, Accounts Receivable, and Payables tracking across all entities.

---

### Slide 10: Automan Prototype Detailed Scope of Work (Week-by-Week)
- **Week 1 (Master Data & Setup)**: Chart of Accounts, Automan Service Master Catalog, Stock Item Barcodes, Shelf Bin QR Tags, POS Profile.
- **Week 2 (Operations Pilot)**: Vehicle Estimates, Job Orders, Front Desk Bay tablet/POS checkout, 30 live pilot transactions.
- **Week 3 (Supply Chain & BIR)**: Link replenishment to Dau Warehouse, test Intercompany PO/SO flow, generate BIR Sales/CRJ journals.
- **Week 4 (UAT & Template Freeze)**: User Acceptance Testing (UAT), Staff training, formal Executive Sign-Off, freeze configuration template for network rollout.

---

### Slide 11: Change Management, Training & Governance
- **Role-Based Training Matrix**: Service Advisors, Cashiers, Warehousemen, Branch Heads, Accountants, and Executive Leadership.
- **Governance Framework**: Executive Steering Committee, daily 15-minute standups, 2-week post-go-live hypercare support, visual SOP manuals.

---

### Slide 12: 12-Week Master Implementation Schedule & Sign-Off
- Comprehensive stage-gate schedule ensuring zero business disruption, structured handoffs, and predictable milestone completion.
