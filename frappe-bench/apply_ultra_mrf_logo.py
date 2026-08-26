"""
Script to:
1. Process ULTRA MRF logo (black on white, transparent, and white on dark).
2. Generate SVG and PNG variants.
3. Save to public files and override system SVGs (loading splash screen & app logos).
4. Update Navbar Settings, Website Settings, and Company records.
"""

import sys, os, base64, io
from PIL import Image, ImageOps

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))

import frappe

frappe.init("site1.local")
frappe.connect()

SRC_PATH = r"C:\Users\josem\Desktop\pxc\ultr\logo.jpg"
if not os.path.exists(SRC_PATH):
    SRC_PATH = r"C:\Users\josem\.gemini\antigravity-ide\brain\1c80b847-ae06-4625-b3a2-bf74676d3227\.user_uploaded\media_1787522534190.jpg"

print(f"Loading logo from {SRC_PATH}...")
img = Image.open(SRC_PATH).convert("RGBA")
w, h = img.size

# 1. Crisp PNG with white background
img_white_bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
img_white_bg.paste(img, (0, 0), img)

# 2. Transparent background version: Make pure white / near-white transparent
datas = img.getdata()
new_data_dark = []
new_data_white = []

for item in datas:
    # item is (R, G, B, A)
    # Check brightness / grayscale value
    brightness = (item[0] + item[1] + item[2]) / 3.0
    if brightness > 220:
        # Transparent for dark logo on transparent bg
        new_data_dark.append((0, 0, 0, 0))
        new_data_white.append((255, 255, 255, 0))
    else:
        # Dark pixel
        alpha = int((1.0 - (brightness / 255.0)) * 255)
        new_data_dark.append((10, 10, 10, 255))
        # Inverted white pixel for dark mode
        new_data_white.append((255, 255, 255, 255))

img_transparent = Image.new("RGBA", (w, h))
img_transparent.putdata(new_data_dark)

img_white_text = Image.new("RGBA", (w, h))
img_white_text.putdata(new_data_white)

bench_dir = os.path.dirname(os.path.abspath(__file__))

# Directories to write to
sites_public_files = os.path.join(bench_dir, "sites", "site1.local", "public", "files")
os.makedirs(sites_public_files, exist_ok=True)

# Save PNGs to public files
logo_png_path = os.path.join(sites_public_files, "ultra_mrf_logo.png")
logo_transparent_path = os.path.join(sites_public_files, "ultra_mrf_logo_transparent.png")
logo_white_path = os.path.join(sites_public_files, "ultra_mrf_logo_white.png")

img_white_bg.save(logo_png_path, "PNG")
img_transparent.save(logo_transparent_path, "PNG")
img_white_text.save(logo_white_path, "PNG")

# Convert transparent PNG to base64 for embedding in SVGs
buffered_dark = io.BytesIO()
img_transparent.save(buffered_dark, format="PNG")
img_b64_dark = base64.b64encode(buffered_dark.getvalue()).decode("utf-8")

buffered_white = io.BytesIO()
img_white_text.save(buffered_white, format="PNG")
img_b64_white = base64.b64encode(buffered_white.getvalue()).decode("utf-8")

svg_content_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <image width="{w}" height="{h}" xlink:href="data:image/png;base64,{img_b64_dark}"/>
</svg>'''

svg_content_white = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <image width="{w}" height="{h}" xlink:href="data:image/png;base64,{img_b64_white}"/>
</svg>'''

# Save SVGs
logo_svg_path = os.path.join(sites_public_files, "ultra_mrf_logo.svg")
with open(logo_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content_dark)

# List of all standard SVG files to replace across Frappe and ERPNext
svg_destinations_dark = [
    os.path.join(bench_dir, "apps", "frappe", "frappe", "public", "images", "frappe-framework-logo.svg"),
    os.path.join(bench_dir, "apps", "frappe", "frappe", "public", "images", "frappe-logo.svg"),
    os.path.join(bench_dir, "apps", "erpnext", "erpnext", "public", "images", "erpnext-logo.svg"),
    os.path.join(bench_dir, "apps", "erpnext", "erpnext", "public", "images", "erp-logo.svg"),
]

svg_destinations_white = [
    os.path.join(bench_dir, "apps", "frappe", "frappe", "public", "images", "frappe-framework-logo-white.svg"),
    os.path.join(bench_dir, "apps", "erpnext", "erpnext", "public", "images", "erpnext-logo-white.svg"),
]

for dst in svg_destinations_dark:
    with open(dst, "w", encoding="utf-8") as f:
        f.write(svg_content_dark)
    print(f"  Replaced dark SVG: {dst}")

for dst in svg_destinations_white:
    with open(dst, "w", encoding="utf-8") as f:
        f.write(svg_content_white)
    print(f"  Replaced white SVG: {dst}")

# Also replace standard PNG assets
png_destinations = [
    os.path.join(bench_dir, "apps", "frappe", "frappe", "public", "images", "frappe-framework-logo.png"),
    os.path.join(bench_dir, "apps", "frappe", "frappe", "public", "images", "frappe-logo.png"),
    os.path.join(bench_dir, "apps", "erpnext", "erpnext", "public", "images", "erpnext-logo.png"),
    os.path.join(bench_dir, "apps", "erpnext", "erpnext", "public", "images", "erpnext-logo-blue.png"),
]

for dst in png_destinations:
    img_transparent.save(dst, "PNG")
    print(f"  Replaced PNG: {dst}")

# 3. Update Website Settings & Navbar Settings in Database
print("\nUpdating Frappe Settings...")

# Navbar Settings
navbar = frappe.get_single("Navbar Settings")
navbar.app_logo = "/files/ultra_mrf_logo.png"
navbar.save(ignore_permissions=True)
print("  Navbar Settings -> app_logo = /files/ultra_mrf_logo.png")

# Website Settings
ws = frappe.get_single("Website Settings")
ws.app_logo = "/files/ultra_mrf_logo.png"
ws.banner_image = "/files/ultra_mrf_logo.png"
ws.splash_image = "/files/ultra_mrf_logo.png"
ws.app_name = "ULTRA MRF"
ws.save(ignore_permissions=True)
print("  Website Settings -> app_logo, banner_image, splash_image, app_name = ULTRA MRF")

# Update all Companies
companies = frappe.get_all("Company", fields=["name"])
for c in companies:
    frappe.db.set_value("Company", c.name, "company_logo", "/files/ultra_mrf_logo.png")
print(f"  Updated company_logo for {len(companies)} Companies")

# Create or update standard Letterhead
if not frappe.db.exists("Letter Head", "ULTRA MRF"):
    lh = frappe.get_doc({
        "doctype": "Letter Head",
        "letter_head_name": "ULTRA MRF",
        "is_default": 1,
        "content": '<div style="text-align: center; margin-bottom: 20px;"><img src="/files/ultra_mrf_logo.png" style="max-height: 80px;" /><p style="margin-top: 5px; font-size: 13px; font-weight: bold; letter-spacing: 2px;">TIRES • MAGS • SERVICES</p></div>'
    })
    lh.insert(ignore_permissions=True)
    print("  Created default Letter Head: ULTRA MRF")
else:
    frappe.db.set_value("Letter Head", "ULTRA MRF", "content", '<div style="text-align: center; margin-bottom: 20px;"><img src="/files/ultra_mrf_logo.png" style="max-height: 80px;" /><p style="margin-top: 5px; font-size: 13px; font-weight: bold; letter-spacing: 2px;">TIRES • MAGS • SERVICES</p></div>')
    print("  Updated default Letter Head: ULTRA MRF")

frappe.db.commit()
print("\nLogo updates complete!")
