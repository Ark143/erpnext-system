import requests
import json
import re

def scrape_autometrik():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })

    # 1. Login
    login_url = "https://app.autometrik.ph/account/login"
    r = session.get(login_url)
    
    # Extract RequestVerificationToken if present
    token_match = re.search(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"', r.text)
    token = token_match.group(1) if token_match else None

    login_data = {
        'Username': 'apacson',
        'Password': 'Cyndi0816!',
        'RememberMe': 'true'
    }
    if token:
        login_data['__RequestVerificationToken'] = token

    r_login = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login Status: {r_login.status_code}, URL: {r_login.url}")

    # 2. Extract Products
    prod_data = {
        "draw": 1,
        "start": 0,
        "length": 5000,
        "search": {"value": "", "regex": False},
        "orders": [],
        "columns": []
    }
    r_prod = session.post("https://app.autometrik.ph/product/getdata", json=prod_data)
    print(f"Product getdata status: {r_prod.status_code}")
    products = []
    if r_prod.status_code == 200:
        prod_json = r_prod.json()
        products = prod_json.get("data", [])
        print(f"Total Products found: {len(products)}")
        with open("C:/Users/josem/erpnext-system/autometrik_products.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2)

    # 3. Extract Customers
    r_cust = session.post("https://app.autometrik.ph/customer/getdata", json=prod_data)
    print(f"Customer getdata status: {r_cust.status_code}")
    customers = []
    if r_cust.status_code == 200:
        cust_json = r_cust.json()
        customers = cust_json.get("data", [])
        print(f"Total Customers found: {len(customers)}")
        with open("C:/Users/josem/erpnext-system/autometrik_customers.json", "w", encoding="utf-8") as f:
            json.dump(customers, f, indent=2)

    # 4. Extract Vehicles
    r_veh = session.post("https://app.autometrik.ph/vehicle/getdata", json=prod_data)
    print(f"Vehicle getdata status: {r_veh.status_code}")
    vehicles = []
    if r_veh.status_code == 200:
        veh_json = r_veh.json()
        vehicles = veh_json.get("data", [])
        print(f"Total Vehicles found: {len(vehicles)}")
        with open("C:/Users/josem/erpnext-system/autometrik_vehicles.json", "w", encoding="utf-8") as f:
            json.dump(vehicles, f, indent=2)

    # Print samples
    if products:
        print("Sample product:", json.dumps(products[0], indent=2))
    if customers:
        print("Sample customer:", json.dumps(customers[0], indent=2))
    if vehicles:
        print("Sample vehicle:", json.dumps(vehicles[0], indent=2))

if __name__ == "__main__":
    scrape_autometrik()
