import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

ss_url = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Meta'
r = opener.open(ss_url)
doc = json.loads(r.read().decode())['data']
orig_script = doc['script']

updater_lines = """frappe.db.set_value("Desktop Icon", "Vehicle Management", "link_type", "Workspace Sidebar")
frappe.db.set_value("Desktop Icon", "Vehicle Management", "link_to", "Vehicle Management")
frappe.db.set_value("Desktop Icon", "Vehicle Management", "icon", "car")
frappe.db.set_value("Desktop Icon", "Vehicle Management", "hidden", 0)
frappe.db.commit()
"""

payload = json.dumps({'script': updater_lines + "\n" + orig_script}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(ss_url, data=payload, headers=H, method='PUT')
opener.open(req)
print("Updated VM POS Meta with commit")

# Call the API once
r_call = opener.open('http://38.247.138.224:10017/api/method/vm_pos_meta')
print("Called API, status:", r_call.status)

# Restore original script
payload_clean = json.dumps({'script': orig_script}).encode()
req_clean = urllib.request.Request(ss_url, data=payload_clean, headers=H, method='PUT')
opener.open(req_clean)
print("Restored original script.")

# Verify Desktop Icon
r_ver = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management')
doc_ver = json.loads(r_ver.read().decode())['data']
print("Verified Desktop Icon in database:")
print("  name:", doc_ver.get('name'))
print("  link_type:", doc_ver.get('link_type'))
print("  link_to:", doc_ver.get('link_to'))
print("  icon:", doc_ver.get('icon'))
print("  hidden:", doc_ver.get('hidden'))
