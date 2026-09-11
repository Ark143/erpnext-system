import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Palette
    NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
    NAVY_CARD = RGBColor(30, 41, 59)      # #1E293B
    BLUE_ACCENT = RGBColor(37, 99, 235)   # #2563EB
    CYAN_ACCENT = RGBColor(14, 165, 233)  # #0EA5E9
    TEAL_ACCENT = RGBColor(20, 184, 166)  # #14B8A6
    ORANGE_ACCENT = RGBColor(245, 158, 11)# #F59E0B
    EMERALD_GREEN = RGBColor(16, 185, 129)# #10B981
    RED_ACCENT = RGBColor(239, 68, 68)    # #EF4444
    PURPLE_ACCENT = RGBColor(139, 92, 246)# #8B5CF6

    BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC
    WHITE = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0
    TEXT_DARK = RGBColor(15, 23, 42)      # #0F172A
    TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
    TEXT_LIGHT = RGBColor(241, 245, 249)  # #F1F5F9

    def add_header(slide, title_text, category_text, dark_mode=False):
        # Header bar
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # Category / Breadcrumb
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN_ACCENT if dark_mode else BLUE_ACCENT
        p_cat.space_after = Pt(2)
        
        # Main Title
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE if dark_mode else TEXT_DARK

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=CARD_BORDER, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
        card = slide.shapes.add_shape(shape_type, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Navy Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, NAVY_DARK)

    # Decorative header glow
    top_glow = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.1))
    top_glow.fill.solid()
    top_glow.fill.fore_color.rgb = BLUE_ACCENT
    top_glow.line.fill.background()

    # Title Card
    tcard = add_card(s1, 0.8, 1.2, 11.733, 4.2, bg_color=NAVY_CARD, border_color=RGBColor(51, 65, 85))
    
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(10.933), Inches(3.6))
    tf = t_box.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = "ENTERPRISE AUTOMOTIVE AFTERMARKET & WORKSHOP SYSTEM"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = CYAN_ACCENT
    p0.space_after = Pt(10)

    p1 = tf.add_paragraph()
    p1.text = "Vehicle Management System (VMS)"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(4)

    p2 = tf.add_paragraph()
    p2.text = "End-to-End Enterprise Architecture: Front-Desk Workshop Operations to Automated General Ledger Accounting"
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(20)

    p3 = tf.add_paragraph()
    p3.text = "Built on ERPNext v16 / Frappe Framework • High-Performance PostgreSQL Engine • 12 Companies / Branches"
    p3.font.size = Pt(11.5)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # 4 Quick Metric Badges on Slide 1
    metrics = [
        ("38,654+", "Registered Vehicles", CYAN_ACCENT),
        ("481+", "Job Orders & Services", BLUE_ACCENT),
        ("₱ 46.99 M", "Managed Stock Valuation", ORANGE_ACCENT),
        ("100% BIR CAS", "Double-Entry GL Compliance", EMERALD_GREEN)
    ]
    for i, (val, lbl, col) in enumerate(metrics):
        m_left = 0.8 + i * 2.98
        m_card = add_card(s1, m_left, 5.7, 2.78, 1.3, bg_color=NAVY_CARD, border_color=RGBColor(51, 65, 85))
        mbx = s1.shapes.add_textbox(Inches(m_left + 0.15), Inches(5.8), Inches(2.48), Inches(1.1))
        mtf = mbx.text_frame
        mtf.word_wrap = True
        
        mp1 = mtf.paragraphs[0]
        mp1.text = val
        mp1.font.size = Pt(18)
        mp1.font.bold = True
        mp1.font.color.rgb = col
        mp1.space_after = Pt(2)
        
        mp2 = mtf.add_paragraph()
        mp2.text = lbl
        mp2.font.size = Pt(9.5)
        mp2.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 2: Executive Overview & What We Have Built
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_LIGHT)
    add_header(s2, "Executive Overview: The Complete Automotive ERP Ecosystem", "System Core & Achievements")

    cards_data_s2 = [
        ("🚗 Workshop & Bay Management", 
         "Fully digitizes front desk intake, 25/50-point electronic vehicle inspections, service estimates, bay labor dispatch, and job order tracking across 38,654+ customer vehicles.",
         BLUE_ACCENT),
        ("⚡ High-Speed Touchscreen POS",
         "Unified standalone (/pos-terminal) & desk counter POS with instant barcode scanning, QR badge cashier shift authentication, multi-payment tender, and automatic branch auto-lock.",
         CYAN_ACCENT),
        ("📦 570-Bin Inventory & Safety Handover",
         "Aisle, rack, shelf, and bin slotting across 3 central warehouses and 8 branch stores. Features camera-based QR receiver verification before parts issuance to bays.",
         ORANGE_ACCENT),
        ("📑 100% BIR CAS & Dual-Ledger Sync",
         "Direct real-time posting from counter POS to standard ERPNext POS Invoices, General Ledger double-entry books (CRJ, CDJ, Sales Journal, Purchases Book, Form 2307), and fixed asset depreciation.",
         EMERALD_GREEN)
    ]

    for i, (title, desc, accent) in enumerate(cards_data_s2):
        row = i // 2
        col = i % 2
        c_left = 0.8 + col * 5.95
        c_top = 1.45 + row * 2.75
        
        add_card(s2, c_left, c_top, 5.75, 2.55, bg_color=WHITE, border_color=CARD_BORDER)
        
        # Accent bar
        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c_left), Inches(c_top), Inches(0.12), Inches(2.55))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        
        tbx = s2.shapes.add_textbox(Inches(c_left + 0.3), Inches(c_top + 0.2), Inches(5.25), Inches(2.15))
        tf = tbx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.line_spacing = 1.25

    # =========================================================================
    # SLIDE 3: Multi-Company Enterprise Network & Hierarchy
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_LIGHT)
    add_header(s3, "Multi-Company Enterprise Topology & Multi-Branch Network", "Network Architecture")

    # Left Column: Central Hubs & Topology Card
    add_card(s3, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_net = s3.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_net = tbx_net.text_frame
    tf_net.word_wrap = True
    
    p = tf_net.paragraphs[0]
    p.text = "12 Corporate Entities in One Unified Database"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    p = tf_net.add_paragraph()
    p.text = "• Corporate Headquarters:\n  - ULTRA MRF (Group Parent Company)"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(8)

    p = tf_net.add_paragraph()
    p.text = "• 3 Central Logistics Hubs & Distribution Warehouses:\n  1. Ultra MRF Warehouse Dau (Main Central Hub)\n  2. San Fernando Warehouse (Regional Pampanga Hub)\n  3. Ultra MRF Mexico Warehouse (Bulk Tires & Rims)"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(8)

    p = tf_net.add_paragraph()
    p.text = "• 8 Full-Service Centers & Retail Branches:\n  - Automan Car Care Center (Phase 1 Prototype Pilot)\n  - Ultra MRF Dau Main & Dau Annex\n  - Ultra MRF San Fernando\n  - Ultra MRF Telebastagan & Telebastagan 2\n  - Wheel Core & The Wheelhub"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK

    # Right Column: Data Isolation & Governance Card
    add_card(s3, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_gov = s3.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_gov = tbx_gov.text_frame
    tf_gov.word_wrap = True

    p = tf_gov.paragraphs[0]
    p.text = "Enterprise Data Scoping & Multi-Tenant Security"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(10)

    features = [
        ("🔒 Strict Branch-Level Data Isolation", "Cashiers and service advisors only access data for their assigned branch. Stock balance, POS registers, and job orders are auto-scoped."),
        ("🏢 Independent Chart of Accounts", "Each entity maintains its own dedicated Chart of Accounts, default warehouse stores (e.g., Stores - UM, Stores - UMDM), and POS profiles."),
        ("🔄 Automated Intercompany Logistics", "Branches request stock from Central Hubs via Material Requests; automatically converts into Intercompany Delivery Notes & Stock Receipts."),
        ("📊 Consolidated Executive Visibility", "Leadership (CEO, COO, CFO) accesses group-wide consolidated dashboards and real-time Profit & Loss reports across all 12 entities.")
    ]

    for ftitle, fdesc in features:
        p = tf_gov.add_paragraph()
        p.text = ftitle
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)

        p = tf_gov.add_paragraph()
        p.text = fdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 4: Master Workflow: End-to-End Operational to Accounting Pipeline
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, NAVY_DARK)
    add_header(s4, "Master Architecture: From Workshop Bay to Financial Statements", "End-to-End Workflow Pipeline", dark_mode=True)

    # 6 Step Horizontal Pipeline
    steps = [
        ("1. INTAKE & REGISTRY", "Customer & Vehicle\nPlate Lookup\n38k+ Master Database", BLUE_ACCENT),
        ("2. INSPECTION", "Multi-Point Digital QC\nCamera Photos\nCondition Checklist", CYAN_ACCENT),
        ("3. JOB ORDER & BAY", "Technician Labor\nParts Allocation\nBay Status Tracking", ORANGE_ACCENT),
        ("4. PARTS ISSUANCE", "570 Bins Slotting\nQR Badge Scan\nHandover Photo Proof", PURPLE_ACCENT),
        ("5. BILLING & POS", "Dual-Ledger Posting\nMulti-Payment Tender\nPOS Invoice Generated", EMERALD_GREEN),
        ("6. GL & REPORTING", "Automated GL Entry\n100% BIR Books\nExecutive Analytics", TEAL_ACCENT)
    ]

    for i, (stitle, sdesc, scol) in enumerate(steps):
        s_left = 0.8 + i * 1.98
        add_card(s4, s_left, 1.6, 1.82, 3.8, bg_color=NAVY_CARD, border_color=scol)
        
        # Step header box
        sbx = s4.shapes.add_textbox(Inches(s_left + 0.1), Inches(1.75), Inches(1.62), Inches(3.5))
        stf = sbx.text_frame
        stf.word_wrap = True
        
        p = stf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = scol
        p.space_after = Pt(12)
        
        p2 = stf.add_paragraph()
        p2.text = sdesc
        p2.font.size = Pt(10)
        p2.font.color.rgb = RGBColor(203, 213, 225)
        p2.line_spacing = 1.3

        # Arrow connector if not last
        if i < len(steps) - 1:
            arr = s4.shapes.add_textbox(Inches(s_left + 1.8), Inches(3.2), Inches(0.2), Inches(0.5))
            atf = arr.text_frame
            ap = atf.paragraphs[0]
            ap.text = "➔"
            ap.font.size = Pt(14)
            ap.font.bold = True
            ap.font.color.rgb = RGBColor(148, 163, 184)

    # Bottom Banner Explaining Data Traceability
    bot_card = add_card(s4, 0.8, 5.65, 11.733, 1.35, bg_color=NAVY_CARD, border_color=RGBColor(51, 65, 85))
    bot_bx = s4.shapes.add_textbox(Inches(1.05), Inches(5.75), Inches(11.2), Inches(1.15))
    bot_tf = bot_bx.text_frame
    bot_tf.word_wrap = True
    
    bp1 = bot_tf.paragraphs[0]
    bp1.text = "Triple Traceability & Zero-Discrepancy Guarantee"
    bp1.font.size = Pt(12)
    bp1.font.bold = True
    bp1.font.color.rgb = CYAN_ACCENT
    bp1.space_after = Pt(3)

    bp2 = bot_tf.add_paragraph()
    bp2.text = "Every physical action in the workshop bay (labor done, part consumed, technician assigned) is cryptographically linked to a double-entry General Ledger record and inventory bin deduction. No unbilled services, no unaccounted stock."
    bp2.font.size = Pt(10.5)
    bp2.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 5: Operation Step 1 - Vehicle Registry & Customer Intake
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_LIGHT)
    add_header(s5, "Phase 1: Customer Vehicle Master Registry & Front Desk Intake", "Operational Workflow")

    # Left Column: Customer Vehicle Schema & Features
    add_card(s5, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_v = s5.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_v = tbx_v.text_frame
    tf_v.word_wrap = True

    p = tf_v.paragraphs[0]
    p.text = "Core Asset Registry (38,654 Active Vehicles)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    specs = [
        ("🚘 Vehicle Master DocType (`tabCustomer Vehicle`)", "Tracks License Plate (unique index), VIN / Chassis Number, Engine Number, Make (Toyota, Mitsubishi, etc.), Model, Year, and Odometer Mileage."),
        ("👤 Relational Customer Linkage", "Tied directly to ERPNext Customer account (`tabCustomer`), maintaining multi-vehicle family or corporate fleet relationships under one billing profile."),
        ("🛡️ Space Normalization Hook", "Pre-save script sanitizes customer strings (e.g., converting legacy double-space anomalies) to guarantee 100% clean checkouts without link validation crashes."),
        ("⏱️ Complete Vehicle Service History Card", "Every past Job Order, Inspection, POS invoice, and part installed is indexed by Plate Number for instant customer history lookup at the front desk.")
    ]

    for stitle, sdesc in specs:
        p = tf_v.add_paragraph()
        p.text = stitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        p = tf_v.add_paragraph()
        p.text = sdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # Right Column: Visual Process Flow Card
    add_card(s5, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_vf = s5.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_vf = tbx_vf.text_frame
    tf_vf.word_wrap = True

    p = tf_vf.paragraphs[0]
    p.text = "Front Desk Vehicle Intake Sequence"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(10)

    flow_steps = [
        ("Step 1: Vehicle Plate Search", "Advisor enters license plate or scans barcode; system instantly retrieves customer profile and historical repair logs."),
        ("Step 2: Mileage & Concern Intake", "Current odometer reading is recorded; customer describes issues (e.g. vibration at 80 km/h, tire replacement, regular PMS)."),
        ("Step 3: Auto-Trigger Inspection", "System automatically provisions a new `Vehicle Inspection` checklist assigned to the bay intake queue."),
        ("Step 4: Real-Time Fleet Alert", "If the vehicle belongs to a corporate fleet, corporate credit limit and negotiated discount pricing rules are automatically applied.")
    ]

    for ftitle, fdesc in flow_steps:
        p = tf_vf.add_paragraph()
        p.text = ftitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)

        p = tf_vf.add_paragraph()
        p.text = fdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 6: Operation Step 2 - Digital Inspection & Workshop Estimates
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_LIGHT)
    add_header(s6, "Phase 2: Digital Vehicle Inspection & Service Estimation", "Operational Workflow")

    # 3 Column Cards
    col_width = 3.75
    gap = 0.24
    
    # Col 1: Electronic Inspection Checklist
    add_card(s6, 0.8, 1.45, col_width, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    b1 = s6.shapes.add_textbox(Inches(0.95), Inches(1.65), Inches(3.45), Inches(5.1))
    t1 = b1.text_frame
    t1.word_wrap = True
    
    p = t1.paragraphs[0]
    p.text = "📋 Electronic Inspection"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    items1 = [
        "• Inspection Templates: Configured for 25-Point, 50-Point, or Tire QC checklists.",
        "• Granular Item Grading: Mark items as Pass, Attention Needed, or Critical Fail.",
        "• Critical Measurements: Tire tread depth (mm), brake pad thickness, battery voltage, and fluid clarity.",
        "• Camera Evidence: Direct mobile/tablet photo uploads capturing tire wear or undercarriage leaks."
    ]
    for itm in items1:
        p = t1.add_paragraph()
        p.text = itm
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Col 2: Service Estimates & Quotations
    add_card(s6, 0.8 + col_width + gap, 1.45, col_width, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    b2 = s6.shapes.add_textbox(Inches(0.95 + col_width + gap), Inches(1.65), Inches(3.45), Inches(5.1))
    t2 = b2.text_frame
    t2.word_wrap = True

    p = t2.paragraphs[0]
    p.text = "💡 Auto-Generated Estimates"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ORANGE_ACCENT
    p.space_after = Pt(8)

    items2 = [
        "• Conversion from QC: Failed inspection items automatically generate proposed line items in Vehicle Estimate.",
        "• Clear Labor & Parts Split: Itemizes technician labor hours alongside required replacement parts & tires.",
        "• Margin & Price Checks: Validates standard price list vs. authorized promotional discounts.",
        "• Customer Approval: Advisor sends digital quote via SMS/Email or prints for counter signature."
    ]
    for itm in items2:
        p = t2.add_paragraph()
        p.text = itm
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Col 3: Conversion to Job Order
    add_card(s6, 0.8 + 2 * (col_width + gap), 1.45, col_width, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    b3 = s6.shapes.add_textbox(Inches(0.95 + 2 * (col_width + gap)), Inches(1.65), Inches(3.45), Inches(5.1))
    t3 = b3.text_frame
    t3.word_wrap = True

    p = t3.paragraphs[0]
    p.text = "⚙️ Job Order Dispatch"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    p.space_after = Pt(8)

    items3 = [
        "• 1-Click Conversion: Approved estimate generates `Vehicle Job Order` (`VJO-YYYY-#####`).",
        "• Bay Routing: Allocates job to specific bay (Wheel Alignment Bay, Heavy Lifter Bay, Express Bay).",
        "• Lead Technician Tagging: Assigns responsible mechanic and records start timestamps.",
        "• Material Reservation: Locks required tires/parts in branch warehouse to prevent out-of-stock."
    ]
    for itm in items3:
        p = t3.add_paragraph()
        p.text = itm
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 7: Operation Step 3 - Workshop Bay Operations & Job Order Lifecycle
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_LIGHT)
    add_header(s7, "Phase 3: Workshop Bay Execution & Job Order Lifecycle", "Operational Workflow")

    # Left: Job Order Lifecycle State Machine
    add_card(s7, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_jo = s7.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_jo = tbx_jo.text_frame
    tf_jo.word_wrap = True

    p = tf_jo.paragraphs[0]
    p.text = "Job Order Lifecycle & Status Progression"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    states = [
        ("🟡 DRAFT", "Intake recorded, initial scope defined, awaiting customer or technician review."),
        ("🔵 IN PROGRESS", "Vehicle mounted on bay lift. Mechanics executing alignment, balancing, or parts overhaul."),
        ("🟠 PENDING PARTS", "Work paused awaiting warehouse transfer or special item arrival from Mexico/Dau hubs."),
        ("🟢 COMPLETED", "Bay service finished, post-service quality check passed by Workshop Supervisor."),
        ("⚪ RELEASED", "Customer settled invoice, gate pass generated, vehicle handed over to owner.")
    ]

    for st_title, st_desc in states:
        p = tf_jo.add_paragraph()
        p.text = st_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(1)

        p = tf_jo.add_paragraph()
        p.text = st_desc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(6)

    # Right: Child Tables & Technician Productivity
    add_card(s7, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_jof = s7.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_jof = tbx_jof.text_frame
    tf_jof.word_wrap = True

    p = tf_jof.paragraphs[0]
    p.text = "Service Items vs. Parts Tracking (`VJO` Schema)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(10)

    jof_items = [
        ("🔧 Job Order Service Items (Labor Table)", "Tracks individual labor services (e.g. 4-Wheel Computerized Alignment, PMS 20K Labor, Camber Adjustment). Directly attributes billing to individual technicians for labor commission analytics."),
        ("📦 Job Order Part Items (Materials Table)", "Itemizes physical stock consumed (e.g. Yokohama 265/65R17 Tires, Synthetic Motor Oil 5W30, Oil Filters). Enforces exact stock deduction from the branch store."),
        ("⚡ Real-Time Labor vs. Parts Financial Split", "Automatically computes `total_labor`, `total_parts`, and `grand_total` in real-time. Live feeds into executive revenue metrics (e.g. ₱104.7k Labor vs ₱2.11M Parts)."),
        ("🛡️ Unbilled Service Protection", "Technicians cannot mark a job 'Completed' if unrecorded parts or unapproved service add-ons are pending.")
    ]

    for jtitle, jdesc in jof_items:
        p = tf_jof.add_paragraph()
        p.text = jtitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)

        p = tf_jof.add_paragraph()
        p.text = jdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(7)

    # =========================================================================
    # SLIDE 8: Operation Step 4 - Warehouse 570-Bin Storage & Safety Handover
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_LIGHT)
    add_header(s8, "Phase 4: Warehouse Bin Slotting & Receiver Safety Handover", "Inventory Control")

    # Left: 570 Bin Locations & Putaway
    add_card(s8, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_bin = s8.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_bin = tbx_bin.text_frame
    tf_bin.word_wrap = True

    p = tf_bin.paragraphs[0]
    p.text = "570 Bin Locations & Shelf Slotting"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    bin_features = [
        ("📍 Granular Bin Hierarchy", "Standardized structure across warehouses: Aisle -> Rack -> Shelf -> Bin (e.g. `DAU-TIRE-A01-R02-S03-B04`)."),
        ("📱 Mobile QR Putaway & Picking", "Warehousemen scan bin QR tags during receiving and pick-list processing, eliminating misplaced tires and alloy wheels."),
        ("🔄 Multi-Warehouse Balance (`tabBin`)", "Real-time stock valuation across ₱46.99M inventory across 3 central warehouses and 8 branch workshop stores."),
        ("⚡ Rapid Stock Lookup Join", "Optimized SQL join (`vm_pos_get_items`) filters active branch stock in zero latency (<50ms) for high-speed counter POS.")
    ]

    for btitle, bdesc in bin_features:
        p = tf_bin.add_paragraph()
        p.text = btitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        p = tf_bin.add_paragraph()
        p.text = bdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # Right: Receiver Verification Engine (The Safety Check)
    add_card(s8, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_rec = s8.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_rec = tbx_rec.text_frame
    tf_rec.word_wrap = True

    p = tf_rec.paragraphs[0]
    p.text = "Receiver Verification & Safety Handover Engine"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RED_ACCENT
    p.space_after = Pt(10)

    rec_steps = [
        ("1. Official Technician QR ID Badges", "Every mechanic has an official QR ID badge generated directly from ERPNext Desk with encrypted employee identifier."),
        ("2. Mandatory Handover Scan", "When warehouseman issues parts via Stock Entry (Material Issue), system renders the Receiver Safety Handover Box."),
        ("3. WebRTC Camera Scan & Photo Proof", "Warehouse camera scans the recipient mechanic's QR badge AND snaps a physical photo of the parts handover."),
        ("4. Immutable Audit Verification", "Transaction marked VERIFIED with timestamp, technician ID, and photo proof. Unverified material issues are hard-blocked.")
    ]

    for rtitle, rdesc in rec_steps:
        p = tf_rec.add_paragraph()
        p.text = rtitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK
        p.space_after = Pt(2)

        p = tf_rec.add_paragraph()
        p.text = rdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(7)

    # =========================================================================
    # SLIDE 9: Operation Step 5 - Touchscreen POS Counter Operations
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_LIGHT)
    add_header(s9, "Phase 5: High-Speed Touchscreen POS Counter Operations", "Retail & Checkout")

    # 4 Cards Grid
    pos_cards = [
        ("🔒 Auto-Locked Branch Assignment",
         "The cashier's operating company is automatically detected from their linked Employee / Cashier Profile and permanently locked as a read-only badge. Eliminates accidental cross-branch billing errors.",
         BLUE_ACCENT),
        ("📷 Camera QR Badge Shift Login",
         "Cashiers sign into active shifts by presenting their physical ID badge to the device camera. Automatically links active POS Opening Entry and registers drawer float.",
         CYAN_ACCENT),
        ("💳 Multi-Payment Tender Suite",
         "Supports Cash (with quick denomination buttons +100, +500, +1000), Credit/Debit Card, GCash, Maya, and BDO Bank Transfer. Auto-fills exact balance on card/e-wallet selection.",
         ORANGE_ACCENT),
        ("🧾 Thermal Receipts & Real-Time Sync",
         "Generates 80mm/58mm thermal receipts with official BIR numbers, QR vehicle links, and transaction logs. Standalone POS tab syncs immediately with ERPNext backend.",
         EMERALD_GREEN)
    ]

    for i, (title, desc, accent) in enumerate(pos_cards):
        row = i // 2
        col = i % 2
        c_left = 0.8 + col * 5.95
        c_top = 1.45 + row * 2.75
        
        add_card(s9, c_left, c_top, 5.75, 2.55, bg_color=WHITE, border_color=CARD_BORDER)
        
        # Accent bar
        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c_left), Inches(c_top), Inches(0.12), Inches(2.55))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        
        tbx = s9.shapes.add_textbox(Inches(c_left + 0.3), Inches(c_top + 0.2), Inches(5.25), Inches(2.15))
        tf = tbx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.line_spacing = 1.25

    # =========================================================================
    # SLIDE 10: Critical Bridge - Dual-Ledger Synchronization Engine
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, NAVY_DARK)
    add_header(s10, "The Accounting Bridge: Dual-Ledger Synchronization Engine", "Integration Architecture", dark_mode=True)

    # Left: The Technical Sequence Box
    add_card(s10, 0.8, 1.45, 5.75, 5.5, bg_color=NAVY_CARD, border_color=RGBColor(51, 65, 85))
    tbx_sq = s10.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_sq = tbx_sq.text_frame
    tf_sq.word_wrap = True

    p = tf_sq.paragraphs[0]
    p.text = "Real-Time Transaction Bridge (`create_from_pos`)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    p.space_after = Pt(8)

    seqs = [
        ("1. Front-End Payload Dispatch", "Cashier completes counter sale; POS SPA dispatches JSON containing Customer, Vehicle Plate, Items, Taxes, and Payment Tenders."),
        ("2. Active POS Opening Entry Verification", "Bridge checks for an open `POS Opening Entry` for cashier & branch. If missing, automatically provisions and submits opening float."),
        ("3. Create `Vehicle POS Invoice`", "Instantiates custom `VMSPOS-YYYY-#####` containing vehicle-specific metadata, mileage, and technician attribution."),
        ("4. Auto-Submit ERPNext `POS Invoice`", "Concurrently constructs standard ERPNext `POS Invoice` (`ACC-PSINV-YYYY-#####`), submitting directly to the General Ledger & Stock Ledger.")
    ]

    for stitle, sdesc in seqs:
        p = tf_sq.add_paragraph()
        p.text = stitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.space_after = Pt(2)

        p = tf_sq.add_paragraph()
        p.text = sdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = RGBColor(203, 213, 225)
        p.space_after = Pt(7)

    # Right: Dual Document Relationship Diagram
    add_card(s10, 6.75, 1.45, 5.75, 5.5, bg_color=NAVY_CARD, border_color=RGBColor(51, 65, 85))
    tbx_rel = s10.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_rel = tbx_rel.text_frame
    tf_rel.word_wrap = True

    p = tf_rel.paragraphs[0]
    p.text = "Dual Document Architecture & Integrity"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    p.space_after = Pt(10)

    p = tf_rel.add_paragraph()
    p.text = "🚗 Operational Layer: Vehicle POS Invoice"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    p.space_after = Pt(2)

    p = tf_rel.add_paragraph()
    p.text = "• Record: `tabVehicle POS Invoice` (e.g. VMSPOS-2026-00033)\n• Purpose: Fast counter search, bay job linking, technician commissions, vehicle service history card, and reprint."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(10)

    p = tf_rel.add_paragraph()
    p.text = "🏛️ Accounting Layer: ERPNext POS Invoice"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    p.space_after = Pt(2)

    p = tf_rel.add_paragraph()
    p.text = "• Record: `tabPOS Invoice` (e.g. ACC-PSINV-2026-00032)\n• Purpose: Immutable General Ledger entries, Stock Ledger deductions, BIR CAS tax compliance, and official financial statements."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(10)

    p = tf_rel.add_paragraph()
    p.text = "✅ Cross-Document Integrity: Bidirectional relational linkage stored on both records ensures zero orphan transactions or revenue leakage."
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ORANGE_ACCENT

    # =========================================================================
    # SLIDE 11: Accounting Process 1 - General Ledger & Stock Ledger Posting
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_LIGHT)
    add_header(s11, "Accounting Architecture: General Ledger & Stock Ledger Automation", "Financial Engine")

    # Left: Double Entry Accounting Table
    add_card(s11, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_gl = s11.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_gl = tbx_gl.text_frame
    tf_gl.word_wrap = True

    p = tf_gl.paragraphs[0]
    p.text = "Automated Double-Entry Posting Rules"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    entries = [
        ("💰 Retail Tire / Counter POS Sale", 
         "• DEBIT: Cash / E-Wallet / Bank Clearing (Asset)\n• CREDIT: Sales Revenue (Income)\n• CREDIT: Output VAT 12% (Liability)\n• DEBIT: Cost of Goods Sold / COGS (Expense)\n• CREDIT: Stock-in-Hand (Asset)"),
        ("🔧 Bay Labor & Service Billing",
         "• DEBIT: Cash / Customer Accounts Receivable (Asset)\n• CREDIT: Service & Labor Income (Income)\n• CREDIT: Output VAT 12% (Liability)"),
        ("📦 Workshop Internal Parts Issue",
         "• DEBIT: Workshop Supplies / Repair Expense (Expense)\n• CREDIT: Stock-in-Hand (Asset)")
    ]

    for etitle, edesc in entries:
        p = tf_gl.add_paragraph()
        p.text = etitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        p = tf_gl.add_paragraph()
        p.text = edesc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(6)

    # Right: Perpetual Inventory Valuation & Costing
    add_card(s11, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_sl = s11.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_sl = tbx_sl.text_frame
    tf_sl.word_wrap = True

    p = tf_sl.paragraphs[0]
    p.text = "Stock Ledger & Perpetual Inventory Engine"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(10)

    sl_points = [
        ("📊 Moving Average Valuation", "Automatically re-calculates weighted average unit cost upon every supplier Purchase Receipt (GRN), reflecting freight and import duties accurately."),
        ("⚡ Real-Time Stock Balance (`tabBin`)", "Every counter invoice or material issue instantly writes to `tabStock Ledger Entry` (SLE), decrementing `actual_qty` in `tabBin` with zero batch lag."),
        ("🛡️ Negative Stock Prohibition", "System hard-blocks transactions if stock in the designated branch warehouse is insufficient, preventing fictitious inventory balances."),
        ("🔄 Real-Time Gross Margin Reporting", "Because COGS and Revenue post concurrently, gross profit margins per branch, tire model, or service type are available in real time.")
    ]

    for stitle, sdesc in sl_points:
        p = tf_sl.add_paragraph()
        p.text = stitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)

        p = tf_sl.add_paragraph()
        p.text = sdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(7)

    # =========================================================================
    # SLIDE 12: Accounting Process 2 - Procure-to-Pay (P2P) & 3-Way Matching
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_LIGHT)
    add_header(s12, "Procure-to-Pay (P2P) Lifecycle & Vendor 3-Way Matching", "Purchasing & Payables")

    # 4 Cards in P2P Flow
    p2p_cards = [
        ("1. Material Requisition",
         "Branch managers or auto-reorder triggers generate Material Requests when tire or parts stock drops below safety thresholds.",
         BLUE_ACCENT),
        ("2. Purchase Order (PO)",
         "Commercial POs issued to manufacturers (Yokohama, Michelin, etc.). Integrated executive approval limits prevent unauthorized spending.",
         CYAN_ACCENT),
        ("3. Purchase Receipt (GRN)",
         "Central warehouse verifies physical counts against bill of lading. Accrues temporary inventory liabilities into Stock-in-Hand GL.",
         ORANGE_ACCENT),
        ("4. Purchase Invoice & Settlement",
         "Strict 3-Way Match (PO vs GRN vs Vendor Bill). Posts final Accounts Payable liability with BIR Form 2307 withholding tax deduction.",
         EMERALD_GREEN)
    ]

    for i, (title, desc, accent) in enumerate(p2p_cards):
        c_left = 0.8 + i * 2.98
        add_card(s12, c_left, 1.45, 2.78, 3.8, bg_color=WHITE, border_color=CARD_BORDER)
        
        # Header bar
        bar = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c_left), Inches(1.45), Inches(2.78), Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tbx = s12.shapes.add_textbox(Inches(c_left + 0.15), Inches(1.65), Inches(2.48), Inches(3.5))
        tf = tbx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(10)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_MUTED
        p2.line_spacing = 1.3

    # Bottom Banner: 3-Way Matching Safeguards
    p2p_bot = add_card(s12, 0.8, 5.45, 11.733, 1.5, bg_color=WHITE, border_color=CARD_BORDER)
    p2p_tbx = s12.shapes.add_textbox(Inches(1.05), Inches(5.55), Inches(11.2), Inches(1.3))
    p2p_tf = p2p_tbx.text_frame
    p2p_tf.word_wrap = True

    p = p2p_tf.paragraphs[0]
    p.text = "🛡️ Zero-Overbilling Governance & Accounts Payable Controls"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(3)

    p = p2p_tf.add_paragraph()
    p.text = "• Enforces exact unit price adherence against negotiated supplier contracts.\n• Disallows payment processing on quantities greater than physically received and QC-accepted at the warehouse.\n• Generates real-time Accounts Payable Aging reports to optimize corporate cash flow and capture early-payment discounts."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 13: Accounting Process 3 - Fixed Assets & Automated Depreciation
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, BG_LIGHT)
    add_header(s13, "Workshop Machinery Capitalization & Automated Depreciation (IAS 16)", "Fixed Assets Accounting")

    # Left: Capitalized Workshop Machinery
    add_card(s13, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_fa = s13.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_fa = tbx_fa.text_frame
    tf_fa.word_wrap = True

    p = tf_fa.paragraphs[0]
    p.text = "Workshop Machinery Asset Portfolio"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    assets = [
        ("🔧 3D High-Definition Wheel Aligners", "Capitalized across Dau, San Fernando, and Automan branches with serial tracking and camera sensor calibration schedules."),
        ("🔩 Automated Heavy-Duty Tire Changers", "High-capacity changers with pneumatic helper arms, capitalized under Automotive Machinery."),
        ("⚖️ Dynamic High-Speed Wheel Balancers", "Digital laser balancers capitalized and maintained under preventive calibration routines."),
        ("🏗️ Hydraulic 2-Post & 4-Post Bay Lifts", "Bay lifting equipment capitalized with mandatory hydraulic fluid and safety inspection logging.")
    ]

    for atitle, adesc in assets:
        p = tf_fa.add_paragraph()
        p.text = atitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        p = tf_fa.add_paragraph()
        p.text = adesc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(6)

    # Right: Automated Monthly Depreciation Accounting
    add_card(s13, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_dep = s13.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_dep = tbx_dep.text_frame
    tf_dep.word_wrap = True

    p = tf_dep.paragraphs[0]
    p.text = "Automated Monthly Depreciation Engine"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(10)

    dep_points = [
        ("📅 Straight-Line Method (SLM)", "Calculates monthly depreciation based on capitalized purchase cost, salvage value, and useful life (e.g. 5 to 10 years)."),
        ("⚡ Automated Monthly Journal Entries", "On the 1st of every calendar month, ERPNext automatically generates and submits immutable GL entries:"),
        ("📝 General Ledger Booking:", "  • DEBIT: Depreciation Expense (Operating Expense)\n  • CREDIT: Accumulated Depreciation (Contra Asset)"),
        ("📊 Asset Register & Net Book Value (NBV)", "Real-time Fixed Asset Register (`/desk/fixed-asset-register`) displays current NBV, accumulated depreciation, and asset location per branch.")
    ]

    for dtitle, ddesc in dep_points:
        p = tf_dep.add_paragraph()
        p.text = dtitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)

        p = tf_dep.add_paragraph()
        p.text = ddesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(7)

    # =========================================================================
    # SLIDE 14: Accounting Process 4 - Philippine BIR CAS Tax & Audit Compliance
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, BG_LIGHT)
    add_header(s14, "Philippine BIR CAS Statutory Compliance & Tax Module", "Taxation & Compliance")

    # 4 Compliance Cards
    bir_cards = [
        ("📑 BIR Form 2307 Withholding",
         "Automated generation of Certificate of Creditable Tax Withheld at Source for corporate fleet customers and supplier payables with accurate ATC tax codes.",
         BLUE_ACCENT),
        ("📘 Official Sales Journal & CRJ",
         "Generates Computerized Accounting System (CAS) Sales Journal and Cash Receipts Journal (CRJ) formatted to exact Bureau of Internal Revenue standards.",
         CYAN_ACCENT),
        ("📙 Purchases Book & CDJ",
         "Maintains statutory Purchases Book and Cash Disbursements Journal (CDJ), capturing input VAT and supplier TIN numbers.",
         ORANGE_ACCENT),
        ("🏛️ Audit Trail & General Ledger",
         "100% immutable General Ledger and General Journal transaction history with tamper-proof timestamping and electronic document serial numbers.",
         EMERALD_GREEN)
    ]

    for i, (title, desc, accent) in enumerate(bir_cards):
        row = i // 2
        col = i % 2
        c_left = 0.8 + col * 5.95
        c_top = 1.45 + row * 2.75
        
        add_card(s14, c_left, c_top, 5.75, 2.55, bg_color=WHITE, border_color=CARD_BORDER)
        
        # Accent bar
        bar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c_left), Inches(c_top), Inches(0.12), Inches(2.55))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
        
        tbx = s14.shapes.add_textbox(Inches(c_left + 0.3), Inches(c_top + 0.2), Inches(5.25), Inches(2.15))
        tf = tbx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.line_spacing = 1.25

    # =========================================================================
    # SLIDE 15: Shift Reconciliation, Cash Drawer & Bank Reconciliation
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, BG_LIGHT)
    add_header(s15, "Cashier Shift Balancing, Drawer Control & Bank Reconciliation", "Financial Controls")

    # Left: POS Opening & Closing Shift Control
    add_card(s15, 0.8, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_sh = s15.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_sh = tbx_sh.text_frame
    tf_sh.word_wrap = True

    p = tf_sh.paragraphs[0]
    p.text = "Cashier Shift Balancing (`POS Closing Entry`)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    shift_steps = [
        ("1. Shift Initiation & Drawer Float", "Cashier starts shift with `POS Opening Entry`, recording physical opening petty cash float."),
        ("2. Real-Time Cash Collection Tracking", "System continuously tracks cash, card, GCash, Maya, and bank transfers collected during the shift."),
        ("3. End-of-Day Blind Drawer Count", "Cashier submits physical cash count at shift end. System compares expected vs. actual drawer count."),
        ("4. Discrepancy & Overage/Shortage Posting", "Variance is automatically posted to Cash Short/Over Expense account for branch audit accountability.")
    ]

    for stitle, sdesc in shift_steps:
        p = tf_sh.add_paragraph()
        p.text = stitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        p = tf_sh.add_paragraph()
        p.text = sdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(6)

    # Right: Bank Statement Reconciliation
    add_card(s15, 6.75, 1.45, 5.75, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    tbx_bnk = s15.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.25), Inches(5.1))
    tf_bnk = tbx_bnk.text_frame
    tf_bnk.word_wrap = True

    p = tf_bnk.paragraphs[0]
    p.text = "Bank Statement Import & Automated Reconciliation"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_after = Pt(10)

    bnk_steps = [
        ("📥 Automated Bank Statement Import", "Upload daily/monthly bank CSV/Excel statements (e.g. BDO, BPI, GCash Merchant settlement files)."),
        ("🔍 Rule-Based Auto-Matching", "Reconciliation tool auto-matches bank deposits against ERPNext Payment Entries using transaction reference numbers, amounts, and dates."),
        ("⚡ 1-Click Discrepancy Clearance", "Clears matched transactions in the Bank Clearance ledger and identifies uncredited customer checks or bank charges."),
        ("📊 Reconciled Cash Position", "Provides finance leadership with true live cash positions across all branch bank accounts.")
    ]

    for btitle, bdesc in bnk_steps:
        p = tf_bnk.add_paragraph()
        p.text = btitle
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(2)

        p = tf_bnk.add_paragraph()
        p.text = bdesc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(7)

    # =========================================================================
    # SLIDE 16: Executive BI Dashboards & Management Visibility
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, BG_LIGHT)
    add_header(s16, "Executive Business Intelligence & Multi-Branch Visibility", "Executive Analytics")

    # 3 Column Cards
    # Col 1: Live Analytics Dashboard
    add_card(s16, 0.8, 1.45, col_width, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    eb1 = s16.shapes.add_textbox(Inches(0.95), Inches(1.65), Inches(3.45), Inches(5.1))
    et1 = eb1.text_frame
    et1.word_wrap = True
    
    p = et1.paragraphs[0]
    p.text = "📊 Live Analytics Desk Page"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    p.space_after = Pt(8)

    eitems1 = [
        "• URL: `/desk/vehicle_analytics`",
        "• Dynamic Multi-Filter: Filter by Company, branch, or date timespan (7D, 30D, YTD).",
        "• Revenue Split: Real-time visualization of Labor vs. Parts & Tires sales.",
        "• Top 10 Rankings: Highest billing labor services (PMS, Alignment) and top-selling tire SKUs."
    ]
    for itm in eitems1:
        p = et1.add_paragraph()
        p.text = itm
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Col 2: Dedicated Executive Portals
    add_card(s16, 0.8 + col_width + gap, 1.45, col_width, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    eb2 = s16.shapes.add_textbox(Inches(0.95 + col_width + gap), Inches(1.65), Inches(3.45), Inches(5.1))
    et2 = eb2.text_frame
    et2.word_wrap = True

    p = et2.paragraphs[0]
    p.text = "🏢 12 Dedicated Dashboards"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ORANGE_ACCENT
    p.space_after = Pt(8)

    eitems2 = [
        "• Executive Portals: Dedicated web portals for each of the 12 companies (e.g. `/executive-ultra-mrf-dau-main`).",
        "• Canonical Path Routing: Deep links directly open pre-filtered ERPNext Desk forms (`/desk/purchase-order?company=...`).",
        "• Pending Approvals Tab: High-level view of draft POs, Job Orders, and Invoices awaiting C-suite approval."
    ]
    for itm in eitems2:
        p = et2.add_paragraph()
        p.text = itm
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Col 3: Consolidated Financial Reporting
    add_card(s16, 0.8 + 2 * (col_width + gap), 1.45, col_width, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
    eb3 = s16.shapes.add_textbox(Inches(0.95 + 2 * (col_width + gap)), Inches(1.65), Inches(3.45), Inches(5.1))
    et3 = eb3.text_frame
    et3.word_wrap = True

    p = et3.paragraphs[0]
    p.text = "📈 Consolidated Financials"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    p.space_after = Pt(8)

    eitems3 = [
        "• Consolidated P&L: Real-time Profit & Loss statement rolling up all 12 corporate entities.",
        "• Accounts Receivable Aging: Track fleet corporate receivables by 0-30, 31-60, 61-90, 90+ days.",
        "• Inventory Turnover: Monitor fast-moving vs dead-stock tires across 3 central warehouses."
    ]
    for itm in eitems3:
        p = et3.add_paragraph()
        p.text = itm
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 17: Phased Rollout Plan & Implementation Roadmap
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17, BG_LIGHT)
    add_header(s17, "Phased Implementation Plan & Multi-Branch Rollout Schedule", "Implementation Strategy")

    phases = [
        ("PHASE 1: PROTOTYPE PILOT", "Weeks 1 – 4", "Automan Car Care Center", 
         "• Master Data & Service Catalog Setup\n• Touchscreen POS & Job Orders Live Pilot\n• QR Receiver Safety Handover Testing\n• BIR Invoicing & Staff Sign-Off",
         BLUE_ACCENT),
        ("PHASE 2: CENTRAL HUBS", "Weeks 5 – 7", "3 Central Warehouses", 
         "• Dau, San Fernando & Mexico Warehouses\n• 570-Bin QR Tagging & Physical Count\n• Automated Intercompany Order Flow\n• Minimum Re-Order Level Triggers",
         CYAN_ACCENT),
        ("PHASE 3: CLUSTER 1 BRANCHES", "Weeks 8 – 10", "Dau Main, Annex, San Fernando", 
         "• Rapid POS Terminal Deployment\n• Workshop Bay Hardware Setup (Tablets)\n• Cashier & Advisor Training\n• Live Cutover & Branch Hypercare",
         ORANGE_ACCENT),
        ("PHASE 4: CLUSTER 2 & GO-LIVE", "Weeks 11 – 12", "Wheel Core, Wheelhub, Telebastagan", 
         "• Onboard Remaining 3 Branches\n• Full Consolidated Executive BI Launch\n• Final External Audit Verification\n• Transition to BAU Maintenance",
         EMERALD_GREEN)
    ]

    for i, (ptitle, pdur, pscope, pdesc, paccent) in enumerate(phases):
        c_left = 0.8 + i * 2.98
        add_card(s17, c_left, 1.45, 2.78, 5.5, bg_color=WHITE, border_color=CARD_BORDER)
        
        # Header bar
        bar = s17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c_left), Inches(1.45), Inches(2.78), Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = paccent
        bar.line.fill.background()

        tbx = s17.shapes.add_textbox(Inches(c_left + 0.15), Inches(1.65), Inches(2.48), Inches(5.1))
        tf = tbx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = ptitle
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = paccent
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = pdur
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2)

        p = tf.add_paragraph()
        p.text = pscope
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        p.space_after = Pt(10)

        p = tf.add_paragraph()
        p.text = pdesc
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.line_spacing = 1.3

    # =========================================================================
    # SLIDE 18: Summary & Key Business Value
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, NAVY_DARK)
    add_header(s18, "Summary: Business Transformation & Strategic Value", "Conclusion & Impact", dark_mode=True)

    # 3 Summary Cards
    scards = [
        ("🏆 Operational Excellence",
         "Eliminates paper-based job orders and disjointed point solutions. Unifies 38,654 vehicles, 481+ job orders, and 570 bin locations into a synchronized digital workflow from vehicle intake to vehicle release.",
         BLUE_ACCENT),
        ("🛡️ 100% Financial & Stock Integrity",
         "Perpetual inventory tracking, mandatory QR receiver handover proof, and dual-ledger posting to standard ERPNext POS Invoices ensure zero stock slippage and audit-proof accounting.",
         EMERALD_GREEN),
        ("📈 Real-Time Multi-Branch Control",
         "Empowers executive leadership with live consolidated Profit & Loss, branch-by-branch rankings, labor vs. parts revenue splits, and 100% Philippine BIR CAS tax compliance.",
         ORANGE_ACCENT)
    ]

    for i, (title, desc, accent) in enumerate(scards):
        c_left = 0.8 + i * 3.95
        add_card(s18, c_left, 1.5, 3.75, 4.0, bg_color=NAVY_CARD, border_color=accent)
        
        tbx = s18.shapes.add_textbox(Inches(c_left + 0.2), Inches(1.7), Inches(3.35), Inches(3.6))
        tf = tbx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = accent
        p.space_after = Pt(12)
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(203, 213, 225)
        p2.line_spacing = 1.35

    # Bottom Contact / Sign-off bar
    s_bot = add_card(s18, 0.8, 5.8, 11.733, 1.2, bg_color=NAVY_CARD, border_color=RGBColor(51, 65, 85))
    s_tbx = s18.shapes.add_textbox(Inches(1.05), Inches(5.9), Inches(11.2), Inches(1.0))
    s_tf = s_tbx.text_frame
    s_tf.word_wrap = True

    p = s_tf.paragraphs[0]
    p.text = "ULTRA MRF • ERPNext v16 Enterprise Vehicle Management System (VMS)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_after = Pt(2)

    p = s_tf.add_paragraph()
    p.text = "Ready for Executive Review, Prototype Pilot Deployment, and Multi-Branch Enterprise Scaling."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(148, 163, 184)

    # Save presentation
    output_path = r"c:\Users\josem\erpnext-system\VEHICLE_MANAGEMENT_SYSTEM_OPERATIONS_TO_ACCOUNTING.pptx"
    prs.save(output_path)
    print(f"Successfully generated: {output_path}")

    # Also save a copy in docs/
    docs_path = r"c:\Users\josem\erpnext-system\docs\VEHICLE_MANAGEMENT_SYSTEM_OPERATIONS_TO_ACCOUNTING.pptx"
    prs.save(docs_path)
    print(f"Successfully generated copy in docs: {docs_path}")

if __name__ == "__main__":
    create_deck()
