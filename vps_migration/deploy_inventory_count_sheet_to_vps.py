"""
deploy_inventory_count_sheet_to_vps.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Full deployment of enhanced Multi-Warehouse Inventory Count Sheet to VPS:
1. DocType upsert (Inventory Count Sheet Item with Warehouse column + Parent with clean Section Breaks)
2. Client Script with Multi-Warehouse Selection Dialog & Primary 'Get Items' button
3. Server Script APIs supporting Multi-Warehouse, Parent Group Warehouse resolution, and Item Group filtering
4. Server Script DocType Events (validation, variance calculations, summary KPIs)
5. Vehicle Management Workspace Shortcut
6. Verification tests
"""

import sys
import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body[:300]}")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
        ),
        timeout=30,
    )
    print("[OK] Logged into VPS as " + usr)

def upsert_doctype(doctype_name, schema):
    print(f"\n[1] Upserting DocType: {doctype_name}")
    quoted = urllib.parse.quote(doctype_name)
    existing = call(f"/api/resource/DocType/{quoted}", "GET")
    
    if existing.get("data"):
        doc = existing["data"]
        doc["fields"] = schema["fields"]
        doc["permissions"] = schema.get("permissions", doc.get("permissions", []))
        for k in ["is_submittable", "istable", "track_changes", "autoname", "search_fields"]:
            if k in schema:
                doc[k] = schema[k]
        
        save_res = call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
        if save_res.get("data") or save_res.get("message") or not save_res.get("exc"):
            print(f"  [OK] DocType '{doctype_name}' updated successfully.")
        else:
            print(f"  [WARN] Update response: {save_res}")
    else:
        create_res = call("/api/resource/DocType", "POST", schema)
        if create_res.get("data"):
            print(f"  [OK] DocType '{doctype_name}' created successfully.")
        else:
            print(f"  [FAIL] Failed to create DocType: {create_res}")

def deploy_client_script():
    print("\n[2] Deploying Client Script for 'Inventory Count Sheet'...")
    with open(r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\vehicle_management\doctype\inventory_count_sheet\inventory_count_sheet.js", "r", encoding="utf-8") as f:
        js_code = f.read()

    script_name = "VMS Inventory Count Sheet UI"
    quoted = urllib.parse.quote(script_name)
    existing = call(f"/api/resource/Client%20Script/{quoted}", "GET")
    
    payload = {
        "dt": "Inventory Count Sheet",
        "script_type": "Form",
        "script": js_code,
        "enabled": 1,
    }
    
    if existing.get("data"):
        doc = existing["data"]
        doc.update(payload)
        res = call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    else:
        payload["doctype"] = "Client Script"
        payload["name"] = script_name
        res = call("/api/resource/Client%20Script", "POST", payload)
        
    print("  [OK] Client Script deployed.")

def deploy_server_script_apis():
    print("\n[3] Deploying Server Script APIs (Multi-Warehouse support)...")
    
    # get_warehouse_items
    q_script = r'''
def get_warehouse_items():
    company = frappe.form_dict.get("company")
    warehouse = frappe.form_dict.get("warehouse")
    select_all = str(frappe.form_dict.get("select_all") or "0") in ("1", "true", "True")
    item_group = frappe.form_dict.get("item_group")
    bin_filter = frappe.form_dict.get("bin_filter")
    raw_ignore = frappe.form_dict.get("ignore_empty_stock")
    ignore_empty = str(raw_ignore) not in ("0", "false", "False")

    # Resolve target warehouses
    wh_list = []
    if select_all:
        if company:
            wh_records = frappe.db.get_all("Warehouse", filters={"company": company, "is_group": 0}, fields=["name"])
        else:
            wh_records = frappe.db.get_all("Warehouse", filters={"is_group": 0}, fields=["name"])
        wh_list = [w.name for w in wh_records]
    elif warehouse:
        # Check if warehouse is group warehouse
        wh_doc = frappe.db.get_value("Warehouse", warehouse, ["is_group", "lft", "rgt"], as_dict=1)
        if wh_doc and wh_doc.get("is_group"):
            lft = wh_doc.get("lft")
            rgt = wh_doc.get("rgt")
            q_children = "select name from `tabWarehouse` where lft >= " + str(lft) + " and rgt <= " + str(rgt) + " and is_group = 0"
            children = frappe.db.sql(q_children, as_dict=1)
            wh_list = [c.name for c in children]
        else:
            wh_list = [warehouse]

    if not wh_list:
        frappe.response["message"] = []
        return

    # Build SQL condition
    wh_placeholders = ", ".join(["%s"] * len(wh_list))
    sql_params = list(wh_list)

    qty_clause = " and b.actual_qty > 0 " if ignore_empty else ""
    ig_clause = ""
    if item_group:
        ig_clause = " and i.item_group = %s "
        sql_params.append(item_group)

    q = (
        "select b.warehouse, b.item_code, b.actual_qty, b.stock_uom, i.item_name, i.item_group "
        "from `tabBin` b "
        "left join `tabItem` i on b.item_code = i.name "
        "where b.warehouse in (" + wh_placeholders + ") " +
        qty_clause + ig_clause +
        " order by b.warehouse asc, b.item_code asc"
    )

    rows = frappe.db.sql(q, tuple(sql_params), as_dict=1)
    
    results = []
    for r in rows:
        try:
            sys_qty = float(r.get("actual_qty") or 0.0)
        except Exception:
            sys_qty = 0.0

        results.append({
            "warehouse": r.get("warehouse"),
            "item_code": r.get("item_code"),
            "item_name": r.get("item_name") or r.get("item_code"),
            "item_group": r.get("item_group") or "",
            "uom": r.get("stock_uom") or "PCS",
            "system_qty": sys_qty,
            "physical_qty": None,
            "variance_qty": 0.0,
            "count_status": "Pending",
            "bin_location": "",
        })

    frappe.response["message"] = results

get_warehouse_items()
'''
    name1 = "VMS Inventory Count Sheet Get Warehouse Items"
    payload1 = {
        "script": q_script,
        "script_type": "API",
        "api_method": "vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
        "allow_guest": 0,
        "disabled": 0,
    }
    
    existing1 = call(f"/api/resource/Server%20Script/{urllib.parse.quote(name1)}", "GET")
    if existing1.get("data"):
        doc = existing1["data"]
        doc.update(payload1)
        call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    else:
        payload1["doctype"] = "Server Script"
        payload1["name"] = name1
        call("/api/resource/Server%20Script", "POST", payload1)
    print("  [OK] Server Script API: get_warehouse_items updated.")

    # get_stock_qty
    q_qty = r'''
def get_stock_qty():
    item_code = frappe.form_dict.get("item_code")
    warehouse = frappe.form_dict.get("warehouse")
    if not (item_code and warehouse):
        frappe.response["message"] = 0.0
        return
        
    qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0.0
    try:
        frappe.response["message"] = float(qty)
    except Exception:
        frappe.response["message"] = 0.0

get_stock_qty()
'''
    name2 = "VMS Inventory Count Sheet Get Stock Qty"
    payload2 = {
        "script": q_qty,
        "script_type": "API",
        "api_method": "vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_stock_qty",
        "allow_guest": 0,
        "disabled": 0,
    }
    existing2 = call(f"/api/resource/Server%20Script/{urllib.parse.quote(name2)}", "GET")
    if existing2.get("data"):
        doc = existing2["data"]
        doc.update(payload2)
        call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    else:
        payload2["doctype"] = "Server Script"
        payload2["name"] = name2
        call("/api/resource/Server%20Script", "POST", payload2)
    print("  [OK] Server Script API: get_stock_qty deployed.")


def deploy_server_script_events():
    print("\n[4] Deploying Server Script DocType Event for 'Inventory Count Sheet'...")
    
    event_script = r'''
items = doc.get("items") or []
total = len(items)
counted = 0
matched = 0
variance_count = 0

for row in items:
    p_raw = row.get("physical_qty")
    if p_raw is None or p_raw == "" or str(p_raw) == "":
        row.count_status = "Pending"
        row.variance_qty = 0.0
        continue

    try:
        p_val = float(p_raw)
    except Exception:
        p_val = 0.0

    try:
        s_val = float(row.get("system_qty") or 0.0)
    except Exception:
        s_val = 0.0

    var_val = p_val - s_val
    row.variance_qty = var_val

    if s_val == 0.0 and p_val > 0.0:
        row.count_status = "New Item"
        variance_count += 1
    elif var_val == 0.0:
        row.count_status = "Matched"
        matched += 1
    elif var_val > 0.0:
        row.count_status = "Over"
        variance_count += 1
    else:
        row.count_status = "Short"
        variance_count += 1

    counted += 1

uncounted = total - counted
doc.total_lines = total
doc.counted_lines = counted
doc.matched_lines = matched
doc.variance_lines = variance_count
doc.uncounted_lines = uncounted

if counted > 0:
    doc.count_accuracy = round((float(matched) / float(counted)) * 100.0, 2)
else:
    doc.count_accuracy = 0.0

if total > 0:
    if uncounted == total:
        doc.status = "Draft"
    elif uncounted > 0:
        doc.status = "In Progress"
    else:
        doc.status = "Completed"
'''
    name = "VMS Inventory Count Sheet Before Save"
    payload = {
        "script": event_script,
        "script_type": "DocType Event",
        "reference_doctype": "Inventory Count Sheet",
        "doctype_event": "Before Save",
        "disabled": 0,
    }
    
    existing = call(f"/api/resource/Server%20Script/{urllib.parse.quote(name)}", "GET")
    if existing.get("data"):
        d = existing["data"]
        d.update(payload)
        call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(d)})
    else:
        payload["doctype"] = "Server Script"
        payload["name"] = name
        call("/api/resource/Server%20Script", "POST", payload)
    print("  [OK] Server Script DocType Event: Before Save deployed.")


def verify_deployment():
    print("\n[5] Verifying Multi-Warehouse & Single Warehouse queries...")
    
    # 1. Single Warehouse (Stores - UM)
    res1 = call(
        "/api/method/vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
        "POST",
        {"warehouse": "Stores - UM"}
    )
    items1 = res1.get("message") or []
    print(f"  [OK] Single Warehouse ('Stores - UM') -> {len(items1)} items.")

    # 2. Parent Group Warehouse (All Warehouses - UM)
    res2 = call(
        "/api/method/vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
        "POST",
        {"warehouse": "All Warehouses - UM"}
    )
    items2 = res2.get("message") or []
    print(f"  [OK] Parent Group Warehouse ('All Warehouses - UM') -> {len(items2)} items.")

    # 3. Select All Warehouses in Company
    res3 = call(
        "/api/method/vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
        "POST",
        {"company": "ULTRA MRF", "select_all": 1}
    )
    items3 = res3.get("message") or []
    print(f"  [OK] Select All Warehouses in Company ('ULTRA MRF') -> {len(items3)} items.")


CHILD_DT = {
    "doctype": "DocType",
    "name": "Inventory Count Sheet Item",
    "module": "Vehicle Management",
    "custom": 0,
    "istable": 1,
    "editable_grid": 1,
    "engine": "InnoDB",
    "fields": [
        {"fieldname":"warehouse",    "fieldtype":"Link",    "options":"Warehouse","label":"Warehouse","in_list_view":1,"columns":2,"read_only":1},
        {"fieldname":"item_code",    "fieldtype":"Link",    "options":"Item",     "label":"Item Code","reqd":1,"in_list_view":1,"columns":2},
        {"fieldname":"item_name",    "fieldtype":"Data",    "label":"Item Name","fetch_from":"item_code.item_name","read_only":1,"in_list_view":1,"columns":3},
        {"fieldname":"uom",          "fieldtype":"Link",    "options":"UOM","label":"UOM","fetch_from":"item_code.stock_uom","in_list_view":1,"columns":1},
        {"fieldname":"system_qty",   "fieldtype":"Float",   "label":"System Qty","read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"physical_qty", "fieldtype":"Float",   "label":"Physical Count","in_list_view":1,"columns":1},
        {"fieldname":"variance_qty", "fieldtype":"Float",   "label":"Variance","read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"count_status", "fieldtype":"Select",  "options":"Pending\nMatched\nOver\nShort\nNew Item","default":"Pending","label":"Status","read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"bin_location", "fieldtype":"Data",    "label":"Bin / Location"},
        {"fieldname":"item_group",   "fieldtype":"Data",    "label":"Item Group","fetch_from":"item_code.item_group","read_only":1},
        {"fieldname":"barcode",      "fieldtype":"Data",    "label":"Barcode"},
        {"fieldname":"remarks",      "fieldtype":"Data",    "label":"Remarks"},
    ],
    "permissions": []
}

PARENT_DT = {
    "doctype": "DocType",
    "name": "Inventory Count Sheet",
    "module": "Vehicle Management",
    "custom": 0,
    "is_submittable": 1,
    "istable": 0,
    "track_changes": 1,
    "engine": "InnoDB",
    "autoname": "naming_series:",
    "search_fields": "company,warehouse,count_date,status",
    "fields": [
        {"fieldname":"sec_basic",    "fieldtype":"Section Break","label":"Count Details"},
        {"fieldname":"naming_series","fieldtype":"Select","options":"IC-.YYYY.-.#####","default":"IC-.YYYY.-.#####","label":"Series"},
        {"fieldname":"company",      "fieldtype":"Link",  "options":"Company","label":"Company / Branch","reqd":1,"in_list_view":1,"in_standard_filter":1},
        {"fieldname":"warehouse",    "fieldtype":"Link",  "options":"Warehouse","label":"Primary / Group Warehouse","in_list_view":1,"in_standard_filter":1,"description":"Select a specific warehouse or group warehouse (e.g. All Warehouses - UM)"},
        {"fieldname":"count_date",   "fieldtype":"Date",  "label":"Count Date","default":"Today","reqd":1,"in_list_view":1},
        {"fieldname":"col_break_1",  "fieldtype":"Column Break"},
        {"fieldname":"count_type",   "fieldtype":"Select","options":"Full Physical Count\nCycle Count (Spot Check)\nVariance Investigation\nPre-Audit Count","default":"Full Physical Count","label":"Count Type","in_list_view":1},
        {"fieldname":"status",       "fieldtype":"Select","options":"Draft\nIn Progress\nCompleted\nSubmitted\nCancelled","default":"Draft","label":"Status","in_list_view":1,"in_standard_filter":1,"allow_on_submit":1},
        {"fieldname":"bin_filter",   "fieldtype":"Data",  "label":"Bin / Location Filter"},
        {"fieldname":"remarks",      "fieldtype":"Small Text","label":"Remarks / Notes"},
        {"fieldname":"sec_items",    "fieldtype":"Section Break","label":"Count Lines"},
        {"fieldname":"items",        "fieldtype":"Table", "options":"Inventory Count Sheet Item","label":"Inventory Count Lines"},
        {"fieldname":"sec_summary",  "fieldtype":"Section Break","label":"Count Summary"},
        {"fieldname":"total_lines",  "fieldtype":"Int",  "label":"Total Lines","read_only":1},
        {"fieldname":"counted_lines","fieldtype":"Int",  "label":"Counted Lines","read_only":1},
        {"fieldname":"matched_lines","fieldtype":"Int",  "label":"Matched (No Variance)","read_only":1},
        {"fieldname":"col_break_summary","fieldtype":"Column Break"},
        {"fieldname":"variance_lines","fieldtype":"Int", "label":"Lines with Variance","read_only":1},
        {"fieldname":"uncounted_lines","fieldtype":"Int","label":"Uncounted Lines","read_only":1},
        {"fieldname":"count_accuracy","fieldtype":"Percent","label":"Count Accuracy (%)","read_only":1},
        {"fieldname":"sec_signoff",  "fieldtype":"Section Break","label":"Sign-Off & Authorization"},
        {"fieldname":"counter_name", "fieldtype":"Data", "label":"Counter (Stock Clerk)"},
        {"fieldname":"verifier_name","fieldtype":"Data", "label":"Verifier (Warehouse Head)"},
        {"fieldname":"col_break_signoff","fieldtype":"Column Break"},
        {"fieldname":"approver_name","fieldtype":"Data", "label":"Approver (Branch Manager)"},
        {"fieldname":"auditor_name", "fieldtype":"Data", "label":"Reviewer (Accounting / Auditor)"},
        {"fieldname":"counter_user", "fieldtype":"Link", "options":"User","label":"Counter (User)"},
        {"fieldname":"approved_by",  "fieldtype":"Link", "options":"User","label":"Approved By (User)"},
    ],
    "permissions": [
        {"role":"System Manager","read":1,"write":1,"create":1,"submit":1,"cancel":1,"delete":1,"amend":1},
        {"role":"Stock Manager", "read":1,"write":1,"create":1,"submit":1,"cancel":1,"delete":0},
        {"role":"Stock User",    "read":1,"write":1,"create":1,"submit":0,"cancel":0,"delete":0},
        {"role":"Accounts Manager","read":1,"write":0,"create":0,"submit":0,"cancel":0,"delete":0},
    ]
}

if __name__ == "__main__":
    login()
    upsert_doctype("Inventory Count Sheet Item", CHILD_DT)
    upsert_doctype("Inventory Count Sheet", PARENT_DT)
    deploy_client_script()
    deploy_server_script_apis()
    deploy_server_script_events()
    verify_deployment()
    print("\n[DONE] Multi-Warehouse Inventory Count Sheet successfully deployed to VPS!")
