import requests

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
html = wp['data']['main_section_html']

with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated local current_pos_terminal.html from live Web Page")
