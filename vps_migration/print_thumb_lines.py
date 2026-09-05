import requests

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
html = wp['data']['main_section_html']
lines = html.split('\n')
for i in range(15240, min(15275, len(lines))):
    print(f"{i+1}: {lines[i]}")
