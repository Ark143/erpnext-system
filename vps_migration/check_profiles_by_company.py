import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. All companies
r = opener.open('http://38.247.138.224:10017/api/resource/Company?limit_page_length=50')
comps = [c['name'] for c in json.loads(r.read().decode())['data']]
print('All Companies:', comps)

# 2. All POS Profiles
r2 = opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile?limit_page_length=50')
p_list = json.loads(r2.read().decode())['data']
prof_by_co = {}
for p in p_list:
    pname = urllib.parse.quote(p['name'])
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile/' + pname).read().decode())['data']
    if not doc.get('disabled'):
        co = doc.get('company')
        prof_by_co.setdefault(co, []).append({
            'name': doc['name'],
            'warehouse': doc.get('warehouse'),
            'users': [u['user'] for u in doc.get('applicable_for_users', [])]
        })

print('\nPOS Profiles by Company:')
for co, plist in prof_by_co.items():
    print(co + ':')
    for pr in plist:
        print('    ' + pr['name'] + ' (users=' + str(pr['users']) + ', wh=' + str(pr['warehouse']) + ')')

missing = [c for c in comps if c not in prof_by_co]
print('\nCompanies WITHOUT POS Profile:')
for m in missing:
    print('   -', m)
