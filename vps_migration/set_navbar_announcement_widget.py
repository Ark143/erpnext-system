import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

widget_html = """
<div id="vm-global-header-injector" style="display:none;"></div>
<script>
(function() {
  function mountVMHeader() {
    // 1. Desktop page header (.desktop-navbar)
    const deskContainer = $('.desktop-navbar .desktop-notifications');
    if (deskContainer.length && !$('#vm-header-pill-btn').length) {
      deskContainer.before(`
        <div id="vm-header-pill-btn" style="display:inline-flex; align-items:center; gap:8px; margin-right:12px;">
          <a href="/desk#workspace/Vehicle%20Management" style="background:#16c784; color:#04201a; font-weight:800; font-size:12.5px; border-radius:8px; padding:5px 12px; height:32px; display:inline-flex; align-items:center; text-decoration:none; box-shadow:0 2px 5px rgba(22,199,132,0.35); transition:all 0.15s ease;">
            <span style="font-size:14px; margin-right:5px;">🚗</span>
            <span>Vehicle Management</span>
          </a>
          <a href="/desk/vehicle_pos" style="background:#0c1a18; color:#16c784; font-weight:800; font-size:12.5px; border:1px solid #16c784; border-radius:8px; padding:5px 10px; height:32px; display:inline-flex; align-items:center; text-decoration:none;">
            <span style="margin-right:4px;">🐴</span>
            <span>POS</span>
          </a>
        </div>
      `);
    }

    // 2. Standard Desk header (#toolbar-user)
    const stdUser = $('#toolbar-user');
    if (stdUser.length && !$('#vm-std-header-pill').length) {
      stdUser.before(`
        <li class="nav-item d-flex align-items-center mr-2" id="vm-std-header-pill">
          <a href="/desk#workspace/Vehicle%20Management" class="btn btn-sm" style="background:#16c784; color:#04201a; font-weight:800; border-radius:8px; padding:4px 10px; height:30px; display:inline-flex; align-items:center; text-decoration:none; box-shadow:0 2px 4px rgba(22,199,132,0.3);">
            <span style="margin-right:4px;">🚗</span>
            <span>Vehicle Management</span>
          </a>
        </li>
      `);
    }
  }

  mountVMHeader();
  setInterval(mountVMHeader, 400);
})();
</script>
"""

ns_url = 'http://38.247.138.224:10017/api/resource/Navbar%20Settings/Navbar%20Settings'
payload = json.dumps({
    'announcement_widget': widget_html
}).encode()

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}
req = urllib.request.Request(ns_url, data=payload, headers=H, method='PUT')
res = opener.open(req)
print('Updated Navbar Settings announcement_widget: HTTP', res.status)
