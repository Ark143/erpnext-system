import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Employee record
r = opener.open('http://38.247.138.224:10017/api/resource/Employee?limit_page_length=50')
emps = json.loads(r.read().decode())['data']
for e in emps:
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Employee/' + e['name']).read().decode())['data']
    if doc.get('user_id'):
        print('Employee:', doc['name'], '| User:', doc.get('user_id'), '| Company:', doc.get('company'), '| Branch:', doc.get('branch'))

# Cashier Profile
r2 = opener.open('http://38.247.138.224:10017/api/resource/Cashier%20Profile?limit_page_length=50')
cp = json.loads(r2.read().decode())['data']
print('\nCashier Profiles:', cp)
for c in cp:
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Cashier%20Profile/' + c['name']).read().decode())['data']
    print('CP:', c['name'], '| Company:', doc.get('company'), '| Enabled:', doc.get('enabled'))
