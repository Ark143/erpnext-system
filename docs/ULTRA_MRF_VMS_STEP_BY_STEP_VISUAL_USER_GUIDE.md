# ULTRA MRF — ERPNext & VMS End-to-End Step-by-Step Visual User Guide

This manual provides a detailed, step-by-step user guide accompanied by live production screenshots for every process flow in **ERPNext v16** and the custom **Vehicle Management System (VMS)**.

---

## Table of Contents
1. [Module 1: Vehicle Management Workspace & Live Analytics](#module-1-vehicle-management-workspace--live-analytics)
2. [Module 2: Touchscreen Vehicle POS Counter Operations](#module-2-touchscreen-vehicle-pos-counter-operations)
3. [Module 3: Workshop Bay Operations & Job Order Lifecycle](#module-3-workshop-bay-operations--job-order-lifecycle)
4. [Module 4: Inventory Management & Receiver Safety Handover](#module-4-inventory-management--receiver-safety-handover)
5. [Module 5: Buying, Procurement & Executive Approvals](#module-5-buying-procurement--executive-approvals)
6. [Module 6: Fixed Assets & Automated Depreciation Accounting](#module-6-fixed-assets--automated-depreciation-accounting)

---

## Module 1: Vehicle Management Workspace & Live Analytics

The Vehicle Management Workspace is the primary command center in ERPNext Desk. When users navigate to `/desk/vehicle-management`, the system presents the live Vehicle Analytics & Performance Dashboard as the first view.

### 1.1 Workspace Top View: KPI Cards & Live Performance Charts
* **Navigation**: Navigate to `http://38.247.138.224:10017/desk/vehicle-management`.
* **What You See**:
  * **4 Real-Time KPI Cards**:
    * Total Registered Vehicles: `38,654`
    * Total Job Orders: `481`
    * Vehicle POS Invoices Count: `33`
    * Lifetime Total Revenue: `₱ 2.22 M`
  * **4 Interactive Live Charts**:
    * `VM Job Orders by Company`: Branch-by-branch distribution of workshop activity.
    * `Vehicle POS Sales by Company`: Branch-by-branch POS revenue comparison.
    * `Customer Vehicles by Make`: Donut chart breakdown (Toyota, Mitsubishi, Nissan, Ford, Isuzu, etc.).
    * `Vehicle Job Orders by Status`: Progress status breakdown (Released, Completed, In Progress, Pending Parts).

![Vehicle Management Workspace Top View](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/top_view_charts_kpi_1788339306097.png)

---

### 1.2 Workspace Quick Shortcuts & Module Cards
* **Quick Shortcuts with Live Badge Counters**:
  * `Vehicle Analytics Dashboard` (Page: `vehicle_analytics`)
  * `Vehicle POS Terminal` (Page: `vehicle_pos`)
  * `Customer Vehicles` (38,654 records)
  * `Vehicle Job Orders` (481 records)
  * `Vehicle Inspections` (476 records)
  * `Vehicle POS Invoices` (33 records)
  * `POS Invoices` (32 records)
  * `Bin Locations` (570 records)
* **Organized Module Cards**:
  * **Operations & Front Desk**: POS Terminal, POS Invoices, Job Orders, Inspections, Estimates.
  * **Vehicle Masters & Registry**: Customer Vehicle, Customer, Make, Model, Service Reminders.
  * **Reports & Analytics**: Vehicle Analytics Dashboard, POS Register, Sales Trends, Stock Balance.
  * **Inventory & Parts**: Items, Stock Entry, Compatibility, Cross References, Warehouses.

![Vehicle Management Workspace Shortcuts](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/shortcuts_module_cards_1788339339522.png)

---

### 1.3 Interactive Multi-Filter Vehicle Analytics Page
* **Navigation**: Click the `Vehicle Analytics Dashboard` shortcut or visit `/desk/vehicle_analytics`.
* **Features**:
  * Filter by **Company** (All Companies or specific branch e.g. `Ultra MRF Dau Main`).
  * Filter by **Timespan** (Last 7 Days, Last 30 Days, Year to Date).
  * Visualizes **Sales Split (Labor vs. Parts & Tires)**.
  * Highlights **Top 10 Selling Services & Labor** (PMS 20K, 4-Wheel Computerized Alignment).
  * Highlights **Top 10 Selling Tires & Wheels** (Yokohama ES32, TE37 Large PCD Mags).

![Vehicle Analytics Dashboard](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/vehicle_analytics_page_1788339634886.png)

---

## Module 2: Touchscreen Vehicle POS Counter Operations

The Vehicle POS Terminal provides an ultra-fast checkout experience for retail tire sales, parts, and express bay services. It supports camera QR login, plate number lookups, auto-locked cashier branch assignment, multi-payment options, and dual-ledger ERPNext posting.

### 2.1 Cashier Sign-In via QR Badge or Credentials
* **Navigation**: Open `http://38.247.138.224:10017/pos-terminal` (or `/desk/vehicle_pos`).
* **Step 1**: Enter Username/Password or click **📷 Scan QR Code / Camera**.
* **Step 2**: Present your printed ID badge or smartphone screen to the lens.
* **Step 3**: The system automatically verifies your active shift and loads the cash register.

![POS Terminal QR Login Modal](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/desk_pos_scan_qr_modal_1788231488356.png)

---

### 2.2 Unified POS Counter Interface, Product Cards & Auto-Locked Branch
* **Catalog vs. Ticket Unification**: On desktop and tablet POS screens, product browsing (left catalog) and the active order lines (right ticket) operate together side-by-side. The separate "Ticket" tab on the left rail has been unified under Point of Sale to eliminate redundancy.
* **Product Card Standardized Sizing & Images**:
  * **Actual Item Images**: Product cards now display the item's uploaded image (or a clean automotive category graphic as fallback) instead of an icon initial.
  * **Standardized Unit Price**: Uniform typography sized to support large numerical prices up to `₱ 9,999,999.00` cleanly without wrapping.
  * **Standardized +ADD Button**: Consistent pill dimensions (`height: 34px; min-width: 72px; padding: 0 14px; border-radius: 999px;`) across all cards.
* **Auto-Locked Branch**: The cashier's operating company is automatically detected from their linked **Employee record** (or Cashier Profile) and locked as a read-only badge (`🏢 BRANCH: ULTRA MRF`). Cashiers cannot alter the branch via a dropdown, preventing cross-branch billing errors.

![POS Terminal Counter Interface](/pos_main_screen_full_1788372031782.png)
![Product Cards with Item Images and Standard Add Buttons](/pos_catalog_cards_1788373167294.png)
![Desk Vehicle POS with In-Stock: ON](/desk_vehicle_pos_in_stock_on_1788335919298.png)

---

### 2.3 Payment Method Selection Buttons & Order Notes/Remarks
* **Payment Tender Selection**: Tap any of the quick payment buttons:
  * `💵 Cash` (Default tender)
  * `💳 Card` (Credit / Debit Card)
  * `📱 GCash` (E-Wallet)
  * `💳 Maya` (Digital Wallet)
  * `🏦 BDO` (Bank Transfer / POS Terminal)
  * `🏦 Bank Transfer` (Direct Bank Deposit)
  * *Note*: Selecting any digital/card payment automatically defaults the paid amount to match the bill total.
* **Notes / Remarks**: Enter customer purchase order numbers, bank approval codes, check numbers, or bay service notes. Saved directly into both `Vehicle POS Invoice` and ERPNext `POS Invoice`.

![POS Payment Methods and Notes](/pos_payment_methods_notes_1788372062912.png)

---

### 2.4 Real-Time Transaction History with Live Filters & Sync
* **Real-Time Data Fetch**: Clicking the **📊 Transaction History** icon on the navigation rail immediately queries the live ERPNext database.
* **Interactive Filters**:
  * Filter pills: `All`, `Today`, `This Month`
  * Date range pickers: `From Date` to `To Date` with `Apply` button.
  * Search box: Filter in-memory by customer name, vehicle plate, or invoice #.
  * `🔄 Refresh` button: Triggers on-demand synchronization with visual feedback.
* **Clickable Desk Deep Links**: Click on any invoice card (`VMSPOS-...` or `🔗 ACC-PSINV-...`) to open the record directly in ERPNext Desk.

![POS Terminal Real-Time History Screen](/pos_history_screen_1788373176463.png)

---

### 2.5 Official Cashier ID Profile Card
* Click the **👤 Cashier Profile** icon on the left navigation rail.
* Renders a clean, single official ID profile card with employee name, employee number, designation, assigned company, branch, department, reports-to manager, and vector QR code.
* Actions: `🖨️ Print Badge`, `⬇️ Download SVG`, and `📋 Copy Code`. No duplicate unstyled elements.

![Cashier ID Profile Card](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/pos_profile_badge_1788372096745.png)

---

### 2.6 Dual-Ledger Financial Posting (POS Invoice)
* Every completed POS counter transaction concurrently creates a `Vehicle POS Invoice` and auto-submits a standard ERPNext `POS Invoice` (`ACC-PSINV-YYYY-#####`).
* Immediately posts General Ledger entries (Debit Cash/Clearing, Credit Sales Income & 12% Output VAT, Debit COGS, Credit Inventory Asset) and updates stock quantities in `tabBin`.

![Submitted POS Invoice in Desk](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/pos_invoice_submitted_1788368405271.png)

---

## Module 3: Workshop Bay Operations & Job Order Lifecycle

Automotive workshop operations link vehicle intake, digital inspections, estimating, technician bay dispatch, and parts consumption.

### 3.1 Customer Vehicle Registry (38,654 Vehicles)
* **Navigation**: Open `/desk/customer-vehicle`.
* Search by plate number. Displays make, model, year, chassis/VIN, engine number, and registered customer account.
* Space normalization hooks automatically sanitize customer strings to prevent checkout validation errors.

![Customer Vehicle Form](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/customer_vehicle_form_1788368486364.png)

---

### 3.2 Multi-Point Electronic Vehicle Inspection
* **Navigation**: Open `/desk/vehicle-inspection`.
* Service advisors select an inspection template (25-point, 50-point, or Tire QC).
* Evaluate tire tread depth, brake pads, battery health, and fluid levels.
* Snap vehicle intake photos directly through the camera and attach to the record.

![Electronic Vehicle Inspection Form](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/vehicle_inspection_form_1788368513066.png)

---

### 3.3 Vehicle Job Order Bay Dispatch & Technician Allocation
* **Navigation**: Open `/desk/vehicle-job-order`.
* Service advisors dispatch jobs to bay technicians, tracking:
  * **Labor tasks** (`Job Order Service Item`): PMS, alignment, balancing, camber adjustment.
  * **Parts consumption** (`Job Order Part Item`): Tires, filters, motor oils.
* Status progression: `Draft` $\rightarrow$ `In Progress` $\rightarrow$ `Pending Parts` $\rightarrow$ `Completed` $\rightarrow$ `Released`.

![Vehicle Job Orders List in Desk](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/vjo_ultra_mrf_desk_1788337950096.png)

---

## Module 4: Inventory Management & Receiver Safety Handover

Warehouse controls manage 570 bin locations, inter-branch transfers, and mandatory receiver verification to eliminate unauthorized withdrawals.

### 4.1 Stock Entry (Material Issue) Safety Verification Check
* **Navigation**: Open `/desk/stock-entry` and create a `Material Issue`.
* The **Receiver Verification & Handover Safety Check** box appears at the top.
* Click **📷 Scan Receiver QR & Photo**:
  * **Step 1**: Point the device camera at the recipient technician's QR badge or smartphone screen.
  * **Step 2**: Snap a photo proof of the physical handover.
* The transaction is marked `VERIFIED` with timestamp and photo evidence. Submissions without verification are blocked by the system.

![Stock Entry Receiver Verification Safety Box](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/stock_entry_receiver_verification_1788368390547.png)

---

### 4.2 Employee ID Badges with QR Code
* Every technician has an official employee ID badge generated directly from ERPNext Desk (`/desk/employee` $\rightarrow$ **🖨️ Print QR Badge**) or the POS Terminal.
* The badge features the ULTRA MRF corporate header, employee photo/avatar, designation, department, employee ID, and high-resolution QR code.

![Official Employee QR ID Badge](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/employee_qr_badge_1788367919149.png)

---

## Module 5: Buying, Procurement & Executive Approvals

Governs commercial tire contracts, spare part purchases, and multi-branch management approvals.

### 5.1 Purchase Orders & 3-Way Matching
* **Navigation**: Open `/desk/purchase-order`.
* Draft commercial purchase orders specifying item codes, quantities, agreed supplier rates, and warehouse destination.
* Compares against Goods Receipts (GRN) and Supplier Invoices before disbursements.

![Purchase Order Form](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/pur_ord_2026_00010_form_1788337528286.png)

---

### 5.2 Executive Dashboard Approvals Tab with Direct Desk Routing
* **Navigation**: Open `http://38.247.138.224:10017/executive-dashboard` and click the **Approvals** tab.
* Real-time cards summarize pending drafts across 9 DocTypes.
* Click **View all [DocType]s in Desk $\rightarrow$** to open the canonical desk list view pre-filtered to the operating company (e.g. `/desk/purchase-order?company=...`).

![Executive Dashboard Approvals Tab](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/approvals_tab_1788337848963.png)

---

## Module 6: Fixed Assets & Automated Depreciation Accounting

Capitalizes heavy automotive workshop machinery across all service centers with automated straight-line depreciation accounting under IAS 16.

### 6.1 Workshop Machinery Asset Master (10 Capitalized Machines)
* **Navigation**: Open `/desk/asset`.
* Capitalized machines include 3D Wheel Aligners, Tire Changers, Dynamic Balancers, 2-Post Lifts, and AC Recovery Stations.
* Tracks asset category, purchase value, location, and maintenance logs.

![Fixed Asset Master Form](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/asset_form_top_1788312156436.png)

---

### 6.2 Automated Monthly Straight-Line Depreciation Schedule
* Open the **Depreciation Schedule** tab on any asset record.
* ERPNext calculates exact monthly depreciation amounts over the asset's useful life.
* The system automatically generates and posts monthly General Ledger journal entries crediting Accumulated Depreciation.

![Fixed Asset Straight-Line Depreciation Schedule](file:///C:/Users/josem/.gemini/antigravity-ide/brain/ad9d29ca-966c-454f-b5c8-9ae935c95822/asset_depreciation_schedule_scrolled_1788312168154.png)
