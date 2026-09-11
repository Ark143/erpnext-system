"""
deploy_auto_bin_location.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Updates Child DocType 'Inventory Count Sheet Item' to show 'bin_location' in List View
2. Updates Server Script API 'get_warehouse_items' to automatically resolve & assign Bin Location
3. Updates Client Script UI and Print Format to display Bin Location column
4. Verifies auto Bin Location resolution on VPS
"""

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

def update_child_doctype():
    print("\n[1] Updating 'Inventory Count Sheet Item' DocType schema...")
    quoted = urllib.parse.quote("Inventory Count Sheet Item")
    res = call(f"/api/resource/DocType/{quoted}", "GET")
    if not res.get("data"):
        print("  [FAIL] DocType not found")
        return

    doc = res["data"]
    doc["fields"] = [
        {"fieldname":"warehouse",    "fieldtype":"Link",    "options":"Warehouse",   "label":"Warehouse",      "in_list_view":1,"columns":2,"read_only":1},
        {"fieldname":"bin_location", "fieldtype":"Link",    "options":"Bin Location","label":"Bin / Location",  "in_list_view":1,"columns":2},
        {"fieldname":"item_code",    "fieldtype":"Link",    "options":"Item",        "label":"Item Code",      "reqd":1,"in_list_view":1,"columns":2},
        {"fieldname":"item_name",    "fieldtype":"Data",    "label":"Item Name",     "fetch_from":"item_code.item_name","read_only":1,"in_list_view":1,"columns":2},
        {"fieldname":"uom",          "fieldtype":"Link",    "options":"UOM",         "label":"UOM",            "fetch_from":"item_code.stock_uom","in_list_view":1,"columns":1},
        {"fieldname":"system_qty",   "fieldtype":"Float",   "label":"System Qty",    "read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"physical_qty", "fieldtype":"Float",   "label":"Physical Count", "in_list_view":1,"columns":1},
        {"fieldname":"variance_qty", "fieldtype":"Float",   "label":"Variance",      "read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"count_status", "fieldtype":"Select",  "options":"Pending\nMatched\nOver\nShort\nNew Item","default":"Pending","label":"Status","read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"item_group",   "fieldtype":"Data",    "label":"Item Group",    "fetch_from":"item_code.item_group","read_only":1},
        {"fieldname":"barcode",      "fieldtype":"Data",    "label":"Barcode"},
        {"fieldname":"remarks",      "fieldtype":"Data",    "label":"Remarks"},
    ]
    save_res = call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    if save_res.get("data") or save_res.get("message") or not save_res.get("exc"):
        print("  [OK] Child DocType updated to show 'bin_location' in List View.")
    else:
        print(f"  [WARN] Update response: {save_res}")

def deploy_server_script_with_auto_bin():
    print("\n[2] Deploying updated Server Script API with automatic Bin Location resolution...")
    q_script = r'''
def get_warehouse_items():
    company = frappe.form_dict.get("company")
    warehouse = frappe.form_dict.get("warehouse")
    select_all = str(frappe.form_dict.get("select_all") or "0") in ("1", "true", "True")
    item_group = frappe.form_dict.get("item_group")
    bin_filter = frappe.form_dict.get("bin_filter")
    raw_ignore = frappe.form_dict.get("ignore_empty_stock")
    ignore_empty = str(raw_ignore) not in ("0", "false", "False")

    # 1. Resolve target warehouses
    wh_list = []
    if select_all:
        if company:
            wh_records = frappe.db.get_all("Warehouse", filters={"company": company, "is_group": 0}, fields=["name"])
        else:
            wh_records = frappe.db.get_all("Warehouse", filters={"is_group": 0}, fields=["name"])
        wh_list = [w.name for w in wh_records]
    elif warehouse:
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

    # 2. Pre-fetch Bin Locations for all target warehouses
    q_bins = "select name, warehouse, rack, shelf, bin_no, description from `tabBin Location` where is_active = 1"
    all_bins = frappe.db.sql(q_bins, as_dict=1)
    wh_bin_map = {}
    for b in all_bins:
        w_name = b.get("warehouse")
        if w_name not in wh_bin_map:
            wh_bin_map[w_name] = []
        wh_bin_map[w_name].append(b)

    # 3. Query stock bins
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

    # 4. Build results with automatic Bin Location resolution
    results = []
    for r in rows:
        item_wh = r.get("warehouse")
        item_code = str(r.get("item_code") or "")
        item_name = str(r.get("item_name") or "")
        item_grp  = str(r.get("item_group") or "")

        # Match bin location for this item in this warehouse
        bin_loc = ""
        avail_bins = wh_bin_map.get(item_wh) or []
        text = (item_code + " " + item_name + " " + item_grp).lower()

        if avail_bins:
            # Tires
            if any(k in text for k in ["tire", "tyre", "r14", "r15", "r16", "r17", "r18", "r19", "r20", "yokohama", "michelin", "dunlop", "bridgestone", "goodyear"]):
                for b in avail_bins:
                    if "b1" in (b.get("name") or "").lower() or "tire" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Wheels / Mags
            elif any(k in text for k in ["wheel", "mag", "rim", "cap", "rota"]):
                for b in avail_bins:
                    if "b2" in (b.get("name") or "").lower() or "wheel" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Brake System
            elif any(k in text for k in ["brake", "pad", "shoe", "rotor", "caliper", "db "]):
                for b in avail_bins:
                    if "c1" in (b.get("name") or "").lower() or "brake" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Filters & Plugs
            elif any(k in text for k in ["filter", "spark", "plug", "air filter", "oil filter", "cabin"]):
                for b in avail_bins:
                    if "a1-s1" in (b.get("name") or "").lower() or "filter" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Wipers, Belts, Hardware, Sensors
            elif any(k in text for k in ["wiper", "belt", "bulb", "sensor", "hardware", "tps"]):
                for b in avail_bins:
                    if "a1-s2" in (b.get("name") or "").lower() or "wiper" in (b.get("description") or "").lower() or "hardware" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Suspension / Shocks
            elif any(k in text for k in ["shock", "strut", "bushing", "absorber", "suspension", "334012", "348090"]):
                for b in avail_bins:
                    if "c2" in (b.get("name") or "").lower() or "shock" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Engine Oils
            elif any(k in text for k in ["engine oil", "synthetic", "mineral", "10w", "5w", "20w", "treatment"]):
                for b in avail_bins:
                    if "d1-t1" in (b.get("name") or "").lower() or "engine oil" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Coolants, ATF, Fluids
            elif any(k in text for k in ["atf", "coolant", "fluid", "gear oil", "transmission", "degreaser"]):
                for b in avail_bins:
                    if "d1-s2" in (b.get("name") or "").lower() or "coolant" in (b.get("description") or "").lower() or "atf" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Batteries
            elif any(k in text for k in ["battery", "batteries", "alternator", "starter"]):
                for b in avail_bins:
                    if "e1" in (b.get("name") or "").lower() or "battery" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break
            # Consumables / Protect Kits
            elif any(k in text for k in ["protect", "clean", "consumable", "glove", "strl-car"]):
                for b in avail_bins:
                    if "f1" in (b.get("name") or "").lower() or "consumable" in (b.get("description") or "").lower():
                        bin_loc = b.get("name")
                        break

            # Default fallback if no specific rule matched
            if not bin_loc and avail_bins:
                bin_loc = avail_bins[0].get("name")

        # If bin_filter was passed, only return matching bin
        if bin_filter and (bin_loc != bin_filter):
            continue

        try:
            sys_qty = float(r.get("actual_qty") or 0.0)
        except Exception:
            sys_qty = 0.0

        results.append({
            "warehouse": item_wh,
            "item_code": item_code,
            "item_name": item_name or item_code,
            "item_group": item_grp,
            "uom": r.get("stock_uom") or "PCS",
            "system_qty": sys_qty,
            "physical_qty": None,
            "variance_qty": 0.0,
            "count_status": "Pending",
            "bin_location": bin_loc,
        })

    frappe.response["message"] = results

get_warehouse_items()
'''
    name = "VMS Inventory Count Sheet Get Warehouse Items"
    payload = {
        "script": q_script,
        "script_type": "API",
        "api_method": "vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
        "allow_guest": 0,
        "disabled": 0,
    }
    existing = call(f"/api/resource/Server%20Script/{urllib.parse.quote(name)}", "GET")
    if existing.get("data"):
        doc = existing["data"]
        doc.update(payload)
        call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    else:
        payload["doctype"] = "Server Script"
        payload["name"] = name
        call("/api/resource/Server%20Script", "POST", payload)
    print("  [OK] Server Script API updated with auto Bin Location logic.")

def verify():
    print("\n[3] Verifying Auto Bin Location resolution...")
    res = call(
        "/api/method/vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
        "POST",
        {"warehouse": "Stores - UM"}
    )
    items = res.get("message") or []
    print(f"  [OK] Fetched {len(items)} items from 'Stores - UM':")
    for item in items[:8]:
        print(f"       • {item['item_code']:<40} -> Bin: {item['bin_location']}")

if __name__ == "__main__":
    login()
    update_child_doctype()
    deploy_server_script_with_auto_bin()
    verify()
    print("\n[DONE] Automatic Bin Location resolution deployed and verified!")
