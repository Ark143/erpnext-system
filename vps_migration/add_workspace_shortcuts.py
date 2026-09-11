import requests, json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=15)

# 1. Update Financial Reports workspace
fr_res = session.get(f"{BASE_URL}/api/resource/Workspace/Financial%20Reports")
if fr_res.status_code == 200:
    fr_doc = fr_res.json().get('data', {})
    shortcuts = fr_doc.get('shortcuts', [])
    existing_labels = [s.get('label') or s.get('shortcut_name') for s in shortcuts]
    
    new_shortcuts = [
        {"label": "💵 Cash Flow Statement (Daily/Monthly/Yearly)", "type": "URL", "url": "/consolidated-financials#cash_flow", "color": "Green"},
        {"label": "📥 AR Aging (30, 60, 90 Days)", "type": "URL", "url": "/consolidated-financials#ar_aging", "color": "Blue"},
        {"label": "📤 AP Aging (30, 60, 90 Days)", "type": "URL", "url": "/consolidated-financials#ap_aging", "color": "Orange"},
        {"label": "📊 Consolidated Financials Console", "type": "URL", "url": "/consolidated-financials", "color": "Purple"},
    ]

    for ns in new_shortcuts:
        if ns['label'] not in existing_labels:
            shortcuts.append({
                "label": ns['label'],
                "type": ns['type'],
                "url": ns['url'],
                "color": ns['color']
            })

    fr_doc['shortcuts'] = shortcuts
    save_res = session.put(f"{BASE_URL}/api/resource/Workspace/Financial%20Reports", json=fr_doc)
    print("Updated Financial Reports Workspace shortcuts:", save_res.status_code)

# 2. Update Vehicle Management workspace
vm_res = session.get(f"{BASE_URL}/api/resource/Workspace/Vehicle%20Management")
if vm_res.status_code == 200:
    vm_doc = vm_res.json().get('data', {})
    shortcuts = vm_doc.get('shortcuts', [])
    existing_labels = [s.get('label') or s.get('shortcut_name') for s in shortcuts]

    new_shortcuts = [
        {"label": "💵 Cash Flow Statement", "type": "URL", "url": "/consolidated-financials#cash_flow", "color": "Green"},
        {"label": "📥 AR Aging (30/60/90 Days)", "type": "URL", "url": "/consolidated-financials#ar_aging", "color": "Blue"},
        {"label": "📤 AP Aging (30/60/90 Days)", "type": "URL", "url": "/consolidated-financials#ap_aging", "color": "Orange"},
        {"label": "📊 Consolidated Financials", "type": "URL", "url": "/consolidated-financials", "color": "Purple"},
    ]

    for ns in new_shortcuts:
        if ns['label'] not in existing_labels:
            shortcuts.append({
                "label": ns['label'],
                "type": ns['type'],
                "url": ns['url'],
                "color": ns['color']
            })

    vm_doc['shortcuts'] = shortcuts
    save_res = session.put(f"{BASE_URL}/api/resource/Workspace/Vehicle%20Management", json=vm_doc)
    print("Updated Vehicle Management Workspace shortcuts:", save_res.status_code)
