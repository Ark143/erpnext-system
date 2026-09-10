"""
install_inventory_count_sheet.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installs the Inventory Count Sheet + Inventory Count Sheet Item
doctypes into the live ERPNext site via the Frappe REST API.

Also adds the shortcut to the Vehicle Management workspace so it
shows up in the sidebar.

Usage:
    cd c:/Users/josem/erpnext-system/frappe-bench
    python install_inventory_count_sheet.py [--site site1.local]
                                            [--host http://localhost:8000]
                                            [--user Administrator]
                                            [--password admin]
"""

import sys
import json
import argparse
import requests

# ── CLI args ────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--site",     default="site1.local")
parser.add_argument("--host",     default="http://localhost:8000")
parser.add_argument("--user",     default="Administrator")
parser.add_argument("--password", default="admin")
args = parser.parse_args()

BASE  = args.host
LOGIN = {"usr": args.user, "pwd": args.password}

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})


def login():
    r = session.post(f"{BASE}/api/method/login", json=LOGIN)
    r.raise_for_status()
    print(f"[OK] Logged in as {args.user}")


def api_post(method, **kwargs):
    r = session.post(f"{BASE}/api/method/{method}", json=kwargs)
    try:
        data = r.json()
    except Exception:
        data = {}
    if r.status_code not in (200, 201):
        print(f"  [FAIL] {method} -> {r.status_code}: {r.text[:200]}")
        return None
    return data.get("message") or data


def upsert_doctype(doctype_name, doctype_def):
    """Create or update a DocType via Frappe API."""
    print(f"  -> Installing DocType: {doctype_name}")
    existing = session.get(
        f"{BASE}/api/resource/DocType/{doctype_name.replace(' ', '%20')}"
    )
    method = "frappe.client.save"
    payload = dict(doc=json.dumps(doctype_def))

    if existing.status_code == 200:
        # Update
        r = session.post(f"{BASE}/api/method/{method}", json={"doc": json.dumps(doctype_def)})
    else:
        # Insert
        r = session.post(
            f"{BASE}/api/resource/DocType",
            json=doctype_def,
        )

    if r.status_code in (200, 201):
        print(f"    [OK] {doctype_name} installed.")
    else:
        print(f"    [FAIL] ({r.status_code}): {r.text[:300]}")


def run_migrate():
    print("  -> Running bench migrate (reload doctypes)...")
    result = api_post("frappe.reload_doctype", doctype="Inventory Count Sheet")
    result2 = api_post("frappe.reload_doctype", doctype="Inventory Count Sheet Item")
    print("    [OK] Migrate complete.")


def add_workspace_shortcut():
    """Add 'Inventory Count Sheet' shortcut to the Vehicle Management workspace."""
    print("  -> Adding workspace shortcut...")
    ws_name = "Vehicle Management"
    r = session.get(f"{BASE}/api/resource/Workspace/{ws_name.replace(' ', '%20')}")
    if r.status_code != 200:
        print(f"    [FAIL] Workspace '{ws_name}' not found - skipping shortcut.")
        return

    ws = r.json().get("data", {})
    shortcuts = ws.get("shortcuts", [])

    # Avoid duplicate
    if any(s.get("label") == "Inventory Count Sheet" for s in shortcuts):
        print("    [OK] Shortcut already exists.")
        return

    shortcuts.append({
        "doctype": "Workspace Shortcut",
        "type":    "DocType",
        "label":   "Inventory Count Sheet",
        "link_to": "Inventory Count Sheet",
        "icon":    "stock",
        "color":   "Orange",
    })
    ws["shortcuts"] = shortcuts

    put = session.put(
        f"{BASE}/api/resource/Workspace/{ws_name.replace(' ', '%20')}",
        json=ws,
    )
    if put.status_code in (200, 201):
        print("    [OK] Workspace shortcut added.")
    else:
        print(f"    [FAIL] Could not update workspace ({put.status_code}): {put.text[:200]}")


# ── DOCTYPE DEFINITIONS ─────────────────────────────────────────────

CHILD_DT = {
    "doctype": "DocType",
    "name": "Inventory Count Sheet Item",
    "module": "Vehicle Management",
    "custom": 0,
    "istable": 1,
    "editable_grid": 1,
    "engine": "InnoDB",
    "fields": [
        {"fieldname":"item_code",    "fieldtype":"Link",    "options":"Item",  "label":"Item Code","reqd":1,"in_list_view":1,"columns":3},
        {"fieldname":"item_name",    "fieldtype":"Data",    "label":"Item Name","fetch_from":"item_code.item_name","read_only":1,"in_list_view":1,"columns":3},
        {"fieldname":"bin_location", "fieldtype":"Data",    "label":"Bin / Location","in_list_view":1,"columns":1},
        {"fieldname":"uom",          "fieldtype":"Link",    "options":"UOM","label":"UOM","fetch_from":"item_code.stock_uom","in_list_view":1,"columns":1},
        {"fieldname":"system_qty",   "fieldtype":"Float",   "label":"System Qty","read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"physical_qty", "fieldtype":"Float",   "label":"Physical Count","in_list_view":1,"columns":1},
        {"fieldname":"variance_qty", "fieldtype":"Float",   "label":"Variance","read_only":1,"in_list_view":1,"columns":1},
        {"fieldname":"count_status", "fieldtype":"Select",  "options":"Pending\nMatched\nOver\nShort\nNew Item","default":"Pending","label":"Status","read_only":1,"in_list_view":1,"columns":1},
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
        {"fieldname":"naming_series","fieldtype":"Select","options":"IC-.YYYY.-.#####","default":"IC-.YYYY.-.#####","label":"Series"},
        {"fieldname":"company",      "fieldtype":"Link",  "options":"Company","label":"Company / Branch","reqd":1,"in_list_view":1,"in_standard_filter":1},
        {"fieldname":"warehouse",    "fieldtype":"Link",  "options":"Warehouse","label":"Warehouse","reqd":1,"in_list_view":1,"in_standard_filter":1},
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


# ── MAIN ────────────────────────────────────────────────────────────

def main():
    print("\n==========================================================")
    print("   VMS -- Inventory Count Sheet Installer               ")
    print("==========================================================\n")


    print(f"Target: {BASE} | Site: {args.site}\n")

    login()
    print()
    print("-- Installing DocTypes -------------------------------------")
    upsert_doctype("Inventory Count Sheet Item", CHILD_DT)
    upsert_doctype("Inventory Count Sheet",      PARENT_DT)

    print()
    print("-- Post-install --------------------------------------------")
    run_migrate()
    add_workspace_shortcut()

    print("[OK] Installation complete.")
    print("  Open ERPNext -> Vehicle Management -> Inventory Count Sheet")
    print()


if __name__ == "__main__":
    main()
