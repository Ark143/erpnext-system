import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
html = wp['data']['main_section_html']

# Replace /desk#Form/POS Invoice/ with /app/pos-invoice/
replacements = [
    ("/desk#Form/POS Invoice/", "/app/pos-invoice/"),
    ("/desk#Form/POS%20Invoice/", "/app/pos-invoice/"),
    ("/desk#Form/Vehicle POS Invoice/", "/app/pos-invoice/"),
    ("/desk#Form/Vehicle%20POS%20Invoice/", "/app/pos-invoice/")
]

for old, new in replacements:
    if old in html:
        count = html.count(old)
        html = html.replace(old, new)
        print(f"Replaced {count} instances of '{old}' with '{new}'")

# Also check for any remaining /desk#Form in the HTML
if "/desk#Form" in html:
    print("Remaining /desk#Form found in HTML. Listing context:")
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if "/desk#Form" in line:
            print(f"  Line {i+1}: {line[:120]}")

res = s.put(f'{URL}/api/resource/Web Page/vehicle-pos-terminal', json={'main_section_html': html})
print("Web Page vehicle-pos-terminal updated HTTP status:", res.status_code)
