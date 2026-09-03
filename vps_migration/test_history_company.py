import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

companies = ['All Branches', 'Automan Car Care Center', '', 'ULTRA MRF', 'null']
for comp in companies:
    url = f"http://38.247.138.224:10017/api/method/vm_pos_history?period=all&company={urllib.parse.quote(comp)}"
    r = opener.open(url)
    data = json.loads(r.read().decode())
    msg = data.get('message') or []
    print(f"company='{comp}' -> {len(msg)} invoices")
