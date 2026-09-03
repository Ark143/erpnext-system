import json, urllib.request, urllib.parse

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update Web Page/vehicle-pos-terminal in ERPNext
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Update Web Page document properties
web_page_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

update_payload = json.dumps({
    'main_section_html': content,
    'show_sidebar': 0,
    'show_title': 0,
    'show_breadcrumbs': 0,
    'full_width': 1
}).encode()

req = urllib.request.Request(web_page_url, data=update_payload, headers=H, method='PUT')
res = opener.open(req)
print('Updated Web Page properties and HTML: HTTP', res.status)

# 2. Verify GET /pos-terminal
r_web = opener.open('http://38.247.138.224:10017/pos-terminal')
print('GET /pos-terminal response status:', r_web.status)
