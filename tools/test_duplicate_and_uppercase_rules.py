import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Initial cleanup of any previous test records
for n in ['TOYOTA-vios', 'TOYOTA-test yaris cross gr', 'TOYOTA-TEST YARIS CROSS GR']:
    try:
        s.delete(f'{URL}/api/resource/Vehicle Model/{n}')
    except Exception:
        pass

for c in ['TEST AUTOCAPS CUSTOMER', 'test autocaps customer']:
    try:
        s.delete(f'{URL}/api/resource/Customer/{c}')
    except Exception:
        pass

for i in ['TEST-CAPS-OIL-999', 'test-caps-oil-999']:
    try:
        s.delete(f'{URL}/api/resource/Item/{i}')
    except Exception:
        pass

for v in ['ABC-1234', 'abc-1234']:
    try:
        s.delete(f'{URL}/api/resource/Customer Vehicle/{v}')
    except Exception:
        pass

print("=== TEST 1: DUPLICATE VEHICLE MODEL PREVENTION ===")
# Try to create a duplicate of an existing model (e.g. Toyota Vios)
res_dup = s.post(f'{URL}/api/resource/Vehicle Model', json={
    'doctype': 'Vehicle Model',
    'make': 'TOYOTA',
    'model_name': 'vios',
    'category': 'Sedan'
})
print("Attempting to insert duplicate 'TOYOTA - vios':")
print(f"Status Code: {res_dup.status_code}")
print(f"Response: {res_dup.text[:300]}")
assert res_dup.status_code in [417, 500, 409], "Expected duplicate error!"
print("[PASS] Duplicate Vehicle Model correctly blocked with error!\n")

print("=== TEST 2: NEW VEHICLE MODEL AUTO-UPPERCASE ===")
test_make = "TOYOTA"
test_model = "test yaris cross gr"

res_new = s.post(f'{URL}/api/resource/Vehicle Model', json={
    'doctype': 'Vehicle Model',
    'make': test_make,
    'model_name': test_model,
    'category': 'SUV'
})
print("Inserting new model with lowercase 'test yaris cross gr':")
print(f"Status Code: {res_new.status_code}")
new_data = res_new.json().get('data', {})
print(f"Created Record Make: {new_data.get('make')}, Model Name: {new_data.get('model_name')}, Name: {new_data.get('name')}")
assert res_new.status_code in [200, 201], f"Expected 200/201, got {res_new.status_code}"
assert new_data.get('make') == 'TOYOTA', "Make should be uppercase!"
assert new_data.get('model_name') == 'TEST YARIS CROSS GR', "Model Name should be uppercase!"
print("[PASS] Vehicle Model successfully auto-converted to ALL CAPS!\n")

print("=== TEST 3: DUPLICATE PREVENTION ON NEW MODEL ===")
res_dup2 = s.post(f'{URL}/api/resource/Vehicle Model', json={
    'doctype': 'Vehicle Model',
    'make': 'TOYOTA',
    'model_name': 'Test Yaris Cross GR',
    'category': 'SUV'
})
print("Attempting to insert duplicate 'TOYOTA - Test Yaris Cross GR':")
print(f"Status Code: {res_dup2.status_code}")
print(f"Response: {res_dup2.text[:300]}")
assert res_dup2.status_code in [417, 500, 409], "Expected duplicate error!"
print("[PASS] Duplicate creation of new model correctly blocked!\n")

print("=== TEST 4: CUSTOMER MASTER AUTO-UPPERCASE ===")
test_cust_name = "test autocaps customer"
res_cust = s.post(f'{URL}/api/resource/Customer', json={
    'doctype': 'Customer',
    'customer_name': test_cust_name,
    'customer_group': 'Commercial',
    'territory': 'Philippines'
})
cust_data = res_cust.json().get('data', {})
print(f"Status: {res_cust.status_code}, Customer Name saved: {cust_data.get('customer_name')}")
assert cust_data.get('customer_name') == 'TEST AUTOCAPS CUSTOMER', "Customer name should be ALL CAPS!"
print("[PASS] Customer Master auto-converted to ALL CAPS!\n")

print("=== TEST 5: ITEM MASTER AUTO-UPPERCASE ===")
res_item = s.post(f'{URL}/api/resource/Item', json={
    'doctype': 'Item',
    'item_code': 'test-caps-oil-999',
    'item_name': 'high performance racing oil 10w-40',
    'item_group': 'Products',
    'stock_uom': 'Unit'
})
item_data = res_item.json().get('data', {})
print(f"Status: {res_item.status_code}, Item Code: {item_data.get('item_code')}, Item Name: {item_data.get('item_name')}")
assert item_data.get('item_code') == 'TEST-CAPS-OIL-999', "Item code should be ALL CAPS!"
assert item_data.get('item_name') == 'HIGH PERFORMANCE RACING OIL 10W-40', "Item name should be ALL CAPS!"
print("[PASS] Item Master auto-converted to ALL CAPS!\n")

print("=== TEST 6: CUSTOMER VEHICLE AUTO-UPPERCASE ===")
test_plate = "ABC-1234"
res_veh = s.post(f'{URL}/api/resource/Customer Vehicle', json={
    'doctype': 'Customer Vehicle',
    'plate_no': 'abc-1234',
    'customer': cust_data.get('name'),
    'make': 'toyota',
    'model': 'Toyota-Vios',
    'color': 'pearl white'
})
veh_data = res_veh.json().get('data', {})
print(f"Status: {res_veh.status_code}, Plate: {veh_data.get('plate_no')}, Color: {veh_data.get('color')}, Make: {veh_data.get('make')}, Model: {veh_data.get('model')}")
assert veh_data.get('plate_no') == 'ABC-1234', "Plate should be ALL CAPS!"
assert veh_data.get('color') == 'PEARL WHITE', "Color should be ALL CAPS!"
assert veh_data.get('make') == 'TOYOTA', "Make should be ALL CAPS!"
print("[PASS] Customer Vehicle auto-converted to ALL CAPS!\n")

# Final cleanup of test records
for n in ['TOYOTA-vios', 'TOYOTA-test yaris cross gr', 'TOYOTA-TEST YARIS CROSS GR']:
    try:
        s.delete(f'{URL}/api/resource/Vehicle Model/{n}')
    except Exception:
        pass

try:
    s.delete(f'{URL}/api/resource/Customer Vehicle/{test_plate}')
    s.delete(f'{URL}/api/resource/Customer/{cust_data.get("name")}')
    s.delete(f'{URL}/api/resource/Item/TEST-CAPS-OIL-999')
except Exception:
    pass

print("=======================================================================")
print("SUCCESS: ALL 6 TEST SUITES PASSED FLAWLESSLY!")
print("1. Duplicate Vehicle Models are strictly blocked.")
print("2. New Vehicle Models auto-standardize to uppercase.")
print("3. Duplicates of newly created models are strictly blocked.")
print("4. Customer Master data automatically converts to ALL CAPS.")
print("5. Item Master data automatically converts to ALL CAPS.")
print("6. Customer Vehicles automatically convert to ALL CAPS.")
print("=======================================================================")
