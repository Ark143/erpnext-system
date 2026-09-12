import urllib.request
import urllib.parse
import json
import http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H))

script_clean_merge = '''
# 1. Deduplicate and Merge Vehicle Makes using Frappe ORM
all_makes = frappe.get_all("Vehicle Make", fields=["name", "make_name"], limit_page_length=500)
canonical_makes = {}
merged_makes = []

for m in all_makes:
    raw_name = m["name"]
    clean = (m.get("make_name") or raw_name or "").strip().upper()
    if not clean:
        continue
    if raw_name == clean:
        canonical_makes[clean] = clean

for m in all_makes:
    raw_name = m["name"]
    clean = (m.get("make_name") or raw_name or "").strip().upper()
    if not clean or raw_name == clean:
        continue
    if clean in canonical_makes:
        try:
            frappe.rename_doc("Vehicle Make", raw_name, clean, merge=True, ignore_permissions=True)
            merged_makes.append({"from": raw_name, "to": clean, "action": "merged"})
        except Exception as ex:
            merged_makes.append({"from": raw_name, "to": clean, "error": str(ex)})
    else:
        try:
            frappe.rename_doc("Vehicle Make", raw_name, clean, ignore_permissions=True)
            canonical_makes[clean] = clean
            merged_makes.append({"from": raw_name, "to": clean, "action": "renamed"})
        except Exception as ex:
            merged_makes.append({"from": raw_name, "to": clean, "error": str(ex)})

# 2. Deduplicate and Merge Vehicle Models
all_models = frappe.get_all("Vehicle Model", fields=["name", "make", "model_name"], limit_page_length=2000)
seen_models = {}
merged_models = []

for row in all_models:
    raw_name = row["name"]
    clean_make = (row.get("make") or "").strip().upper()
    clean_model = (row.get("model_name") or "").strip().upper()
    if not clean_make or not clean_model:
        continue
        
    canonical_name = f"{clean_make}-{clean_model}"
    key = (clean_make, clean_model)
    
    if key in seen_models:
        target_name = seen_models[key]
        try:
            frappe.rename_doc("Vehicle Model", raw_name, target_name, merge=True, ignore_permissions=True)
            merged_models.append({"from": raw_name, "to": target_name, "action": "merged"})
        except Exception:
            try:
                frappe.delete_doc("Vehicle Model", raw_name, ignore_permissions=True, force=1)
                merged_models.append({"from": raw_name, "to": target_name, "action": "deleted"})
            except Exception as ex:
                merged_models.append({"from": raw_name, "to": target_name, "error": str(ex)})
    else:
        seen_models[key] = canonical_name
        if raw_name != canonical_name:
            try:
                frappe.rename_doc("Vehicle Model", raw_name, canonical_name, ignore_permissions=True)
                merged_models.append({"from": raw_name, "to": canonical_name, "action": "renamed"})
            except Exception:
                frappe.db.set_value("Vehicle Model", raw_name, "make", clean_make, update_modified=False)
                frappe.db.set_value("Vehicle Model", raw_name, "model_name", clean_model, update_modified=False)
        else:
            frappe.db.set_value("Vehicle Model", raw_name, "make", clean_make, update_modified=False)
            frappe.db.set_value("Vehicle Model", raw_name, "model_name", clean_model, update_modified=False)

frappe.db.commit()

# Return summary
frappe.response["message"] = {
    "status": "success",
    "total_unique_makes": len(canonical_makes),
    "makes_merged_count": len(merged_makes),
    "total_unique_models": len(seen_models),
    "models_merged_count": len(merged_models),
    "merged_makes_sample": merged_makes[:10],
    "merged_models_sample": merged_models[:10]
}
'''

server_script_payload = {
    'doctype': 'Server Script',
    'name': 'VM Clean Merge Makes Models',
    'script_type': 'API',
    'api_method': 'vm_clean_merge_makes_models',
    'allow_guest': 1,
    'disabled': 0,
    'script': script_clean_merge
}

req = urllib.request.Request(
    f'{URL}/api/resource/Server%20Script/VM%20Clean%20Merge%20Makes%20Models',
    data=json.dumps(server_script_payload).encode(),
    headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
    method='PUT'
)
try:
    op.open(req)
except Exception:
    req = urllib.request.Request(
        f'{URL}/api/resource/Server%20Script',
        data=json.dumps(server_script_payload).encode(),
        headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        method='POST'
    )
    op.open(req)

r_call = op.open(urllib.request.Request(f'{URL}/api/method/vm_clean_merge_makes_models', data=b'', headers=H))
print("Clean merge result:\n", json.dumps(json.loads(r_call.read().decode()), indent=2))
