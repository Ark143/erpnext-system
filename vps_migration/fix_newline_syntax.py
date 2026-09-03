import json, urllib.request, urllib.parse, re, subprocess, os

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix literal newline in string
broken = 'alert("⚠️ Failed to create invoice:\n" + err);'
# In file, it might be literally alert("⚠️ Failed to create invoice:\n" or alert("⚠️ Failed to create invoice:\r\n"
content = re.sub(r'alert\("⚠️ Failed to create invoice:[\r\n]+"\s*\+\s*err\);', 'alert("⚠️ Failed to create invoice: " + err);', content)

# Check for any other unescaped multiline quotes
content = content.replace('alert("⚠️ Failed to create invoice:\n"', 'alert("⚠️ Failed to create invoice: "')

# Save to test_script_2 and run node -c
scripts = re.findall(r'<script\b[^>]*>([\s\S]*?)<\/script>', content, re.I)
with open('vps_migration/test_script_2.js', 'w', encoding='utf-8') as sf:
    sf.write(scripts[2])

res = subprocess.run(['node', '-c', 'vps_migration/test_script_2.js'], capture_output=True, text=True)
if res.returncode != 0:
    print('Still error in script 2:', res.stderr)
else:
    print('script 2: Syntax 100% OK!')

# Save locally
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
print('Deployed fix to Web Page: HTTP', res.status)
