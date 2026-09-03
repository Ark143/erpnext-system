import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# Check if Print Format exists
pf_name = "Employee ID Badge with QR Code"
url_get = f"http://38.247.138.224:10017/api/resource/Print%20Format/{urllib.parse.quote(pf_name)}"

html_template = """
<div style="width: 320px; border: 2px solid #1e3a8a; border-radius: 12px; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background: #fff; margin: 20px auto; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: #fff; padding: 14px; text-align: center;">
        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.9;">ULTRA MRF GROUP</div>
        <div style="font-size: 16px; font-weight: 800; margin-top: 2px;">{{ doc.company or 'Automotive Service Center' }}</div>
        <div style="font-size: 10px; opacity: 0.8; margin-top: 1px;">OFFICIAL EMPLOYEE ID BADGE</div>
    </div>
    
    <div style="padding: 16px; text-align: center;">
        {% if doc.image %}
            <img src="{{ doc.image }}" style="width: 84px; height: 84px; border-radius: 50%; object-fit: cover; border: 3px solid #e2e8f0; margin: 0 auto;" />
        {% else %}
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #f1f5f9; border: 2px dashed #cbd5e1; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 32px; line-height: 80px;">👤</div>
        {% endif %}
        
        <div style="font-size: 17px; font-weight: 800; color: #0f172a; margin-top: 10px;">{{ doc.employee_name }}</div>
        <div style="font-size: 12px; font-weight: 600; color: #2563eb; margin-top: 2px;">{{ doc.designation or 'Technician / Staff' }}</div>
        <div style="font-size: 11px; color: #64748b;">Dept: {{ doc.department or 'Operations' }} · Emp #: <b>{{ doc.name }}</b></div>
        
        <div style="margin: 14px 0 8px 0; padding: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; display: inline-block;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=140x140&margin=4&data={{ doc.user_id or doc.name }}" style="width: 130px; height: 130px; display: block; margin: 0 auto;" alt="Employee QR Code" />
            <div style="font-size: 10px; color: #64748b; font-family: monospace; margin-top: 4px;">{{ doc.user_id or doc.name }}</div>
        </div>
        
        <div style="font-size: 9.5px; color: #94a3b8; line-height: 1.3;">Scan this badge for POS login and Warehouse Receiver Handover Safety Verification.</div>
    </div>
    <div style="background: #f1f5f9; padding: 6px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 9px; color: #64748b; font-weight: 600;">
        PROPERTY OF ULTRA MRF · AUTHORIZED PERSONNEL ONLY
    </div>
</div>
"""

payload = {
    "doctype": "Print Format",
    "name": pf_name,
    "doc_type": "Employee",
    "module": "Vehicle Management",
    "standard": "No",
    "custom_format": 1,
    "print_format_type": "Jinja",
    "html": html_template.strip()
}

req_headers = {'Content-Type': 'application/json'}
try:
    req = urllib.request.Request(url_get)
    r = opener.open(req)
    # Update existing
    url_put = url_get
    req_put = urllib.request.Request(url_put, data=json.dumps(payload).encode(), headers=req_headers, method='PUT')
    opener.open(req_put)
    print(f"Updated Print Format '{pf_name}'")
except urllib.error.HTTPError as e:
    if e.code == 404:
        # Create new
        url_post = "http://38.247.138.224:10017/api/resource/Print%20Format"
        req_post = urllib.request.Request(url_post, data=json.dumps(payload).encode(), headers=req_headers, method='POST')
        opener.open(req_post)
        print(f"Created Print Format '{pf_name}'")
    else:
        print(f"HTTP Error: {e.code} - {e.read().decode()}")
