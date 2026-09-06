import pathlib, json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

# File paths
files = [
    pathlib.Path(r'C:\Users\josem\Documents\Codex\2026-09-06\can-you-add-openai-to-my\work\reconciliation\pos_after.html'),
    pathlib.Path(r'c:\Users\josem\erpnext-system\vps_migration\current_pos_terminal.html'),
    pathlib.Path(r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html'),
    pathlib.Path(r'c:\Users\josem\erpnext-system\vps_migration\vehicle_pos_page.js')
]

replacements = [
    ("/desk#Form/POS Invoice/", "/desk/pos-invoice/"),
    ("/desk#Form/POS%20Invoice/", "/desk/pos-invoice/"),
    ("/desk#Form/Vehicle POS Invoice/", "/desk/pos-invoice/"),
    ("/desk#Form/Vehicle%20POS%20Invoice/", "/desk/pos-invoice/"),
    ("`/desk#Form/POS Invoice/${r.message.pos_invoice}`", "`/desk/pos-invoice/${encodeURIComponent(r.message.pos_invoice)}`"),
]

for p in files:
    if not p.exists():
        print("Skipping non-existent:", p)
        continue
    content = p.read_text(encoding='utf-8')
    orig = content
    for old, new in replacements:
        content = content.replace(old, new)
    if content != orig:
        p.write_text(content, encoding='utf-8')
        print(f"Patched: {p}")
    else:
        print(f"No changes needed: {p}")

# Now deploy to ERPNext live server
BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
login_res.raise_for_status()
print("\n[OK] Logged in to ERPNext as Administrator")

# Update Web Page vehicle-pos-terminal
html_content = pathlib.Path(r'C:\Users\josem\Documents\Codex\2026-09-06\can-you-add-openai-to-my\work\reconciliation\pos_after.html').read_text(encoding='utf-8')
r1 = session.put(
    f"{BASE_URL}/api/resource/Web%20Page/vehicle-pos-terminal",
    json={'main_section_html': html_content},
    timeout=60
)
r1.raise_for_status()
print("[OK] Deployed updated HTML to Web Page: vehicle-pos-terminal")

# Check if vehicle-pos exists and update if so
try:
    r2 = session.put(
        f"{BASE_URL}/api/resource/Web%20Page/vehicle-pos",
        json={'main_section_html': html_content},
        timeout=60
    )
    if r2.status_code == 200:
        print("[OK] Deployed updated HTML to Web Page: vehicle-pos")
except Exception as e:
    print("Web Page vehicle-pos note:", e)

print("\nDeployment of history desk links completed successfully!")
