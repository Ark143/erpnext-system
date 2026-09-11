# -*- coding: utf-8 -*-
"""
Full Business Blueprint Generator for ULTRA MRF: Automan
System: ERPNext v16 Enterprise with Vehicle Management System (VMS) & Consolidated Multi-Company Suite
Author / Lead Architect: Jose Mangiliman Jr.
Timeline: 45 Implementation Days + 10 Days Change Request
"""

import os, docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_styled_table(doc, headers, data, col_widths=None, header_bg="0f172a", zebra=True):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], header_bg)
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=160, right=160)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(9.5)
            run.font.name = "Arial"

    # Data Rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "f8fafc" if (zebra and row_idx % 2 == 1) else "ffffff"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=140, right=140)
            p = row_cells[col_idx].paragraphs[0]
            for run in p.runs:
                run.font.size = Pt(9.0)
                run.font.color.rgb = RGBColor(30, 41, 59)
                run.font.name = "Arial"

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = width

    doc.add_paragraph()
    return table

def add_callout_box(doc, title, text_lines, box_type="info"):
    colors = {
        "info": {"border": "0284c7", "bg": "f0f9ff", "title": "0369a1"},
        "success": {"border": "16a34a", "bg": "f0fdf4", "title": "15803d"},
        "warning": {"border": "d97706", "bg": "fffbeb", "title": "b45309"},
        "dark": {"border": "0f172a", "bg": "f8fafc", "title": "0f172a"}
    }
    cfg = colors.get(box_type, colors["info"])
    
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, cfg["bg"])
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    p = cell.paragraphs[0]
    r_title = p.add_run(f"📌 {title}\n")
    r_title.bold = True
    r_title.font.size = Pt(10)
    r_title.font.name = "Arial"
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    
    for line in text_lines:
        r_line = p.add_run(f"• {line}\n" if not line.startswith("  ") else f"{line}\n")
        r_line.font.size = Pt(9)
        r_line.font.name = "Arial"
        r_line.font.color.rgb = RGBColor(51, 65, 85)
        
    doc.add_paragraph()

def build_docx_and_md():
    doc = Document()
    
    # Page setup - Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # ── COVER PAGE ──
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_pre = p_pre.add_run("ULTRA MRF GROUP · AUTOMAN CAR CARE CENTER")
    r_pre.font.size = Pt(9)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph("\n\n")

    p_main_title = doc.add_paragraph()
    p_main_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_type = p_main_title.add_run("ENTERPRISE SOFTWARE ARCHITECTURE & IMPLEMENTATION\n")
    r_type.font.size = Pt(13)
    r_type.font.bold = True
    r_type.font.color.rgb = RGBColor(2, 132, 199)

    r_doc_title = p_main_title.add_run("BUSINESS BLUEPRINT DOCUMENT\n")
    r_doc_title.font.size = Pt(26)
    r_doc_title.font.bold = True
    r_doc_title.font.color.rgb = RGBColor(15, 23, 42)

    r_client = p_main_title.add_run("ULTRA MRF: AUTOMAN\n")
    r_client.font.size = Pt(20)
    r_client.font.bold = True
    r_client.font.color.rgb = RGBColor(30, 41, 59)

    r_sub = p_main_title.add_run("Enterprise ERPNext v16 Implementation with Vehicle Management System (VMS) & Consolidated Multi-Company Suite")
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph("\n\n\n")

    # Cover Meta Box
    meta_box = doc.add_table(rows=5, cols=2)
    meta_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_items = [
        ("Prepared For:", "ULTRA MRF / Automan Car Care Center Management"),
        ("Prepared By:", "Jose Mangiliman Jr. — Lead ERP Solutions Architect & Consultant"),
        ("Implementation Scope:", "Day 45 (Standard Delivery) + 10 Days (Change Request Buffer) = 55 Days Total"),
        ("Date of Document:", "11th September 2026"),
        ("Release Version:", "Release v1.0 (Production Blueprint Baseline)")
    ]
    for idx, (label, val) in enumerate(meta_items):
        r_c1 = meta_box.rows[idx].cells[0]
        r_c2 = meta_box.rows[idx].cells[1]
        r_c1.text = label
        r_c2.text = val
        set_cell_background(r_c1, "f1f5f9")
        set_cell_background(r_c2, "ffffff")
        set_cell_margins(r_c1, 80, 80, 120, 120)
        set_cell_margins(r_c2, 80, 80, 120, 120)
        r_c1.paragraphs[0].runs[0].font.bold = True
        r_c1.paragraphs[0].runs[0].font.size = Pt(9.5)
        r_c2.paragraphs[0].runs[0].font.size = Pt(9.5)
        r_c1.width = Inches(2.2)
        r_c2.width = Inches(4.3)

    doc.add_paragraph("\n\n")
    p_conf = doc.add_paragraph()
    p_conf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_conf = p_conf.add_run("CONFIDENTIAL & PROPRIETARY\nThe materials presented in this document contain trade secrets and architectural specifications of ULTRA MRF, Automan Car Care Center, and Jose Mangiliman Jr. No part of this document may be reproduced without prior written authorization.")
    r_conf.font.size = Pt(8.5)
    r_conf.font.color.rgb = RGBColor(148, 163, 184)

    doc.add_page_break()

    # ── SECTION 1: CHANGE HISTORY ──
    h1 = doc.add_heading("1. CHANGE HISTORY & DOCUMENT CONTROL", level=1)
    h1.paragraph_format.space_before = Pt(12)
    
    change_headers = ["Version", "Date", "Author", "Description of Change"]
    change_data = [
        ["v1.0", "11 Sep 2026", "Jose Mangiliman Jr.", "Initial comprehensive Business Blueprint for ULTRA MRF: Automan ERPNext v16 + VMS rollout."],
        ["v1.1", "11 Sep 2026", "Jose Mangiliman Jr.", "Incorporated Hierarchical Exploded Cash Flow (Year-Month-Day), 30/60/90 Day AR/AP Aging, and Multi-Company Consolidation."]
    ]
    create_styled_table(doc, change_headers, change_data, [Inches(1.0), Inches(1.2), Inches(1.8), Inches(2.5)])

    # ── SECTION 2: INTRODUCTION ──
    doc.add_heading("2. PROJECT INTRODUCTION & EXECUTIVE SUMMARY", level=1)
    
    p = doc.add_paragraph("This document serves as the formal Business Blueprint (BBP) for the end-to-end design, configuration, customization, and rollout of ERPNext v16 integrated with the specialized Vehicle Management System (VMS) across ULTRA MRF, Automan Car Care Center, and its group of 13 operating companies.")
    
    p = doc.add_paragraph("Automan Car Care Center and ULTRA MRF operate a multi-branch automotive service, tire distribution, preventive maintenance, spare parts trading, and fleet care enterprise. To achieve operational excellence, real-time inventory precision, automated workshop throughput, and consolidated multi-entity financial clarity, this project transitions the enterprise from fragmented manual logs into a unified, high-performance ERPNext v16 architecture.")

    doc.add_heading("2.1 Acceptance & Signatory of Specification", level=2)
    p = doc.add_paragraph("Signature on this Business Blueprint indicates formal acceptance of the system requirements, functional scope, process flows, integration points, and delivery schedule. Post-sign-off scope enhancements are managed through the 10-day Change Request procedure.")

    sign_headers = ["Role / Representation", "Name", "Position / Organization", "Signature", "Date"]
    sign_data = [
        ["Lead Solutions Architect", "Jose Mangiliman Jr.", "Lead ERP Solutions Architect", "", ""],
        ["Project Sponsor", "Management Executive", "Managing Director / ULTRA MRF", "", ""],
        ["Operations Lead", "Workshop Operations Manager", "Automan Car Care Center", "", ""],
        ["Finance Lead", "Chief Financial Controller", "ULTRA MRF Group", "", ""]
    ]
    create_styled_table(doc, sign_headers, sign_data, [Inches(1.5), Inches(1.4), Inches(1.6), Inches(1.0), Inches(1.0)])

    doc.add_heading("2.2 Purpose of Document", level=2)
    p = doc.add_paragraph("The primary purpose of this Blueprint is to:")
    add_callout_box(doc, "Blueprint Core Objectives", [
        "Standardize workshop workflows from Vehicle Intake, Inspection, Estimate, Job Order (VJO) to Point of Sale (POS) and Release.",
        "Establish multi-company financial consolidation across 13 operating entities with dynamic P&L, Balance Sheet, and General Ledger audit.",
        "Deploy the real-time Hierarchical Exploded Cash Flow Statement (Daily, Monthly, Yearly) with horizontal drilldown.",
        "Implement Terms-based Accounts Receivable (AR) & Accounts Payable (AP) Aging analysis across 30, 60, 90, 90+ day buckets.",
        "Enforce strict serialized part tracking, bin location routing, receiver safety checks, and multi-branch warehouse transfers.",
        "Ensure full Philippine BIR Tax compliance (BIR 2307, Sales Book, Purchases Book, Cash Receipts/Disbursements, VAT Returns)."
    ], "info")

    doc.add_heading("2.3 Stakeholder & Intended Audience Matrix", level=2)
    aud_headers = ["Stakeholder Group", "Primary Roles", "Key Responsibilities in ERPNext v16"]
    aud_data = [
        ["Executive Management", "Board / General Managers", "Review consolidated financial health, cash flow projections, branch P&L, and AR/AP aging."],
        ["Workshop Service Team", "Service Advisors, Mechanics, QA", "Execute Vehicle Inspections, Estimates, Job Orders, part issues, and vehicle release."],
        ["Cashier & POS Staff", "Cashiers, Shift Supervisors", "Conduct shift opening/closing, invoice encoding, multi-mode payment collection (Cash, Card, GCash)."],
        ["Warehouse & Parts Team", "Stock Custodians, Parts Managers", "Stock entry receiving, bin location assignments, item compatibility checks, and physical count audits."],
        ["Accounting & Finance", "Accountants, Bookkeepers, Auditors", "General ledger audit, bank reconciliation, BIR tax journal reporting, and vendor payment disbursement."],
        ["System Administration", "Jose Mangiliman Jr. / IT Team", "Role-based access control, server script maintenance, data backups, and technical infrastructure."]
    ]
    create_styled_table(doc, aud_headers, aud_data, [Inches(1.8), Inches(1.8), Inches(2.9)])

    doc.add_heading("2.4 Multi-Company Enterprise Landscape (13 Entities)", level=2)
    p = doc.add_paragraph("The enterprise architecture natively consolidates 13 operating companies under unified Chart of Accounts and intercompany transaction controls:")
    
    co_headers = ["#", "Company Name", "Code / Abbr", "Primary Business Domain", "Default Currency"]
    co_data = [
        ["1", "Automan Car Care Center", "ACCC", "Automotive Service, Mechanical Repair, Tire Center", "PHP (₱)"],
        ["2", "Ultra MRF Dau Main", "UMDM", "Central Hub, Fleet Maintenance, Parts Wholesale", "PHP (₱)"],
        ["3", "Ultra MRF San Fernando", "UMSF", "Branch Service Center & Quick Lube Operations", "PHP (₱)"],
        ["4", "Ultra MRF Telebastagan", "UMTB", "Automotive Care, Tire Fitting, Alignment Center", "PHP (₱)"],
        ["5", "Ultra MRF Telebastagan 2", "UMT2", "Commercial Vehicle & Heavy Fleet Maintenance", "PHP (₱)"],
        ["6", "Ultra MRF Dau Annex", "UMDA", "Parts Warehousing & Overflow Distribution", "PHP (₱)"],
        ["7", "The Wheelhub", "TWHB", "Premium Wheel, Rim & Specialty Tire Retail", "PHP (₱)"],
        ["8", "Wheel Core", "WCRL", "Wheel Distribution & Wholesale Trading", "PHP (₱)"],
        ["9", "Ultra MRF", "UMRF", "Holding & Corporate Management Entity", "PHP (₱)"],
        ["10", "Ultra MRF Warehouse Dau", "UMWD", "Central Logistics & Regional Part Depot", "PHP (₱)"],
        ["11", "Ultra MRF Mexico Warehouse", "UMMW", "Bulk Tire, Lubricant & Battery Storage", "PHP (₱)"],
        ["12", "San Fernando Warehouse", "SFWH", "Regional Warehouse & Subcontracting Depot", "PHP (₱)"],
        ["13", "ULTRA MRF Group (Consolidated)", "UMGC", "Virtual Top-Level Consolidated Reporting Entity", "PHP (₱)"]
    ]
    create_styled_table(doc, co_headers, co_data, [Inches(0.4), Inches(2.2), Inches(1.0), Inches(2.2), Inches(0.7)])

    doc.add_page_break()

    # ── SECTION 3: ABBREVIATIONS ──
    doc.add_heading("3. ABBREVIATIONS & ENTERPRISE GLOSSARY", level=1)
    abbr_headers = ["Abbreviation", "Definition / Expansion", "Abbreviation", "Definition / Expansion"]
    abbr_data = [
        ["VMS", "Vehicle Management System", "VJO", "Vehicle Job Order"],
        ["VE", "Vehicle Estimate", "VI", "Vehicle Inspection"],
        ["VIN", "Vehicle Identification Number", "POS", "Point of Sale"],
        ["COA", "Chart of Accounts", "GL", "General Ledger"],
        ["P&L", "Profit and Loss Statement", "BS", "Balance Sheet"],
        ["AR", "Accounts Receivable", "AP", "Accounts Payable"],
        ["DII", "Days in Inventory", "MIL", "Minimum Inventory Level"],
        ["BOM", "Bill of Materials", "SKU", "Stock Keeping Unit"],
        ["SLE", "Stock Ledger Entry", "PCount", "Physical Inventory Count"],
        ["BIR", "Bureau of Internal Revenue", "EWT", "Expanded Withholding Tax"],
        ["O2C", "Order to Cash Workflow", "P2P", "Procure to Pay Workflow"],
        ["MOP", "Mode of Payment", "SoD", "Segregation of Duties"],
        ["RBAC", "Role-Based Access Control", "UAT", "User Acceptance Testing"]
    ]
    create_styled_table(doc, abbr_headers, abbr_data, [Inches(1.1), Inches(2.1), Inches(1.1), Inches(2.2)])

    # ── SECTION 4: FLOWCHART LEGENDS ──
    doc.add_heading("4. PROCESS FLOW NOTATION & FLOWCHART LEGENDS", level=1)
    flow_headers = ["Symbol", "Element Type", "Description & Usage in ERPNext v16 / VMS"]
    flow_data = [
        ["[ START / END ]", "Terminal", "Represents process initiation (e.g. Vehicle Intake) or terminal completion (e.g. Payment Released)."],
        ["[ PROCESS ]", "Operational Step", "A distinct action executed by a user (e.g. Service Advisor encodes Estimate lines)."],
        ["[ AUTOMATION ]", "System Trigger", "An automated script execution (e.g. Auto-creation of Stock Ledger Entry, GL Journal posting)."],
        ["[ DECISION ]", "Condition / Gate", "A branching validation point (e.g. Is customer estimate approved? Is stock available in bin?)."],
        ["[ DOCUMENT ]", "DocType / Record", "A transactional record in ERPNext (e.g. Sales Invoice, Purchase Order, Vehicle Job Order)."],
        ["[ DATA STORE ]", "Database Entity", "Persistent relational tables (e.g. TabGL Entry, TabBin, TabCustomer Vehicle)."]
    ]
    create_styled_table(doc, flow_headers, flow_data, [Inches(1.5), Inches(1.5), Inches(3.5)])

    # ── SECTION 5: BUSINESS REQUIREMENTS ──
    doc.add_heading("5. BUSINESS REQUIREMENTS & SYSTEM ARCHITECTURE", level=1)
    
    doc.add_heading("5.1 Scope of Requirements & Engagement Parameters", level=2)
    add_callout_box(doc, "Engagement Parameters (45 + 10 Days)", [
        "Standard Implementation Lifecycle: 45 Working Days (Discovery, Build, Data Migration, Testing, Training, Cutover).",
        "Change Request (CR) Contingency Buffer: 10 Working Days dedicated to post-discovery scope expansions and custom enhancements.",
        "Total Dedicated Delivery Window: 55 Working Days.",
        "Target Concurrent System Users: Up to 500 active concurrent operators across 13 branches and warehouses.",
        "Primary Deployment Target: Cloud VPS Server (Linux Ubuntu 24.04, Dockerized ERPNext v16, Caddy SSL Reverse Proxy).",
        "Data Sovereignty: High-availability automated nightly database dumps and persistent file storage."
    ], "success")

    doc.add_heading("5.2 VMS & ERPNext v16 Functional Modules", level=2)
    p = doc.add_paragraph("The solution encompasses seven core operational domains:")
    
    p = doc.add_paragraph("1. Workshop Operations & VMS: Complete vehicle lifecycle tracking from intake, preliminary inspection, quotation/estimate, formal Vehicle Job Order (VJO), technician assignment, parts allocation, repair execution, quality assurance, to gate pass release.")
    p = doc.add_paragraph("2. Point of Sale (POS) & Cashier Shifts: High-speed POS interface designed for automotive express counters, shift opening balances, multi-cashier shift management, card/cash/e-wallet settlements, and thermal receipt printing.")
    p = doc.add_paragraph("3. Multi-Warehouse & Bin Inventory Logistics: Real-time stock visibility across all 13 entities, automated bin location routing, item-vehicle compatibility matching, cross-reference lookup, receiver safety checks, and physical count (PCount) reconciliation.")
    p = doc.add_paragraph("4. Multi-Company Financial Accounting: Dynamic consolidated P&L, Balance Sheet, and GL Explorer with real-time currency conversion, branch-wise comparison, and single-click drill-down to underlying vouchers.")
    p = doc.add_paragraph("5. Hierarchical Exploded Cash Flow: Real-time cash positioning with on-demand drilldown from Year ➔ Month ➔ Individual Operating Days across cash inflows, disbursements, and net cash flow.")
    p = doc.add_paragraph("6. AR / AP Aging Analysis: Terms-based aging calculations tracking customer receivables and supplier obligations across standard 30, 60, 90, 90+ day buckets based on actual credit terms and invoice due dates.")
    p = doc.add_paragraph("7. Philippine BIR Tax Compliance: Native generation of BIR Form 2307 withholding certificates, Sales Book, Purchases Book, Cash Receipts Journal, Cash Disbursements Journal, General Journal, and VAT Return 2550.")

    doc.add_page_break()

    # ── SECTION 6: MASTER DATA ──
    doc.add_heading("6. MASTER DATA GOVERNANCE & STRUCTURE", level=1)
    
    doc.add_heading("6.1 Master Data Catalogs", level=2)
    md_headers = ["Master Data Entity", "Key Attributes / Fields", "Validation & Business Rules"]
    md_data = [
        ["Customer Vehicle", "Plate No, VIN, Chassis No, Engine No, Make, Model, Year, Color, Fuel, Mileage", "Plate Number and VIN must be strictly unique. Links directly to Customer Account."],
        ["Item / Spare Part", "Item Code, Part No, Item Group, Brand, Stock UOM, Valuation Rate, Default Bin", "Enforces serialized or batch tracking where required. Barcode scan-enabled."],
        ["Item Compatibility", "Item Code, Vehicle Make, Vehicle Model, Year From, Year To, Engine Type", "Filters allowable parts during estimate and job order selection to prevent wrong parts installation."],
        ["Bin Location", "Bin Name, Warehouse, Rack, Shelf, Bin Code, Capacity Qty", "Automatically assigned during Stock Entry / Purchase Receipt for efficient picking."],
        ["Chart of Accounts", "Account Code, Account Name, Root Type, Account Type, Currency, Company", "Unified multi-company chart of accounts with standard 5-digit BIR compliant naming."],
        ["Supplier / Vendor", "Supplier Name, Tax ID (TIN), Address, Payment Terms, Bank Details, EWT Rate", "Required for 2307 generation and purchase order procurement."],
        ["Employee / Technician", "Employee ID, Full Name, Designation, Department, Branch, Skill Level, QR Badge", "QR-enabled employee badges for rapid technician tagging on Job Orders."]
    ]
    create_styled_table(doc, md_headers, md_data, [Inches(1.6), Inches(2.6), Inches(2.3)])

    # ── SECTION 7: DETAILED BUSINESS PROCESS FLOWS ──
    doc.add_heading("7. CORE BUSINESS PROCESS FLOWS & OPERATIONAL RUNBOOKS", level=1)

    doc.add_heading("7.1 Process 1: Vehicle Intake, Inspection & Estimate (Quotation)", level=2)
    add_callout_box(doc, "Vehicle Intake & Estimate Runbook", [
        "Step 1: Vehicle arrives at Automan / ULTRA MRF service bay. Service Advisor scans plate number or searches VIN.",
        "Step 2: If vehicle is new, Service Advisor registers Customer Vehicle record with Make, Model, Fuel, and Mileage.",
        "Step 3: Service Advisor conducts Vehicle Inspection (VI) recording exterior body condition, tire tread depth, battery health, and customer complaints.",
        "Step 4: System auto-populates Vehicle Estimate (VE) with recommended service packages, labor charges, and spare parts filtered by Item-Vehicle Compatibility.",
        "Step 5: Customer reviews and approves Estimate via digital signature or physical printout.",
        "Step 6: On customer confirmation, Estimate is converted to an active Vehicle Job Order (VJO) with 1 click."
    ], "info")

    doc.add_heading("7.2 Process 2: Vehicle Job Order (VJO) Execution & Part Allocation", level=2)
    add_callout_box(doc, "VJO Execution Runbook", [
        "Step 1: Job Order is dispatched to Lead Technician. Technician badge is scanned via QR Code reader.",
        "Step 2: Parts requisition triggers automated warehouse check. Parts are reserved from branch Stock.",
        "Step 3: Parts Custodian executes Material Issue against VJO, moving parts from Bin Location to Work-in-Progress (WIP).",
        "Step 4: Technician completes mechanical/electrical service tasks and logs completion timestamps.",
        "Step 5: Quality Assurance (QA) Inspector executes final road test checklist and signs off VJO as 'Ready for Billing'."
    ], "dark")

    doc.add_heading("7.3 Process 3: Point of Sale (POS) Billing & Cashier Shift Governance", level=2)
    add_callout_box(doc, "Cashier Shift & Billing Protocol", [
        "Step 1: Cashier opens shift by entering cash float opening balance in POS Opening Voucher.",
        "Step 2: Cashier pulls 'Ready for Billing' VJO or encodes direct OTC counter sale.",
        "Step 3: System validates stock availability, applies pre-configured pricing, and computes VAT/discounts.",
        "Step 4: Payment is collected via multi-mode split: Cash, Credit Card, GCash, Maya, Bank Transfer, or Accounts Receivable Charge.",
        "Step 5: POS Invoice is submitted, auto-creating Sales Invoice, Stock Ledger Entry, and General Ledger debit/credit postings.",
        "Step 6: Shift Closing: Cashier counts physical cash, prints Shift Summary report, and submits POS Closing Voucher for Supervisor audit."
    ], "success")

    doc.add_heading("7.4 Process 4: Procure-to-Pay (P2P) & Automated Stock Entry Receiving", level=2)
    p = doc.add_paragraph("Material replenishment is triggered by Minimum Inventory Level (MIL) alerts. Purchase Orders (PO) submitted to vendors require three-way matching against Purchase Receipt (PR) and Supplier Purchase Invoice (PI).")
    p = doc.add_paragraph("Receiver Safety Check Customization: Enforces that receiving staff must confirm package integrity, part verification, and bin location assignment before Stock Ledger Entry is permanently committed.")

    doc.add_heading("7.5 Process 5: Multi-Branch Transfers & Physical Count (PCount) Audit", level=2)
    p = doc.add_paragraph("Inter-branch stock transfers operate under structured 'In-Transit' governance: Releasing branch issues Stock Entry (Material Transfer), moving goods to 'In-Transit Warehouse'. Receiving branch verifies physical parts, scans serials/barcodes, and completes receipt into local bins.")
    p = doc.add_paragraph("Physical Inventory Count (PCount) module allows scheduled cycle counts and blind audits. Discrepancies between system on-hand balances and physical counts generate automatic Stock Reconciliation vouchers subject to General Manager sign-off.")

    doc.add_page_break()

    # ── SECTION 8: CONSOLIDATED FINANCIALS & CASH FLOW ──
    doc.add_heading("8. MULTI-COMPANY FINANCIAL SUITE & CASH FLOW ARCHITECTURE", level=1)

    doc.add_heading("8.1 Hierarchical Exploded Cash Flow Statement (Daily, Monthly, Yearly)", level=2)
    p = doc.add_paragraph("A core innovation in the Automan ERPNext v16 deployment is the live Exploded Horizontal Cash Flow engine:")
    add_callout_box(doc, "Exploded Cash Flow Engine Architecture", [
        "Hierarchical Structure: Rows represent fixed financial activities (Opening Cash Balance, Operating Inflows, Operating Outflows, Net Cash Flow, Closing Cash Balance).",
        "Horizontal Time Axis: Columns dynamically represent time periods (Years ➔ Months ➔ Days).",
        "Interactive Drilldown: Clicking any Year expands into 12 constituent Months; clicking any Month explodes into all individual operating Days.",
        "Scoping Control: Operators can view Consolidated Group totals or isolate any single operating company with instantaneous recalculation.",
        "Excel Export & Print: Full formatted .xlsx workbooks and clean landscape print stylesheets built natively into the console."
    ], "success")

    doc.add_heading("8.2 AR & AP Aging Analysis Engine (Terms & Credit Date Based)", level=2)
    p = doc.add_paragraph("Unlike legacy systems that calculate aging based solely on invoice posting date, the Automan ERPNext engine calculates overdue aging based on agreed credit terms (e.g. Net 30, Net 60) and actual payment due dates:")
    
    aging_headers = ["Aging Bracket", "Days Range", "Operational Significance & Credit Control Action"]
    aging_data = [
        ["Current / Not Due", "≤ 0 Days Overdue", "Invoices within agreed credit term grace period. No collection action required."],
        ["1 – 30 Days Overdue", "1 to 30 Days", "First notice reminder issued to customer/fleet account. Standard follow-up."],
        ["31 – 60 Days Overdue", "31 to 60 Days", "Second formal demand letter. Account flagged for credit hold on new work orders."],
        ["61 – 90 Days Overdue", "61 to 90 Days", "Critical collection escalation. Service suspension and direct management outreach."],
        ["90+ Days Overdue", "91+ Days", "Default risk category. Legal recovery review and bad debt provisioning."]
    ]
    create_styled_table(doc, aging_headers, aging_data, [Inches(1.8), Inches(1.5), Inches(3.2)])

    doc.add_heading("8.3 Philippine BIR Tax Compliance & Journals", level=2)
    p = doc.add_paragraph("The accounting engine includes out-of-the-box BIR compliance:")
    p = doc.add_paragraph("• BIR Form 2307: Automated generation of Certificate of Creditable Tax Withheld at Source for corporate customers and vendor disbursements.")
    p = doc.add_paragraph("• Statutory Journal Books: Real-time exportable Sales Journal (Sales Book), Purchases Journal (Purchases Book), Cash Receipts Journal (CRJ), Cash Disbursements Journal (CDJ), and General Journal (GJ).")
    p = doc.add_paragraph("• VAT Return 2550: Automated tracking of Output VAT on sales and Input VAT on purchases with tax relief summaries.")

    doc.add_page_break()

    # ── SECTION 9: IMPLEMENTATION METHODOLOGY & TIMELINE ──
    doc.add_heading("9. IMPLEMENTATION METHODOLOGY, TIMELINE & CHANGE MANAGEMENT", level=1)

    doc.add_heading("9.1 45-Day Implementation + 10-Day Change Request Schedule", level=2)
    p = doc.add_paragraph("The project is executed across five structured phases totaling 45 standard implementation days plus a 10-day dedicated Change Request buffer (55 Days Total):")

    time_headers = ["Phase", "Timeline", "Key Deliverables & Milestones", "Responsible Lead"]
    time_data = [
        ["Phase 1: Discovery & Architecture", "Day 1 – Day 7 (7 Days)", "Business blueprint sign-off, Chart of Accounts mapping, multi-company hierarchy definition.", "Jose Mangiliman Jr."],
        ["Phase 2: Core Build & VMS Customization", "Day 8 – Day 22 (15 Days)", "DocType creation, VJO/POS workflows, Server Scripts, Client Scripts, Receipt print formats.", "Jose Mangiliman Jr."],
        ["Phase 3: Financials & Reports Build", "Day 23 – Day 32 (10 Days)", "Exploded Cash Flow engine, AR/AP Aging, BIR tax journals, Consolidated P&L / Balance Sheet.", "Jose Mangiliman Jr."],
        ["Phase 4: Data Migration & UAT", "Day 33 – Day 40 (8 Days)", "Master data upload (Items, Vehicles, Customers, Opening GL balances), user acceptance testing.", "Jose Mangiliman Jr. & Client"],
        ["Phase 5: Training, Cutover & Go-Live", "Day 41 – Day 45 (5 Days)", "End-user workshop training, shift cashier dry runs, production cutover, live deployment.", "Jose Mangiliman Jr."],
        ["Phase 6: Change Request (CR) Window", "Day 46 – Day 55 (10 Days)", "Dedicated scope enhancement window for client change requests, fine-tuning, and post-go-live stabilization.", "Jose Mangiliman Jr."]
    ]
    create_styled_table(doc, time_headers, time_data, [Inches(1.8), Inches(1.3), Inches(2.4), Inches(1.0)])

    doc.add_heading("9.2 Technology Stack & Hosting Infrastructure", level=2)
    tech_headers = ["Architecture Layer", "Technology Component", "Specification & Deployment Detail"]
    tech_data = [
        ["Enterprise Core", "ERPNext v16 (Frappe Framework)", "Python 3.11+, MariaDB / PostgreSQL database backend, Redis cache."],
        ["Custom App Layer", "Vehicle Management System (VMS)", "Integrated Frappe app with custom DocTypes, Server Scripts, and Client Scripts."],
        ["Frontend UI", "HTML5 / Vanilla CSS / SheetJS", "Ultra-fast, zero-dependency responsive interface with dark/light themes and Excel export."],
        ["Server Infrastructure", "Cloud VPS (Linux Ubuntu)", "38.247.138.224:10017 with Caddy SSL Reverse Proxy and automated containerized backups."],
        ["Security & Audit", "Role-Based Access Control (RBAC)", "Multi-level permission manager, Super User audit logs, and secure REST APIs."]
    ]
    create_styled_table(doc, tech_headers, tech_data, [Inches(1.6), Inches(2.2), Inches(2.7)])

    doc.add_heading("9.3 Formal Change Management Protocol", level=2)
    p = doc.add_paragraph("Any functional alteration or additional workflow requested beyond the signed blueprint is formally processed through a Change Request (CR) document detailing technical impact, effort estimation, and delivery milestone within the 10-day CR buffer.")

    # ── SECTION 10: SIGN-OFF ──
    doc.add_heading("10. BLUEPRINT ACCEPTANCE & AUTHORIZATION", level=1)
    p = doc.add_paragraph("By signing below, the authorized executive stakeholders of ULTRA MRF and Automan Car Care Center approve this Business Blueprint as the definitive baseline for system configuration, deployment, and acceptance testing.")

    doc.add_paragraph("\n")
    final_sign = doc.add_table(rows=3, cols=2)
    final_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    c1 = final_sign.rows[0].cells[0]
    c2 = final_sign.rows[0].cells[1]
    c1.text = "FOR THE CONSULTING ARCHITECT:"
    c2.text = "FOR ULTRA MRF / AUTOMAN:"
    set_cell_background(c1, "f1f5f9")
    set_cell_background(c2, "f1f5f9")
    c1.paragraphs[0].runs[0].font.bold = True
    c2.paragraphs[0].runs[0].font.bold = True
    
    r2_c1 = final_sign.rows[1].cells[0]
    r2_c2 = final_sign.rows[1].cells[1]
    r2_c1.text = "\n_____________________________________\nJOSE MANGILIMAN JR.\nLead ERP Solutions Architect\nDate: September 11, 2026\n"
    r2_c2.text = "\n_____________________________________\nEXECUTIVE AUTHORIZED SIGNATORY\nManaging Director / Chief Operating Officer\nDate: ________________________\n"
    
    r3_c1 = final_sign.rows[2].cells[0]
    r3_c2 = final_sign.rows[2].cells[1]
    r3_c1.text = "Status: APPROVED & SIGNED"
    r3_c2.text = "Status: PENDING CLIENT COUNTERSIGN"
    set_cell_background(r3_c1, "f0fdf4")
    set_cell_background(r3_c2, "fffbeb")
    r3_c1.paragraphs[0].runs[0].font.bold = True
    r3_c2.paragraphs[0].runs[0].font.bold = True

    for r in final_sign.rows:
        r.cells[0].width = Inches(3.2)
        r.cells[1].width = Inches(3.2)

    doc.add_paragraph("\n\n~ END OF BUSINESS BLUEPRINT DOCUMENT ~")

    # Save docx
    docx_path = r"c:\Users\josem\erpnext-system\vps_migration\ULTRA_MRF_Automan_Business_Blueprint.docx"
    public_docx = r"c:\Users\josem\erpnext-system\public\ULTRA_MRF_Automan_Business_Blueprint.docx"
    doc.save(docx_path)
    doc.save(public_docx)
    print(f"Generated DOCX: {docx_path}")
    print(f"Generated DOCX: {public_docx}")

    # Generate matching Markdown document
    generate_markdown_document()

def generate_markdown_document():
    md_content = """# Business Blueprint Document: ULTRA MRF: Automan
## Implementation of ERPNext v16 Enterprise with Vehicle Management System (VMS) & Consolidated Multi-Company Suite

**Prepared For:** ULTRA MRF / Automan Car Care Center  
**Prepared By:** Jose Mangiliman Jr. (Lead ERP Solutions Architect & Consultant)  
**Implementation Timeline:** 45 Working Days (Implementation) + 10 Working Days (Change Request Buffer) = **55 Days Total**  
**Date of Document:** 11th September 2026  
**Release Version:** v1.0 Production Baseline  

---

## 1. CHANGE HISTORY & DOCUMENT CONTROL

| Version | Date | Author | Description of Change |
| :--- | :--- | :--- | :--- |
| **v1.0** | 11 Sep 2026 | Jose Mangiliman Jr. | Initial release of Business Blueprint Document for ULTRA MRF: Automan ERPNext v16 + VMS rollout. |
| **v1.1** | 11 Sep 2026 | Jose Mangiliman Jr. | Integrated Exploded Horizontal Cash Flow (Year-Month-Day), 30/60/90 Day AR/AP Aging, and Multi-Company Consolidation. |

---

## 2. PROJECT INTRODUCTION & EXECUTIVE SUMMARY

This document serves as the formal **Business Blueprint (BBP)** for the design, development, configuration, data migration, and deployment of **ERPNext v16 Enterprise** integrated with the custom **Vehicle Management System (VMS)** for **ULTRA MRF: Automan**.

Automan Car Care Center and ULTRA MRF operate a multi-branch automotive repair, preventive maintenance, tire wholesale/retail, spare parts warehousing, and fleet care enterprise across 13 operating entities in Central Luzon.

### 2.1 Acceptance & Signatories

| Role | Name | Designation / Organization | Status |
| :--- | :--- | :--- | :--- |
| **Lead Solutions Architect** | **Jose Mangiliman Jr.** | Lead ERP Solutions Architect | Approved |
| **Project Sponsor** | Executive Management | Managing Director / ULTRA MRF | For Countersign |
| **Operations Lead** | Workshop Operations Manager | Automan Car Care Center | For Countersign |
| **Finance Lead** | Chief Financial Controller | ULTRA MRF Group | For Countersign |

### 2.2 Enterprise Operating Entities (13 Companies Matrix)

1. **Automan Car Care Center** (`ACCC`) — Automotive Service, Mechanical Repair, Quick Lube & Tire Center
2. **Ultra MRF Dau Main** (`UMDM`) — Central Headquarters, Fleet Maintenance Hub & Wholesale Parts
3. **Ultra MRF San Fernando** (`UMSF`) — Branch Service Center & Quick Lube Operations
4. **Ultra MRF Telebastagan** (`UMTB`) — Automotive Care, Tire Fitting & Wheel Alignment
5. **Ultra MRF Telebastagan 2** (`UMT2`) — Heavy Fleet Maintenance & Commercial Vehicles
6. **Ultra MRF Dau Annex** (`UMDA`) — Parts Warehousing & Overflow Distribution
7. **The Wheelhub** (`TWHB`) — Premium Wheels, Rims & Specialty Tire Retail
8. **Wheel Core** (`WCRL`) — Wheel Distribution & Wholesale Trading
9. **Ultra MRF** (`UMRF`) — Corporate Holding & Administrative Management
10. **Ultra MRF Warehouse Dau** (`UMWD`) — Central Logistics & Regional Parts Depot
11. **Ultra MRF Mexico Warehouse** (`UMMW`) — Bulk Tire, Lubricant & Battery Storage
12. **San Fernando Warehouse** (`SFWH`) — Regional Warehouse & Subcontracting Depot
13. **ULTRA MRF Group (Consolidated)** (`UMGC`) — Top-Level Consolidated Financial Reporting Entity

---

## 3. ABBREVIATIONS & GLOSSARY

- **VMS**: Vehicle Management System
- **VJO**: Vehicle Job Order
- **VE**: Vehicle Estimate / Quotation
- **VI**: Vehicle Inspection
- **VIN**: Vehicle Identification Number
- **POS**: Point of Sale Terminal
- **COA**: Chart of Accounts
- **GL**: General Ledger
- **P&L**: Profit and Loss Statement
- **BS**: Balance Sheet
- **AR**: Accounts Receivable
- **AP**: Accounts Payable
- **SLE**: Stock Ledger Entry
- **PCount**: Physical Inventory Count & Audit
- **BIR**: Bureau of Internal Revenue
- **EWT**: Expanded Withholding Tax (BIR Form 2307)
- **O2C**: Order-to-Cash Lifecycle
- **P2P**: Procure-to-Pay Lifecycle
- **RBAC**: Role-Based Access Control

---

## 4. BUSINESS REQUIREMENTS & ARCHITECTURE

### 4.1 Engagement Parameters
- **Implementation Window:** 45 Working Days
- **Change Request (CR) Buffer:** 10 Working Days
- **Total Usable Man-Days:** 55 Working Days
- **Concurrent Users:** 500 Supported Active Users
- **Hosting Environment:** Cloud VPS (Linux Ubuntu 24.04, Docker, Caddy SSL) at `http://38.247.138.224:10017`

### 4.2 Core Functional Modules

1. **Vehicle Operations & Workshop Management (VMS):**
   - Vehicle Intake & VIN/Plate Master Registration.
   - Comprehensive multi-point Vehicle Inspection (VI).
   - Dynamic Vehicle Estimate (VE) with automated parts compatibility filtering.
   - Vehicle Job Order (VJO) execution, mechanic QR badge scanning, and QA gate pass release.

2. **Point of Sale (POS) & Cashier Shifts:**
   - Multi-cashier shift management with POS Opening & Closing Vouchers.
   - Fast counter billing with multi-mode payment splitting (Cash, Card, GCash, Maya, Charge).
   - Automated Sales Invoice, Stock Ledger, and GL journal generation.

3. **Supply Chain, Warehousing & Bin Routing:**
   - Multi-warehouse inventory tracking across all 13 operating entities.
   - Automated Bin Location assignment (Aisle/Rack/Shelf).
   - Receiver Safety Check validation on all incoming purchase receipts.
   - Inter-branch stock transfers with 'In-Transit' status controls.
   - Physical Count (PCount) module with variance reporting and automated reconciliation.

4. **Multi-Company Financial Consolidation Suite:**
   - Consolidated Multi-Company Profit & Loss (P&L) Statement.
   - Consolidated Statement of Financial Position (Balance Sheet).
   - Multi-Company General Ledger Audit Trail Explorer.
   - Interactive multi-company popover filter with 'Select All' and individual branch checkboxes.

5. **Hierarchical Exploded Cash Flow Engine:**
   - Fixed activity rows: Beginning Cash Balance, Cash Inflows, Cash Outflows, Net Cash Flow, Ending Cash Balance.
   - **Horizontal Drilldown:** Clicking Year expands to 12 Months; clicking Month explodes to individual operating Days!
   - Instant switching between Consolidated Group and individual operating companies.

6. **Accounts Receivable (AR) & Accounts Payable (AP) Aging Engine:**
   - Evaluates outstanding balances based on **actual credit terms and invoice due dates**.
   - Standard 5-tier aging buckets: Current/Not Due, 1-30 Days, 31-60 Days, 61-90 Days, and 90+ Days Overdue.
   - Customer & Supplier summaries with instant invoice drill-down drawers.

7. **Philippine BIR Tax Compliance & Statutory Books:**
   - Automated BIR Form 2307 Withholding Certificate generation.
   - Real-time statutory journal books: Sales Book, Purchases Book, Cash Receipts Journal, Cash Disbursements Journal, General Journal, and VAT Return 2550.

---

## 5. 45-DAY IMPLEMENTATION + 10-DAY CHANGE REQUEST TIMELINE

```mermaid
gantt
    title ULTRA MRF: Automan ERPNext v16 Implementation Schedule (55 Days)
    dateFormat  YYYY-MM-DD
    section Phase 1: Discovery
    Scope Analysis & Blueprint Sign-off       :done, p1, 2026-09-15, 7d
    section Phase 2: Core Build
    VMS Workshop & POS Shift Engine Build    :active, p2, 2026-09-22, 15d
    section Phase 3: Financials
    Exploded Cash Flow, Aging & BIR Books    :p3, 2026-10-07, 10d
    section Phase 4: Migration & UAT
    Master Data Loading & User Testing       :p4, 2026-10-17, 8d
    section Phase 5: Cutover & Go-Live
    Cashier Training & Production Go-Live    :p5, 2026-10-25, 5d
    section Phase 6: Change Requests
    Dedicated Scope Enhancements & CR Buffer:p6, 2026-10-30, 10d
```

| Phase | Duration | Key Milestone & Deliverables | Owner |
| :--- | :--- | :--- | :--- |
| **Phase 1: Discovery & Architecture** | Days 1 – 7 (7d) | Business Blueprint sign-off, Chart of Accounts, Multi-Company Matrix | Jose Mangiliman Jr. |
| **Phase 2: Core Build & VMS Customization** | Days 8 – 22 (15d) | DocTypes, VJO/POS workflows, Server Scripts, Print Templates | Jose Mangiliman Jr. |
| **Phase 3: Financials & Reports Suite** | Days 23 – 32 (10d) | Exploded Cash Flow, AR/AP Aging, BIR Journals, Consolidated P&L | Jose Mangiliman Jr. |
| **Phase 4: Data Migration & UAT** | Days 33 – 40 (8d) | Items, Vehicles, Customers, Opening GL upload, UAT execution | Jose Mangiliman Jr. & Team |
| **Phase 5: Training, Cutover & Go-Live** | Days 41 – 45 (5d) | Staff training, cashier dry runs, cutover to live production | Jose Mangiliman Jr. |
| **Phase 6: Change Request (CR) Window** | Days 46 – 55 (10d) | Dedicated scope buffer for custom requests and post-go-live tuning | Jose Mangiliman Jr. |

---

## 6. SIGN-OFF & BLUEPRINT APPROVAL

**Lead Solutions Architect:**  
Jose Mangiliman Jr.  
*Lead ERP Solutions Architect & Consultant*  
Date: September 11, 2026  
Status: **APPROVED & SIGNED**  

**Client Executive Management:**  
Managing Director / Chief Operating Officer  
*ULTRA MRF / Automan Car Care Center*  
Date: ________________________  
Status: **READY FOR COUNTERSIGN**  

---
*Document Reference: ULTRA_MRF_AUTOMAN_BBP_V1.0*
"""
    md_path = r"c:\Users\josem\erpnext-system\vps_migration\ULTRA_MRF_Automan_Business_Blueprint.md"
    public_md = r"c:\Users\josem\erpnext-system\public\ULTRA_MRF_Automan_Business_Blueprint.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(public_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Generated MD: {md_path}")
    print(f"Generated MD: {public_md}")

if __name__ == '__main__':
    build_docx_and_md()
