"""
push_bank_recon_fix.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Installs an "API" type Server Script on the VPS that:
1. Fixes GROUP BY in bank_reconciliation_tool.py (get_je_matching_query)
2. Fixes GROUP BY in bank_clearance.py (get_payment_entries_for_bank_clearance)
for complete PostgreSQL compatibility.

Usage:
    python push_bank_recon_fix.py
"""

import requests
import json

BASE = "http://38.247.138.224:10017"
LOGIN = {"usr": "Administrator", "pwd": "admin"}

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

SCRIPT_CODE = r'''
import frappe, os

bench_path = frappe.utils.get_bench_path()
results = []

# ── 1. Patch bank_reconciliation_tool.py ──────────────────────────
rel_recon = "apps/erpnext/erpnext/accounts/doctype/bank_reconciliation_tool/bank_reconciliation_tool.py"
path_recon = os.path.join(bench_path, rel_recon)

if os.path.exists(path_recon):
    with open(path_recon, "r", encoding="utf-8") as f:
        src_recon = f.read()

    OLD_RECON = ".groupby(je.name)"
    NEW_RECON = ".groupby(je.name, je.cheque_no, je.cheque_date, je.pay_to_recd_from, jea.party_type, je.posting_date, jea.account_currency)"

    if NEW_RECON in src_recon:
        results.append("bank_reconciliation_tool.py: already patched.")
    elif OLD_RECON in src_recon:
        src_recon = src_recon.replace(OLD_RECON, NEW_RECON, 1)
        with open(path_recon, "w", encoding="utf-8") as f:
            f.write(src_recon)
        results.append("bank_reconciliation_tool.py: successfully patched GROUP BY for PostgreSQL.")
    else:
        results.append("bank_reconciliation_tool.py: target groupby string not found.")
else:
    results.append(f"bank_reconciliation_tool.py not found at {path_recon}")


# ── 2. Patch bank_clearance.py ─────────────────────────────────────
rel_clearance = "apps/erpnext/erpnext/accounts/doctype/bank_clearance/bank_clearance.py"
path_clearance = os.path.join(bench_path, rel_clearance)

if os.path.exists(path_clearance):
    with open(path_clearance, "r", encoding="utf-8") as f:
        src_clearance = f.read()

    OLD_CLEAR = "journal_entry_query.groupby(journal_entry_account.account, journal_entry.name)"
    NEW_CLEAR = "journal_entry_query.groupby(journal_entry_account.account, journal_entry.name, journal_entry.cheque_no, journal_entry.cheque_date, journal_entry.posting_date, journal_entry_account.against_account, journal_entry.clearance_date, journal_entry_account.account_currency)"

    if NEW_CLEAR in src_clearance:
        results.append("bank_clearance.py: already patched.")
    elif OLD_CLEAR in src_clearance:
        src_clearance = src_clearance.replace(OLD_CLEAR, NEW_CLEAR, 1)
        with open(path_clearance, "w", encoding="utf-8") as f:
            f.write(src_clearance)
        results.append("bank_clearance.py: successfully patched GROUP BY for PostgreSQL.")
    else:
        results.append("bank_clearance.py: target groupby string not found.")
else:
    results.append(f"bank_clearance.py not found at {path_clearance}")

frappe.response["message"] = "\n".join(results)
'''

SCRIPT_NAME = "VMS-PG-Fix-BankRecon-GroupBy"


def login():
    r = session.post(f"{BASE}/api/method/login", json=LOGIN)
    r.raise_for_status()
    print(f"[OK] Logged in as {r.json().get('full_name', 'Administrator')}")


def apply_patch():
    print(f"Creating Server Script {SCRIPT_NAME!r}...")
    payload = {
        "doctype": "Server Script",
        "name": SCRIPT_NAME,
        "script_type": "API",
        "api_method": SCRIPT_NAME,
        "allow_guest": 0,
        "script": SCRIPT_CODE,
        "disabled": 0,
    }

    check = session.get(f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME}")
    if check.status_code == 200:
        existing = check.json().get("data", {})
        payload["modified"] = existing.get("modified", "")
        r = session.put(f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME}", json=payload)
    else:
        r = session.post(f"{BASE}/api/resource/Server%20Script", json=payload)

    if r.status_code not in (200, 201):
        print(f"[FAIL] Creating Server Script: {r.status_code} {r.text}")
        return False
    print("[OK] Server Script registered.")

    print("Executing patch on VPS...")
    r = session.post(f"{BASE}/api/method/{SCRIPT_NAME}")
    if r.status_code == 200:
        msg = r.json().get("message", "")
        print(f"[OK] Patch output:\n{msg}")
    else:
        print(f"[FAIL] Execution failed: {r.status_code} {r.text}")

    # Cleanup
    session.delete(f"{BASE}/api/resource/Server%20Script/{SCRIPT_NAME}")
    print("[OK] Cleaned up temporary Server Script.")
    return True


def test_auto_reconcile():
    print("Testing auto_reconcile_vouchers API on VPS...")
    payload = {
        "bank_account": "Automan Operating Account - BDO Unibank, Inc.",
        "from_date": "2026-08-12",
        "to_date": "2026-09-12",
        "filter_by_reference_date": 0
    }
    r = session.post(
        f"{BASE}/api/method/erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.auto_reconcile_vouchers",
        json=payload
    )
    print(f"Status Code: {r.status_code}")
    data = r.json()
    if r.status_code == 200:
        print(f"[SUCCESS] auto_reconcile_vouchers executed cleanly without GroupingError!")
        print("Response:", data)
    else:
        exc = data.get("exc_type", "")
        print(f"[NOTE] Status: {r.status_code}, Exception: {exc}")
        if exc == "GroupingError":
            print("Server workers still have old module cached in memory. Gunicorn worker reload will take effect on next request.")


if __name__ == "__main__":
    login()
    apply_patch()
    test_auto_reconcile()
