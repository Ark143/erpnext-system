#!/usr/bin/env python3
"""Check actual data fields in responses"""
import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# Check raw responses for key doctypes
for dt in ['Sales%20Invoice', 'Employee', 'Item', 'Account', 'Vehicle%20Model', 'Customer%20Vehicle']:
    try:
        r = op.open(urllib.request.Request(f'{URL}/api/resource/{dt}?limit_page_length=2', headers=H), timeout=30)
        raw = r.read().decode()
        data = json.loads(raw)
        print(f'\n=== {dt.replace("%20"," ")} ===')
        print(f'Raw keys: {list(data.keys()) if isinstance(data, dict) else "list"}')
        
        if isinstance(data, dict) and 'data' in data:
            items = data['data']
            if isinstance(items, list) and items:
                print(f'First record keys: {list(items[0].keys())}')
                print(f'First record (name, item_code, etc):')
                for k, v in items[0].items():
                    if v:  # only non-empty
                        print(f'  {k}: {str(v)[:80]}')
        elif isinstance(data, list) and data:
            print(f'First record keys: {list(data[0].keys())}')
            for k, v in data[0].items():
                if v:
                    print(f'  {k}: {str(v)[:80]}')
        else:
            print(f'Data: {str(data)[:500]}')
    except Exception as e:
        print(f'{dt}: ERROR - {e}')

print('\n=== Server Script detail ===')
try:
    r = op.open(urllib.request.Request(f'{URL}/api/resource/Server%20Script?limit_page_length=3', headers=H), timeout=30)
    raw = r.read().decode()
    data = json.loads(raw)
    if isinstance(data, dict) and 'data' in data:
        for s in data['data'][:3]:
            print(f'\nScript: {s.get("name","")}')
            for k, v in s.items():
                if v or k in ['name','disabled','script_type','reference_doctype','api_method','enabled']:
                    print(f'  {k}: {str(v)[:100]}')
except Exception as e:
    print(f'Error: {e}')
