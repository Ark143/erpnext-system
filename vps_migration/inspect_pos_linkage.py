import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

print('=== ALL VEHICLE POS INVOICES ===')
vpis = api_get('http://38.247.138.224:10017/api/resource/Vehicle%20POS%20Invoice?limit=50').get('data', [])
print(f'Total Vehicle POS Invoices: {len(vpis)}')

linked_count = 0
unlinked_count = 0

for v in vpis:
    doc = api_get('http://38.247.138.224:10017/api/resource/Vehicle%20POS%20Invoice/' + urllib.parse.quote(v['name'])).get('data', {})
    pi = doc.get('pos_invoice')
    status = doc.get('status')
    docstatus = doc.get('docstatus')
    total = doc.get('total_amount')
    if pi:
        linked_count += 1
        print(f"  [LINKED] {doc['name']} -> POS Invoice: {pi} | Total: PHP {total} | Status: {status} (docstatus: {docstatus})")
    else:
        unlinked_count += 1
        print(f"  [NOT LINKED!] {doc['name']} -> No POS Invoice! | Total: PHP {total} | Status: {status} (docstatus: {docstatus})")

print(f'\nSummary: Linked = {linked_count}, Unlinked = {unlinked_count}')

print('\n=== ERPNEXT POS INVOICES ===')
pis = api_get('http://38.247.138.224:10017/api/resource/POS%20Invoice?limit=50').get('data', [])
print(f'Total ERPNext POS Invoices: {len(pis)}')
for p in pis:
    p_doc = api_get('http://38.247.138.224:10017/api/resource/POS%20Invoice/' + urllib.parse.quote(p['name'])).get('data', {})
    print(f"  {p_doc['name']} | Customer: {p_doc.get('customer')} | Grand Total: {p_doc.get('grand_total')} | Linked VMS: {p_doc.get('vehicle_pos_invoice')}")
