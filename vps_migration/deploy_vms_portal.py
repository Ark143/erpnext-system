import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

with open(r'c:\Users\josem\erpnext-system\vps_migration\vms_portal.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

pages_to_deploy = [
    {
        'name': 'vehicle-management-system',
        'title': 'Vehicle Management System',
        'route': 'vms',
        'published': 1,
        'full_width': 1,
        'show_sidebar': 0,
        'show_title': 0,
        'content_type': 'HTML',
        'dynamic_template': 0,
        'main_section_html': html_content,
        'main_section': html_content
    },
    {
        'name': 'vehicle-management-system-portal',
        'title': 'Vehicle Management System Portal',
        'route': 'vms-portal',
        'published': 1,
        'full_width': 1,
        'show_sidebar': 0,
        'show_title': 0,
        'content_type': 'HTML',
        'dynamic_template': 0,
        'main_section_html': html_content,
        'main_section': html_content
    }
]

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

for p in pages_to_deploy:
    target_url = f'http://38.247.138.224:10017/api/resource/Web%20Page/{p["name"]}'
    payload = json.dumps(p).encode()
    req = urllib.request.Request(target_url, data=payload, headers=H, method='PUT')
    res = opener.open(req)
    print(f'Updated Web Page/{p["name"]}: HTTP {res.status}')

# Sync copy to bench app www
try:
    bench_www = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\vms.html'
    with open(bench_www, 'w', encoding='utf-8') as bw:
        bw.write(html_content)
    print('Synced copy to apps/vehicle_management/vehicle_management/www/vms.html')
except Exception as ex:
    print('Bench sync note:', ex)
