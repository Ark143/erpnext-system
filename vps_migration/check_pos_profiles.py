import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Check existing POS Profiles
r = opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile?limit_page_length=50')
profiles = json.loads(r.read().decode())['data']
print('POS Profiles:')
for p in profiles:
    pname = urllib.request.quote(p['name'])
    r2 = opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile/' + pname)
    pd = json.loads(r2.read().decode())['data']
    print('  [' + pd['name'] + '] company=' + str(pd.get('company')) + ', warehouse=' + str(pd.get('warehouse')))

# Check if test@gmail.com has any POS Opening Entry today
print()
r3 = opener.open('http://38.247.138.224:10017/api/resource/POS%20Opening%20Entry?limit_page_length=10&filters=[[%22user%22,%22=%22,%22test%40gmail.com%22]]')
opening_entries = json.loads(r3.read().decode())['data']
print('POS Opening Entries for test@gmail.com:', opening_entries)

# Also check what open POS Opening Entries exist
print()
r4 = opener.open('http://38.247.138.224:10017/api/resource/POS%20Opening%20Entry?limit_page_length=20&filters=[[%22status%22,%22=%22,%22Open%22],[%22docstatus%22,%22=%22,1]]')
open_entries = json.loads(r4.read().decode())['data']
print('All currently OPEN POS Opening Entries:', [e['name'] for e in open_entries])
