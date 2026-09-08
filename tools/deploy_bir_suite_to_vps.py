import urllib.request
import urllib.parse
import json
import os
import glob
import http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

VPS_BASE = 'http://38.247.138.224:10017'

# Login to VPS
login_data = urllib.parse.urlencode({'usr': 'Administrator', 'pwd': 'admin'}).encode()
login_res = op.open(urllib.request.Request(f'{VPS_BASE}/api/method/login', data=login_data, headers=H))
print("VPS Login Status:", login_res.getcode())

def vps_get(path):
    try:
        req = urllib.request.Request(f'{VPS_BASE}/api/{path}', headers=H)
        r = op.open(req)
        return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {'error_code': e.code, 'error_msg': str(e)}
    except Exception as e:
        return {'error': str(e)}

def vps_post(path, data_dict):
    try:
        req_data = urllib.parse.urlencode(data_dict).encode('utf-8')
        req = urllib.request.Request(f'{VPS_BASE}/api/{path}', data=req_data, headers=H)
        r = op.open(req)
        return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_content = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        return {'error_code': e.code, 'error_content': err_content}
    except Exception as e:
        return {'error': str(e)}

def vps_put(path, data_dict):
    try:
        req_data = urllib.parse.urlencode(data_dict).encode('utf-8')
        req = urllib.request.Request(f'{VPS_BASE}/api/{path}', data=req_data, headers=H)
        req.get_method = lambda: 'PUT'
        r = op.open(req)
        return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err_content = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        return {'error_code': e.code, 'error_content': err_content}
    except Exception as e:
        return {'error': str(e)}

# -----------------------------------------------------------------------------
# STEP 1: Deploy Child Tables First
# -----------------------------------------------------------------------------
child_tables = [
    'BIR CDJ Invoice Row',
    'BIR CDJ Summary Row',
    'BIR CRJ Invoice Row',
    'BIR CRJ Summary Row',
    'BIR Form 2307 Row',
    'BIR GJ Entry Row',
    'BIR GL Entry Row',
    'BIR Purchases Book Row',
    'BIR Sales Journal Row',
    'BIR Sales Summary Row',
    'BIR VAT Summary Row',
    'BIR VAT Summary Total Row',
    'BIR Withholding Summary Row'
]

# -----------------------------------------------------------------------------
# STEP 2: Deploy Parent DocTypes
# -----------------------------------------------------------------------------
parent_tables = [
    'BIR Cash Disbursement Journal',
    'BIR Cash Receipt Journal',
    'BIR Form 2307',
    'BIR General Journal',
    'BIR General Ledger',
    'BIR Purchases Book',
    'BIR Sales Journal',
    'BIR VAT Summary',
    'BIR Withholding Summary'
]

def clean_doctype_payload(doc):
    # Remove system auto-generated metadata fields that shouldn't be sent on insert/update
    keys_to_clean = ['creation', 'modified', 'modified_by', 'owner', 'docstatus', 'idx', '_user_tags', '_comments', '_assign', '_liked_by']
    cleaned = {k: v for k, v in doc.items() if k not in keys_to_clean}
    
    # Ensure custom=1 and module is Accounts
    cleaned['custom'] = 1
    cleaned['module'] = 'Accounts'
    
    # Clean fields list
    if 'fields' in cleaned:
        cleaned_fields = []
        for f in cleaned['fields']:
            cf = {k: v for k, v in f.items() if k not in keys_to_clean}
            cf['parent'] = cleaned['name']
            cf['parenttype'] = 'DocType'
            cf['parentfield'] = 'fields'
            cleaned_fields.append(cf)
        cleaned['fields'] = cleaned_fields
        
    # Clean permissions list
    if 'permissions' in cleaned:
        cleaned_perms = []
        for p in cleaned['permissions']:
            cp = {k: v for k, v in p.items() if k not in keys_to_clean}
            cp['parent'] = cleaned['name']
            cp['parenttype'] = 'DocType'
            cp['parentfield'] = 'permissions'
            cleaned_perms.append(cp)
        cleaned['permissions'] = cleaned_perms
    else:
        # Default permissions for Administrator, Accounts User, Accounts Manager, System Manager
        cleaned['permissions'] = [
            {'role': 'System Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'report': 1, 'export': 1, 'print': 1, 'email': 1},
            {'role': 'Accounts Manager', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'report': 1, 'export': 1, 'print': 1, 'email': 1},
            {'role': 'Accounts User', 'read': 1, 'write': 1, 'create': 1, 'delete': 1, 'report': 1, 'export': 1, 'print': 1, 'email': 1}
        ]
        
    return cleaned

def deploy_doctype(dt_name):
    file_path = f"tools/bir_export/doctypes/{dt_name.replace(' ', '_')}.json"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        doc = json.load(f)
        
    payload = clean_doctype_payload(doc)
    
    # Check if doctype exists on VPS
    check = vps_get(f"resource/DocType/{urllib.parse.quote(dt_name)}")
    if check.get('data'):
        print(f"DocType '{dt_name}' already exists on VPS, updating...")
        res = vps_put(f"resource/DocType/{urllib.parse.quote(dt_name)}", {'data': json.dumps(payload)})
        if 'data' in res:
            print(f" -> Updated DocType: {dt_name}")
        else:
            print(f" -> Failed updating {dt_name}: {res}")
    else:
        print(f"Creating DocType '{dt_name}' on VPS...")
        res = vps_post("resource/DocType", {'data': json.dumps(payload)})
        if 'data' in res:
            print(f" -> Created DocType: {dt_name}")
        else:
            print(f" -> Failed creating {dt_name}: {res}")

print("\n--- DEPLOYING CHILD TABLE DOCTYPES ---")
for ct in child_tables:
    deploy_doctype(ct)

print("\n--- DEPLOYING PARENT DOCTYPES ---")
for pt in parent_tables:
    deploy_doctype(pt)

# -----------------------------------------------------------------------------
# STEP 3: Deploy Client Scripts
# -----------------------------------------------------------------------------
print("\n--- DEPLOYING CLIENT SCRIPTS ---")
cs_files = glob.glob('tools/bir_export/client_scripts/BIR_*.json')
for cs_file in cs_files:
    with open(cs_file, 'r', encoding='utf-8') as f:
        cs_doc = json.load(f)
    
    cs_name = cs_doc.get('name')
    cs_payload = {
        'dt': cs_doc.get('dt'),
        'view': cs_doc.get('view', 'Form'),
        'script': cs_doc.get('script'),
        'enabled': 1
    }
    
    # Check if exists on VPS
    check = vps_get(f"resource/Client%20Script/{urllib.parse.quote(cs_name)}")
    if check.get('data'):
        print(f"Client Script '{cs_name}' exists, updating...")
        res = vps_put(f"resource/Client%20Script/{urllib.parse.quote(cs_name)}", {'data': json.dumps(cs_payload)})
        if 'data' in res:
            print(f" -> Updated Client Script: {cs_name}")
        else:
            print(f" -> Update failed: {res}")
    else:
        print(f"Creating Client Script '{cs_name}'...")
        cs_payload['name'] = cs_name
        res = vps_post("resource/Client%20Script", {'data': json.dumps(cs_payload)})
        if 'data' in res:
            print(f" -> Created Client Script: {cs_name}")
        else:
            print(f" -> Creation failed: {res}")

# -----------------------------------------------------------------------------
# STEP 4: Deploy Print Formats
# -----------------------------------------------------------------------------
print("\n--- DEPLOYING PRINT FORMATS ---")
pf_files = glob.glob('tools/bir_export/print_formats/BIR_*.json')
for pf_file in pf_files:
    with open(pf_file, 'r', encoding='utf-8') as f:
        pf_doc = json.load(f)
        
    pf_name = pf_doc.get('name')
    pf_payload = {
        'name': pf_name,
        'doc_type': pf_doc.get('doc_type'),
        'module': 'Accounts',
        'standard': 'No',
        'custom_format': 1,
        'print_format_type': pf_doc.get('print_format_type', 'Jinja'),
        'html': pf_doc.get('html'),
        'css': pf_doc.get('css', ''),
        'raw_printing': 0,
        'disabled': 0
    }
    
    check = vps_get(f"resource/Print%20Format/{urllib.parse.quote(pf_name)}")
    if check.get('data'):
        print(f"Print Format '{pf_name}' exists, updating...")
        res = vps_put(f"resource/Print%20Format/{urllib.parse.quote(pf_name)}", {'data': json.dumps(pf_payload)})
        if 'data' in res:
            print(f" -> Updated Print Format: {pf_name}")
        else:
            print(f" -> Update failed: {res}")
    else:
        print(f"Creating Print Format '{pf_name}'...")
        res = vps_post("resource/Print%20Format", {'data': json.dumps(pf_payload)})
        if 'data' in res:
            print(f" -> Created Print Format: {pf_name}")
        else:
            print(f" -> Creation failed: {res}")

# -----------------------------------------------------------------------------
# STEP 5: Update Default Print Formats on DocTypes
# -----------------------------------------------------------------------------
print("\n--- SETTING DEFAULT PRINT FORMATS ---")
pf_map = {
    'BIR Cash Disbursement Journal': 'BIR Cash Disbursement Journal Print Format',
    'BIR Cash Receipt Journal': 'BIR Cash Receipt Journal Print Format',
    'BIR Form 2307': 'BIR Form 2307 Print Format',
    'BIR General Journal': 'BIR General Journal Print Format',
    'BIR General Ledger': 'BIR General Ledger Print Format',
    'BIR Purchases Book': 'BIR Purchases Book Print Format',
    'BIR Sales Journal': 'BIR Sales Journal Print Format',
    'BIR VAT Summary': 'BIR VAT Summary Print Format',
    'BIR Withholding Summary': 'BIR Withholding Summary Print Format'
}

for dt, pf in pf_map.items():
    res = vps_put(f"resource/DocType/{urllib.parse.quote(dt)}", {'data': json.dumps({'default_print_format': pf})})
    print(f"Attached default print format '{pf}' to {dt}")

print("\n=== BIR SUITE DEPLOYMENT COMPLETE ===")
