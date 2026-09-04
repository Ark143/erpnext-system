import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

ss_url = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Meta'
r = opener.open(ss_url)
doc = json.loads(r.read().decode())['data']
script_content = doc['script']

# Remove any old helper
if '/* --- REST OF SCRIPT --- */' in script_content:
    script_clean = script_content.split('/* --- REST OF SCRIPT --- */')[-1]
elif 'if frappe.form_dict.get("cmd_action") == "fix_desktop_icon":' in script_content:
    script_clean = script_content.split('# return immediately')[-1].strip()
else:
    script_clean = script_content

helper_set_val = """if frappe.form_dict.get("cmd_action") == "fix_desktop_icon":
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "link_type", "External")
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "link", "/desk/vehicle-management")
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "icon", "car")
    frappe.db.set_value("Desktop Icon", "Vehicle Management", "hidden", 0)
    frappe.clear_cache()
    frappe.response["message"] = "SET_VALUE_SUCCESS"
"""

payload = json.dumps({'script': helper_set_val + "\n" + script_clean}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(ss_url, data=payload, headers=H, method='PUT')
opener.open(req)
print("Saved set_value in VM POS Meta")

# Call API
r_exec = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_meta?cmd_action=fix_desktop_icon')
print("Execution response:", r_exec.read().decode())

# Clean script
payload_clean = json.dumps({'script': script_clean}).encode()
req_clean = urllib.request.Request(ss_url, data=payload_clean, headers=H, method='PUT')
opener.open(req_clean)
print("Cleaned VM POS Meta")

# Verify Desktop Icon
r_ver = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management')
print("Verified Desktop Icon:", json.loads(r_ver.read().decode())['data'])
