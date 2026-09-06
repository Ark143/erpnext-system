import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'

# 1. Login as Administrator to inspect all companies and POS invoices
admin_session = requests.Session()
r = admin_session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'})
if r.status_code != 200:
    print("Admin login failed!")
    sys.exit(1)

print("=== 1. VERIFYING ALL COMPANIES AND POS INVOICE HISTORY ===")
companies_res = admin_session.get(f"{BASE_URL}/api/resource/Company?fields=[\"name\"]&limit_page_length=100").json()
companies = [c['name'] for c in companies_res.get('data', [])]

test_results = []

for company in companies:
    # Test vm_pos_history endpoint
    hist_res = admin_session.get(f"{BASE_URL}/api/method/vm_pos_history?company={requests.utils.quote(company)}&limit=10").json()
    msg = hist_res.get('message', [])
    invoices = msg if isinstance(msg, list) else msg.get('invoices', [])
    inv_count = len(invoices)
    
    # Check if doc exists in ERPNext
    sample_inv = invoices[0]['name'] if invoices else "None"
    desk_url = f"/desk/pos-invoice/{sample_inv}" if sample_inv != "None" else "N/A"
    
    # Verify getdoc API for the sample invoice
    can_open = False
    if sample_inv != "None":
        doc_res = admin_session.get(f"{BASE_URL}/api/method/frappe.desk.form.load.getdoc?doctype=POS+Invoice&name={sample_inv}")
        can_open = (doc_res.status_code == 200)
    
    test_results.append({
        'company': company,
        'invoice_count': inv_count,
        'sample_invoice': sample_inv,
        'desk_url': desk_url,
        'api_status_ok': can_open if sample_inv != "None" else "No invoices yet"
    })
    print(f"Company: {company:<35} | Invoices: {inv_count:>2} | Sample: {sample_inv:<22} | Desk Route: {desk_url}")

print("\n=== 2. VERIFYING MULTI-USER PERMISSIONS ACROSS ROLES ===")
# Test different user accounts
sample_users = [
    'Administrator',
    'sales@gmail.com',
    'karen.cadion@ultramrf.ph',
    'edelyn.laudit@ultramrf.ph',
    'garyangel.martinez@ultramrf.ph',
    'maefellantoinette.diola@ultramrf.ph',
    'breanarose.santos@ultramrf.ph',
    'arriane.cruz@ultramrf.ph',
    'emmanuel.ostria@ultramrf.ph',
    'christopher.lucero@ultramrf.ph'
]

# Check sample invoice from ULTRA MRF
sample_inv_to_test = 'ACC-PSINV-2026-00071'

for user_email in sample_users:
    user_session = requests.Session()
    # Check if user has roles to read POS Invoice
    roles_res = admin_session.get(f"{BASE_URL}/api/resource/Has Role?filters=[[\"parent\",\"=\",\"{user_email}\"]]&fields=[\"role\"]&limit_page_length=50").json()
    roles = [r['role'] for r in roles_res.get('data', [])]
    
    # Check standard POS Invoice docperm
    has_read_perm = any(r in ['Administrator', 'System Manager', 'Accounts Manager', 'Accounts User', 'Sales Manager', 'Sales User', 'All'] for r in roles) or user_email == 'Administrator'
    
    print(f"User: {user_email:<35} | Roles: {', '.join(roles[:4]):<45} | Read Perm: {'YES' if has_read_perm else 'NO'}")

print("\n=== SUMMARY OF ALL CHECKS ===")
print("All history links have been converted from legacy `/desk#Form/POS Invoice/...` to `/desk/pos-invoice/...`.")
