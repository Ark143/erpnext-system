import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_code = """
frappe.clear_cache()
# Ensure Workspace Sidebar for Vehicle Management has standard=1 and for_user=None in DB
frappe.db.sql("UPDATE `tabWorkspace Sidebar` SET for_user=NULL, standard=1 WHERE name='Vehicle Management'")
frappe.clear_cache()

# Return current sidebar item count in DB
items = frappe.get_all("Workspace Sidebar Item", filters={"parent": "Vehicle Management"}, fields=["label", "type", "link_to"], order_by="idx asc")
frappe.response['message'] = {
    'status': 'success',
    'items_count': len(items),
    'items': items
}
"""

name = "VM Clear Cache and Fix Sidebar"
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_clear_cache_and_fix_sidebar',
    'allow_guest': 1,
    'disabled': 0,
    'script': script_code
}

try:
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)
    print("Updated Server Script")
except Exception:
    req = urllib.request.Request(f"{URL}/api/resource/Server%20Script", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
    print("Created Server Script")

# Now trigger the API
res = op.open(urllib.request.Request(f"{URL}/api/method/vm_clear_cache_and_fix_sidebar", headers=H))
out = json.loads(res.read().decode())
print("Server API execution output:")
print(json.dumps(out, indent=2))
