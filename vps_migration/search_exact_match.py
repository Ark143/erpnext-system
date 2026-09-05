import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

test_script = """
# Search Customer
custs = frappe.db.sql("SELECT name, customer_name FROM `tabCustomer` WHERE name LIKE '%GUAJIO%' OR customer_name LIKE '%GUAJIO%' OR name LIKE '%12020%' OR customer_name LIKE '%12020%'", as_dict=1)

# Search Customer Vehicle
vehs = frappe.db.sql("SELECT name, plate_no, customer FROM `tabCustomer Vehicle` WHERE name LIKE '%12020%' OR plate_no LIKE '%12020%' OR customer LIKE '%GUAJIO%'", as_dict=1)

# Search Items
items = frappe.db.sql("SELECT name, item_name FROM `tabItem` WHERE item_name LIKE '%185/70 R14 YOKOHAMA%' OR item_name LIKE '%265/65 R18 MICHELIN%'", as_dict=1)

frappe.response['message'] = {
    'custs': custs,
    'vehs': vehs,
    'items': items
}
"""

script_payload = {
    "name": "Search Exact Match",
    "script_type": "API",
    "api_method": "search_exact_match",
    "disabled": 0,
    "allow_guest": 1,
    "script": test_script
}

s.put(f'{URL}/api/resource/Server%20Script/Search%20Exact%20Match', json=script_payload)
res = s.get(f'{URL}/api/method/search_exact_match')
print("Search Results:", json.dumps(res.json(), indent=2))
