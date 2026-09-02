import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_stock_up = """
def stock_up_items():
    # Pick 25 sellable stock items
    items = frappe.get_all(
        "Item",
        filters={"is_stock_item": 1, "disabled": 0, "is_sales_item": 1},
        fields=["name", "stock_uom", "standard_rate", "item_name"],
        limit=25
    )
    
    companies = [
        {"company": "ULTRA MRF", "wh": "Stores - UM"},
        {"company": "Ultra MRF Dau Main", "wh": "Stores - UMDM"},
        {"company": "Ultra MRF Dau Annex", "wh": "Stores - UMDA"}
    ]
    
    created = []
    for c in companies:
        company = c["company"]
        wh = c["wh"]
        
        # Check existing Stock Entry for this company
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.company = company
        se.to_warehouse = wh
        
        for it in items:
            rate = float(it.standard_rate or 50.0)
            se.append("items", {
                "item_code": it.name,
                "qty": 50,
                "uom": it.stock_uom or "Nos",
                "stock_uom": it.stock_uom or "Nos",
                "conversion_factor": 1,
                "t_warehouse": wh,
                "basic_rate": rate
            })
            
        try:
            se.insert()
            se.submit()
            frappe.db.commit()
            created.append({"company": company, "stock_entry": se.name, "items_count": len(items)})
        except Exception as e:
            created.append({"company": company, "error": str(e)[:200]})
            
    frappe.response["message"] = created

stock_up_items()
"""

name = 'VM Stock Up Demo Items'
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_stock_up_demo_items',
    'allow_guest': 1,
    'disabled': 0,
    'script': script_stock_up
}

try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
except Exception:
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}', data=urllib.parse.urlencode({'data': json.dumps({'script': script_stock_up})}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_stock_up_demo_items', headers=H))
print('Stock Up Result:', r.read().decode())
