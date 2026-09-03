import re, json, urllib.request, urllib.parse, glob, subprocess, os

html_path = r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the syntax error in vehicle assignment
broken = 'const vehicle = sale.vehicle ? (sale.vehicle + (sale.vehicle_name ? " — " + sale.vehicle_name : "") : "");'
fixed = 'const vehicle = sale.vehicle ? (sale.vehicle + (sale.vehicle_name ? (" — " + sale.vehicle_name) : "")) : "";'

assert broken in content, "broken line not found in content"
content = content.replace(broken, fixed)
print("Fixed syntax error.")

# Save to local file
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Extract scripts again and validate ALL with node -c
scripts = re.findall(r'<script\b[^>]*>([\s\S]*?)<\/script>', content, re.I)
for idx, s in enumerate(scripts):
    sf_name = f'c:\\Users\\josem\\erpnext-system\\vps_migration\\script_{idx}.js'
    with open(sf_name, 'w', encoding='utf-8') as sf:
        sf.write(s)
    res = subprocess.run(['node', '-c', sf_name], capture_output=True, text=True)
    if res.returncode != 0:
        print(f'ERROR in script {idx}:', res.stderr)
    else:
        print(f'script_{idx}.js: Syntax OK')
    try:
        os.remove(sf_name)
    except:
        pass

# Sync to bench app
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

# Verify GET /pos-terminal
r_web = opener.open('http://38.247.138.224:10017/pos-terminal')
print('GET /pos-terminal status:', r_web.status)
