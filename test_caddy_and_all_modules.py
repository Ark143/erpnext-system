import urllib.request
import json
import sys

endpoints = [
    ("Login Page", "http://localhost/login"),
    ("Desk UI", "http://localhost/desk"),
    ("Executive Dashboard Web Page", "http://localhost/executive-dashboard"),
    ("Executive Universal Page", "http://localhost/executive"),
    ("Socket.IO Polling", "http://localhost/socket.io/?EIO=4&transport=polling"),
    ("Realtime User Info API", "http://localhost/api/method/frappe.realtime.get_user_info"),
    ("Dashboard API (Meta)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=meta"),
    ("Dashboard API (Exec Summary)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=exec_summary&company=Ultra+MRF+Dau+Main"),
    ("Dashboard API (Sales)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=sales&company=Ultra+MRF+Dau+Main"),
    ("Dashboard API (Procurement)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=procurement&company=Ultra+MRF+Dau+Main"),
    ("Dashboard API (Finance)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=finance&company=Ultra+MRF+Dau+Main"),
    ("Dashboard API (Operations)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=operations&company=Ultra+MRF+Dau+Main"),
    ("Dashboard API (Approvals)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=approvals&company=Ultra+MRF+Dau+Main"),
    ("Dashboard API (Alerts)", "http://localhost/api/method/vehicle_management.vehicle_management.executive_dashboard.executive_dashboard?view=alerts&company=Ultra+MRF+Dau+Main"),
    ("Company Profile (San Fernando)", "http://localhost/executive-ultra-mrf-san-fernando"),
    ("Company Profile (Wheel Core)", "http://localhost/executive-wheel-core"),
    ("Company Profile (Automan)", "http://localhost/executive-automan-car-care-center")
]

print(f"{'Endpoint':35s} | {'Status':6s} | {'Response Preview'}")
print("-" * 80)
all_ok = True
for name, url in endpoints:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            code = res.getcode()
            body = res.read(120).decode("utf-8", errors="ignore").replace("\n", " ").strip()
            print(f"{name:35s} | {code:<6d} | {body[:50]}...")
    except Exception as e:
        print(f"{name:35s} | ERROR  | {e}")
        all_ok = False

if all_ok:
    print("\n>>> ALL CADDY ROUTES, WEBPAGES & APIS ARE 100% OPERATIONAL! <<<")
else:
    print("\n>>> SOME ENDPOINTS RETURNED ERRORS <<<")
    sys.exit(1)
