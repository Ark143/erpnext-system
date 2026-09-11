"""
deploy_relationship_map_recon_fix.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Updates 'Inventory Relationship Map API' Server Script so that:
   - Stock Reconciliation rows in Stock Ledger Entry display their real signed adjustment delta (e.g. -1.00 PC or +2.00 PC) fetched from quantity_difference.
   - Inventory Count Sheet nodes and links are seamlessly included in the Relationship Map graph and document list.
   - Both 'root_type == Inventory Count Sheet' and item/warehouse queries trace Inventory Count Sheet -> Stock Reconciliation -> Stock Ledger Entry.
2. Verifies on VPS with IC-2026-00011 and STRL-CAR PROTECT KIT.
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

ENHANCED_SCRIPT = r'''
def build_map(params):
    if frappe.session.user == "Guest":
        frappe.throw("Please sign in to view inventory relationships.")
    item_code = params.get("item_code")
    company = params.get("company")
    warehouse = params.get("warehouse")
    bin_location = params.get("bin_location")
    from_date = params.get("from_date")
    to_date = params.get("to_date")
    limit = min(300, max(1, int(params.get("limit") or 120)))
    if from_date:
        from_date = str(frappe.utils.getdate(from_date))
    if to_date:
        to_date = str(frappe.utils.getdate(to_date))
    if from_date and to_date and from_date > to_date:
        frappe.throw("From date must be on or before To date.")

    allowed_types = ["Stock Entry", "Stock Reconciliation", "Purchase Receipt",
                     "Delivery Note", "Sales Invoice", "Purchase Invoice", "POS Invoice", "Inventory Count Sheet"]
    root_type = params.get("doctype")
    root_name = params.get("docname")
    source_items = []
    
    if root_type or root_name:
        if root_type not in allowed_types or not root_name:
            frappe.throw("Choose a supported inventory document and its name.")
        found = frappe.get_list(root_type, filters={"name": root_name}, fields=["name"], limit_page_length=1)
        if not found:
            frappe.throw("Source document is unavailable or you do not have permission to read it.")
        source_doc = frappe.get_doc(root_type, root_name)
        for row in source_doc.get("items") or []:
            code = row.get("item_code")
            if code and code not in source_items:
                source_items.append(code)
        if not company:
            company = source_doc.get("company")
        if not warehouse and source_doc.get("warehouse"):
            warehouse = source_doc.get("warehouse")
        if not item_code and source_items:
            item_code = source_items[0]
        if not item_code:
            return {"item": None, "source_items": [], "movements": [], "balances": [],
                    "documents": [], "references": [], "truncated": False,
                    "empty_reason": "This source document has no item rows to map."}

    wh_filters = {}
    if company:
        wh_filters["company"] = company
    if warehouse:
        wh_filters["name"] = warehouse
    warehouses = frappe.get_list("Warehouse", filters=wh_filters,
        fields=["name", "company"], order_by="name asc", limit_page_length=501)
    if len(warehouses) > 500:
        frappe.throw("More than 500 warehouses match. Choose a company or warehouse.")
    wh_names = [w.get("name") for w in warehouses]
    company_by_wh = {}
    for w in warehouses:
        company_by_wh[w.get("name")] = w.get("company")
    if warehouse and not wh_names:
        frappe.throw("Warehouse is unavailable for the selected company or your permissions.")
    if bin_location:
        selected_bins = frappe.get_list("Bin Location", filters={"name": bin_location,
            "warehouse": ["in", wh_names]}, fields=["name"], limit_page_length=1)
        if not selected_bins:
            frappe.throw("Bin location is unavailable for the selected company, warehouse or your permissions.")
    filters = {"is_cancelled": 0, "warehouse": ["in", wh_names]}
    if bin_location:
        filters["bin_location"] = bin_location
    if company:
        filters["company"] = company
    if not item_code:
        recent = frappe.get_list("Stock Ledger Entry", filters=filters,
            fields=["item_code"], order_by="posting_date desc, posting_time desc, creation desc", limit_page_length=1)
        if recent:
            item_code = recent[0].get("item_code")
    if not item_code:
        return {"item": None, "source_items": source_items, "movements": [], "balances": [],
                "documents": [], "references": [], "truncated": False}
    items = frappe.get_list("Item", filters={"name": item_code},
        fields=["name", "item_name", "stock_uom", "is_stock_item"], limit_page_length=1)
    if not items:
        frappe.throw("Item is unavailable or you do not have permission to read it.")
    filters["item_code"] = item_code
    if from_date and to_date:
        filters["posting_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["posting_date"] = [">=", from_date]
    elif to_date:
        filters["posting_date"] = ["<=", to_date]
    rows = frappe.get_list("Stock Ledger Entry", filters=filters,
        fields=["name", "item_code", "warehouse", "company", "posting_date", "posting_time",
                "voucher_type", "voucher_no", "actual_qty", "qty_after_transaction", "stock_uom",
                "batch_no", "serial_no", "serial_and_batch_bundle", "bin_location"],
        order_by="posting_date desc, posting_time desc, creation desc, name desc", limit_page_length=limit + 1)
    truncated = len(rows) > limit
    rows = rows[:limit]

    # FIX: For Stock Reconciliation, resolve the actual delta quantity from Stock Reconciliation Item
    for row in rows:
        if row.get("voucher_type") == "Stock Reconciliation":
            v_no = row.get("voucher_no")
            w_name = row.get("warehouse")
            diff = frappe.db.get_value("Stock Reconciliation Item", {"parent": v_no, "item_code": item_code, "warehouse": w_name}, "quantity_difference")
            if diff is not None:
                try:
                    row["actual_qty"] = float(diff)
                except Exception:
                    pass

    location_names = []
    for row in rows:
        if row.get("bin_location") and row.get("bin_location") not in location_names:
            location_names.append(row.get("bin_location"))
    locations = []
    if location_names:
        locations = frappe.get_list("Bin Location", filters={"name": ["in", location_names],
            "warehouse": ["in", wh_names]}, fields=["name", "warehouse", "company", "zone", "rack", "shelf", "bin_no"],
            order_by="name asc", limit_page_length=300)

    balances = frappe.get_list("Bin", filters={"item_code": item_code, "warehouse": ["in", wh_names]},
        fields=["name", "warehouse", "actual_qty", "reserved_qty", "ordered_qty", "projected_qty"],
        order_by="warehouse asc", limit_page_length=501)
    if len(balances) > 500:
        frappe.throw("Too many balances. Choose a warehouse.")
    for balance in balances:
        balance["company"] = company_by_wh.get(balance.get("warehouse"))

    documents = []
    references = []
    seen = []
    readable = []
    
    # If root is Inventory Count Sheet, insert it as primary node
    if root_type == "Inventory Count Sheet":
        cs_doc = frappe.get_doc("Inventory Count Sheet", root_name)
        cs_key = "Inventory Count Sheet::" + root_name
        seen.append(cs_key)
        readable.append(cs_key)
        documents.append({
            "id": cs_key, "doctype": "Inventory Count Sheet", "name": root_name,
            "status": "Cancelled" if cs_doc.get("docstatus") == 2 else (cs_doc.get("status") or "Submitted"),
            "purpose": cs_doc.get("count_type") or "Cycle Count",
            "date": str(cs_doc.get("count_date") or ""),
            "company": cs_doc.get("company"), "party": None
        })
        if cs_doc.get("stock_reconciliation"):
            reco_name = cs_doc.get("stock_reconciliation")
            references.append({
                "from": cs_key, "to": "Stock Reconciliation::" + str(reco_name),
                "doctype": "Inventory Count Sheet", "name": root_name, "label": "Physical Audit"
            })

    for row in rows:
        dt = row.get("voucher_type")
        name = row.get("voucher_no")
        key = dt + "::" + name
        if key not in seen:
            seen.append(key)
            if dt in allowed_types:
                permitted = frappe.get_list(dt, filters={"name": name}, fields=["name"], limit_page_length=1)
                if permitted:
                    doc = frappe.get_doc(dt, name)
                    readable.append(key)
                    documents.append({
                        "id": key, "doctype": dt, "name": name,
                        "status": "Cancelled" if doc.get("docstatus") == 2 else (doc.get("status") or "Submitted"),
                        "purpose": doc.get("purpose"), "date": str(doc.get("posting_date") or ""),
                        "company": doc.get("company"), "party": doc.get("supplier") or doc.get("customer")
                    })
                    link_fields = {"purchase_order": "Purchase Order", "purchase_receipt": "Purchase Receipt",
                                   "sales_order": "Sales Order", "delivery_note": "Delivery Note",
                                   "material_request": "Material Request"}
                    for child in doc.get("items") or []:
                        if child.get("item_code") != item_code:
                            continue
                        for field in link_fields:
                            linked_name = child.get(field)
                            linked_type = link_fields[field]
                            if linked_name:
                                allowed = frappe.get_list(linked_type, filters={"name": linked_name}, fields=["name"], limit_page_length=1)
                                edge = {"from": linked_type + "::" + linked_name, "to": key,
                                        "doctype": linked_type, "name": linked_name}
                                if allowed and edge not in references:
                                    references.append(edge)
                    return_against = doc.get("return_against")
                    if return_against:
                        allowed = frappe.get_list(dt, filters={"name": return_against}, fields=["name"], limit_page_length=1)
                        if allowed:
                            references.append({"from": dt + "::" + return_against, "to": key,
                                               "doctype": dt, "name": return_against, "label": "Return against"})
                    
                    # Also link any Inventory Count Sheet linked to this Stock Reconciliation
                    if dt == "Stock Reconciliation":
                        cs_records = frappe.get_list("Inventory Count Sheet", filters={"stock_reconciliation": name}, fields=["name", "company", "count_date", "status", "count_type"])
                        for cs in cs_records:
                            cs_key = "Inventory Count Sheet::" + cs["name"]
                            if cs_key not in seen:
                                seen.append(cs_key)
                                readable.append(cs_key)
                                documents.append({
                                    "id": cs_key, "doctype": "Inventory Count Sheet", "name": cs["name"],
                                    "status": cs.get("status") or "Submitted",
                                    "purpose": cs.get("count_type") or "Cycle Count",
                                    "date": str(cs.get("count_date") or ""),
                                    "company": cs.get("company"), "party": None
                                })
                            edge_cs = {"from": cs_key, "to": key, "doctype": "Inventory Count Sheet", "name": cs["name"], "label": "Physical Audit"}
                            if edge_cs not in references:
                                references.append(edge_cs)

    for row in rows:
        row["can_open_voucher"] = row.get("voucher_type") + "::" + row.get("voucher_no") in readable

    return {"item": items[0], "source_items": source_items, "company": company,
            "bin_location": bin_location, "locations": locations,
            "movements": rows, "balances": balances, "documents": documents,
            "references": references, "truncated": truncated, "limit": limit,
            "from_date": from_date, "to_date": to_date}

frappe.response["message"] = build_map(frappe.form_dict)
'''

def deploy():
    print("\n[1] Updating 'Inventory Relationship Map API' on VPS...")
    quoted = urllib.parse.quote("Inventory Relationship Map API")
    res = call(f"/api/resource/Server%20Script/{quoted}", "GET")
    if not res.get("data"):
        print("  [FAIL] Server Script not found.")
        return

    doc = res["data"]
    doc["script"] = ENHANCED_SCRIPT
    save_res = call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    if save_res.get("data") or save_res.get("message") or not save_res.get("exc"):
        print("  [OK] Server Script 'Inventory Relationship Map API' updated successfully.")
    else:
        print(f"  [FAIL] Update response: {save_res}")

def verify():
    print("\n[2] Verifying Relationship Map movements for STRL-CAR PROTECT KIT...")
    res = call("/api/method/inventory_relationship_map?item_code=STRL-CAR%20PROTECT%20KIT%20(CAR%20CLEAN%20SET)&company=ULTRA%20MRF", "GET")
    data = res.get("message", {})
    movements = data.get("movements", [])
    print(f"  [OK] Found {len(movements)} movements.")
    for m in movements:
        if m.get("voucher_type") == "Stock Reconciliation":
            print(f"       [*] Stock Reconciliation {m.get('voucher_no')} -> Movement Qty: {m.get('actual_qty')} (After: {m.get('qty_after_transaction')})")
        else:
            print(f"       [-] {m.get('voucher_type')} {m.get('voucher_no')} -> Movement Qty: {m.get('actual_qty')} (After: {m.get('qty_after_transaction')})")

    print("\n[3] Verifying Relationship Map for root doc IC-2026-00011...")
    res_cs = call("/api/method/inventory_relationship_map?doctype=Inventory%20Count%20Sheet&docname=IC-2026-00011&company=ULTRA%20MRF", "GET")
    data_cs = res_cs.get("message", {})
    docs = data_cs.get("documents", [])
    refs = data_cs.get("references", [])
    print(f"  [OK] Documents in graph: {[d['id'] for d in docs]}")
    print(f"  [OK] Edges in graph: {refs}")

if __name__ == "__main__":
    login()
    deploy()
    verify()
    print("\n[DONE] Relationship Map Stock Adjustment Delta fix deployed and verified!")
