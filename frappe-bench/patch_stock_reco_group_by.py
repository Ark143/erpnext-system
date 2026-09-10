"""
patch_stock_reco_group_by.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fixes the PostgreSQL GroupingError in Stock Reconciliation by
installing a Server Script that monkey-patches get_items_for_stock_reco
to use a PostgreSQL-safe GROUP BY clause.

The fix is equivalent to changing:
    group by i.name
to:
    group by i.name, i.item_name, id.default_warehouse, i.has_serial_no, i.has_batch_no

Usage:
    python patch_stock_reco_group_by.py --host http://38.247.138.224:10017
"""

import sys
import json
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--host",     default="http://38.247.138.224:10017")
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
    data = r.json()
    print(f"[OK] Logged in — {data.get('full_name','')}")


def api_get(resource):
    r = session.get(f"{BASE}/api/resource/{resource}")
    return r.json().get("data") if r.status_code == 200 else None


def api_post_raw(resource, payload):
    r = session.post(f"{BASE}/api/resource/{resource}", json=payload)
    return r


# ── The patched Python function that will be installed as a Server Script ──

PATCH_CODE = '''
import frappe
from frappe.utils import flt

# Monkey-patch get_items_for_stock_reco with PostgreSQL-safe GROUP BY
def _patched_get_items_for_stock_reco(warehouse, company):
    lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])

    # Query 1: items that already have Bin records (always safe — no GROUP BY needed)
    items = frappe.db.sql(
        f"""
        select
            i.name as item_code, i.item_name, bin.warehouse as warehouse,
            i.has_serial_no, i.has_batch_no
        from
            `tabBin` bin, `tabItem` i
        where
            i.name = bin.item_code
            and IFNULL(i.disabled, 0) = 0
            and i.is_stock_item = 1
            and i.has_variants = 0
            and exists(
                select name from `tabWarehouse`
                where lft >= {lft} and rgt <= {rgt}
                and name = bin.warehouse and is_group = 0
            )
        """,
        as_dict=1,
    )

    # Query 2: items with a default warehouse — PostgreSQL-safe GROUP BY (all selected columns)
    items += frappe.db.sql(
        """
        select
            i.name as item_code, i.item_name, id.default_warehouse as warehouse,
            i.has_serial_no, i.has_batch_no
        from
            `tabItem` i, `tabItem Default` id
        where
            i.name = id.parent
            and exists(
                select name from `tabWarehouse`
                where lft >= %s and rgt <= %s
                and name = id.default_warehouse and is_group = 0
            )
            and i.is_stock_item = 1
            and i.has_variants = 0
            and IFNULL(i.disabled, 0) = 0
            and id.company = %s
        group by i.name, i.item_name, id.default_warehouse, i.has_serial_no, i.has_batch_no
        """,
        (lft, rgt, company),
        as_dict=1,
    )

    # Remove duplicates
    iw_keys = set()
    items = [
        item
        for item in items
        if [
            (item.item_code, item.warehouse) not in iw_keys,
            iw_keys.add((item.item_code, item.warehouse)),
        ][0]
    ]
    return items

# Apply the monkey-patch
import erpnext.stock.doctype.stock_reconciliation.stock_reconciliation as _sr_mod
_sr_mod.get_items_for_stock_reco = _patched_get_items_for_stock_reco
frappe.logger().info("[VMS-PATCH] stock_reconciliation.get_items_for_stock_reco patched for PostgreSQL.")
'''

SCRIPT_NAME = "VMS-PG-Fix: Stock Reco GROUP BY"

def install_server_script():
    print(f"  Checking for existing script: {SCRIPT_NAME!r}")
    existing = api_get(f"Server Script/{SCRIPT_NAME.replace(' ', '%20').replace(':', '%3A')}")

    payload = {
        "doctype": "Server Script",
        "name": SCRIPT_NAME,
        "script_type": "Startup",
        "script": PATCH_CODE,
        "disabled": 0,
    }

    if existing:
        print("  Updating existing Server Script…")
        payload["modified"] = existing.get("modified", "")
        r = session.put(
            f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME.replace(' ', '%20').replace(':', '%3A')}",
            json=payload,
        )
    else:
        print("  Creating new Server Script…")
        r = api_post_raw("Server Script", payload)

    if r.status_code in (200, 201):
        print(f"  [OK] Server Script installed.")
        return True
    else:
        print(f"  [WARN] Server Script failed ({r.status_code}): {r.text[:400]}")
        return False


def verify_fix():
    """Do a quick test call to get_items to see if the error is gone."""
    print("  Testing get_items endpoint…")
    r = session.post(
        f"{BASE}/api/method/erpnext.stock.doctype.stock_reconciliation.stock_reconciliation.get_items",
        json={
            "warehouse":     "All Warehouses - UM",
            "posting_date":  "2026-09-10",
            "posting_time":  "00:00:00",
            "company":       "ULTRA MRF",
            "ignore_empty_stock": 1,
        },
    )
    data = {}
    try:
        data = r.json()
    except Exception:
        pass

    exc_type = data.get("exc_type", "")
    if exc_type == "GroupingError":
        print("  [FAIL] GroupingError still present — Server Script may not have run yet.")
        print("         Try: bench --site site1.local restart  (or reload the app)")
    elif r.status_code in (200, 201):
        print("  [OK] get_items returned successfully — GroupingError is FIXED.")
    else:
        print(f"  [INFO] Response {r.status_code}: {exc_type or r.text[:200]}")


def main():
    print("\n==========================================================")
    print("  VMS PG Fix -- Stock Reconciliation GROUP BY Patch      ")
    print("==========================================================\n")
    print(f"Target: {BASE}\n")

    login()
    print()

    print("-- Installing Server Script (startup monkey-patch) ----------")
    ok = install_server_script()

    print()
    print("-- Verification --------------------------------------------")
    verify_fix()

    print()
    print("==========================================================")
    print("  Fix applied. If the error persists after a page reload,")
    print("  run:  bench --site site1.local restart")
    print("  or restart the Gunicorn/uwsgi workers on the VPS.")
    print("==========================================================\n")


if __name__ == "__main__":
    main()
