import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Check all Mode of Payment documents
r = opener.open('http://38.247.138.224:10017/api/resource/Mode%20of%20Payment?limit_page_length=100')
mops = json.loads(r.read().decode())['data']
print('=== EXISTING MODES OF PAYMENT ===')
for m in mops:
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/Mode%20of%20Payment/' + urllib.parse.quote(m['name'])).read().decode())['data']
    accts = [(a['company'], a['default_account']) for a in doc.get('accounts', [])]
    print('  [' + doc['name'] + '] type=' + str(doc.get('type')) + ', enabled=' + str(doc.get('enabled')) + ' -> ' + str(len(accts)) + ' accounts')
    for co, acc in accts[:3]:
        print('      ' + co + ' -> ' + acc)
    if len(accts) > 3:
        print('      ... (' + str(len(accts) - 3) + ' more)')

# 2. Check POS Profiles and their payments child table
print('\n=== POS PROFILES AND THEIR PAYMENTS ===')
r2 = opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile?limit_page_length=50')
profs = json.loads(r2.read().decode())['data']
for p in profs:
    doc = json.loads(opener.open('http://38.247.138.224:10017/api/resource/POS%20Profile/' + urllib.parse.quote(p['name'])).read().decode())['data']
    payments = [(pay.get('mode_of_payment'), pay.get('default')) for pay in doc.get('payments', [])]
    print('  [' + doc['name'] + '] Company: ' + str(doc.get('company')) + ' -> Payments: ' + str(payments))
