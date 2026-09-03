import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Test vm_pos_get_items without only_stock
r1 = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_items?company=' + urllib.parse.quote('Ultra MRF Dau Annex') + '&only_stock=0')
res1 = json.loads(r1.read().decode())['message']
print('Only stock 0 for Ultra MRF Dau Annex:', len(res1), 'items returned')
if res1:
    print('  Sample item:', res1[0])

# 2. Test vm_pos_get_items WITH only_stock=1
r2 = opener.open('http://38.247.138.224:10017/api/method/vm_pos_get_items?company=' + urllib.parse.quote('Ultra MRF Dau Annex') + '&only_stock=1')
res2 = json.loads(r2.read().decode())['message']
print('Only stock 1 for Ultra MRF Dau Annex:', len(res2), 'items returned')
if res2:
    print('  Sample item:', res2[0])

# 3. Check what stock actually exists in tabBin
codes_sample = [x['code'] for x in res1[:10]]
sql_test = opener.open('http://38.247.138.224:10017/api/method/vm_pos_stock?codes=' + ','.join(codes_sample))
res3 = json.loads(sql_test.read().decode())['message']
print('\nStock API result for first 10 items:')
for k, v in res3.items():
    print('  ' + k + ': stock=' + str(v.get('stock')) + ', bins=' + str(v.get('bins')))

# 4. Check all items that have actual_qty > 0 across warehouses
r4 = opener.open('http://38.247.138.224:10017/api/resource/Bin?filters=[[%22actual_qty%22,%22%3E%22,0]]&limit_page_length=50&fields=[%22item_code%22,%22warehouse%22,%22actual_qty%22]')
bins = json.loads(r4.read().decode())['data']
print('\nTotal positive stock bins in ERPNext:', len(bins))
for b in bins[:10]:
    print('  Bin:', b['item_code'], '| WH:', b['warehouse'], '| Qty:', b['actual_qty'])
