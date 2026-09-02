import urllib.request, urllib.parse, json, http.cookiejar, sys

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def api_get(url):
    req = urllib.request.Request(url, headers=H)
    return json.loads(op.open(req).read().decode())

def api_post(doctype, doc):
    doc_payload = dict(doc)
    doc_payload['doctype'] = doctype
    req = urllib.request.Request(
        f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}',
        data=urllib.parse.urlencode({'data': json.dumps(doc_payload)}).encode(),
        headers=H
    )
    return json.loads(op.open(req).read().decode()).get('data', {})

def api_put(doctype, name, doc):
    req = urllib.request.Request(
        f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}',
        data=urllib.parse.urlencode({'data': json.dumps(doc)}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    return json.loads(op.open(req).read().decode()).get('data', {})

def api_submit(doctype, name):
    return api_put(doctype, name, {'docstatus': 1})

company = "ULTRA MRF"

items_data = [
    {
        "item_code": "FA-ALN-001",
        "item_name": "3D HD Wheel Alignment System with Target Cameras",
        "asset_category": "Heavy Workshop Machinery",
        "cost": 485000.0,
        "salvage": 48500.0,
        "dep_months": 36,
        "purchase_date": "2025-01-15",
        "dep_start_date": "2025-02-28",
        "location": "Ultra MRF Dau Main"
    },
    {
        "item_code": "FA-LIFT-002",
        "item_name": "Heavy-Duty 4-Post Hydraulic Vehicle Lift (5 Ton)",
        "asset_category": "Heavy Workshop Machinery",
        "cost": 340000.0,
        "salvage": 34000.0,
        "dep_months": 36,
        "purchase_date": "2025-01-20",
        "dep_start_date": "2025-02-28",
        "location": "Ultra MRF Dau Main"
    },
    {
        "item_code": "FA-BAL-003",
        "item_name": "Computerized Dynamic Wheel Balancing Machine",
        "asset_category": "Heavy Workshop Machinery",
        "cost": 215000.0,
        "salvage": 21500.0,
        "dep_months": 24,
        "purchase_date": "2025-02-01",
        "dep_start_date": "2025-02-28",
        "location": "Ultra MRF Dau Main"
    },
    {
        "item_code": "FA-DIAG-004",
        "item_name": "Autel MaxiSys Ultra Professional Diagnostic Scanner",
        "asset_category": "Diagnostic & Electronic Equipment",
        "cost": 175000.0,
        "salvage": 17500.0,
        "dep_months": 24,
        "purchase_date": "2025-02-10",
        "dep_start_date": "2025-02-28",
        "location": "Ultra MRF San Fernando"
    },
    {
        "item_code": "FA-AC-005",
        "item_name": "Automatic R134a/R1234yf A/C Recovery & Recharge Station",
        "asset_category": "Diagnostic & Electronic Equipment",
        "cost": 260000.0,
        "salvage": 26000.0,
        "dep_months": 24,
        "purchase_date": "2025-03-01",
        "dep_start_date": "2025-03-31",
        "location": "Ultra MRF Dau Main"
    },
    {
        "item_code": "FA-COMP-006",
        "item_name": "Industrial Rotary Screw Air Compressor (15 HP with Dryer)",
        "asset_category": "Facility & Power Equipment",
        "cost": 310000.0,
        "salvage": 31000.0,
        "dep_months": 48,
        "purchase_date": "2025-01-10",
        "dep_start_date": "2025-01-31",
        "location": "San Fernando Warehouse"
    },
    {
        "item_code": "FA-POS-007",
        "item_name": "Dual-Screen Touch POS Terminal with Thermal Printer & Scanner",
        "asset_category": "Office & POS Computing",
        "cost": 68000.0,
        "salvage": 6800.0,
        "dep_months": 24,
        "purchase_date": "2025-01-05",
        "dep_start_date": "2025-01-31",
        "location": "Ultra MRF Dau Main"
    },
    {
        "item_code": "FA-FORK-008",
        "item_name": "Electric Hydraulic Forklift / Pallet Truck (2.5 Ton)",
        "asset_category": "Facility & Power Equipment",
        "cost": 420000.0,
        "salvage": 42000.0,
        "dep_months": 48,
        "purchase_date": "2025-02-15",
        "dep_start_date": "2025-02-28",
        "location": "San Fernando Warehouse"
    },
    {
        "item_code": "FA-WELD-009",
        "item_name": "Digital Inverter MIG/TIG Spot Welding Workstation",
        "asset_category": "Heavy Workshop Machinery",
        "cost": 185000.0,
        "salvage": 18500.0,
        "dep_months": 36,
        "purchase_date": "2025-03-10",
        "dep_start_date": "2025-03-31",
        "location": "Ultra MRF Dau Main"
    },
    {
        "item_code": "FA-GEN-010",
        "item_name": "Heavy Duty Silent Diesel Standby Power Generator (50 kVA)",
        "asset_category": "Facility & Power Equipment",
        "cost": 650000.0,
        "salvage": 65000.0,
        "dep_months": 48,
        "purchase_date": "2025-01-01",
        "dep_start_date": "2025-01-31",
        "location": "Ultra MRF Dau Main"
    }
]

print("\n--- Creating & Submitting 10 Assets ---")
created_assets = []
for item in items_data:
    asset_payload = {
        "asset_name": item["item_name"],
        "item_code": item["item_code"],
        "asset_category": item["asset_category"],
        "company": company,
        "location": item["location"],
        "gross_purchase_amount": item["cost"],
        "net_purchase_amount": item["cost"],
        "purchase_amount": item["cost"],
        "is_existing_asset": 1,
        "purchase_date": item["purchase_date"],
        "available_for_use_date": item["purchase_date"],
        "calculate_depreciation": 1,
        "finance_books": [
            {
                "depreciation_method": "Straight Line",
                "total_number_of_depreciations": item["dep_months"],
                "frequency_of_depreciation": 1,
                "depreciation_start_date": item["dep_start_date"],
                "expected_value_after_useful_life": item["salvage"]
            }
        ]
    }
    try:
        res = api_post("Asset", asset_payload)
        docname = res.get("name")
        print(f"Created draft Asset '{docname}'")
        
        # Submit the Asset to generate depreciation schedule
        sub_res = api_submit("Asset", docname)
        print(f"Submitted Asset '{docname}' -> Status: {sub_res.get('status')}")
        created_assets.append(docname)
    except urllib.error.HTTPError as e:
        err = e.fp.read().decode('utf-8', 'ignore') if e.fp else ""
        print(f"Error creating/submitting asset for {item['item_code']}: {e.code} -> {err[:300]}")
    except Exception as e:
        print(f"Error creating/submitting asset for {item['item_code']}: {e}")

print(f"\nSuccessfully created and submitted {len(created_assets)} assets!")
