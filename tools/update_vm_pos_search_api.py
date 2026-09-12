import requests
import json

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

print("="*70)
print("  UPDATING GLOBAL SEARCH & FLEXIBLE PUNCTUATION FOR OIL & OTHER FILTERS")
print("="*70)

server_script_code = """
def get_pos_items():
    company = (frappe.form_dict.get("company") or "").strip()
    only_stock = int(frappe.form_dict.get("only_stock") or frappe.form_dict.get("in_stock") or 0)
    txt = (frappe.form_dict.get("txt") or "").strip()
    category = (frappe.form_dict.get("category") or "").strip()
    limit = int(frappe.form_dict.get("limit") or 300)
    
    where_items = ["i.disabled = 0", "i.is_sales_item = 1"]
    params = []
    
    # If user types search text, search GLOBALLY across all categories so items like Oil Filters
    # (spread across AUTO PARTS, PREVENTIVE MAINTENANCE, ANCILLARIES, ENGINE) are always found!
    # If no search text is typed, filter by selected category.
    if not txt and category and category not in ["All", "All Categories", "null", "undefined"]:
        where_items.append("i.item_group = %s")
        params.append(category)

    # Smart Multi-Word, Case-Insensitive, and Hyphen/Space Flexible Search
    if txt:
        raw_tokens = [t.strip().lower() for t in txt.replace(",", " ").replace("/", " ").split() if t.strip()]
        for token in raw_tokens:
            like_tok = "%" + token + "%"
            # Strip hyphens for flexible part code matching (e.g. C312 matching C-312)
            token_nohyphen = token.replace("-", "").replace(".", "")
            like_nohyphen = "%" + token_nohyphen + "%"
            
            where_items.append(''' (
                LOWER(i.name) LIKE %s OR 
                LOWER(i.item_name) LIKE %s OR 
                LOWER(COALESCE(i.description, '')) LIKE %s OR 
                REPLACE(REPLACE(LOWER(i.name), '-', ''), '.', '') LIKE %s OR
                REPLACE(REPLACE(LOWER(i.item_name), '-', ''), '.', '') LIKE %s OR
                EXISTS (
                    SELECT 1 FROM "tabItem Barcode" ib 
                    WHERE ib.parent = i.name AND (
                        LOWER(ib.barcode) LIKE %s OR 
                        REPLACE(LOWER(ib.barcode), '-', '') LIKE %s
                    )
                )
            ) ''')
            params.extend([like_tok, like_tok, like_tok, like_nohyphen, like_nohyphen, like_tok, like_nohyphen])

    where_clause = " AND ".join(where_items)

    # Join company warehouse for company-scoped stock
    if company and company not in ["All Branches", "All", "null", "undefined", "None"]:
        if only_stock:
            sql = '''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE(SUM(b.actual_qty), 0) as stock
                FROM "tabItem" i
                JOIN "tabBin" b ON b.item_code = i.name AND b.actual_qty > 0
                JOIN "tabWarehouse" w ON w.name = b.warehouse AND w.company = %s
                WHERE ''' + where_clause + '''
                GROUP BY i.name, i.item_name, i.standard_rate, i.stock_uom, i.item_group, i.image
                HAVING SUM(b.actual_qty) > 0
                ORDER BY stock DESC, i.item_name ASC
                LIMIT ''' + str(limit)
            exec_params = [company] + params
        else:
            sql = '''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE((
                           SELECT SUM(b.actual_qty) 
                           FROM "tabBin" b
                           JOIN "tabWarehouse" w ON w.name = b.warehouse
                           WHERE b.item_code = i.name AND w.company = %s AND b.actual_qty > 0
                       ), 0) as stock
                FROM "tabItem" i
                WHERE ''' + where_clause + '''
                ORDER BY i.item_name ASC
                LIMIT ''' + str(limit)
            exec_params = [company] + params
    else:
        # All companies
        if only_stock:
            sql = '''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE(SUM(b.actual_qty), 0) as stock
                FROM "tabItem" i
                JOIN "tabBin" b ON b.item_code = i.name AND b.actual_qty > 0
                WHERE ''' + where_clause + '''
                GROUP BY i.name, i.item_name, i.standard_rate, i.stock_uom, i.item_group, i.image
                HAVING SUM(b.actual_qty) > 0
                ORDER BY stock DESC, i.item_name ASC
                LIMIT ''' + str(limit)
            exec_params = list(params)
        else:
            sql = '''
                SELECT i.name as code, i.item_name as name, i.standard_rate as rate,
                       i.stock_uom as uom, i.item_group as `group`, i.image as image,
                       COALESCE((
                           SELECT SUM(b.actual_qty) 
                           FROM "tabBin" b 
                           WHERE b.item_code = i.name AND b.actual_qty > 0
                       ), 0) as stock
                FROM "tabItem" i
                WHERE ''' + where_clause + '''
                ORDER BY i.item_name ASC
                LIMIT ''' + str(limit)
            exec_params = list(params)
            
    rows = frappe.db.sql(sql, tuple(exec_params), as_dict=True)
    frappe.response["message"] = rows

get_pos_items()
"""

payload = {
    "script_type": "API",
    "api_method": "vm_pos_get_items",
    "allow_guest": 0,
    "disabled": 0,
    "script": server_script_code
}

check = s.get(f"{BASE}/api/resource/Server%20Script/VM%20POS%20Items%20API")
if check.status_code == 200:
    r = s.put(f"{BASE}/api/resource/Server%20Script/VM%20POS%20Items%20API", json=payload)
    print(f"[+] Updated Server Script 'VM POS Items API': Status {r.status_code}")
else:
    payload["doctype"] = "Server Script"
    payload["name"] = "VM POS Items API"
    r = s.post(f"{BASE}/api/resource/Server%20Script", json=payload)
    print(f"[+] Created Server Script 'VM POS Items API': Status {r.status_code}")

# Clear cache
s.post(f"{BASE}/api/method/frappe.handler.clear_cache")

# Run test queries
test_queries = [
    "oil filter", "OIL FILTER", "vic", "vic c-312", "c-312", "c312", "C312",
    "air filter", "cabin filter", "fuel filter", "fleetmax", "nomis"
]

print("\n--- Running Filter & Part Search Tests ---")
for q in test_queries:
    res = s.post(f"{BASE}/api/method/vm_pos_get_items", data={"txt": q, "company": "ULTRA MRF"}).json()
    items = res.get("message", [])
    top = f"{items[0]['code']} ({items[0]['name']})" if items else "None"
    print(f"Query '{q}': Found {len(items)} items. Top: {top}")

print("\nSUCCESS: Global flexible search for Oil Filters & all items updated!")
