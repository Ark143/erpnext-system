#!/usr/bin/env python3
"""Patch the served Web Page (vehicle-pos-terminal) main_section_html:
1. Replace 'V' placeholder icons with the company logo (profile card, HTML ID card, download SVG).
2. Add responsive rules so the Cashier ID fits mobile/tablet/pc without scrolling.
"""
import frappe, base64, os

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")

logo_path = "/workspace/frappe-bench/sites/site1.local/public/files/ultra_mrf_logo.png"
logo_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
LOGO_DATA_URL = "data:image/png;base64," + logo_b64
LOGO_URL = "/files/ultra_mrf_logo.png"
print("logo data url len:", len(LOGO_DATA_URL))

d = frappe.get_doc("Web Page", "vehicle-pos-terminal")
html = d.main_section_html or ""
orig_len = len(html)

def rep(old, new, label):
    global html
    n = html.count(old)
    if n == 0:
        print(f"  !! NOT FOUND ({n}): {label}")
        return False
    html = html.replace(old, new)
    print(f"  ok ({n}x): {label}")
    return True

# 1. Profile card logo (HTML)
rep('<div class="vpos-prof-logo">V</div>',
    f'<div class="vpos-prof-logo"><img src="{LOGO_URL}" alt="company logo"></div>',
    "profile logo")

# 2. HTML ID card logo (header)
rep('<div class="vpos-id-logo">V</div>',
    f'<div class="vpos-id-logo"><img src="{LOGO_URL}" alt="company logo"></div>',
    "idcard header logo")

# 3. Download SVG card: mint badge + "V" -> company logo image
rep('<!-- Mint accent logo badge -->',
    '<!-- Company logo -->', "svg comment")
rep('<rect x="28" y="22" width="58" height="58" rx="14" fill="url(#mintg)"/>\n  <text x="57" y="63" font-family="Arial,Helvetica,sans-serif" font-size="38" font-weight="900" fill="#04201a" text-anchor="middle">V</text>',
    f'<image x="30" y="24" width="54" height="54" href="{LOGO_DATA_URL}" preserveAspectRatio="xMidYMid meet"/>',
    "svg logo image")

# 4. CSS: logo img sizing + white bg (so PNG shows, not mint icon block)
rep('.vpos-prof-logo { width: 50px; height: 50px; border-radius: 14px; background: var(--mint); color: #04201a; font-family: var(--font-head); font-weight: 800; font-size: 26px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; }',
    '.vpos-prof-logo { width: 64px; height: 64px; border-radius: 14px; background: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; overflow: hidden; border: 1px solid var(--line); }',
    "prof logo css")
rep('.vpos-id-logo { width: 26px; height: 26px; border-radius: 7px; background: var(--mint); color: #04201a; font-family: var(--font-head); font-weight: 700; font-size: 15px; display: flex; align-items: center; justify-content: center; }',
    '.vpos-id-logo { width: 30px; height: 30px; border-radius: 7px; background: #fff; display: flex; align-items: center; justify-content: center; overflow: hidden; }',
    "id logo css")

# add img sizing rule after the prof-logo rule
rep('.vpos-prof-card h3 {',
    '.vpos-prof-logo img, .vpos-id-logo img { width: 100%; height: 100%; object-fit: contain; display: block; }\n.vpos-prof-card h3 {',
    "img sizing rule")

# 5. Responsive: idcard + profile fit mobile (no scroll)
rep('@media print {',
    '''/* Cashier ID responsive: fit mobile/tablet/pc, no scroll */
@media (max-width: 768px) {
  .vpos-prof { padding: 6px 0 16px; }
  .vpos-prof-card { padding: 16px; width: 100%; }
  .vpos-prof-qr svg { width: 150px; height: 150px; }
  .vpos-prof-row { font-size: 12px; }
  .vpos-idcard { width: 100% !important; height: auto !important; aspect-ratio: 85.6 / 54; }
  .vpos-id-head { padding: 5px 8px; }
  .vpos-id-logo { width: 24px; height: 24px; }
  .vpos-id-qr { width: 34mm; height: 34mm; flex-basis: 34mm; }
  .vpos-id-qr svg { width: 100%; height: 100%; }
  .vpos-id-name { font-size: 12px; }
  .vpos-id-line { font-size: 8px; }
}
@media (min-width: 769px) and (max-width: 1024px) {
  .vpos-prof-card { width: 400px; }
}
@media print {''',
    "responsive + print")

print("orig len:", orig_len, "-> new len:", len(html))

# persist
frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
frappe.db.commit()
print("PATCHED + committed")
# verify read-back
rb = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
print("readback len:", len(rb), "has logo img:", LOGO_URL in rb, "has data url:", "data:image/png;base64" in rb)
