import requests
import json

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

notif_script = """
doctype = frappe.form_dict.get('doctype')
name = frappe.form_dict.get('name')
raw_items = frappe.form_dict.get('items')

items = []
if raw_items:
    if isinstance(raw_items, list):
        items = raw_items
    elif isinstance(raw_items, str):
        try:
            items = frappe.parse_json(raw_items)
        except Exception:
            items = []

out = {
    "external_links_found": [],
    "internal_links_found": []
}

CHILD_ITEM_TABLES = {
    "Sales Order": "Sales Order Item",
    "Sales Invoice": "Sales Invoice Item",
    "Delivery Note": "Delivery Note Item",
    "Quotation": "Quotation Item",
    "Purchase Order": "Purchase Order Item",
    "Purchase Receipt": "Purchase Receipt Item",
    "Purchase Invoice": "Purchase Invoice Item",
    "Supplier Quotation": "Supplier Quotation Item",
    "Material Request": "Material Request Item",
    "Stock Entry": "Stock Entry Detail",
    "Stock Reconciliation": "Stock Reconciliation Item",
    "BOM": "BOM Item",
    "Product Bundle": "Product Bundle Item"
}

for d in items:
    try:
        cnt = 0
        if doctype == "Item" and d in CHILD_ITEM_TABLES:
            child_dt = CHILD_ITEM_TABLES[d]
            parents = frappe.get_all(child_dt, filters={"item_code": name, "docstatus": ["!=", 2]}, pluck="parent", distinct=True, limit=100)
            cnt = len(parents)
            out["external_links_found"].append({"doctype": d, "open_count": 0, "count": cnt})
        else:
            d_meta = frappe.get_meta(d)
            field_to_check = None
            for f in d_meta.fields:
                if f.fieldtype == 'Link' and f.options == doctype:
                    field_to_check = f.fieldname
                    break
                    
            if not field_to_check:
                candidate = doctype.lower().replace(' ', '_')
                if d_meta.has_field(candidate):
                    field_to_check = candidate
                elif doctype == 'Item' and d_meta.has_field('item_code'):
                    field_to_check = 'item_code'
                    
            if field_to_check:
                cnt = frappe.db.count(d, filters={field_to_check: name, "docstatus": ["!=", 2]})
                out["external_links_found"].append({"doctype": d, "open_count": 0, "count": cnt})
            else:
                out["external_links_found"].append({"doctype": d, "open_count": 0, "count": 0})
    except Exception:
        out["external_links_found"].append({"doctype": d, "open_count": 0, "count": 0})

res_out = {
    "count": out
}

# PostgreSQL-safe timeline data
timeline_dict = {}
if doctype == "Item":
    try:
        sle_res = frappe.db.sql(
            '''SELECT EXTRACT(epoch FROM posting_date)::bigint, COUNT(*) FROM "tabStock Ledger Entry" WHERE item_code = %s AND posting_date > CURRENT_DATE - INTERVAL '1 year' GROUP BY posting_date''',
            (name,),
            as_dict=False
        )
        for r in (sle_res or []):
            if r[0]:
                timeline_dict[str(r[0])] = r[1]
    except Exception:
        timeline_dict = {}

res_out["timeline_data"] = timeline_dict
frappe.response['message'] = res_out
"""

res = s.put(f"{VPS_BASE}/api/resource/Server Script/VM%20Patch%20Get%20Open%20Count", json={
    'doctype': 'Server Script',
    'name': 'VM Patch Get Open Count',
    'script': notif_script,
    'script_type': 'API',
    'api_method': 'frappe.desk.notifications.get_open_count',
    'allow_guest': 0,
    'disabled': 0
})
print("Updated get_open_count Server Script:", res.status_code)
