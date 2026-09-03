import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

methods = ['Cash', 'Card', 'Credit Card', 'GCash', 'Maya', 'BDO', 'Bank Transfer']

for m in methods:
    payload = json.dumps({
        'customer': 'JOAN CHIIETE',
        'vehicle': '0301 650263',
        'company': 'ULTRA MRF',
        'paid_amount': 70.0,
        'payment_method': m,
        'remarks': f'Verification test payment method {m}',
        'items': [{
            'item_code': '#16 WIRE DM-DAS-OS',
            'qty': 1,
            'rate': 70.0,
            'discount_amount': 0,
            'uom': 'Nos'
        }]
    }).encode()
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/method/vm_pos_create_invoice',
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    try:
        r = opener.open(req)
        d = json.loads(r.read().decode())
        res = d.get('message', {})
        print(f"METHOD: {m:<15} -> SUCCESS! {res.get('name')} | Method: {res.get('payment_method')} | Status: {res.get('status')}")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        try:
            ej = json.loads(err)
            exc = ej.get('exception') or ej.get('exc') or err
            print(f"METHOD: {m:<15} -> FAILED {e.code}: {str(exc)[:250]}")
        except:
            print(f"METHOD: {m:<15} -> FAILED {e.code}: {err[:250]}")
