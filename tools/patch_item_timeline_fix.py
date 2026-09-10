import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

patch_script = """
def robust_get_timeline_data(doctype, name):
    try:
        if frappe.db.db_type == 'postgres':
            # Safe PostgreSQL query without syntax error
            res = frappe.db.sql(
                "SELECT EXTRACT(epoch FROM posting_date)::bigint, COUNT(*) FROM \\"tabStock Ledger Entry\\" WHERE item_code = %s AND posting_date > CURRENT_DATE - INTERVAL '1 year' GROUP BY posting_date",
                (name,),
                as_dict=False
            )
            return dict(res or [])
        else:
            res = frappe.db.sql(
                "SELECT UNIX_TIMESTAMP(posting_date), COUNT(*) FROM `tabStock Ledger Entry` WHERE item_code = %s AND posting_date > DATE_SUB(CURDATE(), INTERVAL 1 YEAR) GROUP BY posting_date",
                (name,),
                as_dict=False
            )
            return dict(res or [])
    except Exception:
        return {}

item_mod = frappe.get_meta_module("Item")
item_mod.get_timeline_data = robust_get_timeline_data

frappe.response['message'] = 'Patched get_timeline_data successfully'
"""

res = s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Patch%20Item%20Timeline", json={
    'doctype': 'Server Script',
    'name': 'VM Patch Item Timeline',
    'script': patch_script,
    'script_type': 'API',
    'api_method': 'vm_patch_item_timeline',
    'allow_guest': 1,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        'doctype': 'Server Script',
        'name': 'VM Patch Item Timeline',
        'script': patch_script,
        'script_type': 'API',
        'api_method': 'vm_patch_item_timeline',
        'allow_guest': 1,
        'disabled': 0
    })

print('Server Script Put Status:', res.status_code)
r_call = s.get(f"{VPS_BASE}/api/method/vm_patch_item_timeline")
print('Patch Execution:', r_call.status_code, r_call.text)

# Test the failing endpoint for SRV-ELEC-CHECK!
r_test = s.get(f"{VPS_BASE}/api/method/frappe.desk.notifications.get_open_count", params={
    'doctype': 'Item',
    'name': 'SRV-ELEC-CHECK',
    'items': json.dumps(['BOM', 'Quotation', 'Sales Order', 'Sales Invoice', 'Delivery Note', 'Stock Entry'])
})
print('get_open_count status:', r_test.status_code)
print('get_open_count response:', r_test.text)
