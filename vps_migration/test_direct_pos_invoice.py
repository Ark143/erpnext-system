import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Check current count of POS Invoices
r = opener.open('http://38.247.138.224:10017/api/resource/POS%20Invoice?limit=1')
res = json.loads(r.read().decode())
print("Connected to ERPNext POS Invoice API successfully!")
