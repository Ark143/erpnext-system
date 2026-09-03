import re, json, urllib.request, urllib.parse

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences of .__ in the HTML
# 1. module.__esModule -> module["__esModule"]
content = content.replace('module.__esModule', 'module["__esModule"]')

# 2. window.__vposPwd -> window._vposPwd
content = content.replace('window.__vposPwd', 'window._vposPwd')

# 3. Any other .__
# Let's check remaining
rem = [m.start() for m in re.finditer(r'\.__', content)]
print('Remaining .__ occurrences:', len(rem))
for idx in rem:
    print(' ', content[max(0, idx-30):min(len(content), idx+40)])

# Replace any generic object.__property with object["__property"]
content = re.sub(r'\.__([a-zA-Z0-9_$]+)', r'["__\1"]', content)

assert '.__' not in content, "Error: .__ still found in content!"
print('SUCCESS: Verified ".__" is 100% eliminated from template!')

# Save to local files
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

bench_path = r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html'
with open(bench_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Deploy to live ERPNext Web Page
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

web_page_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload_web = json.dumps({'main_section_html': content}).encode()
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(web_page_url, data=payload_web, headers=H, method='PUT')
res = opener.open(req)
print('Deployed fix to Web Page/vehicle-pos-terminal: HTTP', res.status)

# Test accessing http://38.247.138.224:10017/pos-terminal directly
r_web = opener.open('http://38.247.138.224:10017/pos-terminal')
print('Direct GET /pos-terminal status:', r_web.status)
print('Response length:', len(r_web.read()))
