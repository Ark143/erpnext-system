import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

r = opener.open('http://38.247.138.224:10017/api/resource/Company?limit_page_length=50')
companies = [c['name'] for c in json.loads(r.read().decode())['data']]

print(f'Total companies: {len(companies)}')

for c in companies:
    cname = urllib.parse.quote(c)
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Company/' + cname).read().decode())['data']
    
    # warehouse
    wh_res = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Warehouse?filters=[[%22company%22,%22=%22,%22' + cname + '%22],[%22is_group%22,%22=%22,0]]&limit_page_length=10').read().decode())['data']
    warehouses = [w['name'] for w in wh_res]
    
    # income account
    inc_res = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Account?filters=[[%22company%22,%22=%22,%22' + cname + '%22],[%22root_type%22,%22=%22,%22Income%22],[%22is_group%22,%22=%22,0]]&limit_page_length=10').read().decode())['data']
    incomes = [a['name'] for a in inc_res]
    
    # cost center
    cc_res = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Cost%20Center?filters=[[%22company%22,%22=%22,%22' + cname + '%22],[%22is_group%22,%22=%22,0]]&limit_page_length=10').read().decode())['data']
    cost_centers = [cc['name'] for cc in cc_res]
    
    print('----------------------------------------')
    print('Company:', c)
    print('  Default Warehouse:', doc.get('default_fg_warehouse') or (warehouses[0] if warehouses else 'None'))
    print('  Default Income Account:', doc.get('default_income_account') or (incomes[0] if incomes else 'None'))
    print('  Default Cost Center:', doc.get('cost_center') or (cost_centers[0] if cost_centers else 'None'))
    print('  Currency:', doc.get('default_currency') or 'PHP')
