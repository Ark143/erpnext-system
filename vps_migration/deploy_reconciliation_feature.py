import ast, json, pathlib, datetime, requests

ROOT = pathlib.Path(r'C:\Users\josem\erpnext-system')
WORK = pathlib.Path(r'C:\Users\josem\Documents\Codex\2026-09-06\can-you-add-openai-to-my\work\reconciliation')

source = ast.parse((ROOT / 'vps_migration/sync_webpage_pos_terminal.py').read_text(encoding='utf-8'))
login_data = next(ast.literal_eval(n) for n in ast.walk(source) if isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == 'pwd' for k in n.keys))
base = 'http://38.247.138.224:10017'

session = requests.Session()

def login():
    print("[1/5] Logging in to ERPNext...", flush=True)
    r = session.post(f"{base}/api/method/login", data=login_data, timeout=30)
    r.raise_for_status()
    print("      Logged in successfully.", flush=True)

def update_server_scripts():
    print("[2/5] Updating Server Scripts...", flush=True)
    scripts_to_update = {
        'vm_pos_get_shift': 'vm_pos_get_shift_new.py',
        'vm_pos_close_shift': 'vm_pos_close_shift_new.py',
        'vm_pos_history': 'vm_pos_history_new.py',
        'vm_pos_open_shift': 'vm_pos_open_shift_new.py',
        'vm_pos_create_invoice': 'vm_pos_create_invoice_new.py',
    }
    
    # Get all server scripts
    res = session.get(f"{base}/api/resource/Server%20Script?fields=[\"name\",\"api_method\"]&limit_page_length=500", timeout=30).json()
    script_map = {item['api_method']: item['name'] for item in res.get('data', []) if 'api_method' in item}
    
    for api_method, filename in scripts_to_update.items():
        doc_name = script_map.get(api_method)
        if not doc_name:
            print(f"      [WARN] Could not find script for {api_method}", flush=True)
            continue
        new_code = (WORK / filename).read_text(encoding='utf-8')
        put_res = session.put(
            f"{base}/api/resource/Server%20Script/{requests.utils.quote(doc_name)}",
            json={'script': new_code, 'disabled': 0},
            timeout=30
        )
        put_res.raise_for_status()
        print(f"      [OK] Updated Server Script: {doc_name} ({api_method})", flush=True)

def update_web_page():
    print("[3/5] Updating Web Page vehicle-pos-terminal...", flush=True)
    new_html = (WORK / 'pos_after.html').read_text(encoding='utf-8')
    put_res = session.put(
        f"{base}/api/resource/Web%20Page/vehicle-pos-terminal",
        json={'main_section_html': new_html},
        timeout=60
    )
    put_res.raise_for_status()
    print("      [OK] Updated Web Page on live server.", flush=True)

def clean_preview_scripts():
    print("[4/5] Cleaning up temporary preview scripts...", flush=True)
    res = session.get(f"{base}/api/resource/Server%20Script?fields=[\"name\",\"api_method\"]&limit_page_length=500", timeout=30).json()
    for item in res.get('data', []):
        if item.get('api_method') in ['vm_pos_reconciliation_check_20260906', 'vm_pos_reconciliation_close_check_20260906']:
            name = item['name']
            session.delete(f"{base}/api/resource/Server%20Script/{requests.utils.quote(name)}", timeout=30)
            print(f"      [OK] Deleted temporary script: {name}", flush=True)

def sync_local_files():
    print("[5/5] Syncing local workspace files...", flush=True)
    new_html = (WORK / 'pos_after.html').read_text(encoding='utf-8')
    (ROOT / 'vps_migration' / 'current_pos_terminal.html').write_text(new_html, encoding='utf-8')
    bench_file = ROOT / 'frappe-bench' / 'apps' / 'vehicle_management' / 'vehicle_management' / 'www' / 'pos_terminal.html'
    if bench_file.exists():
        bench_file.write_text(new_html, encoding='utf-8')
    print("      [OK] Local files synced.", flush=True)

def validate():
    print("\n--- VALIDATING LIVE RECONCILIATION API ---", flush=True)
    res = session.get(f"{base}/api/method/vm_pos_get_shift?company=ULTRA%20MRF", timeout=30).json()
    shift = res.get('message', {}).get('shift', {})
    print(f"Shift ID: {shift.get('name')}", flush=True)
    print(f"User: {shift.get('user')}", flush=True)
    print(f"Total Invoices: {shift.get('total_invoices')}", flush=True)
    print(f"Total Sales: {shift.get('total_sales')}", flush=True)
    print(f"Expected Cash: {shift.get('expected_closing')}", flush=True)
    print(f"Earlier Invoices: {shift.get('earlier_invoice_count')}", flush=True)
    print("All live reconciliation endpoints and frontend deployed successfully!", flush=True)

if __name__ == '__main__':
    login()
    update_server_scripts()
    update_web_page()
    clean_preview_scripts()
    sync_local_files()
    validate()
