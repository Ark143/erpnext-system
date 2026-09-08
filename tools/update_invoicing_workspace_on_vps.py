import urllib.request
import urllib.parse
import json
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
op.open(urllib.request.Request(f'{VPS_BASE}/api/method/login', data=login_data, headers=H))

# Fetch current Invoicing workspace from VPS
req = urllib.request.Request(f'{VPS_BASE}/api/resource/Workspace/Invoicing', headers=H)
res = op.open(req)
invoicing_ws = json.loads(res.read().decode('utf-8')).get('data', {})

# Parse content JSON
content_list = json.loads(invoicing_ws.get('content', '[]'))

# Check if BIR card is already in content
has_bir = any('BIR' in str(c) for c in content_list)

bir_card_id = "bir_compliance_card_01"
bir_header_id = "bir_compliance_header_01"

if not has_bir:
    # Insert BIR header and card at the top after number cards or before other cards
    # Find insert index
    insert_idx = 0
    for idx, item in enumerate(content_list):
        if item.get('type') == 'card' or item.get('type') == 'header':
            insert_idx = idx
            break
    if insert_idx == 0:
        insert_idx = len(content_list)
        
    bir_header = {
        "id": bir_header_id,
        "type": "header",
        "data": {
            "text": "<span class=\"h4\"><b>BIR Compliance &amp; Tax Modules (Philippines)</b></span>",
            "col": 12
        }
    }
    bir_card = {
        "id": bir_card_id,
        "type": "card",
        "data": {
            "card_name": "BIR Compliance & Books",
            "col": 6
        }
    }
    content_list.insert(insert_idx, bir_header)
    content_list.insert(insert_idx + 1, bir_card)

# Update workspace links
links = invoicing_ws.get('links', [])

# Remove existing BIR links if any to avoid duplicates
links = [l for l in links if not l.get('label', '').startswith('BIR') and l.get('label') != 'BIR Compliance & Books']

# Add Card Break and links for BIR
bir_links = [
    {
        "type": "Card Break",
        "label": "BIR Compliance & Books",
        "link_type": "DocType",
        "onboard": 0,
        "is_query_report": 0,
        "link_count": 9,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR Form 2307 (Withholding Certificate)",
        "link_type": "DocType",
        "link_to": "BIR Form 2307",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR Sales Journal (Sales Book)",
        "link_type": "DocType",
        "link_to": "BIR Sales Journal",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR Purchases Book (Purchases Journal)",
        "link_type": "DocType",
        "link_to": "BIR Purchases Book",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR Cash Receipt Journal (CRJ)",
        "link_type": "DocType",
        "link_to": "BIR Cash Receipt Journal",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR Cash Disbursement Journal (CDJ)",
        "link_type": "DocType",
        "link_to": "BIR Cash Disbursement Journal",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR General Journal (GJ)",
        "link_type": "DocType",
        "link_to": "BIR General Journal",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR General Ledger (GL)",
        "link_type": "DocType",
        "link_to": "BIR General Ledger",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR VAT Summary (VAT Return 2550)",
        "link_type": "DocType",
        "link_to": "BIR VAT Summary",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    },
    {
        "type": "Link",
        "label": "BIR Withholding Summary (EWT/FWT)",
        "link_type": "DocType",
        "link_to": "BIR Withholding Summary",
        "onboard": 0,
        "is_query_report": 0,
        "parent": "Invoicing",
        "parentfield": "links",
        "parenttype": "Workspace",
        "doctype": "Workspace Link"
    }
]

# Prepend BIR links to the links array
updated_links = bir_links + links
for idx, l in enumerate(updated_links):
    l['idx'] = idx + 1

# Update shortcuts
shortcuts = invoicing_ws.get('shortcuts', [])
bir_shortcuts = [
    {
        "type": "DocType",
        "link_to": "BIR Form 2307",
        "label": "BIR Form 2307",
        "color": "Grey",
        "docstatus": 0,
        "parent": "Invoicing",
        "parentfield": "shortcuts",
        "parenttype": "Workspace",
        "doctype": "Workspace Shortcut"
    },
    {
        "type": "DocType",
        "link_to": "BIR Sales Journal",
        "label": "BIR Sales Book",
        "color": "Grey",
        "docstatus": 0,
        "parent": "Invoicing",
        "parentfield": "shortcuts",
        "parenttype": "Workspace",
        "doctype": "Workspace Shortcut"
    },
    {
        "type": "DocType",
        "link_to": "BIR VAT Summary",
        "label": "BIR VAT Summary",
        "color": "Grey",
        "docstatus": 0,
        "parent": "Invoicing",
        "parentfield": "shortcuts",
        "parenttype": "Workspace",
        "doctype": "Workspace Shortcut"
    }
]

# Update workspace payload
payload = {
    'content': json.dumps(content_list),
    'links': updated_links,
    'shortcuts': bir_shortcuts + [s for s in shortcuts if 'BIR' not in s.get('label', '')]
}

req = urllib.request.Request(
    f'{VPS_BASE}/api/resource/Workspace/Invoicing',
    data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode('utf-8'),
    headers=H
)
req.get_method = lambda: 'PUT'
res = op.open(req)
print("Invoicing Workspace Update Status:", res.getcode())

# Clear cache
op.open(urllib.request.Request(f'{VPS_BASE}/api/method/frappe.desk.doctype.workspace.workspace.clear_workspace_cache', headers=H))
print("Cleared Workspace Cache on VPS")
