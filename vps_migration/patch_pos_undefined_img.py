import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
html = wp['data']['main_section_html']

# Replace if (it.image) check
old_img_check = 'if (it.image) {'
new_img_check = "if (it.image && it.image !== 'undefined' && it.image !== 'null' && String(it.image).trim() !== '') {"

if old_img_check in html:
    html = html.replace(old_img_check, new_img_check)
    print("Replaced old_img_check")

# Save updated HTML to Web Page
res = s.put(f'{URL}/api/resource/Web Page/vehicle-pos-terminal', json={
    'main_section_html': html
})
print("Updated Web Page vehicle-pos-terminal:", res.status_code)
