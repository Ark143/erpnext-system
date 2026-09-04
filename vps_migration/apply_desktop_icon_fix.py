import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

ss_url = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Meta'
r = opener.open(ss_url)
doc = json.loads(r.read().decode())['data']
script_content = doc['script']

# Remove previous helper block
if 'if frappe.form_dict.get("cmd_action") == "fix_desktop_icon":' in script_content:
    lines = script_content.split('\n')
    cleaned_lines = []
    skip = False
    for l in lines:
        if 'if frappe.form_dict.get("cmd_action") == "fix_desktop_icon":' in l:
            skip = True
        elif skip and l.startswith('    '):
            continue
        else:
            skip = False
            cleaned_lines.append(l)
    script_clean = '\n'.join(cleaned_lines).strip()
else:
    script_clean = script_content

helper_clean = """if frappe.form_dict.get("cmd_action") == "fix_desktop_icon":
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "link_type", "External")
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "link", "/desk/vehicle-management")
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "icon", "car")
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "hidden", 0)
    frappe.response["message"] = "SET_VALUE_SUCCESS"
"""

payload = json.dumps({'script': helper_clean + "\n" + script_clean}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(ss_url, data=payload, headers=H, method='PUT')
opener.open(req)
print("Updated VM POS Meta script")

# Execute action
r_exec = opener.open('http://38.247.138.224:10017/api/method/vm_pos_meta?cmd_action=fix_desktop_icon')
print("Execution result:", r_exec.read().decode())

# Clean script
payload_clean = json.dumps({'script': script_clean}).encode()
req_clean = urllib.request.Request(ss_url, data=payload_clean, headers=H, method='PUT')
opener.open(req_clean)
print("Cleaned VM POS Meta script.")

# Verify Desktop Icon
r_ver = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management')
doc_ver = json.loads(r_ver.read().decode())['data']
print("Verified Desktop Icon in database:")
print("  name:", doc_ver.get('name'))
print("  link_type:", doc_ver.get('link_type'))
print("  link:", doc_ver.get('link'))
print("  icon:", doc_ver.get('icon'))
print("  hidden:", doc_ver.get('hidden'))
