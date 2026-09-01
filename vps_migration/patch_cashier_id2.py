#!/usr/bin/env python3
import frappe, base64
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

logo_path = "/workspace/frappe-bench/sites/site1.local/public/files/ultra_mrf_logo.png"
logo_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
LOGO_DATA_URL = "data:image/png;base64," + logo_b64

html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
orig = len(html)

def rep(old, new, label):
    global html
    n = html.count(old)
    if n == 0:
        print(f"  !! NOT FOUND: {label}")
        return False
    html = html.replace(old, new)
    print(f"  ok ({n}x): {label}")
    return True

# 1. Download SVG: replace mint rect + "V" text with company logo image
rep("""'<rect x="8" y="5" width="22" height="22" rx="5" fill="#16c784"/>'+""",
    """'<image x="8" y="4" width="24" height="24" href=""" + repr(LOGO_DATA_URL) + """ preserveAspectRatio="xMidYMid meet"/>'+""",
    "svg mint rect -> logo image")
rep("""'<text x="34" y="13" font-family="Space Grotesk,Arial,sans-serif" font-size="14" font-weight="700" fill="#04201a">V</text>'+""",
    """'<text x="34" y="13" font-family="Space Grotesk,Arial,sans-serif" font-size="12" font-weight="700" fill="#04201a"></text>'+""",
    "svg V text removed")

# 2. prof-logo CSS: white bg + img containment
rep(".vpos-prof-logo{width:48px;height:48px;border-radius:12px;background:var(--mint);color:#04201a;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:24px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px}",
    ".vpos-prof-logo{width:64px;height:64px;border-radius:12px;background:#fff;border:1px solid var(--line);display:flex;align-items:center;justify-content:center;margin:0 auto 8px;overflow:hidden}",
    "prof-logo css")

# 3. id-logo CSS: white bg + img containment
rep(".vpos-id-logo{width:26px;height:26px;border-radius:7px;background:var(--mint);color:#04201a;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center;}",
    ".vpos-id-logo{width:30px;height:30px;border-radius:7px;background:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden}",
    "id-logo css")

# 4. img sizing rule (anchor before .vpos-prof-card h3)
rep(".vpos-prof-card h3{",
    ".vpos-prof-logo img,.vpos-id-logo img{width:100%;height:100%;object-fit:contain;display:block}.vpos-prof-card h3{",
    "img sizing rule")

# 5. responsive block before @media print
rep("@media print{",
    """/* Cashier ID responsive: fit mobile/tablet/pc, no scroll */
@media (max-width:768px){.vpos-prof{padding:6px 0 16px}.vpos-prof-card{padding:16px;width:100%}.vpos-prof-qr svg{width:150px;height:150px}.vpos-prof-row{font-size:12px}.vpos-idcard{width:100%!important;height:auto!important;aspect-ratio:85.6/54}.vpos-id-head{padding:5px 8px}.vpos-id-logo{width:24px;height:24px}.vpos-id-qr{width:34mm;height:34mm;flex-basis:34mm}.vpos-id-qr svg{width:100%;height:100%}.vpos-id-name{font-size:12px}.vpos-id-line{font-size:8px}}
@media (min-width:769px) and (max-width:1024px){.vpos-prof-card{width:400px}}
@media print{""",
    "responsive + print")

print("orig", orig, "-> new", len(html))

frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
frappe.db.commit()
rb = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
print("readback len:", len(rb), "| logo url:", "/files/ultra_mrf_logo.png" in rb, "| data url:", "data:image/png;base64" in rb, "| responsive:", "aspect-ratio:85.6/54" in rb)
