import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
from frappe.utils import now_datetime

frappe.init(site='erp.localhost')
frappe.connect()

now = now_datetime()

with open('../executive_dashboard_template.html', 'r', encoding='utf-8') as f:
    template = f.read()

companies = frappe.db.sql('SELECT name FROM "tabCompany" WHERE name != %s ORDER BY name', ("My Company",), as_dict=True)

pages = [
    {
        "name": "executive",
        "title": "Executive Dashboard",
        "route": "executive",
        "company": "Ultra MRF Dau Main",
        "is_locked": False
    },
    {
        "name": "executive-dashboard",
        "title": "Executive Dashboard",
        "route": "executive-dashboard",
        "company": "Ultra MRF Dau Main",
        "is_locked": False
    }
]

for c in companies:
    co_name = c['name']
    slug = frappe.scrub(co_name).replace('_', '-')
    pages.append({
        "name": f"executive-{slug}",
        "title": f"{co_name} — Executive Dashboard",
        "route": f"executive-{slug}",
        "company": co_name,
        "is_locked": True
    })

created = 0
updated = 0

for p in pages:
    co = p['company']
    if p['is_locked']:
        sel_html = (
            f'<span class="exd-chip-ctx locked"><span class="k">Company</span><b>{co}</b></span>'
            f'<a href="/executive" class="exd-chip-ctx" style="text-decoration:none;cursor:pointer;color:var(--accent);font-weight:700;" title="Switch Company / View All"><span class="k">Switch</span><b>All Branches ↗</b></a>'
        )
        flag_str = "true"
    else:
        sel_html = '<select class="exd-select" id="companySel" title="Select Operating Company"></select>'
        flag_str = "false"

    html = template.replace('{{COMPANY_NAME}}', co)
    html = html.replace('{{COMPANY_SELECTOR_HTML}}', sel_html)
    html = html.replace('{{IS_LOCKED_FLAG}}', flag_str)

    exists = frappe.db.exists("Web Page", p["name"])
    if exists:
        frappe.db.sql("""
            UPDATE "tabWeb Page"
            SET title=%s, route=%s, content_type='HTML', main_section_html=%s, main_section=%s,
                published=1, full_width=1, show_title=0, show_sidebar=0, modified=%s, modified_by='Administrator'
            WHERE name=%s
        """, (p["title"], p["route"], html, html, now, p["name"]))
        updated += 1
    else:
        frappe.db.sql("""
            INSERT INTO "tabWeb Page"
            (name, title, route, content_type, main_section_html, main_section, published, full_width, show_title, show_sidebar, creation, modified, modified_by, owner, docstatus)
            VALUES (%s, %s, %s, 'HTML', %s, %s, 1, 1, 0, 0, %s, %s, 'Administrator', 'Administrator', 0)
        """, (p["name"], p["title"], p["route"], html, html, now, now))
        created += 1

frappe.db.commit()
frappe.clear_cache()

print(f"Deployed all Web Pages! Locked: 12, Hub: 2. Total: {created+updated}")
