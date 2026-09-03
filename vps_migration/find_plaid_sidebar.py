import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

py_code = """
def vm_find_all_plaid():
    from frappe.desk.doctype.workspace_sidebar.workspace_sidebar import auto_generate_sidebar_from_module
    workspace_sidebars = frappe.get_all(
        "Workspace Sidebar", fields=["name", "header_icon", "module_onboarding"]
    )
    module_sidebars = auto_generate_sidebar_from_module()
    
    matches = []
    
    # Check DB sidebars
    for sb in workspace_sidebars:
        doc = frappe.get_doc("Workspace Sidebar", sb["name"])
        for it in doc.items:
            lt = str(it.link_to or "").lower()
            if "plaid" in lt:
                matches.append({"type": "DB sidebar", "sb": sb["name"], "link_to": it.link_to})
                
    # Check module sidebars
    for msb in module_sidebars:
        title = msb.title or msb.name
        for it in msb.items:
            val = it.get("link_to") if isinstance(it, dict) else getattr(it, "link_to", None)
            if "plaid" in str(val or "").lower():
                matches.append({"type": "Module sidebar", "sb": title, "link_to": val})
                
    frappe.response["message"] = matches

vm_find_all_plaid()
"""

# Create Server Script
req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script',
    data=json.dumps({'name': 'VM Find All Plaid', 'script_type': 'API', 'api_method': 'vm_find_all_plaid', 'script': py_code, 'allow_guest': 0}).encode(),
    headers={'Content-Type': 'application/json'}
)
opener.open(req)

r = opener.open('http://38.247.138.224:10017/api/method/vm_find_all_plaid')
print('Matches:', r.read().decode())

req_del = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Find%20All%20Plaid', method='DELETE')
opener.open(req_del)
