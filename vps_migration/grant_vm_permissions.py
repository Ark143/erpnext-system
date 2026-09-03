import urllib.request, urllib.parse, json, time

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Update Workspace/Vehicle Management roles
ws_url = 'http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management'
r_ws = opener.open(ws_url)
ws_data = json.loads(r_ws.read().decode())['data']

target_roles = ['System Manager', 'Desk User', 'Sales User', 'Sales Manager', 'Maintenance User', 'Maintenance Manager', 'Stock User', 'Stock Manager', 'Accounts User']

ws_roles = [{'role': r} for r in target_roles]
ws_update_payload = json.dumps({'public': 1, 'roles': ws_roles}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(ws_url, data=ws_update_payload, headers=H, method='PUT')
res = opener.open(req)
print("Updated Workspace/Vehicle Management roles: HTTP", res.status)

# 2. Configure Custom DocPerm for all Vehicle Management DocTypes
# Server Script to update Custom DocPerm safely via frappe python API
grant_perms_py = """
roles_config = {
    'Customer Vehicle': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1, 'export': 1},
        {'role': 'Sales Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1, 'export': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
        {'role': 'Maintenance Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1, 'export': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
        {'role': 'Stock Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
        {'role': 'Stock User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
        {'role': 'Desk User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
    ],
    'Vehicle Inspection': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1, 'print': 1, 'export': 1},
        {'role': 'Maintenance Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1, 'print': 1, 'export': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'submit': 1, 'print': 1, 'export': 1},
        {'role': 'Sales Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'submit': 1, 'print': 1, 'export': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
        {'role': 'Desk User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
    ],
    'Vehicle Job Order': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1, 'print': 1, 'export': 1},
        {'role': 'Maintenance Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1, 'print': 1, 'export': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'submit': 1, 'print': 1, 'export': 1},
        {'role': 'Sales Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
        {'role': 'Desk User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
    ],
    'Vehicle Estimate': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1, 'print': 1, 'export': 1},
        {'role': 'Sales Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'submit': 1, 'cancel': 1, 'amend': 1, 'print': 1, 'export': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'submit': 1, 'print': 1, 'export': 1},
        {'role': 'Maintenance Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1, 'export': 1},
    ],
    'Vehicle Service Reminder': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1, 'export': 1},
        {'role': 'Sales Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
    ],
    'Vehicle Make': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1},
        {'role': 'Desk User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
    ],
    'Vehicle Model': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1},
        {'role': 'Desk User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
        {'role': 'Sales User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
    ],
    'Inspection Template': [
        {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'print': 1},
        {'role': 'Maintenance Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 0, 'print': 1},
        {'role': 'Maintenance User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
        {'role': 'Sales User', 'read': 1, 'write': 0, 'create': 0, 'delete': 0, 'print': 1},
    ]
}

for parent_dt, perm_list in roles_config.items():
    # Remove existing Custom DocPerms for this parent
    frappe.db.delete("Custom DocPerm", {"parent": parent_dt})
    
    # Insert new Custom DocPerms
    for idx, p in enumerate(perm_list, 1):
        cdp = frappe.new_doc("Custom DocPerm")
        cdp.parent = parent_dt
        cdp.parenttype = "DocType"
        cdp.parentfield = "permissions"
        cdp.role = p['role']
        cdp.idx = idx
        cdp.permlevel = 0
        for k, v in p.items():
            if k != 'role':
                setattr(cdp, k, v)
        cdp.flags.ignore_permissions = True
        cdp.insert()

frappe.clear_cache()
frappe.response['message'] = 'Permissions granted successfully!'
"""

# Create Server Script to execute permission setup
script_payload = json.dumps({
    'script_type': 'API',
    'api_method': 'vm_setup_user_permissions',
    'allow_guest': 0,
    'script': grant_perms_py
}).encode()

# Upsert Server Script
ss_url = 'http://38.247.138.224:10017/api/resource/Server%20Script/vm_setup_user_permissions'
try:
    req = urllib.request.Request(ss_url, data=script_payload, headers=H, method='PUT')
    opener.open(req)
    print("Updated Server Script vm_setup_user_permissions")
except:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=script_payload, headers=H, method='POST')
    opener.open(req)
    print("Created Server Script vm_setup_user_permissions")

# Execute setup method
r_exec = opener.open('http://38.247.138.224:10017/api/method/vm_setup_user_permissions')
print("Execution result:", r_exec.read().decode())
