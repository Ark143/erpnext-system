import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_content = '''
def fix_list_fields():
    import frappe, json
    fixed = []

    # 1. Check all Custom Fields
    cfs = frappe.get_all("Custom Field", fields=["name", "dt", "fieldname", "link_filters", "depends_on", "mandatory_depends_on", "read_only_depends_on"])
    for cf in cfs:
        doc = frappe.get_doc("Custom Field", cf.name)
        changed = False
        for attr in ["link_filters", "depends_on", "mandatory_depends_on", "read_only_depends_on"]:
            val = getattr(doc, attr, None)
            if isinstance(val, list):
                setattr(doc, attr, json.dumps(val))
                changed = True
                fixed.append(f"Custom Field {cf.name}.{attr} converted from list to string")
        if changed:
            doc.db_update()

    # 2. Check all DocFields in tabDocField
    df_rows = frappe.db.sql("""SELECT name, parent, fieldname, link_filters, depends_on, mandatory_depends_on, read_only_depends_on FROM "tabDocField" """, as_dict=True)
    for df in df_rows:
        for attr in ["link_filters", "depends_on", "mandatory_depends_on", "read_only_depends_on"]:
            val = df.get(attr)
            if isinstance(val, list):
                str_val = json.dumps(val)
                frappe.db.set_value("DocField", df["name"], attr, str_val, update_modified=False)
                fixed.append(f"DocField {df['parent']}.{df['fieldname']}.{attr} converted from list to string")

    # 3. Check DocType meta cache
    frappe.clear_cache()
    frappe.response["message"] = {"fixed_count": len(fixed), "fixed": fixed}

fix_list_fields()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Fix%20List%20Fields',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Fix List Fields',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_fix_list_fields',
        'allow_guest': 1,
        'disabled': 0,
        'script': script_content
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    pass

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_fix_list_fields', headers=H))
res = json.loads(r_call.read().decode())
print("Fix result:", json.dumps(res.get('message', {}), indent=2))
