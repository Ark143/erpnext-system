import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

script_vm_pos_items = """
def get_pos_items():
    company = frappe.form_dict.get("company") or ""
    only_stock = int(frappe.form_dict.get("only_stock") or frappe.form_dict.get("in_stock") or 0)
    txt = (frappe.form_dict.get("txt") or "").strip()
    category = (frappe.form_dict.get("category") or "").strip()
    limit = int(frappe.form_dict.get("limit") or 80)
    
    where_clauses = ["i.disabled = 0", "i.is_sales_item = 1"]
    params = []
    
    if txt:
        like_txt = "%" + txt + "%"
        where_clauses.append("(i.name LIKE %s OR i.item_name LIKE %s)")
        params.extend([like_txt, like_txt])
        
    if category:
        where_clauses.append("i.item_group = %s")
        params.append(category)
        
    wh_join = ""
    if company:
        wh_join = 'JOIN "tabWarehouse" w ON w.name = b.warehouse AND w.company = %s'
        params.append(company)
    
    if only_stock:
        sql = '''
            SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                   i.stock_uom as uom, i.item_group as `group`,
                   COALESCE(SUM(b.actual_qty), 0) as stock
            FROM "tabItem" i
            JOIN "tabBin" b ON b.item_code = i.name AND b.actual_qty > 0
            ''' + wh_join + '''
            WHERE ''' + " AND ".join(where_clauses) + '''
            GROUP BY i.name, i.item_name, i.standard_rate, i.stock_uom, i.item_group
            HAVING SUM(b.actual_qty) > 0
            ORDER BY stock DESC, i.item_name ASC
            LIMIT ''' + str(limit) + '''
        '''
    else:
        sql = '''
            SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                   i.stock_uom as uom, i.item_group as `group`,
                   COALESCE((
                       SELECT SUM(b.actual_qty) FROM "tabBin" b 
                       WHERE b.item_code = i.name AND b.actual_qty > 0
                   ), 0) as stock
            FROM "tabItem" i
            WHERE ''' + " AND ".join(where_clauses) + '''
            ORDER BY i.item_name ASC
            LIMIT ''' + str(limit) + '''
        '''
    
    rows = frappe.db.sql(sql, tuple(params), as_dict=True)
    frappe.response["message"] = rows

get_pos_items()
"""

name = 'VM POS Items API'
payload = {
    'name': name,
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_pos_items',
    'allow_guest': 1,
    'disabled': 0,
    'script': script_vm_pos_items
}

try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script', data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
    op.open(req)
    print("Created Server Script 'VM POS Items API'.")
except Exception:
    req = urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Server%20Script/{urllib.parse.quote(name)}', data=urllib.parse.urlencode({'data': json.dumps({'script': script_vm_pos_items, 'disabled': 0})}).encode(), headers=H)
    req.get_method = lambda: 'PUT'
    op.open(req)
    print("Updated Server Script 'VM POS Items API'.")

# Test calling vm_pos_items?only_stock=1
r1 = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_items?only_stock=1', headers=H))
res1 = json.loads(r1.read().decode())
print("Test vm_pos_items?only_stock=1 response count:", len(res1.get('message', [])))
for it in res1.get('message', []):
    print(f"  - {it['name']} | Stock: {it['stock']} | Rate: PHP {it['rate']}")

# Test calling vm_pos_items?only_stock=0
r0 = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pos_items?only_stock=0&limit=5', headers=H))
res0 = json.loads(r0.read().decode())
print("Test vm_pos_items?only_stock=0 (first 5):", len(res0.get('message', [])))
