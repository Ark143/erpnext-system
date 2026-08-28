import sys, os, subprocess, shutil, json

print("=" * 65)
print("  BUILDING COMPLETE GITHUB PAGES LIVE PORTAL")
print("=" * 65)

# 1. Create a build directory
build_dir = os.path.abspath("gh_pages_build")
os.makedirs(build_dir, exist_ok=True)

# 2. Extract company dashboards HTML from deploy_all_company_webpages.py
deploy_file = os.path.join("frappe-bench", "deploy_all_company_webpages.py")
if not os.path.exists(deploy_file):
    deploy_file = "deploy_all_company_webpages.py"

with open(deploy_file, "r", encoding="utf-8") as f:
    deploy_code = f.read()

# Locate the HTML template inside get_dashboard_html
start_marker = 'return f"""'
end_marker = '"""\n\n'
start_idx = deploy_code.find(start_marker)
if start_idx != -1:
    start_idx += len(start_marker)
    end_idx = deploy_code.find(end_marker, start_idx)
    raw_template = deploy_code[start_idx:end_idx]
else:
    print("Error: Could not extract HTML template from get_dashboard_html")
    sys.exit(1)

COMPANIES = [
    ("Ultra MRF Dau Main", "executive-ultra-mrf-dau-main.html", "Dau, Mabalacat, Pampanga"),
    ("Automan Car Care Center", "executive-automan-car-care-center.html", "San Fernando, Pampanga"),
    ("The Wheelhub", "executive-the-wheelhub.html", "Angeles City, Pampanga"),
    ("San Fernando Warehouse", "executive-san-fernando-warehouse.html", "San Fernando, Pampanga"),
    ("Ultra MRF Telebastagan", "executive-ultra-mrf-telebastagan.html", "Telebastagan, City of San Fernando"),
    ("Wheel Core", "executive-wheel-core.html", "Central Luzon"),
    ("ULTRA MRF", "executive-ultra-mrf.html", "Main Headquarters"),
    ("Ultra MRF Dau Annex", "executive-ultra-mrf-dau-annex.html", "Dau Annex Branch"),
    ("Ultra MRF Mexico Warehouse", "executive-ultra-mrf-mexico-warehouse.html", "Mexico, Pampanga"),
    ("Ultra MRF San Fernando", "executive-ultra-mrf-san-fernando.html", "San Fernando Branch"),
    ("Ultra MRF Telebastagan 2", "executive-ultra-mrf-telebastagan-2.html", "Telebastagan 2 Branch"),
    ("Ultra MRF Warehouse Dau", "executive-ultra-mrf-warehouse-dau.html", "Warehouse Dau Hub")
]

# Generate standalone HTML for each company
for comp_name, filename, location in COMPANIES:
    comp_html = raw_template.replace("{default_company}", comp_name)
    # un-escape {{ }} to { }
    comp_html = comp_html.replace("{{", "{").replace("}}", "}")
    with open(os.path.join(build_dir, filename), "w", encoding="utf-8") as f:
        f.write(comp_html)

# Also create main executive dashboard
with open(os.path.join(build_dir, "executive.html"), "w", encoding="utf-8") as f:
    main_html = raw_template.replace("{default_company}", "Ultra MRF Dau Main").replace("{{", "{").replace("}}", "}")
    f.write(main_html)

# 3. Copy POS Terminal as pos.html & pos_terminal.html + pos_export.json
pos_path = os.path.join("frappe-bench", "apps", "vehicle_management", "vehicle_management", "www", "pos_terminal.html")
if os.path.exists(pos_path):
    with open(pos_path, "r", encoding="utf-8") as f:
        pos_html = f.read()
    pos_html = pos_html.replace('{% extends "templates/web.html" %}', '')
    pos_html = pos_html.replace('{% block page_content %}', '')
    pos_html = pos_html.replace('{% endblock %}', '')
    with open(os.path.join(build_dir, "pos.html"), "w", encoding="utf-8") as f:
        f.write(pos_html)
    with open(os.path.join(build_dir, "pos_terminal.html"), "w", encoding="utf-8") as f:
        f.write(pos_html)

pos_json = os.path.join("frappe-bench", "apps", "vehicle_management", "vehicle_management", "www", "pos_export.json")
if os.path.exists(pos_json):
    shutil.copy(pos_json, os.path.join(build_dir, "pos_export.json"))

# 4. Copy Logo Assets
assets_dir = os.path.join(build_dir, "files")
os.makedirs(assets_dir, exist_ok=True)
src_logo = os.path.join("frappe-bench", "sites", "site1.local", "public", "files", "ultra_mrf_logo.png")
if os.path.exists(src_logo):
    shutil.copy(src_logo, os.path.join(assets_dir, "ultra_mrf_logo.png"))
    shutil.copy(src_logo, os.path.join(build_dir, "ultra_mrf_logo.png"))

# 5. Build Master Landing Index (`index.html`)
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ULTRA MRF Automotive — Live Cloud Portal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Inter+Tight:wght@700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #0B0F19;
  --card: #131B2E;
  --card-border: #1E293B;
  --accent: #3B82F6;
  --accent-glow: rgba(59, 130, 246, 0.25);
  --text: #F8FAFC;
  --muted: #94A3B8;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}}
.bg-glow {{
  position: fixed;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: 1000px;
  height: 600px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, rgba(139, 92, 246, 0.1) 40%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}}
.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
  position: relative;
  z-index: 10;
  width: 100%;
}}
.header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--card-border);
  margin-bottom: 40px;
  flex-wrap: wrap;
  gap: 18px;
}}
.brand {{
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  color: inherit;
}}
.brand img {{
  height: 44px;
  width: auto;
  border-radius: 8px;
  background: #FFFFFF;
  padding: 4px;
}}
.brand-title {{
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
}}
.brand-sub {{
  font-size: 12.5px;
  color: var(--muted);
  font-weight: 500;
}}
.status-pill {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10B981;
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 12.5px;
  font-weight: 700;
}}
.status-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px #10B981;
}}
.hero {{
  text-align: center;
  margin-bottom: 44px;
}}
.hero h1 {{
  font-family: 'Inter Tight', sans-serif;
  font-size: 38px;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.hero p {{
  color: var(--muted);
  font-size: 16px;
  max-width: 680px;
  margin: 0 auto;
  line-height: 1.5;
}}
.grid-primary {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 22px;
  margin-bottom: 48px;
}}
.card-featured {{
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 28px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}}
.card-featured:hover {{
  transform: translateY(-5px);
  border-color: var(--accent);
  box-shadow: 0 16px 36px -8px var(--accent-glow);
}}
.card-icon-box {{
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}}
.card-title {{
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 8px;
  color: #FFFFFF;
}}
.card-desc {{
  font-size: 13.5px;
  color: var(--muted);
  line-height: 1.45;
  margin-bottom: 20px;
  flex: 1;
}}
.card-action {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--accent);
}}
.section-title {{
  font-size: 20px;
  font-weight: 800;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}}
.grid-branches {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}}
.branch-pill {{
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 16px 18px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}}
.branch-pill:hover {{
  background: #1A243D;
  border-color: #38BDF8;
  transform: translateY(-2px);
}}
.branch-name {{
  font-size: 14.5px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 4px;
}}
.branch-loc {{
  font-size: 12px;
  color: var(--muted);
}}
.footer {{
  text-align: center;
  padding: 32px 0 20px;
  color: #64748B;
  font-size: 12.5px;
  border-top: 1px solid var(--card-border);
  margin-top: 60px;
}}
</style>
</head>
<body>
<div class="bg-glow"></div>
<div class="container">
  <header class="header">
    <a href="/" class="brand">
      <img src="ultra_mrf_logo.png" alt="Ultra MRF Logo"/>
      <div>
        <div class="brand-title">ULTRA MRF Automotive</div>
        <div class="brand-sub">Enterprise Management & Analytics Cloud</div>
      </div>
    </a>
    <div class="status-pill">
      <span class="status-dot"></span>
      Live Cloud Online
    </div>
  </header>

  <div class="hero">
    <h1>Automotive Operations & Executive Portals</h1>
    <p>Access real-time branch performance dashboards, inventory bin locations, and POS terminals from any device or internet connection.</p>
  </div>

  <div class="grid-primary">
    <!-- Featured 1: Executive Dashboard (Dau Main) -->
    <a href="executive-ultra-mrf-dau-main.html" class="card-featured">
      <div>
        <div class="card-icon-box" style="background: rgba(59, 130, 246, 0.15); color: #3B82F6;">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9" rx="1.4"/><rect x="14" y="3" width="7" height="5" rx="1.4"/><rect x="14" y="12" width="7" height="9" rx="1.4"/><rect x="3" y="16" width="7" height="5" rx="1.4"/></svg>
        </div>
        <div class="card-title">Executive Dashboard (Main Dau)</div>
        <div class="card-desc">Comprehensive executive summary, sales, procurement, approvals, and multi-zone warehouse bin location tracking.</div>
      </div>
      <div class="card-action">Launch Dashboard &rarr;</div>
    </a>

    <!-- Featured 2: Automan Car Care Center -->
    <a href="executive-automan-car-care-center.html" class="card-featured">
      <div>
        <div class="card-icon-box" style="background: rgba(16, 185, 129, 0.15); color: #10B981;">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>
        </div>
        <div class="card-title">Automan Car Care Center</div>
        <div class="card-desc">Dedicated service center operations, job orders, technician task metrics, and automotive service KPIs.</div>
      </div>
      <div class="card-action" style="color: #10B981;">Launch Dashboard &rarr;</div>
    </a>

    <!-- Featured 3: POS Terminal -->
    <a href="pos.html" class="card-featured">
      <div>
        <div class="card-icon-box" style="background: rgba(139, 92, 246, 0.15); color: #8B5CF6;">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="card-title">Vehicle POS & Cashier Terminal</div>
        <div class="card-desc">Fast front-counter cashier point of sale, customer vehicle selector, tire mounting/balancing labor, and receipt generation.</div>
      </div>
      <div class="card-action" style="color: #8B5CF6;">Launch POS &rarr;</div>
    </a>
  </div>

  <div class="section-title">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
    All Operating Branch Dashboards
  </div>

  <div class="grid-branches">
"""

for comp_name, filename, location in COMPANIES:
    index_html += f"""    <a href="{filename}" class="branch-pill">
      <div class="branch-name">{comp_name}</div>
      <div class="branch-loc">{location}</div>
    </a>\n"""

index_html += """  </div>

  <footer class="footer">
    &copy; 2026 ULTRA MRF Automotive &bull; Enterprise Management System &bull; Powered by Frappe & ERPNext
  </footer>
</div>
</body>
</html>
"""

with open(os.path.join(build_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("[OK] GitHub Pages build directory prepared with all branch dashboards, POS, and landing portal.")
