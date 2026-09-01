import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

validator_script = """
if doc.stock_entry_type == 'Material Issue':
    if not doc.custom_receiver_user:
        frappe.throw(
            '<b>SAFETY CHECK REQUIRED</b><br>' +
            'You cannot submit a Material Issue without scanning the receiver\\'s QR code badge.<br>' +
            'Please click <b>Verify Receiver QR & Capture Photo</b> to verify the receiver.',
            title='Receiver Verification Missing'
        )
    if not doc.custom_receiver_photo:
        frappe.throw(
            '<b>SAFETY CHECK REQUIRED</b><br>' +
            'A handover / receiver photo is required before submitting a Material Issue.<br>' +
            'Please capture or upload a handover photo proof.',
            title='Handover Photo Missing'
        )
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Stock%20Entry%20Safety%20Check',
    data=urllib.parse.urlencode({'data': json.dumps({'script': validator_script})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
op.open(req)
print("Updated VM Stock Entry Safety Check Server Script successfully!")
