import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Fetch current Desktop Layout for Administrator
r = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Layout/Administrator')
doc = json.loads(r.read().decode())['data']
layout_list = json.loads(doc['layout'])

hdr_script = """<script>
if (!window._vm_hdr_injected) {
  window._vm_hdr_injected = true;
  function addVMHeader() {
    var c = $('.desktop-navbar .desktop-notifications');
    if (c.length && !$('#vm-header-shortcut-pill').length) {
      c.before(`
        <a id="vm-header-shortcut-pill" href="/desk#workspace/Vehicle%20Management" style="background:#16c784; color:#04201a; font-weight:900; font-size:13px; border-radius:8px; padding:5px 14px; height:32px; display:inline-flex; align-items:center; text-decoration:none; box-shadow:0 2px 6px rgba(22,199,132,0.4); margin-right:12px; cursor:pointer; transition:all 0.15s ease;">
          <span style="font-size:15px; margin-right:5px;">🚗</span>
          <span>Vehicle Management</span>
        </a>
        <a id="vm-header-pos-pill" href="/desk/vehicle_pos" style="background:#0c1a18; color:#16c784; font-weight:800; font-size:12.5px; border:1px solid #16c784; border-radius:8px; padding:4px 10px; height:32px; display:inline-flex; align-items:center; text-decoration:none; margin-right:12px; cursor:pointer;">
          <span style="margin-right:4px;">🐴</span>
          <span>POS</span>
        </a>
      `);
    }
  }
  setInterval(addVMHeader, 300);
  addVMHeader();
}
</script>"""

# Inject into the first desktop icon
if layout_list:
    layout_list[0]['icon_html'] = hdr_script

payload = json.dumps({
    'layout': json.dumps(layout_list)
}).encode()

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Desktop%20Layout/Administrator', data=payload, headers=H, method='PUT')
res = opener.open(req)
print('Updated Administrator Desktop Layout: HTTP', res.status)

# Also update testdau@gmail.com and any other Desktop Layout records
r_all = opener.open('http://38.247.138.224:10017/api/resource/Desktop%20Layout?limit_page_length=100')
all_layouts = json.loads(r_all.read().decode())['data']
for l in all_layouts:
    if l['name'] != 'Administrator':
        try:
            req_u = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Desktop%20Layout/{urllib.parse.quote(l["name"])}', data=payload, headers=H, method='PUT')
            opener.open(req_u)
            print('Updated layout for:', l['name'])
        except Exception as ex:
            print('Error updating layout for', l['name'], ex)
