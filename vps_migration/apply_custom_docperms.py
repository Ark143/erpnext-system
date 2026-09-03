import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

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

# 1. First delete existing Custom DocPerm for target doctypes
for dt in roles_config.keys():
    try:
        r_list = opener.open('http://38.247.138.224:10017/api/resource/Custom%20DocPerm?filters=' + urllib.parse.quote(json.dumps([['parent', '=', dt]])) + '&limit_page_length=50')
        existing = json.loads(r_list.read().decode())['data']
        for item in existing:
            del_req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Custom%20DocPerm/' + urllib.parse.quote(item['name']), method='DELETE')
            opener.open(del_req)
        print(f"Cleared existing Custom DocPerms for {dt}")
    except Exception as e:
        print(f"Clear error on {dt}:", e)

# 2. Insert new Custom DocPerms
created_count = 0
for dt, perms in roles_config.items():
    for idx, p in enumerate(perms, 1):
        doc_payload = {
            'parent': dt,
            'parenttype': 'DocType',
            'parentfield': 'permissions',
            'role': p['role'],
            'idx': idx,
            'permlevel': 0,
            'read': p.get('read', 0),
            'write': p.get('write', 0),
            'create': p.get('create', 0),
            'delete': p.get('delete', 0),
            'submit': p.get('submit', 0),
            'cancel': p.get('cancel', 0),
            'amend': p.get('amend', 0),
            'print': p.get('print', 0),
            'export': p.get('export', 0),
            'report': 1
        }
        try:
            post_req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Custom%20DocPerm', data=json.dumps(doc_payload).encode(), headers=H, method='POST')
            opener.open(post_req)
            created_count += 1
        except Exception as e:
            print(f"Error creating perm {p['role']} for {dt}:", e)

print(f"Successfully created {created_count} Custom DocPerms across all Vehicle Management DocTypes!")
