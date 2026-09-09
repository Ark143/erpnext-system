import requests
import json
import urllib.parse
import random

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
login_res = s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
print("Logged into VPS:", login_res.status_code)

COMPANY = "Automan Car Care Center"

# 1. Define standard service packages
SERVICES = [
    {"code": "SRV-PMS-SEDAN", "name": "Periodic Maintenance Service (PMS) - Sedan", "rate": 1800.0, "grp": "Services"},
    {"code": "SRV-PMS-SUV", "name": "Periodic Maintenance Service (PMS) - SUV/4x4", "rate": 2600.0, "grp": "Services"},
    {"code": "SRV-ALIGN-4W", "name": "Computerized 4-Wheel Alignment", "rate": 1400.0, "grp": "Services"},
    {"code": "SRV-BAL-ROT", "name": "High-Speed Wheel Balancing & Tire Rotation", "rate": 950.0, "grp": "Services"},
    {"code": "SRV-BRK-CLN", "name": "Brake System Inspection, Cleaning & Caliper Bleed", "rate": 1650.0, "grp": "Services"},
    {"code": "SRV-TUNE-UP", "name": "Full Engine Tune-up & Electronic Diagnostics", "rate": 2200.0, "grp": "Services"},
    {"code": "SRV-AC-CLEAN", "name": "Aircon Evaporator Cleaning & Freon Top-up", "rate": 2800.0, "grp": "Services"},
    {"code": "SRV-INJ-CLEAN", "name": "Fuel Injector Ultrasonic Cleaning & Flow Test", "rate": 1950.0, "grp": "Services"},
    {"code": "SRV-DETAIL-PRO", "name": "Automan Pro Interior & Exterior Auto Detailing", "rate": 4500.0, "grp": "Services"},
    {"code": "SRV-SUSP-REPAIR", "name": "Underchassis Suspension Bushing & Linkage Repair", "rate": 3200.0, "grp": "Services"},
    {"code": "SRV-ATF-FLUSH", "name": "Automatic Transmission Fluid (ATF) Dialysis Flush", "rate": 2400.0, "grp": "Services"},
    {"code": "SRV-ELEC-CHECK", "name": "Battery Load Test, Alternator & Starter Check", "rate": 650.0, "grp": "Services"}
]

# Ensure service items exist
for srv in SERVICES:
    res_get = s.get(f"{VPS_BASE}/api/resource/Item/{urllib.parse.quote(srv['code'])}")
    if res_get.status_code != 200:
        res_create = s.post(f"{VPS_BASE}/api/resource/Item", json={
            "item_code": srv["code"],
            "item_name": srv["name"],
            "item_group": "Services",
            "is_stock_item": 0,
            "include_item_in_manufacturing": 0,
            "stock_uom": "Unit",
            "standard_rate": srv["rate"]
        })
        print(f"Created Service Item: {srv['code']} ({res_create.status_code})")
    else:
        print(f"Service Item exists: {srv['code']}")

# 2. Fetch customers
cust_res = s.get(f"{VPS_BASE}/api/resource/Customer?limit_page_length=100&fields=[\"name\",\"customer_name\"]")
customers = [c["name"] for c in cust_res.json().get("data", []) if c.get("name")]
if not customers:
    customers = ["Juan Dela Cruz", "Maria Santos", "Antonio Luna", "Pedro Penduko"]

# Service scenarios for 30 transactions
random.seed(42) # Deterministic for reproducibility
transactions_summary = []
total_revenue = 0.0

print("\n=== STARTING 30 SERVICE TRANSACTIONS FOR AUTOMAN ===")

for i in range(1, 31):
    cust = random.choice(customers)
    # Pick 1 to 3 services
    num_items = random.choice([1, 1, 2, 2, 3])
    chosen_services = random.sample(SERVICES, num_items)
    
    items_payload = []
    inv_total = 0.0
    for srv in chosen_services:
        qty = 1
        rate = srv["rate"]
        amt = qty * rate
        inv_total += amt
        items_payload.append({
            "item_code": srv["code"],
            "item_name": srv["name"],
            "description": f"Automan Service: {srv['name']}",
            "qty": qty,
            "rate": rate,
            "amount": amt,
            "income_account": "Sales - AUTOMAN",
            "cost_center": "Main - AUTOMAN"
        })
    
    # 1. Create Service Sales Invoice (update_stock = 0)
    sinv_doc = {
        "company": COMPANY,
        "customer": cust,
        "posting_date": "2026-09-08",
        "set_posting_time": 1,
        "due_date": "2026-09-08",
        "update_stock": 0,
        "debit_to": "Debtors - AUTOMAN",
        "items": items_payload,
        "remarks": f"Service Job #{i:02d} - Automan Car Care Center ({', '.join(s['name'] for s in chosen_services)})"
    }
    
    res_inv = s.post(f"{VPS_BASE}/api/resource/Sales Invoice", json=sinv_doc).json()
    inv_name = res_inv.get("data", {}).get("name")
    
    if not inv_name:
        print(f"Transaction #{i:02d} Error creating Invoice:", res_inv)
        continue
        
    # Submit Invoice
    res_sub_inv = s.put(f"{VPS_BASE}/api/resource/Sales Invoice/{inv_name}", json={"docstatus": 1}).json()
    
    # 2. Create Payment Entry
    pay_doc = {
        "payment_type": "Receive",
        "posting_date": "2026-09-08",
        "set_posting_time": 1,
        "company": COMPANY,
        "party_type": "Customer",
        "party": cust,
        "paid_from": "Debtors - AUTOMAN",
        "paid_to": "Cash - AUTOMAN",
        "paid_amount": inv_total,
        "received_amount": inv_total,
        "target_exchange_rate": 1.0,
        "remarks": f"Payment received for Service Job #{i:02d} ({inv_name})",
        "references": [
            {
                "reference_doctype": "Sales Invoice",
                "reference_name": inv_name,
                "total_amount": inv_total,
                "outstanding_amount": inv_total,
                "allocated_amount": inv_total
            }
        ]
    }
    
    res_pay = s.post(f"{VPS_BASE}/api/resource/Payment Entry", json=pay_doc).json()
    pay_name = res_pay.get("data", {}).get("name")
    
    if pay_name:
        s.put(f"{VPS_BASE}/api/resource/Payment Entry/{pay_name}", json={"docstatus": 1})
        
    total_revenue += inv_total
    
    item_desc = ", ".join([f"{it['item_name']} (PHP {it['amount']:,.2f})" for it in items_payload])
    print(f"[{i:02d}/30] Invoice: {inv_name} | Pay: {pay_name} | Customer: {cust[:20]:20s} | Amount: PHP {inv_total:8.2f} | Services: {item_desc}")
    
    transactions_summary.append({
        "tx_no": i,
        "invoice": inv_name,
        "payment": pay_name,
        "customer": cust,
        "amount": inv_total,
        "services": [s["name"] for s in chosen_services]
    })

print(f"\n==========================================")
print(f"COMPLETED 30 SERVICE TRANSACTIONS!")
print(f"Total Service Revenue Generated: PHP {total_revenue:,.2f}")
print(f"==========================================")

# Save transactions summary locally for audit
with open("tools/automan_30_service_transactions.json", "w") as f:
    json.dump(transactions_summary, f, indent=2)
print("Saved summary to tools/automan_30_service_transactions.json")
