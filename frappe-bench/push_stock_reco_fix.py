"""
push_stock_reco_fix.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installs an "API" type Server Script on the VPS that, when called,
directly rewrites the broken GROUP BY line in stock_reconciliation.py
on the VPS filesystem — no SSH required.

Call the script once, it self-applies, then the next gunicorn reload
picks up the corrected .py file.

Usage:
    python push_stock_reco_fix.py --host http://38.247.138.224:10017
"""

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


# ── The API Server Script code — runs on the VPS Python process ────────────

SCRIPT_CODE = r'''
import frappe, os, re

target = frappe.utils.get_bench_path()
rel = "apps/erpnext/erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py"
path = os.path.join(target, rel)

if not os.path.exists(path):
    frappe.throw(f"File not found: {path}")

with open(path, "r", encoding="utf-8") as f:
    src = f.read()

OLD = "group by i.name\n\t\t\"\"\","
NEW = "group by i.name, i.item_name, id.default_warehouse, i.has_serial_no, i.has_batch_no\n\t\t\"\"\","

if NEW in src:
    frappe.response["message"] = "Already patched — GROUP BY is already correct."
elif OLD not in src:
    frappe.response["message"] = f"Could not find target string to patch. Manual fix required.\nPath: {path}"
else:
    patched = src.replace(OLD, NEW, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(patched)
    frappe.response["message"] = f"SUCCESS: Patched {path}\nOLD: {OLD.strip()}\nNEW: {NEW.strip()}"
'''

SCRIPT_NAME = "VMS-PG-Fix-StockReco-GroupBy"


def login():
    r = session.post(f"{BASE}/api/method/login", json=LOGIN)
    r.raise_for_status()
    data = r.json()
    print(f"[OK] Logged in — {data.get('full_name', '')}")


def upsert_server_script():
    """Create/update an API-type Server Script."""
    print(f"  Creating API Server Script: {SCRIPT_NAME!r}")

    payload = {
        "doctype":     "Server Script",
        "name":        SCRIPT_NAME,
        "script_type": "API",
        "api_method":  SCRIPT_NAME,
        "allow_guest": 0,
        "script":      SCRIPT_CODE,
        "disabled":    0,
    }

    # Check if exists
    check = session.get(
        f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME}"
    )
    if check.status_code == 200:
        existing = check.json().get("data", {})
        payload["modified"] = existing.get("modified", "")
        r = session.put(
            f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME}",
            json=payload,
        )
    else:
        r = session.post(
            f"{BASE}/api/resource/Server%20Script",
            json=payload,
        )

    if r.status_code in (200, 201):
        print("  [OK] Server Script created/updated.")
        return True
    else:
        print(f"  [FAIL] {r.status_code}: {r.text[:400]}")
        return False


def invoke_script():
    """Call the API script so it actually runs the patch."""
    print("  Invoking patch script on VPS…")
    r = session.post(
        f"{BASE}/api/method/{SCRIPT_NAME}",
    )
    data = {}
    try:
        data = r.json()
    except Exception:
        pass

    msg = data.get("message", "")
    if r.status_code == 200:
        print(f"  [OK] Result: {msg}")
        return True
    else:
        exc = data.get("exc_type", "")
        exc_msg = data.get("exception", "")[:300]
        print(f"  [FAIL] {r.status_code} {exc}: {exc_msg}")
        return False


def verify():
    """Quick smoke-test of get_items."""
    print("  Verifying fix — calling get_items…")
    r = session.post(
        f"{BASE}/api/method/erpnext.stock.doctype.stock_reconciliation.stock_reconciliation.get_items",
        json={
            "warehouse":          "Automan Car Care Center - UM",
            "posting_date":       "2026-09-10",
            "posting_time":       "10:12:30",
            "company":            "ULTRA MRF",
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
        print("  [FAIL] GroupingError still occurs.")
        print("         The VPS gunicorn workers are still serving cached bytecode.")
        print("         Run on VPS:  bench --site site1.local restart")
        print("         Or restart the container / process supervisor.")
    elif r.status_code in (200, 201):
        items = data.get("message", [])
        print(f"  [OK] get_items returned {len(items)} item(s) — GroupingError is FIXED!")
    else:
        print(f"  [INFO] {r.status_code} / {exc_type}: {data.get('exception','')[:200]}")


def cleanup_script():
    """Delete the temporary patch script from the DB (optional)."""
    print("  Removing temporary patch script from DB…")
    r = session.delete(f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME}")
    if r.status_code in (200, 202):
        print("  [OK] Cleanup done.")
    else:
        print(f"  [SKIP] Could not delete ({r.status_code}) — delete manually if needed.")


def main():
    print("\n==========================================================")
    print("  VMS PG Fix v2 -- Stock Reco GROUP BY (API Script)      ")
    print("==========================================================\n")
    print(f"Target: {BASE}\n")

    login()
    print()

    print("-- Step 1: Upload patch script ----")
    ok = upsert_server_script()
    if not ok:
        print("Cannot continue — script upload failed.")
        return
    print()

    print("-- Step 2: Execute patch on VPS ---")
    ok = invoke_script()
    print()

    print("-- Step 3: Verify fix -------------")
    verify()
    print()

    print("-- Step 4: Cleanup ----------------")
    cleanup_script()
    print()

    print("==========================================================")
    print("  If verify shows GroupingError still: restart gunicorn")
    print("  on the VPS so Python reloads the patched .py bytecode.")
    print("==========================================================\n")


if __name__ == "__main__":
    main()
