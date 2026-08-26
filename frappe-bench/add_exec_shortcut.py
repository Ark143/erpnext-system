import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
from frappe.utils import now_datetime
import json

frappe.init(site='erp.localhost')
frappe.connect()

now = now_datetime()

# Add Executive Dashboard shortcut to Vehicle Management workspace
ws = frappe.db.sql('SELECT content FROM "tabWorkspace" WHERE name = %s', ('Vehicle Management',), as_dict=True)[0]
content = json.loads(ws.content)

existing_ids = [item.get('id') for item in content]
if 'shortcut_exec_dash' not in existing_ids:
    content.append({"id": "shortcut_exec_dash", "type": "shortcut", "data": {"shortcut_name": "Executive Dashboard"}})

frappe.db.sql(
    'UPDATE "tabWorkspace" SET content=%s, modified=%s, modified_by=%s WHERE name=%s',
    (json.dumps(content), now, 'Administrator', 'Vehicle Management')
)

exists = frappe.db.sql(
    'SELECT name FROM "tabWorkspace Shortcut" WHERE name=%s AND parent=%s',
    ('Executive Dashboard', 'Vehicle Management'), as_dict=True
)
if not exists:
    frappe.db.sql(
        '''INSERT INTO "tabWorkspace Shortcut"
           (name, parent, parenttype, parentfield, idx, label, url, type, color, creation, modified, modified_by, owner, docstatus)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)''',
        ('Executive Dashboard', 'Vehicle Management', 'Workspace', 'shortcuts', 12,
         'Executive Dashboard', '/executive', 'URL', 'Green', now, now, 'Administrator', 'Administrator')
    )
    print("Added Executive Dashboard shortcut to workspace!")

frappe.db.commit()
frappe.clear_cache()
print("Workspace updated!")
