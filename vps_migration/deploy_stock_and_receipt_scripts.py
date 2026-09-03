import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# 1. Update VM POS Items API
get_items_script = """
def get_pos_items():
    company = (frappe.form_dict.get("company") or "").strip()
    only_stock = int(frappe.form_dict.get("only_stock") or frappe.form_dict.get("in_stock") or 0)
    txt = (frappe.form_dict.get("txt") or "").strip()
    category = (frappe.form_dict.get("category") or "").strip()
    limit = int(frappe.form_dict.get("limit") or 150)
    
    # Base item filters
    where_items = ["i.disabled = 0", "i.is_sales_item = 1"]
    params = []
    
    if txt:
        like_txt = "%" + txt + "%"
        where_items.append("(i.name LIKE %s OR i.item_name LIKE %s)")
        params.extend([like_txt, like_txt])
        
    if category and category not in ["All", "All Categories", "null", "undefined"]:
        where_items.append("i.item_group = %s")
        params.append(category)

    # If company is provided, we join warehouse for company-specific stock
    if company and company not in ["All Branches", "All", "null", "undefined", "None"]:
        if only_stock:
            sql = f'''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE(SUM(b.actual_qty), 0) as stock
                FROM "tabItem" i
                JOIN "tabBin" b ON b.item_code = i.name AND b.actual_qty > 0
                JOIN "tabWarehouse" w ON w.name = b.warehouse AND w.company = %s
                WHERE {' AND '.join(where_items)}
                GROUP BY i.name, i.item_name, i.standard_rate, i.stock_uom, i.item_group, i.image
                HAVING SUM(b.actual_qty) > 0
                ORDER BY stock DESC, i.item_name ASC
                LIMIT {limit}
            '''
            exec_params = [company] + params
        else:
            sql = f'''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE((
                           SELECT SUM(b.actual_qty) 
                           FROM "tabBin" b
                           JOIN "tabWarehouse" w ON w.name = b.warehouse
                           WHERE b.item_code = i.name AND w.company = %s AND b.actual_qty > 0
                       ), 0) as stock
                FROM "tabItem" i
                WHERE {' AND '.join(where_items)}
                ORDER BY i.item_name ASC
                LIMIT {limit}
            '''
            exec_params = [company] + params
    else:
        # All companies / global stock
        if only_stock:
            sql = f'''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE(SUM(b.actual_qty), 0) as stock
                FROM "tabItem" i
                JOIN "tabBin" b ON b.item_code = i.name AND b.actual_qty > 0
                WHERE {' AND '.join(where_items)}
                GROUP BY i.name, i.item_name, i.standard_rate, i.stock_uom, i.item_group, i.image
                HAVING SUM(b.actual_qty) > 0
                ORDER BY stock DESC, i.item_name ASC
                LIMIT {limit}
            '''
            exec_params = list(params)
        else:
            sql = f'''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE((
                           SELECT SUM(b.actual_qty) 
                           FROM "tabBin" b 
                           WHERE b.item_code = i.name AND b.actual_qty > 0
                       ), 0) as stock
                FROM "tabItem" i
                WHERE {' AND '.join(where_items)}
                ORDER BY i.item_name ASC
                LIMIT {limit}
            '''
            exec_params = list(params)
            
    rows = frappe.db.sql(sql, tuple(exec_params), as_dict=True)
    frappe.response["message"] = rows

get_pos_items()
"""

url_items = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Items%20API'
payload_items = json.dumps({'script': get_items_script}).encode()
req = urllib.request.Request(url_items, data=payload_items, headers=H, method='PUT')
opener.open(req)
print('Updated VM POS Items API successfully.')

# 2. Update VM POS Stock
stock_script = """
def vm_pos_stock():
    fd = frappe.form_dict or {}
    raw = fd.get("codes") or ""
    company = (fd.get("company") or "").strip()
    codes = [c.strip() for c in str(raw).split(",") if c.strip()]
    result = {}
    if not codes:
        frappe.response["message"] = result
        return
        
    ph = ", ".join(["%s"] * len(codes))
    
    if company and company not in ["All Branches", "All", "null", "undefined", "None"]:
        # Company-filtered bins
        bins = frappe.db.sql(f'''
            SELECT b.item_code, b.warehouse, b.actual_qty, w.company
            FROM "tabBin" b
            JOIN "tabWarehouse" w ON w.name = b.warehouse
            WHERE b.item_code IN ({ph}) AND b.actual_qty <> 0
            ORDER BY (w.company = %s) DESC, b.actual_qty DESC
        ''', codes + [company], as_dict=True)
    else:
        bins = frappe.db.sql(f'''
            SELECT b.item_code, b.warehouse, b.actual_qty, '' as company
            FROM "tabBin" b
            WHERE b.item_code IN ({ph}) AND b.actual_qty <> 0
            ORDER BY b.actual_qty DESC
        ''', codes, as_dict=True)
        
    locs = frappe.db.sql(f'''
        SELECT item_code, warehouse, bin_location 
        FROM "tabStock Ledger Entry" 
        WHERE item_code IN ({ph}) AND bin_location IS NOT NULL AND bin_location <> ''
        ORDER BY creation DESC
    ''', codes, as_dict=True)
    
    binmap = {}
    for l in locs:
        key = l['item_code'] + '||' + l['warehouse']
        if key not in binmap:
            binmap[key] = l['bin_location']
            
    for b in bins:
        ic = b['item_code']
        if ic not in result:
            result[ic] = {'stock': 0, 'company_stock': 0, 'bins': []}
        qty = float(b['actual_qty'] or 0)
        
        # If company filter matches, count towards company_stock
        if not company or company in ["All Branches", "All", "null", "undefined", "None"] or b.get('company') == company:
            result[ic]['company_stock'] = result[ic]['company_stock'] + qty
            
        result[ic]['stock'] = result[ic]['stock'] + qty
        loc = binmap.get(ic + '||' + b['warehouse'], '')
        result[ic]['bins'].append({'warehouse': b['warehouse'], 'qty': qty, 'bin': loc, 'company': b.get('company', '')})
        
    for ic in result:
        # Use company_stock as main stock display when company is selected
        if company and company not in ["All Branches", "All", "null", "undefined", "None"]:
            result[ic]['stock'] = round(result[ic]['company_stock'], 2)
        else:
            result[ic]['stock'] = round(result[ic]['stock'], 2)
            
    frappe.response['message'] = result

vm_pos_stock()
"""

url_stock = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Stock'
payload_stock = json.dumps({'script': stock_script}).encode()
req = urllib.request.Request(url_stock, data=payload_stock, headers=H, method='PUT')
opener.open(req)
print('Updated VM POS Stock successfully.')

# 3. Create or update VM POS Get Invoice Receipt Server Script
receipt_script = """
def vm_pos_get_invoice_receipt():
    inv_name = (frappe.form_dict.get('invoice_name') or frappe.form_dict.get('name') or '').strip()
    if not inv_name or not frappe.db.exists('POS Invoice', inv_name):
        frappe.response['message'] = {'error': f'POS Invoice {inv_name} not found'}
        return
        
    doc = frappe.get_doc('POS Invoice', inv_name)
    
    # Items
    items = []
    for it in doc.items:
        items.append({
            'item_code': it.item_code,
            'item_name': it.item_name or it.item_code,
            'qty': float(it.qty or 0),
            'rate': float(it.rate or 0),
            'amount': float(it.amount or (it.qty * it.rate)),
            'uom': it.uom or '',
            'discount_amount': float(it.discount_amount or 0)
        })
        
    # Payment Method
    payment_method = 'Cash'
    if doc.payments:
        payment_method = doc.payments[0].mode_of_payment or 'Cash'
        
    # Cashier name
    cashier_name = doc.owner
    if frappe.db.exists('User', doc.owner):
        u_full = frappe.db.get_value('User', doc.owner, 'full_name')
        if u_full: cashier_name = u_full
        
    # Customer name
    cust_name = doc.customer_name or doc.customer
    
    # Vehicle plate
    plate_no = doc.get('custom_plate_no') or ''
    veh_code = doc.get('custom_customer_vehicle') or ''
    
    res = {
        'invoice_no': doc.name,
        'company': doc.company,
        'cashier': cashier_name,
        'cashier_user': doc.owner,
        'posting_date': str(doc.posting_date or ''),
        'posting_time': str(doc.posting_time or ''),
        'customer': doc.customer,
        'customer_name': cust_name,
        'vehicle': veh_code,
        'plate_no': plate_no,
        'total_amount': float(doc.grand_total or doc.total or 0),
        'paid_amount': float(doc.paid_amount or 0),
        'change_amount': float(doc.change_amount or 0),
        'discount_amount': float(doc.discount_amount or 0),
        'payment_method': payment_method,
        'remarks': doc.remarks or '',
        'items': items
    }
    frappe.response['message'] = res

vm_pos_get_invoice_receipt()
"""

url_receipt = 'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20POS%20Get%20Invoice%20Receipt'
payload_receipt = json.dumps({
    'doctype': 'Server Script',
    'name': 'VM POS Get Invoice Receipt',
    'script_type': 'API',
    'api_method': 'vm_pos_get_invoice_receipt',
    'allow_guest': 0,
    'script': receipt_script
}).encode()

try:
    req = urllib.request.Request(url_receipt, data=payload_receipt, headers=H, method='PUT')
    opener.open(req)
except urllib.error.HTTPError as e:
    if e.code == 404:
        url_post = 'http://38.247.138.224:10017/api/resource/Server%20Script'
        req = urllib.request.Request(url_post, data=payload_receipt, headers=H, method='POST')
        opener.open(req)
    else:
        raise
print('Created/Updated VM POS Get Invoice Receipt Server Script.')
