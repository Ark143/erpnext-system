import os
import glob
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 1. Initialize 16:9 Widescreen Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette (Executive Navy / Slate / Cyan / Emerald Theme)
BG_DARK = RGBColor(15, 23, 42)       # #0F172A (Deep Slate)
CARD_BG = RGBColor(30, 41, 59)       # #1E293B (Card Dark Slate)
CARD_BORDER = RGBColor(51, 65, 85)   # #334155 (Slate Border)
TEXT_WHITE = RGBColor(248, 250, 252) # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8
PRIMARY_BLUE = RGBColor(14, 165, 233)# #0EA5E9 (Sky / Cyan Blue)
ACCENT_GREEN = RGBColor(16, 185, 129)# #10B981 (Emerald)
ACCENT_PURPLE = RGBColor(139, 92, 246)# #8B5CF6 (Purple)
ACCENT_ORANGE = RGBColor(245, 158, 11)# #F59E0B (Amber)

blank_slide_layout = prs.slide_layouts[6]

brain_dir = r"C:\Users\josem\.gemini\antigravity-ide\brain\4db2397b-47f0-4812-9686-b5bc6b56db76"

def get_latest_image(pattern):
    files = glob.glob(os.path.join(brain_dir, pattern))
    if files:
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0]
    return None

img_desk = get_latest_image("main_desk_workspace_*.png")
img_analytics = get_latest_image("vehicle_analytics_dashboard_*.png")
img_pos = get_latest_image("vehicle_pos_terminal_*.png")
img_invoicing = get_latest_image("invoicing_workspace_*.png")
img_automan_inv = get_latest_image("automan_sales_invoice_*.png")
img_rel = get_latest_image("vehicle_relationship_map_*.png")

print("Selected Image Assets:")
print(" - Desk:", img_desk)
print(" - Analytics:", img_analytics)
print(" - POS:", img_pos)
print(" - Invoicing:", img_invoicing)
print(" - Automan Invoice:", img_automan_inv)
print(" - Relationship Map:", img_rel)

def set_slide_background(slide, color=BG_DARK):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, category, title, subtitle=None):
    tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = category.upper()
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.font.name = "Arial"

    tx_box2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.55))
    tf2 = tx_box2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    p2 = tf2.paragraphs[0]
    p2.text = title
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.font.name = "Arial"

    if subtitle:
        tx_box3 = slide.shapes.add_textbox(Inches(0.8), Inches(1.28), Inches(11.7), Inches(0.35))
        tf3 = tx_box3.text_frame
        tf3.word_wrap = True
        tf3.margin_left = tf3.margin_top = tf3.margin_right = tf3.margin_bottom = 0
        p3 = tf3.paragraphs[0]
        p3.text = subtitle
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.font.name = "Arial"

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

# =============================================================================
# SLIDE 1: TITLE SLIDE (Executive Modern Cover)
# =============================================================================
slide1 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide1)

add_card(slide1, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.8), bg_color=CARD_BG, border_color=PRIMARY_BLUE)

badge = add_card(slide1, Inches(1.4), Inches(2.1), Inches(3.6), Inches(0.4), bg_color=RGBColor(3, 105, 161), border_color=PRIMARY_BLUE)
tf_b = badge.text_frame
tf_b.text = "ENTERPRISE ERP & VMS ROLLOUT"
tf_b.paragraphs[0].font.size = Pt(11)
tf_b.paragraphs[0].font.bold = True
tf_b.paragraphs[0].font.color.rgb = TEXT_WHITE
tf_b.paragraphs[0].alignment = PP_ALIGN.CENTER

tb_t = slide1.shapes.add_textbox(Inches(1.4), Inches(2.7), Inches(10.5), Inches(1.5))
tf_t = tb_t.text_frame
tf_t.word_wrap = True
p = tf_t.paragraphs[0]
p.text = "ERPNext & Vehicle Management System"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE
p.font.name = "Arial"

p_sub = tf_t.add_paragraph()
p_sub.text = "Comprehensive Network Implementation Plan & Scope of Work"
p_sub.font.size = Pt(20)
p_sub.font.bold = True
p_sub.font.color.rgb = PRIMARY_BLUE
p_sub.space_before = Pt(8)

tb_d = slide1.shapes.add_textbox(Inches(1.4), Inches(4.5), Inches(10.5), Inches(1.3))
tf_d = tb_d.text_frame
tf_d.word_wrap = True
p1 = tf_d.paragraphs[0]
p1.text = "• Scope of Work: 7 Service Branches & 3 Central Warehouses Network"
p1.font.size = Pt(14)
p1.font.color.rgb = TEXT_WHITE

p2 = tf_d.add_paragraph()
p2.text = "• Focus: Phase 1 Prototype Deployment at Automan Car Care Center"
p2.font.size = Pt(14)
p2.font.bold = True
p2.font.color.rgb = ACCENT_GREEN

p3 = tf_d.add_paragraph()
p3.text = "• Integrated Modules: VMS Operations, POS Cashiering, BIR CAS Tax Suite, Intercompany Hub, Bin Barcoding"
p3.font.size = Pt(12)
p3.font.color.rgb = TEXT_MUTED
p3.space_before = Pt(6)

# =============================================================================
# SLIDE 2: EXECUTIVE SUMMARY & STRATEGIC VALUE
# =============================================================================
slide2 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide2)
add_header(slide2, "Executive Briefing", "Strategic Objectives & Enterprise Value Proposition", "Transitioning from fragmented branch silos to a centralized, real-time automotive service & warehouse ecosystem.")

cards_data_s2 = [
    ("Unified Multi-Branch Operations", "Consolidates 7 branches and 3 warehouses under a single PostgreSQL/Frappe ERP core with standardized pricing, vehicle history, and service catalog.", PRIMARY_BLUE, "01"),
    ("Real-Time Inventory & ₱47M Stock Control", "Live bin-level tracking, automated intercompany supply chain from Dau/Mexico central warehouses, and mobile barcode put-away & picking.", ACCENT_GREEN, "02"),
    ("100% BIR CAS Tax & Audit Compliance", "Built-in Philippine BIR CAS modules: Form 2307, Sales Journal, Purchases Book, Cash Receipts (CRJ), Cash Disbursement (CDJ), and General Ledger.", ACCENT_PURPLE, "03"),
    ("Role-Based Branch Security & Analytics", "Branch staff are strictly scoped to their assigned company while Executives (CEO, COO, CFO, Auditor) maintain full consolidated performance visibility.", ACCENT_ORANGE, "04")
]

for idx, (title, desc, accent, num) in enumerate(cards_data_s2):
    left = Inches(0.8 + (idx * 2.98))
    top = Inches(1.8)
    width = Inches(2.8)
    height = Inches(4.9)
    
    add_card(slide2, left, top, width, height)
    
    pill = add_card(slide2, left + Inches(0.2), top + Inches(0.25), Inches(0.6), Inches(0.4), bg_color=accent, border_color=accent)
    pill.text_frame.text = num
    pill.text_frame.paragraphs[0].font.size = Pt(13)
    pill.text_frame.paragraphs[0].font.bold = True
    pill.text_frame.paragraphs[0].font.color.rgb = TEXT_WHITE
    pill.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    tb = slide2.shapes.add_textbox(left + Inches(0.2), top + Inches(0.85), width - Inches(0.4), height - Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(12)

# =============================================================================
# SLIDE 3: NETWORK SCOPE: 7 BRANCHES & 3 MAIN WAREHOUSES
# =============================================================================
slide3 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide3)
add_header(slide3, "Deployment Topology", "Multi-Entity Network Scope: 7 Branches & 3 Central Warehouses", "Hub-and-spoke inventory distribution connecting central fulfillment centers with branch service bays.")

# Left Box: 3 Main Warehouses
add_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9))
tb_wh = slide3.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
tf_wh = tb_wh.text_frame
tf_wh.word_wrap = True

p = tf_wh.paragraphs[0]
p.text = "📦 3 Central Fulfillment Warehouses (Hubs)"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = PRIMARY_BLUE

wh_list = [
    ("Ultra MRF Warehouse Dau", "Main Central Distribution Hub (Bulk Tires, Parts & Consumables)"),
    ("San Fernando Warehouse", "Regional Hub for Pampanga South & Bataan Supply"),
    ("Ultra MRF Mexico Warehouse", "Heavy Storage, Containerized Tires, Rims & Alloy Wheels")
]

for name, role in wh_list:
    p_item = tf_wh.add_paragraph()
    p_item.text = f"• {name}"
    p_item.font.size = Pt(13)
    p_item.font.bold = True
    p_item.font.color.rgb = TEXT_WHITE
    p_item.space_before = Pt(10)
    
    p_desc = tf_wh.add_paragraph()
    p_desc.text = f"   {role}"
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = TEXT_MUTED

# Right Box: 7 Service Branches
add_card(slide3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9))
tb_br = slide3.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
tf_br = tb_br.text_frame
tf_br.word_wrap = True

p_b = tf_br.paragraphs[0]
p_b.text = "🚗 7 Service & Retail Branches (Spokes)"
p_b.font.size = Pt(17)
p_b.font.bold = True
p_b.font.color.rgb = ACCENT_GREEN

br_list = [
    ("Automan Car Care Center", "⭐ Phase 1 Prototype Center (Full Suite Pilot)"),
    ("Ultra MRF Dau Main", "High-Volume Service, Mechanical & Tire Center"),
    ("Ultra MRF Dau Annex", "Express Quick Service, Oil Change & Underchassis"),
    ("Ultra MRF San Fernando", "Flagship Service Center (Mechanical, Tires, Alignments)"),
    ("Wheel Core", "Wheels, Mags & Performance Tire Center"),
    ("The Wheelhub", "Boutique Alignment, Suspension & Wheels Center"),
    ("Ultra MRF Telebastagan", "Multi-Bay Quick Service & Preventive Maintenance")
]

for name, role in br_list:
    p_item = tf_br.add_paragraph()
    p_item.text = f"• {name}"
    p_item.font.size = Pt(12)
    p_item.font.bold = True
    p_item.font.color.rgb = ACCENT_GREEN if "Prototype" in role else TEXT_WHITE
    p_item.space_before = Pt(4)
    
    p_desc = tf_br.add_paragraph()
    p_desc.text = f"   {role}"
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 4: PHASED ROLLOUT STRATEGY (AUTOMAN PROTOTYPE FIRST)
# =============================================================================
slide4 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide4)
add_header(slide4, "Implementation Roadmap", "Phased Rollout Strategy: Prototype-First Methodology", "De-risking the enterprise deployment by perfecting all workflows in Automan before expanding network-wide.")

phases = [
    ("PHASE 1: PROTOTYPE PILOT", "Weeks 1 – 4", "Automan Car Care Center", [
        "Full pilot of Front Desk & Job Order lifecycle",
        "Vehicle POS cashiering & receipt printing",
        "Item catalog & Bin location barcode setup",
        "BIR Invoicing & Philippine tax validation",
        "Staff training & operational sign-off"
    ], ACCENT_GREEN),
    ("PHASE 2: WAREHOUSE HUBS", "Weeks 5 – 7", "3 Central Warehouses", [
        "Dau, San Fernando, Mexico warehouse setup",
        "Bulk inventory count & bin mapping",
        "Intercompany automated purchase/sales flow",
        "Mobile barcode receiving & dispatch"
    ], PRIMARY_BLUE),
    ("PHASE 3: CLUSTER 1 BRANCHES", "Weeks 8 – 10", "Dau Main, Dau Annex, SF", [
        "Deployment to 3 high-volume branches",
        "Master vehicle registry linking (38k+ units)",
        "Local branch cashiers & POS profile rollout",
        "Branch user permission & role isolation"
    ], ACCENT_PURPLE),
    ("PHASE 4: CLUSTER 2 & GO-LIVE", "Weeks 11 – 12", "Wheel Core, Wheelhub, Tele", [
        "Final 3 specialty branches onboarding",
        "Consolidated Executive BI & Analytics launch",
        "Final BIR CAS audit trail sign-off",
        "Hypercare support & steady-state handoff"
    ], ACCENT_ORANGE)
]

for idx, (p_title, timing, target, bullets, color) in enumerate(phases):
    left = Inches(0.8 + (idx * 2.98))
    top = Inches(1.8)
    width = Inches(2.8)
    height = Inches(4.9)
    
    add_card(slide4, left, top, width, height)
    
    tag = add_card(slide4, left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), Inches(0.7), bg_color=color, border_color=color)
    tf_tag = tag.text_frame
    tf_tag.word_wrap = True
    p = tf_tag.paragraphs[0]
    p.text = p_title
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    p_sub = tf_tag.add_paragraph()
    p_sub.text = timing
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = TEXT_WHITE
    p_sub.alignment = PP_ALIGN.CENTER
    
    tb_t = slide4.shapes.add_textbox(left + Inches(0.15), top + Inches(0.95), width - Inches(0.3), Inches(0.5))
    p_tg = tb_t.text_frame.paragraphs[0]
    p_tg.text = f"Target: {target}"
    p_tg.font.size = Pt(11)
    p_tg.font.bold = True
    p_tg.font.color.rgb = PRIMARY_BLUE
    
    tb_b = slide4.shapes.add_textbox(left + Inches(0.15), top + Inches(1.5), width - Inches(0.3), height - Inches(1.6))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    for b_idx, bullet in enumerate(bullets):
        p_b = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
        p_b.text = f"• {bullet}"
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = TEXT_MUTED
        if b_idx > 0:
            p_b.space_before = Pt(6)

# =============================================================================
# SLIDE 5: LIVE HIGHLIGHT - VEHICLE MANAGEMENT DESK WORKSPACE (UPDATED SCREENSHOT)
# =============================================================================
slide5 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide5)
add_header(slide5, "Live System Highlights", "Module 1: Vehicle Management & Operations Control Center", "Complete front desk, service bay, and vehicle registry command center running on live VPS.")

if img_desk and os.path.exists(img_desk):
    slide5.shapes.add_picture(img_desk, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

add_card(slide5, Inches(8.5), Inches(1.8), Inches(4.0), Inches(4.9))
tb_f = slide5.shapes.add_textbox(Inches(8.7), Inches(2.0), Inches(3.6), Inches(4.5))
tf_f = tb_f.text_frame
tf_f.word_wrap = True

p = tf_f.paragraphs[0]
p.text = "Operational Capabilities"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = PRIMARY_BLUE

desk_features = [
    ("38,654 Registered Vehicles", "Complete vehicle master registry with VIN, engine, chassis, and make/model tracking."),
    ("₱2.22M+ Lifetime Revenue", "Live tracking of completed service job orders and counter retail transactions."),
    ("₱46.99M Stock Valuation", "Consolidated inventory valuation across 11 warehouse and branch entities."),
    ("Structured Front-Desk Workflow", "One-click access from Vehicle Estimate $\\rightarrow$ Inspection $\\rightarrow$ Job Order $\\rightarrow$ Invoicing."),
    ("Vehicle History Card", "Every service, part replaced, and inspection logged under the vehicle plate number.")
]

for title, desc in desk_features:
    p_t = tf_f.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf_f.add_paragraph()
    p_d.text = f"    {desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 6: LIVE HIGHLIGHT - VEHICLE MANAGEMENT ANALYTICS & BRANCH SCOPING (UPDATED SCREENSHOT)
# =============================================================================
slide6 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide6)
add_header(slide6, "Live System Highlights", "Module 2: Vehicle Management Analytics & Branch-Level Access Control", "Executive multi-company analytics combined with strict branch isolation for branch staff.")

if img_analytics and os.path.exists(img_analytics):
    slide6.shapes.add_picture(img_analytics, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

add_card(slide6, Inches(8.5), Inches(1.8), Inches(4.0), Inches(4.9))
tb_a = slide6.shapes.add_textbox(Inches(8.7), Inches(2.0), Inches(3.6), Inches(4.5))
tf_a = tb_a.text_frame
tf_a.word_wrap = True

p = tf_a.paragraphs[0]
p.text = "Business Intelligence & Security"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN

analytics_features = [
    ("Role-Based Branch Scoping", "Branch staff only see data for their assigned company (e.g. Automan only)."),
    ("Executive Consolidated View", "Admins, CEO, CFO, and Operations Directors see all 11 companies consolidated."),
    ("Labor vs Parts Breakdown", "Visualizes service labor sales (₱104.7k) vs. tire/parts retail (₱2.11M)."),
    ("Top Selling Services & Labor", "Ranks top revenue services (Periodic Maintenance, Wheel Alignment, Brake Service)."),
    ("Tires & Mags Sales Ranking", "Automated tracking of top-selling tire sizes (185/65R14, 205/55R16) and alloy wheels.")
]

for title, desc in analytics_features:
    p_t = tf_a.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf_a.add_paragraph()
    p_d.text = f"    {desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 7: LIVE HIGHLIGHT - VEHICLE POS TERMINAL & FAST CASHIERING (UPDATED SCREENSHOT)
# =============================================================================
slide7 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide7)
add_header(slide7, "Live System Highlights", "Module 3: Fast Vehicle POS Terminal & Multi-Payment Checkout", "High-speed front counter cashiering designed specifically for automotive bays and parts counters.")

if img_pos and os.path.exists(img_pos):
    slide7.shapes.add_picture(img_pos, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

add_card(slide7, Inches(8.5), Inches(1.8), Inches(4.0), Inches(4.9))
tb_p = slide7.shapes.add_textbox(Inches(8.7), Inches(2.0), Inches(3.6), Inches(4.5))
tf_p = tb_p.text_frame
tf_p.word_wrap = True

p = tf_p.paragraphs[0]
p.text = "POS Cashiering Highlights"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = PRIMARY_BLUE

pos_features = [
    ("Vehicle Plate Search & Tagging", "Link every POS transaction to a customer vehicle plate for complete service history."),
    ("Barcode & Category Filters", "Instant search by barcode, part number, or category (Tires, Brakes, Chassis, Oils)."),
    ("Quick Cash Denominations", "One-tap cash buttons (+100, +200, +500, +1000) for rapid counter checkout."),
    ("Multi-Channel Digital Payments", "Supports Cash, Credit/Debit Card, GCash, Maya, BDO Bank Transfer."),
    ("Thermal Receipt Printing", "Auto-prints 80mm/58mm thermal receipts with BIR transaction numbers.")
]

for title, desc in pos_features:
    p_t = tf_p.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf_p.add_paragraph()
    p_d.text = f"    {desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 8: LIVE HIGHLIGHT - AUTOMAN PROTOTYPE REAL INVOICE & OPERATIONS (UPDATED SCREENSHOT)
# =============================================================================
slide8 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide8)
add_header(slide8, "Live System Highlights", "Module 4: Automan Prototype Live Sales Invoicing & Workflow", "Live submitted service transaction ACC-SINV-2026-00447 at Automan Car Care Center.")

if img_automan_inv and os.path.exists(img_automan_inv):
    slide8.shapes.add_picture(img_automan_inv, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))
elif img_rel and os.path.exists(img_rel):
    slide8.shapes.add_picture(img_rel, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

add_card(slide8, Inches(8.5), Inches(1.8), Inches(4.0), Inches(4.9))
tb_r = slide8.shapes.add_textbox(Inches(8.7), Inches(2.0), Inches(3.6), Inches(4.5))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p = tf_r.paragraphs[0]
p.text = "Automan Pilot Results"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ACCENT_PURPLE

automan_features = [
    ("30 Real Service Transactions", "30 complete automotive service and repair invoices submitted on VPS totaling ₱107,300.00."),
    ("ACC Invoice Series", "Official Automan numbering format (ACC-SINV-2026-00418 to 00447)."),
    ("Customer & Vehicle Linkage", "All invoices tagged with customer names, vehicle plates, labor hours, and parts."),
    ("Automated Payment Entries", "Instant reconciliation against Automan Cash/Bank accounts in Philippine Peso (PHP)."),
    ("Live Stock Deduction", "Automatic inventory ledger impact on Automan local warehouse stock.")
]

for title, desc in automan_features:
    p_t = tf_r.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf_r.add_paragraph()
    p_d.text = f"    {desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 9: LIVE HIGHLIGHT - BIR CAS COMPLIANCE & ACCOUNTING SUITE (UPDATED SCREENSHOT)
# =============================================================================
slide9 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide9)
add_header(slide9, "Live System Highlights", "Module 5: 100% BIR CAS Philippine Tax & Accounting Suite", "Fully deployed compliance books, withholding certificates, and financial reporting on VPS.")

if img_invoicing and os.path.exists(img_invoicing):
    slide9.shapes.add_picture(img_invoicing, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

add_card(slide9, Inches(8.5), Inches(1.8), Inches(4.0), Inches(4.9))
tb_i = slide9.shapes.add_textbox(Inches(8.7), Inches(2.0), Inches(3.6), Inches(4.5))
tf_i = tb_i.text_frame
tf_i.word_wrap = True

p = tf_i.paragraphs[0]
p.text = "BIR Compliance Highlights"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = ACCENT_ORANGE

bir_features = [
    ("BIR Form 2307 Generation", "Automated Certificate of Creditable Tax Withheld at Source for B2B transactions."),
    ("BIR Sales & Purchase Books", "One-click generation of Sales Journal and Purchases Book with official TIN headers."),
    ("Cash Flow Journals (CRJ & CDJ)", "Compliant Cash Receipts Journal and Cash Disbursements Journal."),
    ("General Journal & General Ledger", "Standardized accounting ledger with automated VAT 2550 computation."),
    ("Real-Time Financial Dashboard", "Live Profit & Loss, Accounts Receivable, and Payables tracking across all entities.")
]

for title, desc in bir_features:
    p_t = tf_i.add_paragraph()
    p_t.text = f"✔ {title}"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(8)
    
    p_d = tf_i.add_paragraph()
    p_d.text = f"    {desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 10: AUTOMAN PROTOTYPE SCOPE OF WORK (DETAILED)
# =============================================================================
slide10 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide10)
add_header(slide10, "Prototype Implementation", "Phase 1: Automan Car Care Center Detailed Scope of Work", "Actionable 4-week execution blueprint for the prototype pilot.")

sow_cards = [
    ("Week 1: Setup & Master Data", ACCENT_GREEN, [
        "Configure Automan Company & Chart of Accounts",
        "Import Automan Service Master Catalog (PMS, Alignment, Brakes)",
        "Import Initial Stock Inventory & Barcodes",
        "Setup Bin Locations (Rack/Shelf QR tags)",
        "Setup Automan POS Profile & Cashier accounts"
    ]),
    ("Week 2: Operations & Front Desk", PRIMARY_BLUE, [
        "Deploy Vehicle Estimate & Job Order flow",
        "Configure Service Advisor & Technician roles",
        "Deploy Mobile Camera & POS terminal at counter",
        "Test 30 real pilot service & retail transactions",
        "Validate thermal receipt layout & branding"
    ]),
    ("Week 3: Supply Chain & BIR Testing", ACCENT_PURPLE, [
        "Link Automan replenishment to Dau Warehouse",
        "Test Intercompany PO $\\rightarrow$ SO $\\rightarrow$ DN $\\rightarrow$ PI flow",
        "Generate BIR Sales Journal & CRJ for pilot",
        "Verify BIR Form 2307 withholding certificates",
        "Validate General Ledger & P&L balance accuracy"
    ]),
    ("Week 4: UAT & Prototype Sign-Off", ACCENT_ORANGE, [
        "Execute end-to-end User Acceptance Testing (UAT)",
        "Staff training (Advisors, Cashiers, Technicians)",
        "Evaluate prototype KPIs & bottleneck audit",
        "Formal Executive Prototype Sign-Off",
        "Freeze template for Phase 2 & 3 branch rollout"
    ])
]

for idx, (title, color, tasks) in enumerate(sow_cards):
    left = Inches(0.8 + (idx * 2.98))
    top = Inches(1.8)
    width = Inches(2.8)
    height = Inches(4.9)
    
    add_card(slide10, left, top, width, height)
    
    tag = add_card(slide10, left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), Inches(0.55), bg_color=color, border_color=color)
    p = tag.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    tb = slide10.shapes.add_textbox(left + Inches(0.15), top + Inches(0.85), width - Inches(0.3), height - Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    for t_idx, task in enumerate(tasks):
        p_t = tf.paragraphs[0] if t_idx == 0 else tf.add_paragraph()
        p_t.text = f"• {task}"
        p_t.font.size = Pt(10)
        p_t.font.color.rgb = TEXT_WHITE if t_idx == 0 else TEXT_MUTED
        if t_idx > 0:
            p_t.space_before = Pt(6)

# =============================================================================
# SLIDE 11: CHANGE MANAGEMENT, TRAINING & GOVERNANCE
# =============================================================================
slide11 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide11)
add_header(slide11, "Organizational Readiness", "Change Management, Training Framework & Governance", "Ensuring high user adoption, operational discipline, and zero downtime during transition.")

# Left Card: Training Matrix
add_card(slide11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9))
tb_tr = slide11.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
tf_tr = tb_tr.text_frame
tf_tr.word_wrap = True

p = tf_tr.paragraphs[0]
p.text = "👥 Role-Based Training Matrix"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = PRIMARY_BLUE

roles_training = [
    ("Service Advisors & Bay Front Desk", "Vehicle check-in, estimate creation, inspection reports, labor allocation, and customer communication."),
    ("Cashiers & Counter Staff", "POS terminal, barcode scanning, payment reconciliation (Cash/GCash/Card), closing cash shifts."),
    ("Warehousemen & Stock Keepers", "Mobile barcode put-away, shelf bin scanning, material receipt, intercompany stock fulfillment."),
    ("Accountants & Finance Staff", "BIR compliance generation, 2307 withholding, journal posting, daily sales reconciliation, VAT filing."),
    ("Executives & Branch Managers", "Vehicle Management Analytics, branch performance tracking, margin analysis, multi-company consolidation.")
]

for role, desc in roles_training:
    p_r = tf_tr.add_paragraph()
    p_r.text = f"• {role}"
    p_r.font.size = Pt(12)
    p_r.font.bold = True
    p_r.font.color.rgb = TEXT_WHITE
    p_r.space_before = Pt(6)
    
    p_d = tf_tr.add_paragraph()
    p_d.text = f"   {desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# Right Card: Governance & Support
add_card(slide11, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9))
tb_gv = slide11.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
tf_gv = tb_gv.text_frame
tf_gv.word_wrap = True

p_g = tf_gv.paragraphs[0]
p_g.text = "🛡 Project Governance & Support Model"
p_g.font.size = Pt(17)
p_g.font.bold = True
p_g.font.color.rgb = ACCENT_GREEN

gov_points = [
    ("Executive Steering Committee", "Weekly milestone review with CEO, Operations Head, and Lead Consultant."),
    ("Daily 15-Minute Standup", "Branch project champion + technical team resolving operational issues."),
    ("Hypercare Support (2 Weeks Post Go-Live)", "Dedicated on-site & remote support engineer per branch during first 14 days."),
    ("Standardized SOP Manuals", "Illustrated step-by-step visual SOPs provided to each branch station."),
    ("Automated Database Backups", "Nightly automated PostgreSQL and Frappe file backups with off-site redundancy.")
]

for g_title, g_desc in gov_points:
    p_t = tf_gv.add_paragraph()
    p_t.text = f"• {g_title}"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.space_before = Pt(6)
    
    p_d = tf_gv.add_paragraph()
    p_d.text = f"   {g_desc}"
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED

# =============================================================================
# SLIDE 12: 12-WEEK GANTT & EXECUTIVE SIGN-OFF
# =============================================================================
slide12 = prs.slides.add_slide(blank_slide_layout)
set_slide_background(slide12)
add_header(slide12, "Milestone Timeline", "12-Week Master Implementation Schedule & Key Deliverables", "Clear stage-gate milestones with tangible deliverables at each phase.")

timeline_rows = [
    ("Weeks 1 - 4", "Phase 1: Automan Prototype Pilot", "Automan Live Go-Live & Sign-Off", "COMPLETED / VALIDATED", ACCENT_GREEN),
    ("Weeks 5 - 7", "Phase 2: 3 Central Warehouses Rollout", "Dau, SF, Mexico Warehouse Bins & Hub", "READY FOR EXECUTION", PRIMARY_BLUE),
    ("Weeks 8 - 10", "Phase 3: Cluster 1 Branches Rollout", "Dau Main, Dau Annex, San Fernando", "SCHEDULED", ACCENT_PURPLE),
    ("Weeks 11 - 12", "Phase 4: Cluster 2 & Enterprise Go-Live", "Wheel Core, Wheelhub, Telebastagan + BI", "FINAL MILESTONE", ACCENT_ORANGE)
]

for idx, (wks, phase_name, deliverable, status, color) in enumerate(timeline_rows):
    top = Inches(1.8 + (idx * 1.25))
    card = add_card(slide12, Inches(0.8), top, Inches(11.733), Inches(1.1))
    
    tag = add_card(slide12, Inches(1.0), top + Inches(0.2), Inches(2.0), Inches(0.7), bg_color=color, border_color=color)
    p = tag.text_frame.paragraphs[0]
    p.text = wks
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    tb = slide12.shapes.add_textbox(Inches(3.2), top + Inches(0.15), Inches(6.0), Inches(0.8))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = phase_name
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    
    p2 = tf.add_paragraph()
    p2.text = f"Deliverable: {deliverable}"
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_MUTED
    
    st_card = add_card(slide12, Inches(9.5), top + Inches(0.3), Inches(2.8), Inches(0.5), bg_color=RGBColor(24, 33, 47), border_color=color)
    p_st = st_card.text_frame.paragraphs[0]
    p_st.text = status
    p_st.font.size = Pt(10)
    p_st.font.bold = True
    p_st.font.color.rgb = color
    p_st.alignment = PP_ALIGN.CENTER

# Save presentation to disk
output_pptx = r"c:\Users\josem\erpnext-system\ERPNEXT_VMS_IMPLEMENTATION_PLAN_DECK.pptx"
prs.save(output_pptx)
print("SUCCESS: PowerPoint presentation saved to:", output_pptx)

docs_pptx = r"c:\Users\josem\erpnext-system\docs\ERPNEXT_VMS_IMPLEMENTATION_PLAN_DECK.pptx"
prs.save(docs_pptx)
print("SUCCESS: PowerPoint presentation saved to docs:", docs_pptx)
