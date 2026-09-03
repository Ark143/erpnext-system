import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Get all accounts for all companies
r = opener.open('http://38.247.138.224:10017/api/resource/Account?limit_page_length=500&filters=[[%22is_group%22,%22=%22,0],[%22account_type%22,%22in%22,[%22Cash%22,%22Bank%22]]]&fields=[%22name%22,%22company%22,%22account_type%22,%22account_name%22]')
accts = json.loads(r.read().decode())['data']

by_company = {}
for a in accts:
    by_company.setdefault(a['company'], []).append(a)

print('=== CASH & BANK ACCOUNTS PER COMPANY ===')
for co, alist in by_company.items():
    print(co + ':')
    for a in alist:
        print('   [' + a['account_type'] + '] ' + a['name'] + ' (' + a['account_name'] + ')')
