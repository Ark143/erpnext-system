import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_clean = """
def clean_vehicle_customers():
    # Update customer names in Customer Vehicle to match exact Customer name
    sql = \"\"\"
        UPDATE "tabCustomer Vehicle" cv
        SET customer = regexp_replace(cv.customer, '[[:space:]]+', ' ', 'g')
        WHERE cv.customer LIKE '%  %'
        AND EXISTS (
            SELECT 1 FROM "tabCustomer" c 
            WHERE c.name = regexp_replace(cv.customer, '[[:space:]]+', ' ', 'g')
        )
    \"\"\"
    frappe.db.sql(sql)
    frappe.db.commit()
    frappe.response["message"] = {"cleaned": True}

clean_vehicle_customers()
"""

name = 'VM Clean Vehicle Customers'
payload = {'name': name, 'doctype': 'Server Script', 'script_type': 'API', 'api_method': 'vm_clean_vehicle_customers', 'allow_guest': 1, 'disabled': 0, 'script': script_clean}
try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
except Exception:
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}', data=urllib.parse.urlencode({'data': json.dumps({'script': script_clean})}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_clean_vehicle_customers', headers=H))
print('Cleaned result:', r.read().decode())
