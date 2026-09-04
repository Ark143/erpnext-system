import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

script_inspect = """
try:
    from frappe.desk.form.load import get_dashboard_data
    dash_vjo = get_dashboard_data('Vehicle Job Order')
    dash_ve = get_dashboard_data('Vehicle Estimate')
    dash_cv = get_dashboard_data('Customer Vehicle')

    frappe.response['message'] = {
        'status': 'success',
        'vjo': dash_vjo,
        've': dash_ve,
        'cv': dash_cv
    }
except Exception as e:
    import traceback
    frappe.response['message'] = {
        'status': 'error',
        'err': str(e),
        'trace': traceback.format_exc()
    }
"""

payload = {
    'name': 'VM Check Dashboard Data',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_check_dashboard_data',
    'allow_guest': 0,
    'disabled': 0,
    'script': script_inspect
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Check Dashboard Data')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
req.get_method = lambda: 'PUT'
op.open(req)

res = op.open(urllib.request.Request(f'{URL}/api/method/vm_check_dashboard_data', headers=H))
print("Current Dashboards:", json.dumps(json.loads(res.read().decode()).get('message', {}), indent=2))
