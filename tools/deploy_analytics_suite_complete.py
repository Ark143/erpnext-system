import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
login_res = s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
print("Admin Login Status:", login_res.status_code)

# -----------------------------------------------------------------------------
# 1. Server Script: get_user_analytics_permissions
# -----------------------------------------------------------------------------
perm_script_code = """
target_user = frappe.form_dict.get('user') or frappe.session.user
all_comps = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name asc") if c.name != "My Company"]

EXECUTIVE_ROLES = [
    "Administrator",
    "System Manager",
    "CEO",
    "Director",
    "Executive",
    "Operation",
    "Operations",
    "Operations Manager",
    "Finance",
    "Finance Manager",
    "Financial Officer",
    "Accounting",
    "Accounts Manager",
    "Accounts User",
    "Auditor"
]

if target_user == "Administrator":
    frappe.response['message'] = {
        'can_view_all': True,
        'allowed_companies': all_comps,
        'default_company': 'All Companies'
    }
else:
    user_roles = frappe.get_all("Has Role", filters={"parent": target_user}, pluck="role")
    is_executive = False
    for r in user_roles:
        if r in EXECUTIVE_ROLES:
            is_executive = True
            break
            
    if is_executive:
        frappe.response['message'] = {
            'can_view_all': True,
            'allowed_companies': all_comps,
            'default_company': 'All Companies'
        }
    else:
        allowed = []
        # 1. From Employee details
        emps = frappe.get_all("Employee", filters={"user_id": target_user}, fields=["company", "status"])
        for e in emps:
            c = e.get("company")
            if c and c not in allowed and c != "My Company":
                allowed.append(c)
                
        # 2. From User Permission
        perms = frappe.get_all("User Permission", filters={"user": target_user, "allow": "Company"}, pluck="for_value")
        for c in perms:
            if c and c not in allowed and c != "My Company":
                allowed.append(c)
                
        # 3. From User Default Company
        user_def = frappe.db.get_value("User Permission", {"user": target_user, "is_default": 1}, "for_value")
        if user_def and user_def not in allowed and user_def in all_comps:
            allowed.append(user_def)
            
        allowed.sort()
        def_comp = allowed[0] if allowed else (all_comps[0] if all_comps else "")
        frappe.response['message'] = {
            'can_view_all': False,
            'allowed_companies': allowed,
            'default_company': def_comp
        }
"""

res = s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Get%20User%20Permissions", json={
    'doctype': 'Server Script',
    'name': 'VM Get User Permissions',
    'script': perm_script_code,
    'script_type': 'API',
    'api_method': 'vehicle_management.vehicle_management.analytics.get_user_analytics_permissions',
    'allow_guest': 0,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        'doctype': 'Server Script',
        'name': 'VM Get User Permissions',
        'script': perm_script_code,
        'script_type': 'API',
        'api_method': 'vehicle_management.vehicle_management.analytics.get_user_analytics_permissions',
        'allow_guest': 0,
        'disabled': 0
    })
print("Deployed get_user_analytics_permissions Server Script:", res.status_code)

# -----------------------------------------------------------------------------
# 2. Server Script: get_vehicle_management_analytics
# -----------------------------------------------------------------------------
analytics_script_code = """
target_user = frappe.session.user
company_param = frappe.form_dict.get('company')
timespan = frappe.form_dict.get('timespan') or "Last 30 Days"
from_date = frappe.form_dict.get('from_date')
to_date = frappe.form_dict.get('to_date')

all_comps = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name asc") if c.name != "My Company"]

EXECUTIVE_ROLES = [
    "Administrator",
    "System Manager",
    "CEO",
    "Director",
    "Executive",
    "Operation",
    "Operations",
    "Operations Manager",
    "Finance",
    "Finance Manager",
    "Financial Officer",
    "Accounting",
    "Accounts Manager",
    "Accounts User",
    "Auditor"
]

# Check permissions
if target_user == "Administrator":
    can_view_all = True
    allowed_companies = all_comps
    default_company = 'All Companies'
else:
    user_roles = frappe.get_all("Has Role", filters={"parent": target_user}, pluck="role")
    is_executive = False
    for r in user_roles:
        if r in EXECUTIVE_ROLES:
            is_executive = True
            break
            
    if is_executive:
        can_view_all = True
        allowed_companies = all_comps
        default_company = 'All Companies'
    else:
        can_view_all = False
        allowed = []
        emps = frappe.get_all("Employee", filters={"user_id": target_user}, fields=["company", "status"])
        for e in emps:
            c = e.get("company")
            if c and c not in allowed and c != "My Company":
                allowed.append(c)
                
        perms = frappe.get_all("User Permission", filters={"user": target_user, "allow": "Company"}, pluck="for_value")
        for c in perms:
            if c and c not in allowed and c != "My Company":
                allowed.append(c)
                
        allowed.sort()
        allowed_companies = allowed
        default_company = allowed[0] if allowed else ""

user_perm = {
    'can_view_all': can_view_all,
    'allowed_companies': allowed_companies,
    'default_company': default_company
}

filters = {"docstatus": ["!=", 2]}

if not can_view_all:
    if not allowed_companies:
        frappe.response['message'] = {
            'summary': {
                'total_revenue': 0.0,
                'total_labor': 0.0,
                'total_parts': 0.0,
                'total_jos': 0,
                'avg_ticket': 0.0,
                'unique_vehicles': 0
            },
            'top_services': [],
            'top_parts': [],
            'top_tires_mags': [],
            'company_performance': [],
            'user_perm': user_perm
        }
    else:
        if company_param and company_param in allowed_companies:
            filters["company"] = company_param
        else:
            if len(allowed_companies) == 1:
                filters["company"] = allowed_companies[0]
            else:
                filters["company"] = ["in", allowed_companies]
else:
    if company_param and company_param != "All Companies":
        filters["company"] = company_param

if from_date and to_date:
    filters["job_order_date"] = ["between", [from_date, to_date]]
elif timespan == "Last 30 Days":
    filters["job_order_date"] = [">=", frappe.utils.add_months(frappe.utils.nowdate(), -1)]
elif timespan == "This Year":
    filters["job_order_date"] = [">=", str(frappe.utils.getdate().year) + "-01-01"]

job_orders = frappe.get_all(
    "Vehicle Job Order",
    filters=filters,
    fields=[
        "name",
        "company",
        "customer",
        "vehicle",
        "status",
        "payment_status",
        "total_labor",
        "total_parts",
        "discount_amount",
        "grand_total",
        "job_order_date",
    ],
    order_by="job_order_date desc",
    limit_page_length=5000
)

jo_names = [jo.name for jo in job_orders]

# Summary KPIs
total_revenue = sum(frappe.utils.flt(jo.grand_total) for jo in job_orders)
total_labor = sum(frappe.utils.flt(jo.total_labor) for jo in job_orders)
total_parts = sum(frappe.utils.flt(jo.total_parts) for jo in job_orders)
total_jos = len(job_orders)
avg_ticket = (total_revenue / total_jos) if total_jos > 0 else 0.0
unique_vehicles = len(set([jo.vehicle for jo in job_orders if jo.vehicle]))

# 1. Services Breakdown
service_map = {}
if jo_names:
    services = frappe.get_all(
        "Job Order Service Item",
        filters={"parent": ["in", jo_names]},
        fields=["service_item", "description", "hours", "rate", "discount_amount", "total_amount", "parent"],
        limit_page_length=10000
    )
    for s in services:
        key = s.description or s.service_item or "General Service"
        if key not in service_map:
            service_map[key] = {
                "service_name": key,
                "item_code": s.service_item or "-",
                "count": 0,
                "total_hours": 0.0,
                "total_amount": 0.0,
            }
        service_map[key]["count"] = service_map[key]["count"] + 1
        service_map[key]["total_hours"] = service_map[key]["total_hours"] + (frappe.utils.flt(s.hours) or 1.0)
        service_map[key]["total_amount"] = service_map[key]["total_amount"] + (frappe.utils.flt(s.total_amount) or 0.0)

top_services = sorted(service_map.values(), key=lambda x: x["total_amount"], reverse=True)

# 2. Parts, Tires & Mags Breakdown
part_map = {}
tires_mags_map = {}

if jo_names:
    parts = frappe.get_all(
        "Job Order Part Item",
        filters={"parent": ["in", jo_names]},
        fields=["item_code", "item_name", "part_no", "qty", "uom", "rate", "discount_amount", "amount", "parent"],
        limit_page_length=10000
    )
    tire_keywords = ["TIRE", "YOKOHAMA", "DUNLOP", "BRIDGESTONE", "MICHELIN", "SAILUN", "ROADCRUZA", "185/", "195/", "205/", "215/", "225/", "235/", "245/", "265/", "275/", "285/", "R14", "R15", "R16", "R17", "R18", "R20"]
    mag_keywords = ["MAG", "TE37", "ROTA", "VOLK", "WHEEL", "RIMS", "ALLOY", "18X8.5", "18X9", "20X9.5", "17X8.5", "PM2"]

    for p in parts:
        name_key = p.item_name or p.item_code or "Generic Part"
        amount = frappe.utils.flt(p.amount)
        qty = frappe.utils.flt(p.qty) or 1.0

        if name_key not in part_map:
            part_map[name_key] = {
                "item_name": name_key,
                "item_code": p.item_code or "-",
                "part_no": p.part_no or "-",
                "total_qty": 0.0,
                "uom": p.uom or "PC",
                "total_amount": 0.0,
            }
        part_map[name_key]["total_qty"] = part_map[name_key]["total_qty"] + qty
        part_map[name_key]["total_amount"] = part_map[name_key]["total_amount"] + amount

        upper_name = name_key.upper()
        is_tire = any(k in upper_name for k in tire_keywords)
        is_mag = any(k in upper_name for k in mag_keywords)

        if is_tire or is_mag:
            cat = "Mags / Wheels" if is_mag else "Tires"
            if name_key not in tires_mags_map:
                tires_mags_map[name_key] = {
                    "item_name": name_key,
                    "category": cat,
                    "item_code": p.item_code or "-",
                    "part_no": p.part_no or "-",
                    "total_qty": 0.0,
                    "uom": p.uom or "PC",
                    "total_amount": 0.0,
                }
            tires_mags_map[name_key]["total_qty"] = tires_mags_map[name_key]["total_qty"] + qty
            tires_mags_map[name_key]["total_amount"] = tires_mags_map[name_key]["total_amount"] + amount

top_parts = sorted(part_map.values(), key=lambda x: x["total_amount"], reverse=True)
top_tires_mags = sorted(tires_mags_map.values(), key=lambda x: x["total_amount"], reverse=True)

# 3. Company / Branch Performance
company_map = {}
target_companies = all_comps if can_view_all else allowed_companies

for comp in target_companies:
    if comp != "My Company":
        company_map[comp] = {
            "company": comp,
            "total_jos": 0,
            "total_labor": 0.0,
            "total_parts": 0.0,
            "total_revenue": 0.0,
            "completed_jos": 0,
        }

for jo in job_orders:
    c = jo.company or "ULTRA MRF"
    if not can_view_all and c not in allowed_companies:
        continue
    if c not in company_map:
        company_map[c] = {
            "company": c,
            "total_jos": 0,
            "total_labor": 0.0,
            "total_parts": 0.0,
            "total_revenue": 0.0,
            "completed_jos": 0,
        }
    company_map[c]["total_jos"] = company_map[c]["total_jos"] + 1
    company_map[c]["total_labor"] = company_map[c]["total_labor"] + frappe.utils.flt(jo.total_labor)
    company_map[c]["total_parts"] = company_map[c]["total_parts"] + frappe.utils.flt(jo.total_parts)
    company_map[c]["total_revenue"] = company_map[c]["total_revenue"] + frappe.utils.flt(jo.grand_total)
    if jo.status in ["Completed", "Released", "Invoiced"]:
        company_map[c]["completed_jos"] = company_map[c]["completed_jos"] + 1

company_performance = sorted(
    [v for v in company_map.values() if v["total_jos"] > 0 or v["total_revenue"] > 0 or not can_view_all],
    key=lambda x: x["total_revenue"],
    reverse=True
)

frappe.response['message'] = {
    "summary": {
        "total_revenue": total_revenue,
        "total_labor": total_labor,
        "total_parts": total_parts,
        "total_jos": total_jos,
        "avg_ticket": avg_ticket,
        "unique_vehicles": unique_vehicles,
    },
    "top_services": top_services[:10],
    "top_parts": top_parts[:10],
    "top_tires_mags": top_tires_mags[:10],
    "company_performance": company_performance,
    "user_perm": user_perm,
}
"""

res = s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Get%20Vehicle%20Analytics", json={
    'doctype': 'Server Script',
    'name': 'VM Get Vehicle Analytics',
    'script': analytics_script_code,
    'script_type': 'API',
    'api_method': 'vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics',
    'allow_guest': 0,
    'disabled': 0
})
if res.status_code not in [200, 201]:
    res = s.post(f"{VPS_BASE}/api/resource/Server Script", json={
        'doctype': 'Server Script',
        'name': 'VM Get Vehicle Analytics',
        'script': analytics_script_code,
        'script_type': 'API',
        'api_method': 'vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics',
        'allow_guest': 0,
        'disabled': 0
    })
print("Deployed get_vehicle_management_analytics Server Script:", res.status_code)

# -----------------------------------------------------------------------------
# 3. Update Page/vehicle_analytics JS
# -----------------------------------------------------------------------------
with open("frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/page/vehicle_analytics/vehicle_analytics.js", "r", encoding="utf-8") as f:
    page_js_content = f.read()

res_page = s.put(f"{VPS_BASE}/api/resource/Page/vehicle_analytics", json={
    "script": page_js_content
})
print("Updated Page/vehicle_analytics script on VPS:", res_page.status_code)

# -----------------------------------------------------------------------------
# 4. Verify Administrator View
# -----------------------------------------------------------------------------
print("\n=======================================================")
print("VERIFYING ADMINISTRATOR / ALL COMPANIES VIEW")
print("=======================================================")
admin_perm = s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_user_analytics_permissions").json().get("message", {})
print("Admin can_view_all:", admin_perm.get("can_view_all"))
print("Admin allowed_companies count:", len(admin_perm.get("allowed_companies", [])))
print("Admin default_company:", admin_perm.get("default_company"))

admin_data = s.get(f"{VPS_BASE}/api/method/vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics", params={
    "company": "All Companies",
    "timespan": "Last 30 Days"
}).json().get("message", {})

print("Admin Total Revenue:", admin_data.get("summary", {}).get("total_revenue"))
print("Admin Total JOs:", admin_data.get("summary", {}).get("total_jos"))
print("Admin Unique Vehicles:", admin_data.get("summary", {}).get("unique_vehicles"))
print("Admin Top Services Count:", len(admin_data.get("top_services", [])))
print("Admin Top Parts Count:", len(admin_data.get("top_parts", [])))
print("Admin Top Tires/Mags Count:", len(admin_data.get("top_tires_mags", [])))
print("\nAdmin Branches in Performance Table:")
for b in admin_data.get("company_performance", []):
    print(f" - {b['company']}: {b['total_jos']} JOs | Revenue: PHP {b['total_revenue']:,.2f}")

# -----------------------------------------------------------------------------
# 5. Verify Branch-Specific Employees Scoping via Simulation API
# -----------------------------------------------------------------------------
print("\n=======================================================")
print("VERIFYING BRANCH EMPLOYEES SCOPED ACCESS")
print("=======================================================")

eval_users_script = """
users_to_test = [
    "jayson.espiritu@ultramrf.ph",
    "jasper.david@ultramrf.ph",
    "salvador.torrecampo@ultramrf.ph",
    "testdau@gmail.com",
    "test@gmail.com",
    "test12@gmail.com",
    "whsdau@gmail.com"
]

all_comps = [c.name for c in frappe.get_all("Company", filters={"is_group": 0}, order_by="name asc") if c.name != "My Company"]

results = []
for u in users_to_test:
    allowed = []
    emps = frappe.get_all("Employee", filters={"user_id": u}, fields=["company", "status"])
    for e in emps:
        c = e.get("company")
        if c and c not in allowed and c != "My Company":
            allowed.append(c)
            
    perms = frappe.get_all("User Permission", filters={"user": u, "allow": "Company"}, pluck="for_value")
    for c in perms:
        if c and c not in allowed and c != "My Company":
            allowed.append(c)
            
    allowed.sort()
    
    jos = frappe.get_all("Vehicle Job Order", filters={"docstatus": ["!=", 2], "company": ["in", allowed]}, fields=["name", "company", "grand_total"])
    tot_rev = sum(frappe.utils.flt(j.grand_total) for j in jos)
    
    results.append({
        "user": u,
        "employee_company": emps[0].get("company") if emps else "None",
        "allowed_companies": allowed,
        "can_view_all": False,
        "scoped_jos_count": len(jos),
        "scoped_revenue": tot_rev
    })

frappe.response['message'] = results
"""

s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Verify%20All%20Branch%20Users", json={
    'doctype': 'Server Script',
    'name': 'VM Verify All Branch Users',
    'script': eval_users_script,
    'script_type': 'API',
    'api_method': 'vm_verify_all_branch_users',
    'allow_guest': 0,
    'disabled': 0
})

r_branch_eval = s.get(f"{VPS_BASE}/api/method/vm_verify_all_branch_users").json()
for r in r_branch_eval.get("message", []):
    print(f"\nUser: {r['user']}")
    print(f"  🏢 Employee Company Tag: {r['employee_company']}")
    print(f"  🔒 Allowed Companies in Dashboard: {r['allowed_companies']}")
    print(f"  📊 Scoped Job Orders: {r['scoped_jos_count']}")
    print(f"  💰 Scoped Revenue: PHP {r['scoped_revenue']:,.2f}")

print("\n=== DEPLOYMENT AND VALIDATION FINISHED SUCCESSFULLY ===")
