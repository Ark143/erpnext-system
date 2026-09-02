import os, re

target_brain = r'C:\Users\josem\.gemini\antigravity-ide\brain\ad9d29ca-966c-454f-b5c8-9ae935c95822\full_technical_and_functional_documentation.md'
target_repo = r'c:\Users\josem\erpnext-system\docs\FULL_TECHNICAL_AND_FUNCTIONAL_DOCUMENTATION.md'

with open(target_repo, 'r', encoding='utf-8') as f:
    doc = f.read()

new_sections = """---

## 3. Order to Cash (O2C) Enterprise Process Flow

The **Order to Cash (O2C)** process orchestrates all customer-facing transactions across two distinct operational tracks: **Track A: Retail & Walk-in Cash/Card Customers** (instant counter settlement) and **Track B: Commercial Fleet & Corporate Credit Accounts** (quotation, sales order, terms, and receivable aging).

```mermaid
graph TD
    subgraph "Intake & Identification"
        O1["Customer Inquiry / Drive-in"] --> O2["Customer Vehicle Lookup / Registration<br/>(Plate No., Specs, Mileage)"]
        O2 --> O3["Intake Inspection & Service Estimation<br/>(Vehicle Inspection & Vehicle Estimate)"]
    end

    subgraph "Sales Channel Routing"
        O3 -->|Retail / Walk-in| O4A["Touchscreen POS Terminal<br/>(/pos-terminal or /desk/vehicle_pos)"]
        O3 -->|Fleet / B2B Terms| O4B["Quotation -> Sales Order<br/>(Credit limit & terms verification)"]
    end

    subgraph "Execution & Bay Service"
        O4A --> O5A["Express Tire Bay / Counter Sale"]
        O4B --> O5B["Vehicle Job Order Dispatch<br/>(Bay technician assignment & parts requisitions)"]
    end

    subgraph "Fulfillment & Invoicing"
        O5A --> O6A["Vehicle POS Invoice (VMSPOS-...)<br/>+ ERPNext POS Invoice (ACC-PSINV-...)"]
        O5B --> O6B["Delivery Note / Standard Sales Invoice<br/>(ACC-SINV-...)"]
    end

    subgraph "Financial & Ledger Settlement"
        O6A --> O7A["Immediate Cash / GCash / Card Settlement<br/>(GL: Cash Dr / Sales Cr / Stock Ledger Decrement)"]
        O6B --> O7B["Accounts Receivable Aging (30/60 Days)<br/>(Payment Entry settlement against Fleet account)"]
    end

    subgraph "Reporting & Analytics"
        O7A --> O8["Executive Dashboard & Daily POS Register"]
        O7B --> O8
    end
```

### Detailed Order to Cash Workflow Steps:

#### Step 1: Customer & Vehicle Intake
1. Customer drives into the branch or calls for inquiry.
2. Cashier/Service Advisor searches for the plate number in `Customer Vehicle`.
3. If new, the vehicle is created with plate number, make, model, year, VIN/chassis number, engine number, and linked customer. Space normalization automatically cleans customer strings.
4. Odometer reading is recorded to evaluate maintenance milestones.

#### Step 2: Intake Inspection & Pre-Service Estimation
1. For mechanical and PMS repairs, Service Advisor executes a `Vehicle Inspection` based on standard checklist templates.
2. An electronic `Vehicle Estimate` is drafted containing recommended labor tasks (`Job Order Service Item`) and required parts (`Job Order Part Item`).
3. Customer receives estimate via SMS/Email or printed sheet for formal approval.

#### Step 3: Sales Channel Execution
* **Track A (Retail Walk-in & Express Tire/Battery Counter)**:
  * Customer orders tires, batteries, lubricants, or express tire mounting/balancing.
  * Cashier pulls up vehicle plate in the **POS Terminal** (`/pos-terminal`).
  * Toggles **In Stock: ON** to verify immediate warehouse on-hand stock for the branch.
  * Cashier selects items, applies valid bundle discounts, and reviews bill summary.
* **Track B (Corporate Fleet & B2B Commercial Accounts)**:
  * Formal `Quotation` is issued and approved by fleet customer.
  * Converted into a confirmed `Sales Order`. The system checks the customer's credit limit and outstanding balance before booking.
  * Stock is allocated and reserved in warehouse inventory.

#### Step 4: Workshop Bay Execution & Parts Consumption
1. For work requiring bay time, a `Vehicle Job Order` is generated in status `In Progress`.
2. Assigned technician draws required tires, motor oils, and filters from branch warehouse stores.
3. If parts are missing, status moves to `Pending Parts` until warehouse replenishment arrives.
4. Upon mechanical completion and test run, status updates to `Completed`.

#### Step 5: Dual-Ledger Invoicing
* **Counter POS**:
  * Cashier clicks **Complete Sale** with payment tender (Cash, Card, GCash, Bank).
  * System concurrently creates `Vehicle POS Invoice` and auto-submits official ERPNext `POS Invoice`.
  * Warehouse inventory is decremented immediately from `tabBin`.
* **Fleet Billing**:
  * Service Advisor marks Job Order `Released`.
  * Generates standard `Sales Invoice` with 30-day payment term.

#### Step 6: Payment Collection & Ledger Posting
1. Immediate tender generates payment entries into Cash/Bank accounts.
2. Fleet receivables are tracked under Accounts Receivable aging.
3. Collection is booked via `Payment Entry`, reconciling outstanding invoices and clearing customer ledger.

---

## 4. Purchase to Pay (P2P) Enterprise Process Flow

The **Purchase to Pay (P2P)** process manages the procurement lifecycle for tires (Michelin, Yokohama), automotive spare parts, bulk lubricants, and workshop consumables.

```mermaid
graph TD
    subgraph "1. Requisition & Need Identification"
        P1["Low Stock Auto-Reorder / Bay Requisition"] --> P2["Material Request (Purchase / Transfer)<br/>(Pending approval)"]
    end

    subgraph "2. Sourcing & Supplier Evaluation"
        P2 --> P3["Request for Quotation (RFQ)"]
        P3 --> P4["Supplier Quotation Analysis<br/>(Price, lead time, payment terms)"]
    end

    subgraph "3. Purchase Ordering & Governance"
        P4 --> P5["Purchase Order (PUR-ORD-...)"]
        P5 --> P6["Executive Dashboard Approval Workflow<br/>(PO threshold approval)"]
    end

    subgraph "4. Inward Receiving & Quality Check"
        P6 --> P7["Physical Delivery at Warehouse Dau / Branch"]
        P7 --> P8["Purchase Receipt / Goods Receipt Note (GRN)<br/>(Technical inspection, barcode labeling & bin slotting)"]
    end

    subgraph "5. Invoice Verification (3-Way Match)"
        P8 --> P9["Supplier Purchase Invoice (PUR-INV-...)<br/>(3-Way Match: PO vs Receipt vs Supplier Bill)"]
    end

    subgraph "6. Disbursement & Accounting"
        P9 --> P10["Payment Entry<br/>(Check, Bank Wire, Corporate ACH)"]
        P10 --> P11["General Ledger & Stock Ledger Settlement<br/>(AP cleared, Landed Cost posted to Inventory)"]
    end
```

### Detailed Purchase to Pay Workflow Steps:

#### Step 1: Demand Sourcing & Material Requests
1. **Automated Re-order**: When actual stock in central warehouses (`Warehouse Dau`, `San Fernando Warehouse`, `Mexico Warehouse`) or branch stores falls below safety thresholds, ERPNext automatically drafts `Material Request` records.
2. **Workshop Bay Requisition**: When technicians require non-stock parts for a specific vehicle repair, a `Material Request` linked to the Job Order is submitted.

#### Step 2: Supplier Sourcing & RFQ
1. For bulk procurements or new product introductions, a `Request for Quotation (RFQ)` is sent to authorized distributors.
2. Submitted vendor bids are entered into `Supplier Quotation` records for price and delivery lead-time comparison.

#### Step 3: Purchase Order Execution & Approval Hierarchy
1. A formal `Purchase Order` (`PUR-ORD-YYYY-#####`) is drafted specifying items, negotiated rates, delivery warehouse, and credit terms.
2. **Approval Hierarchy**:
   * POs under ₱50,000 are approved by Branch / Warehouse Managers.
   * POs exceeding ₱50,000 enter the **Executive Approvals Workflow** and appear under the **Approvals** tab of the Executive Dashboard.
   * Authorized executives review pending drafts directly via canonical desk links (`/desk/purchase-order?company=...`).

#### Step 4: Physical Receiving, QC Inspection & Bin Slotting
1. Shipments arrive at the receiving dock.
2. Storekeepers execute a `Purchase Receipt` (Goods Receipt Note):
   * Inspect tire manufacturing date (DOT codes), tread condition, and specs.
   * Validate lubricant seal integrity and viscosity ratings.
   * Count and verify physical packages against supplier delivery receipts.
3. System automatically slots items into specific warehouse `Bin Location` records (e.g. Aisle 02, Rack 04, Shelf 01, Bin B-03).
4. Physical quantity is credited into `tabBin.actual_qty`.

#### Step 5: Three-Way Matching & Purchase Invoice
1. Accounting receives the supplier's commercial sales invoice.
2. Creates a `Purchase Invoice` (`PUR-INV-YYYY-#####`).
3. **Three-Way Match Verification**:
   * Quantities on Purchase Invoice must match Purchase Receipt.
   * Pricing and terms must match original approved Purchase Order.
4. System posts provisional liabilities to Accounts Payable and credits Goods Received But Not Billed (GRIR) accrual.

#### Step 6: Supplier Disbursement & GL Clearance
1. On payment due date, Finance issues payment via check, bank wire, or online corporate transfer.
2. A `Payment Entry` is posted against the Purchase Invoice, clearing the vendor's Accounts Payable balance.

---

## 5. Financial & Accounting Operational Engine

ERPNext acts as the centralized accounting backbone for all 12 corporate entities, providing multi-company financial consolidation, cost center segregation, and tax compliance.

### A. General Ledger (GL) Accounting Matrix
The table below specifies the automated debit and credit entries generated across key operational events:

| Business Event | Debited Account (Dr) | Credited Account (Cr) | Financial Impact |
| :--- | :--- | :--- | :--- |
| **Retail POS Counter Sale (Cash)** | Cash in Hand / Cash Drawer | Sales Income (Tires/Parts)<br/>Output VAT (12%) | Increases liquid cash, records revenue and tax liability |
| **Retail POS Counter Sale (Digital/Card)** | Bank Clearing / Merchant E-Wallet | Sales Income<br/>Output VAT (12%) | Increases bank clearing assets, records revenue |
| **COGS Recognition on Sale** | Cost of Goods Sold (COGS) | Stock in Hand (Asset) | Decrements inventory asset, books direct operational cost |
| **Fleet B2B Service Sale (On Terms)** | Accounts Receivable (Customer) | Sales Income (Parts/Labor)<br/>Output VAT (12%) | Increases trade receivables, records revenue |
| **Purchase Receipt (GRN Inward)** | Stock in Hand (Inventory Asset) | Stock Received But Not Billed (GRIR) | Capitalizes physical stock into inventory valuation |
| **Purchase Invoice Booking** | Stock Received But Not Billed (GRIR)<br/>Input VAT (12%) | Accounts Payable (Supplier) | Clears temporary inventory accrual, establishes vendor liability |
| **Supplier Payment Disbursement** | Accounts Payable (Supplier) | Bank Account / Operating Cash | Liquidates vendor payable, reduces cash/bank balance |
| **Monthly Fixed Asset Depreciation** | Depreciation Expense (Operating Exp) | Accumulated Depreciation (Contra Asset) | Recognizes monthly asset wear and tear under IAS 16 |
| **Stock Shrinkage / Write-off** | Stock Adjustment / Loss Expense | Stock in Hand (Inventory Asset) | Recognizes physical inventory loss |

### B. Multi-Branch Cost Center Segregation
To calculate profitability per workshop location, every transaction is automatically tagged with its branch Cost Center:
* `Ultra MRF Dau Main - UMDM`
* `Ultra MRF Dau Annex - UMDA`
* `Ultra MRF San Fernando - UMSF`
* `Wheel Core - WC`
* `Automan Car Care Center - ACCC`
* `The Wheelhub - TWH`
* `Ultra MRF Telebastagan - UMT`
* `Corporate Overhead - ULTRA MRF`

### C. Taxation & Compliance
* **Value Added Tax (VAT)**: 12% Output VAT automatically calculated on all retail taxable sales; 12% Input VAT tracked on purchase receipts for tax credit computation.
* **Withholding Tax**: Supports Expanded Withholding Tax (EWT / BIR Form 2307) on rental, subcontracted machine shop services, and corporate fleet billing.

### D. Bank & Payment Reconciliation
* Integrated payment clearing for cash registers, credit card terminal batches, GCash merchant wallets, and online bank transfers.
* Bank Reconciliation Tool (`/desk/bank-reconciliation-tool`) matches bank statement lines against internal payment entries.

---

## 6. Inventory & Multi-Warehouse Operations Engine

### A. Multi-Tier Warehouse Network
```mermaid
graph TD
    Hub["Central Logistics Hubs<br/>(Warehouse Dau / SF / Mexico)"]
    
    subgraph "Frontline Branch Workshop Stores"
        S1["Stores - UM (Ultra MRF)"]
        S2["Stores - UMDM (Dau Main)"]
        S3["Stores - UMDA (Dau Annex)"]
        S4["Stores - UMSF (San Fernando)"]
        S5["Stores - ACCC (Automan)"]
        S6["Stores - UMT (Telebastagan)"]
    end

    subgraph "Workshop Bays & Quarantine"
        B1["Bay Fast-Moving Tire Rack"]
        B2["Lubricant Dispensing Station"]
        Q1["Damaged Cores & Warranty Quarantine"]
    end

    Hub -->|Material Transfer| S1
    Hub -->|Material Transfer| S2
    Hub -->|Material Transfer| S3
    Hub -->|Material Transfer| S4
    Hub -->|Material Transfer| S5
    Hub -->|Material Transfer| S6

    S2 --> B1
    S2 --> B2
    S2 --> Q1
```

### B. Bin Location Slotting (570 Locations)
Every physical storage rack across warehouses is tracked in `Bin Location`:
* **Aisle**: Physical warehouse corridor (e.g. `Aisle 01`, `Aisle 02`).
* **Rack**: Vertical storage shelving system.
* **Shelf**: Height tier (e.g. `Tier 1 - Ground Heavy Tires`, `Tier 4 - Light Filters`).
* **Bin**: Designated slot holding specific SKUs.

### C. Stock Valuation & Perpetual Inventory
* **Perpetual Inventory**: Every stock movement immediately updates the financial balance sheet. No manual year-end inventory valuation journal entries required.
* **Moving Average Valuation**: Real-time landed cost dynamically accounts for purchase price fluctuations, freight, import duties, and handling charges.

### D. Physical Inventory Counting & Reconciliation
* **Cycle Counting**: Periodic partial counts scheduled per item group (e.g. daily tire counts, weekly lubricant barrel soundings).
* **Stock Reconciliation Tool** (`/desk/stock-reconciliation`): Compares physical book quantity against actual counted quantity, automatically posting write-off or surplus adjustments to the General Ledger.

---

## 7. Master Reporting & Analytics Catalog

The system provides an exhaustive suite of real-time management reports accessible directly via ERPNext Desk and web dashboards:

### A. Financial & Accounting Reports
| Report Name | Desk Route | Key Operational Purpose |
| :--- | :--- | :--- |
| **General Ledger** | `/desk/general-ledger` | Comprehensive debit/credit transaction journal by account |
| **Trial Balance** | `/desk/trial-balance` | Summary of all active accounts, debits, credits, and net balances |
| **Profit and Loss Statement** | `/desk/profit-and-loss-statement` | Multi-branch revenue, gross margin, operating expenses, and net profit |
| **Balance Sheet** | `/desk/balance-sheet` | Assets, liabilities, and corporate equity snapshot |
| **Accounts Receivable Summary** | `/desk/accounts-receivable-summary` | Fleet customer aging analysis (0-30, 31-60, 61-90, 90+ days) |
| **Accounts Payable Summary** | `/desk/accounts-payable-summary` | Supplier payment schedules, aging, and upcoming vendor liabilities |
| **POS Register** | `/desk/pos-register` | Daily breakdown of all counter cash, card, and digital payment receipts |
| **Cash Flow Statement** | `/desk/cash-flow` | Operating, investing, and financing cash movements |

### B. Stock & Multi-Warehouse Reports
| Report Name | Desk Route | Key Operational Purpose |
| :--- | :--- | :--- |
| **Stock Balance** | `/desk/stock-balance` | Current on-hand quantity, valuation rate, and stock value per warehouse |
| **Warehouse Wise Stock Balance** | `/desk/warehouse-wise-stock-balance` | Matrix view of item quantities distributed across all 12 branch stores |
| **Stock Ledger** | `/desk/stock-ledger` | Complete chronological audit trail of all inward/outward inventory movements |
| **Item Shortage / Re-order** | `/desk/item-shortage-report` | Identifies SKUs below minimum safety stock requiring replenishment |
| **Stock Ageing** | `/desk/stock-ageing` | Detects slow-moving or obsolete tires and spare parts |

### C. Buying & Procurement Reports
| Report Name | Desk Route | Key Operational Purpose |
| :--- | :--- | :--- |
| **Purchase Order Analysis** | `/desk/purchase-order-analysis` | Tracking delivery completion, outstanding orders, and fulfillment rates |
| **Purchase Register** | `/desk/purchase-register` | Invoice-by-invoice log of all vendor bills, input VAT, and disbursements |
| **Item-wise Purchase History** | `/desk/item-wise-purchase-history` | Historical price trends for tire models, oil drums, and workshop tools |

### D. Sales & Commercial Reports
| Report Name | Desk Route | Key Operational Purpose |
| :--- | :--- | :--- |
| **Sales Order Analysis** | `/desk/sales-order-analysis` | Fleet order delivery and fulfillment tracking |
| **Sales Invoice Trends** | `/desk/sales-invoice-trends` | Monthly, quarterly, and annual sales trajectory by item group and branch |
| **Customer Credit Ledger** | `/desk/customer-credit-balance` | Real-time monitoring of fleet credit lines and available credit balances |

### E. Vehicle Management & Workshop Analytics
| Report Name | Desk Route | Key Operational Purpose |
| :--- | :--- | :--- |
| **Vehicle Analytics Dashboard** | `/desk/vehicle_analytics` | Interactive multi-filter dashboard (Total revenue, labor sales, tire sales, top services) |
| **Job Card Summary** | `/desk/job-card-summary` | Workshop bay job status, completion times, and mechanic allocation |
| **Mechanic Jobs** | `/desk/mechanic-jobs` | Labor hours and revenue generated per technician |
| **Customer Vehicle Service Log** | `/desk/customer-vehicle` | Complete chronological maintenance history for any license plate |

---
"""

# Replace the beginning of section 3 with new sections
old_target = "## 3. Standard Operating Procedures (SOP)"
if old_target in doc:
    doc_expanded = doc.replace(old_target, new_sections + "\n## 8. Standard Operating Procedures (SOP)")
    with open(target_repo, 'w', encoding='utf-8') as f:
        f.write(doc_expanded)
    with open(target_brain, 'w', encoding='utf-8') as f:
        f.write(doc_expanded)
    print("Successfully expanded documentation with O2C, P2P, Accounting, Financial, Inventory, and Reports!")
else:
    print("Error: Could not find target section in documentation!")
