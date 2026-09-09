import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

print("=== CHECKING WEBSITE & NAVBAR ===")
web = s.get(f"{VPS_BASE}/api/resource/Website Settings/Website Settings").json().get("data", {})
nav = s.get(f"{VPS_BASE}/api/resource/Navbar Settings/Navbar Settings").json().get("data", {})
print("Website App Name:", web.get("app_name"))
print("Website App Logo:", web.get("app_logo"))
print("Website Favicon:", web.get("favicon"))
print("Website Banner:", web.get("banner_image"))
print("Navbar App Logo:", nav.get("app_logo"))

print("\n=== CHECKING COMPANIES ===")
comps = s.get(f"{VPS_BASE}/api/resource/Company?fields=[\"name\",\"abbr\",\"company_logo\"]&limit_page_length=100").json().get("data", [])
for c in comps:
    print(f"- {c.get('name')} | Abbr: {c.get('abbr')} | Logo: {c.get('company_logo')}")

print("\n=== CHECKING LETTERHEADS ===")
lhs = s.get(f"{VPS_BASE}/api/resource/Letter Head?fields=[\"name\",\"is_default\",\"disabled\"]&limit_page_length=100").json().get("data", [])
for lh in lhs:
    print(f"- {lh.get('name')} | Default: {lh.get('is_default')} | Disabled: {lh.get('disabled')}")
