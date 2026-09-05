import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Check Web Pages
pages = s.get(f'{URL}/api/resource/Web Page?fields=[\"name\",\"title\",\"route\"]&limit_page_length=50').json()
print("Web Pages:")
for p in pages.get('data', []):
    print(" ", p)

# Check custom Page doctypes
desk_pages = s.get(f'{URL}/api/resource/Page?fields=[\"name\",\"title\",\"module\"]&limit_page_length=50').json()
print("\nDesk Pages:")
for dp in desk_pages.get('data', []):
    print(" ", dp)
