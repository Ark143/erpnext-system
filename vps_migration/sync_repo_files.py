import urllib.request, urllib.parse, json, os

URL = 'http://38.247.138.224:10017'
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open(f'{URL}/api/method/login', data=b'usr=Administrator&pwd=admin')
H = {'Accept': 'application/json'}

# 1. Fetch Workspace doc
res_ws = opener.open(urllib.request.Request(f'{URL}/api/resource/Workspace/Vehicle%20Management', headers=H))
ws_data = json.loads(res_ws.read().decode()).get('data', {})

ws_file = os.path.join(
    r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\vehicle_management\workspace\vehicle_management\vehicle_management.json'
)
with open(ws_file, 'w', encoding='utf-8') as f:
    json.dump(ws_data, f, indent=1, ensure_ascii=False)
print(f"Updated local repo file: {ws_file}")

# 2. Fetch Workspace Sidebar doc
res_sb = opener.open(urllib.request.Request(f'{URL}/api/resource/Workspace%20Sidebar/Vehicle%20Management', headers=H))
sb_data = json.loads(res_sb.read().decode()).get('data', {})

sb_file = os.path.join(
    r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\workspace_sidebar\vehicle_management\vehicle_management.json'
)
with open(sb_file, 'w', encoding='utf-8') as f:
    json.dump(sb_data, f, indent=1, ensure_ascii=False)
print(f"Updated local repo file: {sb_file}")

# 3. Update vehicle_management_desk.js
desk_js_file = os.path.join(
    r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\public\js\vehicle_management_desk.js'
)

with open(r'c:\Users\josem\erpnext-system\vps_migration\deploy_vm_header_client_script.py', 'r', encoding='utf-8') as f:
    content = f.read()
    # extract js_snippet
    start = content.find('js_snippet = """') + len('js_snippet = """\n')
    end = content.find('"""\n\nscript_doc = {')
    js_code = content[start:end]

with open(desk_js_file, 'w', encoding='utf-8') as f:
    f.write(js_code)
print(f"Updated local repo file: {desk_js_file}")
