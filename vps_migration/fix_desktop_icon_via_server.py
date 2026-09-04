import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Inspect or create a quick Server Script API to update Desktop Icon
ss_url = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Meta'
r = opener.open(ss_url)
doc = json.loads(r.read().decode())['data']
script_content = doc['script']

# Add an action handler or update logic in VM POS Meta or execute DB update
update_code = """
frappe.db.set_value("Desktop Icon", "Vehicle Management", {
    "link_type": "External",
    "link": "/desk/vehicle-management",
    "icon": "car",
    "hidden": 0
})

# Also ensure Has Role child records exist for all roles
target_roles = ['System Manager', 'Desk User', 'Sales User', 'Sales Manager', 'Maintenance User', 'Maintenance Manager', 'Stock User', 'Stock Manager', 'Accounts User']
d_doc = frappe.get_doc("Desktop Icon", "Vehicle Management")
d_doc.roles = []
for r in target_roles:
    d_doc.append("roles", {"role": r})
d_doc.link_type = "External"
d_doc.link = "/desk/vehicle-management"
d_doc.flags.ignore_permissions = True
d_doc.save()

frappe.clear_cache()
"""

# Let's create a dedicated helper in VM POS Meta to run it
helper_call = """
if frappe.form_dict.get("cmd_action") == "fix_desktop_icon":
    frappe.db.set_value("Desktop Icon", "Vehicle Management", {
        "link_type": "External",
        "link": "/desk/vehicle-management",
        "icon": "car",
        "hidden": 0
    })
    try:
        d_doc = frappe.get_doc("Desktop Icon", "Vehicle Management")
        d_doc.roles = []
        for r in ['System Manager', 'Desk User', 'Sales User', 'Sales Manager', 'Maintenance User', 'Maintenance Manager', 'Stock User', 'Stock Manager', 'Accounts User']:
            d_doc.append("roles", {"role": r})
        d_doc.link_type = "External"
        d_doc.link = "/desk/vehicle-management"
        d_doc.flags.ignore_permissions = True
        d_doc.save()
    except Exception as e:
        pass
    frappe.clear_cache()
    frappe.response["message"] = "Desktop Icon fixed!"
    # return immediately
"""

if 'fix_desktop_icon' not in script_content:
    new_script = helper_call + "\n" + script_content
    payload = json.dumps({'script': new_script}).encode()
    H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    req = urllib.request.Request(ss_url, data=payload, headers=H, method='PUT')
    opener.open(req)
    print("Updated VM POS Meta script with fix_desktop_icon action.")

# Call the API to execute the fix
r_fix = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_meta?cmd_action=fix_desktop_icon')
print("Fix result:", r_fix.read().decode())

# Clean up helper call from VM POS Meta
r_clean = opener.open(ss_url)
doc_clean = json.loads(r_clean.read().decode())['data']
cleaned_script = doc_clean['script'].replace(helper_call + "\n", "").replace(helper_call, "")
payload_clean = json.dumps({'script': cleaned_script}).encode()
req_clean = urllib.request.Request(ss_url, data=payload_clean, headers={'Content-Type': 'application/json'}, method='PUT')
opener.open(req_clean)
print("Cleaned up VM POS Meta script.")

# Verify Desktop Icon
r_ver = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Icon/Vehicle%20Management')
print("Verified Desktop Icon:", json.loads(r_ver.read().decode())['data'])
