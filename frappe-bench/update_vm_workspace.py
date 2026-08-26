import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
import json

frappe.init(site='erp.localhost')
frappe.connect()

# Read workspace JSON
workspace_json_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'apps/vehicle_management/vehicle_management/vehicle_management/workspace/vehicle_management/vehicle_management.json'
))

with open(workspace_json_path, 'r', encoding='utf-8') as f:
    ws_data = json.load(f)

now = frappe.utils.now_datetime()

exists = frappe.db.exists('Workspace', 'Vehicle Management')
if exists:
    # Update content and links
    frappe.db.sql(
        'UPDATE "tabWorkspace" SET content=%s, modified=%s, modified_by=%s WHERE name=%s',
        (ws_data['content'], now, 'Administrator', 'Vehicle Management')
    )
    print('Workspace content updated')
    
    # Remove existing links
    frappe.db.sql('DELETE FROM "tabWorkspace Link" WHERE parent=%s', ('Vehicle Management',))
    print('Old links deleted')
    
    # Insert new links (cards)
    idx = 1
    for card in ws_data.get('links', []):
        card_label = card.get('label', '')
        card_type = card.get('type', 'Card Break')
        
        frappe.db.sql(
            'INSERT INTO "tabWorkspace Link" (name, parent, parenttype, parentfield, idx, label, type, hidden, is_query_report) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (f'vm-link-{idx}', 'Vehicle Management', 'Workspace', 'links', idx, card_label, card_type, 0, 0)
        )
        idx += 1
        
        for link in card.get('links', []):
            frappe.db.sql(
                'INSERT INTO "tabWorkspace Link" (name, parent, parenttype, parentfield, idx, label, type, link_to, link_type, hidden, is_query_report, onboard) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (f'vm-link-{idx}', 'Vehicle Management', 'Workspace', 'links', idx,
                 link.get('label', ''), 'Link', link.get('link_to', ''), link.get('link_type', 'DocType'),
                 link.get('hidden', 0), link.get('is_query_report', 0), link.get('onboard', 0))
            )
            idx += 1
    
    print(f'Inserted {idx-1} workspace links')

frappe.db.commit()

# Clear cache
frappe.clear_cache()
print('Cache cleared!')
print('Done!')
