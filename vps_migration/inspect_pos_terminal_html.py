import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Fetch Web Page vehicle-pos-terminal
wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
data = wp.get('data', {})
html = data.get('main_section_html', '')
print("Web Page fetched. HTML length:", len(html))

# Check for undefined image references or highlight / socket
lines = html.split('\n')
for i, line in enumerate(lines):
    if 'undefined' in line or 'initHighlighting' in line or 'thumb' in line or 'vpos-thumb' in line:
        print(f"Line {i+1}: {line[:120]}")
