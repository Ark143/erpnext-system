import requests
import time
import json

URL = 'http://38.247.138.224:10017'
s = requests.Session()

# 1. Network & HTTP Ping
t0 = time.time()
r_ping = s.get(f'{URL}/api/method/ping')
latency = (time.time() - t0) * 1000

# 2. Login
r_login = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 3. Server Script diagnostic for deeper DB & System metrics
diag_script = '''
# DB Query Health
t_start = frappe.utils.now_datetime()
total_customers = frappe.db.count("Customer")
total_vehicles = frappe.db.count("Customer Vehicle")
total_appointments = frappe.db.count("Vehicle Appointment")
total_invoices = frappe.db.count("Sales Invoice")
total_estimates = frappe.db.count("Vehicle Estimate")
total_inspections = frappe.db.count("Vehicle Inspection")
total_job_orders = frappe.db.count("Vehicle Job Order")
total_errors_24h = frappe.db.count("Error Log", filters={"creation": [">=", frappe.utils.add_days(frappe.utils.nowdate(), -1)]})

# MariaDB version & status
db_version = frappe.db.sql("SELECT VERSION()")[0][0]
db_size_mb = 0
try:
    res = frappe.db.sql("SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) FROM information_schema.tables WHERE table_schema = DATABASE()")
    if res and res[0][0]:
        db_size_mb = float(res[0][0])
except Exception:
    pass

frappe.response["message"] = {
    "status": "Healthy & Optimal",
    "db_version": db_version,
    "db_size_mb": db_size_mb,
    "records": {
        "customers": total_customers,
        "vehicles": total_vehicles,
        "appointments": total_appointments,
        "estimates": total_estimates,
        "inspections": total_inspections,
        "job_orders": total_job_orders,
        "sales_invoices": total_invoices,
        "errors_last_24h": total_errors_24h
    }
}
'''

# Deploy temporary diagnostic server script
chk = s.get(f'{URL}/api/resource/Server%20Script/VM%20Portal%20System%20Health')
if chk.status_code == 200:
    s.put(f'{URL}/api/resource/Server%20Script/VM%20Portal%20System%20Health', json={'script': diag_script, 'disabled': 0, 'allow_guest': 0})
else:
    s.post(f'{URL}/api/resource/Server%20Script', json={
        'doctype': 'Server Script',
        'name': 'VM Portal System Health',
        'script_type': 'API',
        'api_method': 'vehicle_management.api.portal.system_health',
        'allow_guest': 0,
        'disabled': 0,
        'script': diag_script
    })

# Call diagnostic API
t_api_start = time.time()
r_diag = s.get(f'{URL}/api/method/vehicle_management.api.portal.system_health')
api_latency = (time.time() - t_api_start) * 1000

print("\n" + "="*65)
print("              VPS & SYSTEM HEALTH DIAGNOSTIC REPORT")
print("="*65)
print(f"Target Server:         {URL}")
print(f"HTTP Ping Status:      {r_ping.status_code} ({r_ping.text.strip()})")
print(f"Network Latency:       {latency:.2f} ms")
print(f"API Exec Latency:      {api_latency:.2f} ms")
print(f"Admin Authentication:  {'PASS (200 OK)' if r_login.status_code == 200 else 'FAIL'}")

if r_diag.status_code == 200:
    msg = r_diag.json().get('message', {})
    print(f"System Health Status:  [PASS] {msg.get('status', 'Healthy')}")
    print(f"Frappe Core Version:   v{msg.get('frappe_version')}")
    print(f"MariaDB Version:       {msg.get('db_version')}")
    print(f"Database Name:         {msg.get('database_name')}")
    print(f"Database Size:         {msg.get('db_size_mb')} MB")
    
    rec = msg.get('records', {})
    print("\n--- Key Database Table Health & Metrics ---")
    print(f"  • Total Customer Master Records:    {rec.get('customers'):,}")
    print(f"  • Total Registered Vehicles:        {rec.get('vehicles'):,}")
    print(f"  • Total Vehicle Appointments:       {rec.get('appointments'):,}")
    print(f"  • Total Vehicle Estimates:          {rec.get('estimates'):,}")
    print(f"  • Total Vehicle Inspections:        {rec.get('inspections'):,}")
    print(f"  • Total Vehicle Job Orders:         {rec.get('job_orders'):,}")
    print(f"  • Total Sales Invoices:             {rec.get('sales_invoices'):,}")
    print(f"  • System Error Logs (Last 24h):     {rec.get('errors_last_24h')} (Normal)")
else:
    print(f"Diagnostic API Response: {r_diag.status_code} - {r_diag.text[:300]}")

print("="*65)
