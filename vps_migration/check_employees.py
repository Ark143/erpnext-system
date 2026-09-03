import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

url = 'http://38.247.138.224:10017/api/resource/Employee?fields=["name","employee_name","designation","department","company","user_id"]&limit_page_length=50'
r = opener.open(url)
data = json.loads(r.read().decode())
print(f"Total employees found: {len(data.get('data', []))}")
for e in data.get('data', [])[:10]:
    print(f" - {e['name']}: {e.get('employee_name')} ({e.get('designation', 'Staff')}) | Company: {e.get('company')} | User: {e.get('user_id')}")
