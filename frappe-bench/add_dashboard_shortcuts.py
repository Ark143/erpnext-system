import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

# Add web dashboard shortcut to the Vehicle Management workspace
import json
from frappe.utils import now_datetime

now = now_datetime()

# Read current workspace
ws = frappe.db.sql(
    'SELECT content FROM "tabWorkspace" WHERE name = %s',
    ('Vehicle Management',), as_dict=True
)[0]

# Parse content and add dashboard shortcuts
content = json.loads(ws.content)

# Check if already added
existing_ids = [item.get('id') for item in content]
if 'shortcut_hub' not in existing_ids:
    content.append({"id": "shortcut_hub", "type": "shortcut", "data": {"shortcut_name": "VM Company Hub"}})
if 'shortcut_co_dash' not in existing_ids:
    content.append({"id": "shortcut_co_dash", "type": "shortcut", "data": {"shortcut_name": "VM Company Dashboard"}})

# Update workspace content
frappe.db.sql(
    'UPDATE "tabWorkspace" SET content=%s, modified=%s, modified_by=%s WHERE name=%s',
    (json.dumps(content), now, 'Administrator', 'Vehicle Management')
)

# Add shortcuts to tabWorkspace Shortcut
shortcuts_to_add = [
    ("VM Company Hub", "/vm-dashboard", "URL", "Purple"),
    ("VM Company Dashboard", "/vm-company-dashboard", "URL", "Blue"),
]

for sc_name, sc_url, sc_type, sc_color in shortcuts_to_add:
    exists = frappe.db.sql(
        'SELECT name FROM "tabWorkspace Shortcut" WHERE name=%s AND parent=%s',
        (sc_name, 'Vehicle Management'), as_dict=True
    )
    if not exists:
        frappe.db.sql(
            '''INSERT INTO "tabWorkspace Shortcut"
               (name, parent, parenttype, parentfield, idx, label, url, type, color, creation, modified, modified_by, owner, docstatus)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)''',
            (sc_name, 'Vehicle Management', 'Workspace', 'shortcuts', 10,
             sc_name, sc_url, sc_type, sc_color, now, now, 'Administrator', 'Administrator')
        )
        print(f'Added shortcut: {sc_name}')

frappe.db.commit()
frappe.clear_cache()

print('\nWorkspace updated!')
print('\n=== Dashboard URLs ===')
print('Hub:       http://erp.localhost/vm-dashboard')
print('Dashboard: http://erp.localhost/vm-company-dashboard')
print()
print('Per-company direct links:')
companies = frappe.db.sql(
    'SELECT name, abbr FROM "tabCompany" WHERE name != %s ORDER BY name',
    ('My Company',), as_dict=True
)
for c in companies:
    slug = c['name'].replace(' ', '+')
    print(f'  [{c["abbr"]:8s}] http://erp.localhost/vm-company-dashboard?company={slug}')
