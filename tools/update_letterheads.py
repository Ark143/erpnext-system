import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

lh_html = """<div style="text-align: center; padding: 12px 0; background-color: #000; border-radius: 6px; margin-bottom: 20px;">
    <img src="/files/automan_logo.png" alt="AUTOMAN CAR CARE CENTER" style="max-height: 65px; display: inline-block;">
</div>"""

# 1. Update ULTRA MRF letterhead
res1 = s.put(f"{VPS_BASE}/api/resource/Letter Head/ULTRA%20MRF", json={
    "content": lh_html,
    "is_default": 1
})
print("ULTRA MRF letterhead:", res1.status_code)

# 2. Update Company Letterhead
res2 = s.put(f"{VPS_BASE}/api/resource/Letter Head/Company%20Letterhead", json={
    "content": lh_html
})
print("Company Letterhead:", res2.status_code)

# 3. Create/update AUTOMAN letterhead
res_auto = s.get(f"{VPS_BASE}/api/resource/Letter Head/AUTOMAN")
if res_auto.status_code == 200:
    res3 = s.put(f"{VPS_BASE}/api/resource/Letter Head/AUTOMAN", json={"content": lh_html, "disabled": 0})
    print("Updated AUTOMAN letterhead:", res3.status_code)
else:
    res3 = s.post(f"{VPS_BASE}/api/resource/Letter Head", json={
        "letter_head_name": "AUTOMAN",
        "content": lh_html,
        "is_default": 0,
        "disabled": 0
    })
    print("Created AUTOMAN letterhead:", res3.status_code)

# 4. Create/update Automan Car Care Center letterhead
res_acc = s.get(f"{VPS_BASE}/api/resource/Letter Head/Automan%20Car%20Care%20Center")
if res_acc.status_code == 200:
    res4 = s.put(f"{VPS_BASE}/api/resource/Letter Head/Automan%20Car%20Care%20Center", json={"content": lh_html, "disabled": 0})
    print("Updated Automan Car Care Center letterhead:", res4.status_code)
else:
    res4 = s.post(f"{VPS_BASE}/api/resource/Letter Head", json={
        "letter_head_name": "Automan Car Care Center",
        "content": lh_html,
        "is_default": 0,
        "disabled": 0
    })
    print("Created Automan Car Care Center letterhead:", res4.status_code)

# 5. Update My Company logo too
s.put(f"{VPS_BASE}/api/resource/Company/My%20Company", json={"company_logo": "/files/automan_logo.png"})

print("All Letter Heads and Logos updated successfully!")
