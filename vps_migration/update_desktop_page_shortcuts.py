import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

page_script = """
frappe.pages['desktop'].on_page_load = function(wrapper) {
  function injectVMBtn() {
    if ($('#navbar-vm-header-shortcut').length > 0) return;
    const avatar = $('.desktop-avatar');
    if (!avatar.length) return;
    
    const vmBtn = $(`
      <a id="navbar-vm-header-shortcut" href="/desk#workspace/Vehicle%20Management" class="btn btn-sm" title="Vehicle Management Workspace" style="background:#16c784; color:#04201a; font-weight:900; font-size:13px; border-radius:8px; padding:4px 12px; height:32px; display:inline-flex; align-items:center; text-decoration:none; box-shadow:0 2px 5px rgba(22,199,132,0.35); margin-right:8px; transition:all 0.15s ease; cursor:pointer;">
        <span style="font-size:15px; margin-right:5px;">🚗</span>
        <span>VM Workspace</span>
      </a>
      <a id="navbar-pos-header-shortcut" href="/desk/vehicle_pos" class="btn btn-sm" title="Vehicle POS Terminal" style="background:#0c1a18; color:#16c784; font-weight:800; font-size:12.5px; border:1px solid #16c784; border-radius:8px; padding:4px 10px; height:32px; display:inline-flex; align-items:center; text-decoration:none; margin-right:8px; cursor:pointer;">
        <span style="margin-right:4px;">🐴</span>
        <span>POS</span>
      </a>
    `);
    avatar.before(vmBtn);
  }
  
  injectVMBtn();
  setTimeout(injectVMBtn, 200);
  setTimeout(injectVMBtn, 600);
  setTimeout(injectVMBtn, 1500);
};
"""

page_style = """
#navbar-vm-header-shortcut:hover {
  background: #0fa76d !important;
  color: #ffffff !important;
  transform: translateY(-1px);
}
#navbar-pos-header-shortcut:hover {
  background: #16c784 !important;
  color: #04201a !important;
  transform: translateY(-1px);
}
"""

url = 'http://38.247.138.224:10017/api/resource/Page/desktop'
payload = json.dumps({
    'script': page_script,
    'style': page_style
}).encode()

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(url, data=payload, headers=H, method='PUT')
res = opener.open(req)
print('Updated Page/desktop with VM header shortcuts: HTTP', res.status)

# Verify
doc = json.loads(opener.open(url).read().decode())['data']
print('Page script length:', len(doc.get('script') or ''))
