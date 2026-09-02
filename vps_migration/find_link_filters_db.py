import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_diag = '''
def find_list_fields():
    import frappe
    out = []

    # Check Custom Field
    for row in frappe.db.sql("""SELECT name, dt, fieldname, label, fieldtype, link_filters FROM "tabCustom Field" WHERE link_filters IS NOT NULL AND link_filters != '' """, as_dict=True):
        lf = row.get("link_filters")
        out.append({"type": "Custom Field", "name": row["name"], "dt": row["dt"], "fieldname": row["fieldname"], "link_filters": str(lf)})

    # Check DocField
    for row in frappe.db.sql("""SELECT name, parent, fieldname, label, fieldtype, link_filters FROM "tabDocField" WHERE link_filters IS NOT NULL AND link_filters != '' """, as_dict=True):
        lf = row.get("link_filters")
        out.append({"type": "DocField", "name": row["name"], "parent": row["parent"], "fieldname": row["fieldname"], "link_filters": str(lf)})

    frappe.response["message"] = out

find_list_fields()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Find%20List%20Fields',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Find List Fields',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_find_list_fields',
        'allow_guest': 1,
        'disabled': 0,
        'script': script_diag
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    pass

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_find_list_fields', headers=H))
res = json.loads(r_call.read().decode())
print("Found fields with link_filters in DB:")
print(json.dumps(res.get('message', []), indent=2))
