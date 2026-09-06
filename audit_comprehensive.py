#!/usr/bin/env python3
"""
ERPNext Comprehensive Audit Script
Tests ALL modules end-to-end, web pages, server scripts, error logs
Generates Issue_Logs.md with numbered entries
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
import time
import sys
import re
import base64
from datetime import datetime

BASE_URL = "http://38.247.138.224:10017"
API_BASE = f"{BASE_URL}/api/resource"
AUTH = {"usr": "administrator", "pwd": "admin"}

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Login and get session cookie
def login():
    login_url = f"{BASE_URL}/api/method/login"
    req = urllib.request.Request(login_url, method="POST", data=json.dumps(AUTH).encode())
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "ERPNext-Audit/2.0")
    try:
        response = urllib.request.urlopen(req, timeout=30, context=ssl_context)
        # Extract cookie from response
        cookie_header = response.headers.get("Set-Cookie", "")
        # Parse sid from cookie
        sid = None
        for part in cookie_header.split(";"):
            part = part.strip()
            if part.startswith("sid="):
                sid = part.split("=", 1)[1]
                break
        if sid:
            return sid
        # Fallback: try basic auth with base64
        creds = base64.b64encode(f"{AUTH['usr']}:{AUTH['pwd']}".encode()).decode()
        return f"Basic {creds}"
    except Exception as e:
        print(f"Login failed: {e}")
        # Fallback to basic auth
        creds = base64.b64encode(f"{AUTH['usr']}:{AUTH['pwd']}".encode()).decode()
        return f"Basic {creds}"

SESSION = login()
print(f"Session obtained: {SESSION[:20]}...")

def api_call(method, endpoint, data=None, params=None):
    # URL-encode endpoint to handle spaces in doctype names
    encoded_endpoint = urllib.parse.quote(endpoint, safe="@:!/$&'()*+,;=-._~")
    url = f"{API_BASE}/{encoded_endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    if method == "GET":
        req = urllib.request.Request(url, method="GET")
    else:
        req = urllib.request.Request(url, method=method, data=json.dumps(data).encode() if data else None)
        req.add_header("Content-Type", "application/json")
    # Use session cookie
    if SESSION.startswith("Basic "):
        req.add_header("Authorization", SESSION)
    else:
        req.add_header("Cookie", f"sid={SESSION}")
    req.add_header("User-Agent", "ERPNext-Audit/2.0")
    try:
        response = urllib.request.urlopen(req, timeout=30, context=ssl_context)
        return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            return e.code, json.loads(body)
        except:
            return e.code, {"error": body[:500], "exc": str(e)[:200]}
    except Exception as e:
        return 0, {"error": str(e)[:500]}

def web_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method="GET")
    if SESSION.startswith("Basic "):
        req.add_header("Authorization", SESSION)
    else:
        req.add_header("Cookie", f"sid={SESSION}")
    req.add_header("User-Agent", "ERPNext-Audit/2.0")
    try:
        response = urllib.request.urlopen(req, timeout=15, context=ssl_context)
        return response.status, response.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200] if e.fp else ""
    except Exception as e:
        return 0, str(e)[:200]

def run_full_audit():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    issues = []  # list of dicts
    test_results = []  # list of dicts
    
    def add_issue(severity, module, title, detail="", repro="", root_cause="", fix=""):
        issues.append({
            "severity": severity,
            "module": module,
            "title": title,
            "detail": detail,
            "repro": repro,
            "root_cause": root_cause,
            "fix": fix,
        })
    
    def add_test(module, test_name, passed, detail=""):
        test_results.append({
            "module": module,
            "test": test_name,
            "passed": passed,
            "detail": detail,
        })
        return passed

    # ============================================================
    # 1. CONNECTIVITY
    # ============================================================
    print("[1] Testing connectivity...")
    status, body = api_call("GET", "Company", params={"limit_page_length": 1})
    add_test("System", "Connectivity", status == 200, f"Status: {status}")
    if status != 200:
        add_issue("CRITICAL", "System", "Cannot connect to VPS",
                  f"Status: {status}", "GET /api/resource/Company", "VPS is down or not responding", "Check Docker containers on VPS")
        return timestamp, issues, test_results

    # Get master data
    status, companies = api_call("GET", "Company", params={"limit_page_length": 100})
    companies = companies.get("data", [])
    print(f"  Companies: {len(companies)}")

    status, warehouses = api_call("GET", "Warehouse", params={"limit_page_length": 100})
    warehouses = warehouses.get("data", [])
    print(f"  Warehouses: {len(warehouses)}")

    status, customers = api_call("GET", "Customer", params={"limit_page_length": 50})
    customers = customers.get("data", [])
    print(f"  Customers: {len(customers)}")

    status, items = api_call("GET", "Item", params={"limit_page_length": 50})
    items = items.get("data", [])
    print(f"  Items: {len(items)}")

    status, suppliers = api_call("GET", "Supplier", params={"limit_page_length": 50})
    suppliers = suppliers.get("data", [])
    print(f"  Suppliers: {len(suppliers)}")

    status, employees = api_call("GET", "Employee", params={"limit_page_length": 50})
    employees = employees.get("data", [])
    print(f"  Employees: {len(employees)}")

    status, accounts = api_call("GET", "Account", params={"limit_page_length": 100})
    accounts = accounts.get("data", [])
    print(f"  Accounts: {len(accounts)}")

    # Get ULTRA MRF specific data
    ultra_mrf_wh = [w for w in warehouses if "ULTRA" in w.get("name", "").upper() or "UM" in w.get("name", "").upper()]
    ultra_mrf_accts = [a for a in accounts if "ULTRA" in a.get("name", "").upper() or "UM" in a.get("name", "").upper()]
    ultra_mrf_cust = [c for c in customers if "ULTRA" in c.get("company", "").upper() or "UM" in c.get("company", "").upper()]
    ultra_mrf_items = [i for i in items if "ULTRA" in i.get("company", "").upper() or "UM" in i.get("company", "").upper()]

    print(f"  ULTRA MRF Warehouses: {len(ultra_mrf_wh)}")
    print(f"  ULTRA MRF Accounts: {len(ultra_mrf_accts)}")
    print(f"  ULTRA MRF Customers: {len(ultra_mrf_cust)}")
    print(f"  ULTRA MRF Items: {len(ultra_mrf_items)}")

    # Pick a default company
    default_company = companies[0]["name"] if companies else "Unknown"
    print(f"  Default Company: {default_company}")

    # ============================================================
    # 2. SELLING MODULE
    # ============================================================
    print("\n[2] Testing Selling Module...")
    
    # Quotation
    status, resp = api_call("POST", "Quotation", {
        "quotation_to": "Customer",
        "customer": customers[0]["name"] if customers else "Test Customer",
        "company": default_company,
        "items": [{"item_code": items[0]["name"] if items else "Test Item", "qty": 1, "rate": 100}]
    })
    if status == 200:
        q_name = resp.get("data", {}).get("name", "")
        add_test("Selling", "Quotation Create", True, q_name)
        # Submit
        s2, r2 = api_call("POST", f"Quotation/{q_name}", {"docstatus": 1})
        add_test("Selling", "Quotation Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Selling", "Quotation submit failed", str(r2)[:300], "POST Quotation/{name} docstatus=1", "Validation error on submit", "Check server-side validation hooks")
    else:
        add_test("Selling", "Quotation Create", False, str(resp)[:300])
        add_issue("HIGH", "Selling", "Quotation creation failed", str(resp)[:300], "POST /api/resource/Quotation", "Missing mandatory fields or company mismatch", "Verify customer/item exists for company")

    # Sales Order
    so_payload = {
        "customer": customers[0]["name"] if customers else "Test Customer",
        "delivery_date": "2026-09-10",
        "company": default_company,
        "items": [{"item_code": items[0]["name"] if items else "Test Item", "qty": 1, "rate": 100}]
    }
    status, resp = api_call("POST", "Sales Order", so_payload)
    if status == 200:
        so_name = resp.get("data", {}).get("name", "")
        add_test("Selling", "Sales Order Create", True, so_name)
        s2, r2 = api_call("POST", f"Sales Order/{so_name}", {"docstatus": 1})
        add_test("Selling", "Sales Order Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            err_msg = str(r2)
            if "DatatypeMismatch" in err_msg or "CASE/WHEN" in err_msg:
                add_issue("CRITICAL", "Selling", "Sales Order submit fails — PostgreSQL DatatypeMismatch",
                          err_msg[:300], "Submit Sales Order", "PostgreSQL query uses integer in CASE WHEN instead of boolean",
                          "Patch erpnext/selling/doctype/sales_order/sales_order.py:501")
            else:
                add_issue("CRITICAL", "Selling", "Sales Order submit failed", err_msg[:300], "Submit Sales Order", "Unknown error", "Check error log for details")
    else:
        add_test("Selling", "Sales Order Create", False, str(resp)[:300])
        err_str = str(resp)
        if "MandatoryError" in err_str:
            add_issue("CRITICAL", "Selling", "Sales Order create fails — mandatory fields missing",
                      err_str[:300], "POST Sales Order", "Customer/Item not linked to company", "Link master data to correct company")
        elif "company" in err_str.lower():
            add_issue("HIGH", "Selling", "Sales Order create fails — company mismatch", err_str[:300], "POST Sales Order", "Company filter mismatch", "Use correct company for testing")
        else:
            add_issue("HIGH", "Selling", "Sales Order creation failed", err_str[:300], "POST Sales Order", "Unknown", "Investigate")

    # Sales Invoice
    inv_payload = {
        "customer": customers[0]["name"] if customers else "Test Customer",
        "due_date": "2026-09-10",
        "company": default_company,
        "items": [{"item_code": items[0]["name"] if items else "Test Item", "qty": 1, "rate": 100}]
    }
    status, resp = api_call("POST", "Sales Invoice", inv_payload)
    if status == 200:
        inv_name = resp.get("data", {}).get("name", "")
        add_test("Selling", "Sales Invoice Create", True, inv_name)
        s2, r2 = api_call("POST", f"Sales Invoice/{inv_name}", {"docstatus": 1})
        add_test("Selling", "Sales Invoice Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Selling", "Sales Invoice submit failed", str(r2)[:300], "Submit Sales Invoice", "Validation error", "Check server scripts")
    else:
        add_test("Selling", "Sales Invoice Create", False, str(resp)[:300])
        add_issue("HIGH", "Selling", "Sales Invoice creation failed", str(resp)[:300], "POST Sales Invoice", "Unknown", "Check mandatory fields")

    # Delivery Note
    dn_payload = {
        "customer": customers[0]["name"] if customers else "Test Customer",
        "company": default_company,
        "items": [{
            "item_code": items[0]["name"] if items else "Test Item",
            "qty": 1,
            "rate": 100,
            "warehouse": ultra_mrf_wh[0]["name"] if ultra_mrf_wh else "Stores - ULTRA MRF"
        }]
    }
    status, resp = api_call("POST", "Delivery Note", dn_payload)
    if status == 200:
        dn_name = resp.get("data", {}).get("name", "")
        add_test("Selling", "Delivery Note Create", True, dn_name)
        s2, r2 = api_call("POST", f"Delivery Note/{dn_name}", {"docstatus": 1})
        add_test("Selling", "Delivery Note Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Selling", "Delivery Note submit failed", str(r2)[:300], "Submit Delivery Note", "Validation error", "Check warehouse company")
    else:
        add_test("Selling", "Delivery Note Create", False, str(resp)[:300])
        if "Warehouse" in str(resp):
            add_issue("HIGH", "Selling", "Delivery Note create fails — warehouse mandatory",
                      str(resp)[:300], "POST Delivery Note", "Warehouse not set on item row", "Add warehouse to item payload")
        else:
            add_issue("HIGH", "Selling", "Delivery Note creation failed", str(resp)[:300], "POST Delivery Note", "Unknown", "Investigate")

    # ============================================================
    # 3. BUYING MODULE
    # ============================================================
    print("\n[3] Testing Buying Module...")

    # Supplier Quotation
    status, resp = api_call("POST", "Supplier Quotation", {
        "supplier": suppliers[0]["name"] if suppliers else "Test Supplier",
        "company": default_company,
        "items": [{
            "item_code": items[0]["name"] if items else "Test Item",
            "qty": 1, "rate": 100,
            "warehouse": ultra_mrf_wh[0]["name"] if ultra_mrf_wh else "Stores - ULTRA MRF",
            "schedule_date": "2026-09-10"
        }]
    })
    if status == 200:
        add_test("Buying", "Supplier Quotation Create", True, resp.get("data", {}).get("name", ""))
    else:
        add_test("Buying", "Supplier Quotation Create", False, str(resp)[:300])
        if "Warehouse" in str(resp):
            add_issue("HIGH", "Buying", "Supplier Quotation create fails — warehouse mandatory",
                      str(resp)[:300], "POST Supplier Quotation", "Warehouse not set", "Add warehouse to item row")
        else:
            add_issue("HIGH", "Buying", "Supplier Quotation creation failed", str(resp)[:300], "POST Supplier Quotation", "Unknown", "Investigate")

    # Purchase Order
    po_payload = {
        "supplier": suppliers[0]["name"] if suppliers else "Test Supplier",
        "company": default_company,
        "items": [{
            "item_code": items[0]["name"] if items else "Test Item",
            "qty": 1, "rate": 100,
            "warehouse": ultra_mrf_wh[0]["name"] if ultra_mrf_wh else "Stores - ULTRA MRF",
            "schedule_date": "2026-09-10"
        }]
    }
    status, resp = api_call("POST", "Purchase Order", po_payload)
    if status == 200:
        po_name = resp.get("data", {}).get("name", "")
        add_test("Buying", "Purchase Order Create", True, po_name)
        s2, r2 = api_call("POST", f"Purchase Order/{po_name}", {"docstatus": 1})
        add_test("Buying", "Purchase Order Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Buying", "Purchase Order submit failed", str(r2)[:300], "Submit Purchase Order", "Validation error", "Check server scripts")
    else:
        add_test("Buying", "Purchase Order Create", False, str(resp)[:300])
        if "Warehouse" in str(resp):
            add_issue("HIGH", "Buying", "Purchase Order create fails — warehouse mandatory",
                      str(resp)[:300], "POST Purchase Order", "Warehouse not set", "Add warehouse to item row")
        else:
            add_issue("HIGH", "Buying", "Purchase Order creation failed", str(resp)[:300], "POST Purchase Order", "Unknown", "Investigate")

    # Purchase Invoice
    status, resp = api_call("POST", "Purchase Invoice", {
        "supplier": suppliers[0]["name"] if suppliers else "Test Supplier",
        "due_date": "2026-09-10",
        "company": default_company,
        "items": [{
            "item_code": items[0]["name"] if items else "Test Item",
            "qty": 1, "rate": 100,
            "warehouse": ultra_mrf_wh[0]["name"] if ultra_mrf_wh else "Stores - ULTRA MRF"
        }]
    })
    if status == 200:
        pi_name = resp.get("data", {}).get("name", "")
        add_test("Buying", "Purchase Invoice Create", True, pi_name)
        s2, r2 = api_call("POST", f"Purchase Invoice/{pi_name}", {"docstatus": 1})
        add_test("Buying", "Purchase Invoice Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Buying", "Purchase Invoice submit failed", str(r2)[:300], "Submit Purchase Invoice", "Validation error", "Check server scripts")
    else:
        add_test("Buying", "Purchase Invoice Create", False, str(resp)[:300])
        add_issue("HIGH", "Buying", "Purchase Invoice creation failed", str(resp)[:300], "POST Purchase Invoice", "Unknown", "Investigate")

    # Purchase Receipt
    status, resp = api_call("POST", "Purchase Receipt", {
        "supplier": suppliers[0]["name"] if suppliers else "Test Supplier",
        "company": default_company,
        "items": [{
            "item_code": items[0]["name"] if items else "Test Item",
            "qty": 1, "rate": 100,
            "warehouse": ultra_mrf_wh[0]["name"] if ultra_mrf_wh else "Stores - ULTRA MRF"
        }]
    })
    if status == 200:
        pr_name = resp.get("data", {}).get("name", "")
        add_test("Buying", "Purchase Receipt Create", True, pr_name)
        s2, r2 = api_call("POST", f"Purchase Receipt/{pr_name}", {"docstatus": 1})
        add_test("Buying", "Purchase Receipt Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Buying", "Purchase Receipt submit failed", str(r2)[:300], "Submit Purchase Receipt", "Validation error", "Check server scripts")
    else:
        add_test("Buying", "Purchase Receipt Create", False, str(resp)[:300])
        if "Warehouse" in str(resp):
            add_issue("HIGH", "Buying", "Purchase Receipt create fails — warehouse mandatory",
                      str(resp)[:300], "POST Purchase Receipt", "Warehouse not set", "Add warehouse to item row")
        else:
            add_issue("HIGH", "Buying", "Purchase Receipt creation failed", str(resp)[:300], "POST Purchase Receipt", "Unknown", "Investigate")

    # ============================================================
    # 4. STOCK MODULE
    # ============================================================
    print("\n[4] Testing Stock Module...")

    wh_name = ultra_mrf_wh[0]["name"] if ultra_mrf_wh else "Stores - ULTRA MRF"

    # Material Receipt
    status, resp = api_call("POST", "Stock Entry", {
        "stock_entry_type": "Material Receipt",
        "company": default_company,
        "items": [{"item_code": items[0]["name"] if items else "Test Item", "qty": 10, "t_warehouse": wh_name, "rate": 100}]
    })
    if status == 200:
        se_name = resp.get("data", {}).get("name", "")
        add_test("Stock", "Stock Entry (Receipt) Create", True, se_name)
        s2, r2 = api_call("POST", f"Stock Entry/{se_name}", {"docstatus": 1})
        add_test("Stock", "Stock Entry (Receipt) Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            err_str = str(r2)
            if "InvalidWarehouseCompany" in err_str:
                add_issue("CRITICAL", "Stock", "Material Receipt submit fails — warehouse company mismatch",
                          err_str[:300], "Submit Stock Entry", "Warehouse belongs to different company", "Use warehouse from correct company")
            else:
                add_issue("CRITICAL", "Stock", "Material Receipt submit failed", err_str[:300], "Submit Stock Entry", "Unknown", "Check error log")
    else:
        add_test("Stock", "Stock Entry (Receipt) Create", False, str(resp)[:300])
        add_issue("HIGH", "Stock", "Stock Entry (Receipt) creation failed", str(resp)[:300], "POST Stock Entry", "Unknown", "Investigate")

    # Material Issue
    status, resp = api_call("POST", "Stock Entry", {
        "stock_entry_type": "Material Issue",
        "company": default_company,
        "items": [{"item_code": items[0]["name"] if items else "Test Item", "qty": 1, "s_warehouse": wh_name}]
    })
    if status == 200:
        se_name = resp.get("data", {}).get("name", "")
        add_test("Stock", "Stock Entry (Issue) Create", True, se_name)
        s2, r2 = api_call("POST", f"Stock Entry/{se_name}", {"docstatus": 1})
        add_test("Stock", "Stock Entry (Issue) Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            err_str = str(r2)
            if "SAFETY CHECK" in err_str or "safety" in err_str.lower():
                add_issue("CRITICAL", "Stock", "Material Issue submit blocked by VM Stock Entry Safety Check Server Script",
                          err_str[:300], "Submit Stock Entry (Issue)", "Server Script 'VM Stock Entry Safety Check' blocks submit without QR badge",
                          "Add API bypass flag or disable Server Script for API context")
            else:
                add_issue("CRITICAL", "Stock", "Material Issue submit failed", err_str[:300], "Submit Stock Entry (Issue)", "Unknown", "Check error log")
    else:
        add_test("Stock", "Stock Entry (Issue) Create", False, str(resp)[:300])
        add_issue("HIGH", "Stock", "Stock Entry (Issue) creation failed", str(resp)[:300], "POST Stock Entry", "Unknown", "Investigate")

    # Material Transfer
    wh2 = ultra_mrf_wh[1]["name"] if len(ultra_mrf_wh) > 1 else wh_name
    status, resp = api_call("POST", "Stock Entry", {
        "stock_entry_type": "Material Transfer",
        "company": default_company,
        "items": [{"item_code": items[0]["name"] if items else "Test Item", "qty": 1, "s_warehouse": wh_name, "t_warehouse": wh2}]
    })
    if status == 200:
        se_name = resp.get("data", {}).get("name", "")
        add_test("Stock", "Stock Entry (Transfer) Create", True, se_name)
        s2, r2 = api_call("POST", f"Stock Entry/{se_name}", {"docstatus": 1})
        add_test("Stock", "Stock Entry (Transfer) Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("CRITICAL", "Stock", "Material Transfer submit failed", str(r2)[:300], "Submit Stock Entry (Transfer)", "Unknown", "Check error log")
    else:
        add_test("Stock", "Stock Entry (Transfer) Create", False, str(resp)[:300])
        add_issue("HIGH", "Stock", "Stock Entry (Transfer) creation failed", str(resp)[:300], "POST Stock Entry", "Unknown", "Investigate")

    # ============================================================
    # 5. ACCOUNTS MODULE
    # ============================================================
    print("\n[5] Testing Accounts Module...")

    # Payment Entry (Receive)
    status, resp = api_call("POST", "Payment Entry", {
        "payment_type": "Receive",
        "party_type": "Customer",
        "party": customers[0]["name"] if customers else "Test Customer",
        "paid_amount": 100,
        "received_amount": 100,
        "company": default_company
    })
    if status == 200:
        pe_name = resp.get("data", {}).get("name", "")
        add_test("Accounts", "Payment Entry (Receive) Create", True, pe_name)
        s2, r2 = api_call("POST", f"Payment Entry/{pe_name}", {"docstatus": 1})
        add_test("Accounts", "Payment Entry (Receive) Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            err_str = str(r2)
            if "does not belong to Company" in err_str:
                add_issue("CRITICAL", "Accounts", "Payment Entry submit fails — account company mismatch",
                          err_str[:300], "Submit Payment Entry", "Account belongs to different company", "Use accounts from correct company")
            else:
                add_issue("CRITICAL", "Accounts", "Payment Entry (Receive) submit failed", err_str[:300], "Submit Payment Entry", "Unknown", "Check error log")
    else:
        add_test("Accounts", "Payment Entry (Receive) Create", False, str(resp)[:300])
        add_issue("HIGH", "Accounts", "Payment Entry (Receive) creation failed", str(resp)[:300], "POST Payment Entry", "Unknown", "Investigate")

    # Payment Entry (Pay)
    status, resp = api_call("POST", "Payment Entry", {
        "payment_type": "Pay",
        "party_type": "Supplier",
        "party": suppliers[0]["name"] if suppliers else "Test Supplier",
        "paid_amount": 100,
        "received_amount": 100,
        "source_exchange_rate": 1,
        "company": default_company
    })
    if status == 200:
        pe_name = resp.get("data", {}).get("name", "")
        add_test("Accounts", "Payment Entry (Pay) Create", True, pe_name)
        s2, r2 = api_call("POST", f"Payment Entry/{pe_name}", {"docstatus": 1})
        add_test("Accounts", "Payment Entry (Pay) Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Accounts", "Payment Entry (Pay) submit failed", str(r2)[:300], "Submit Payment Entry", "Unknown", "Check error log")
    else:
        add_test("Accounts", "Payment Entry (Pay) Create", False, str(resp)[:300])
        if "Source Exchange Rate" in str(resp):
            add_issue("MEDIUM", "Accounts", "Payment Entry (Pay) needs source_exchange_rate",
                      str(resp)[:300], "POST Payment Entry", "Missing source_exchange_rate field", "Add source_exchange_rate: 1 to payload")
        else:
            add_issue("HIGH", "Accounts", "Payment Entry (Pay) creation failed", str(resp)[:300], "POST Payment Entry", "Unknown", "Investigate")

    # Journal Entry
    status, resp = api_call("POST", "Journal Entry", {
        "posting_date": "2026-09-06",
        "company": default_company,
        "accounts": [
            {"account": ultra_mrf_accts[0]["name"] if ultra_mrf_accts else "Cash - ULTRA MRF", "debit_in_account_currency": 100},
            {"account": ultra_mrf_accts[1]["name"] if len(ultra_mrf_accts) > 1 else "Cash - ULTRA MRF", "credit_in_account_currency": 100}
        ]
    })
    if status == 200:
        jv_name = resp.get("data", {}).get("name", "")
        add_test("Accounts", "Journal Entry Create", True, jv_name)
        s2, r2 = api_call("POST", f"Journal Entry/{jv_name}", {"docstatus": 1})
        add_test("Accounts", "Journal Entry Submit", s2 == 200, str(r2.get("exception", r2.get("error", "")))[:200])
        if s2 != 200:
            add_issue("HIGH", "Accounts", "Journal Entry submit failed", str(r2)[:300], "Submit Journal Entry", "Unknown", "Check error log")
    else:
        add_test("Accounts", "Journal Entry Create", False, str(resp)[:300])
        if "posting_date" in str(resp):
            add_issue("MEDIUM", "Accounts", "Journal Entry needs posting_date",
                      str(resp)[:300], "POST Journal Entry", "Missing posting_date field", "Add posting_date to payload")
        else:
            add_issue("HIGH", "Accounts", "Journal Entry creation failed", str(resp)[:300], "POST Journal Entry", "Unknown", "Investigate")

    # ============================================================
    # 6. HR MODULE
    # ============================================================
    print("\n[6] Testing HR Module...")

    # Employee list
    status, resp = api_call("GET", "Employee", params={"limit_page_length": 5})
    add_test("HR", "Employee List", status == 200, f"{len(resp.get('data', []))} records")
    if status != 200:
        add_issue("HIGH", "HR", "Employee list failed", str(resp)[:300], "GET Employee", "Unknown", "Check module access")

    # Check payroll doctypes
    payroll_doctypes = ["Salary Structure", "Salary Slip", "Expense Claim", "Leave Application", "Attendance", "Payroll Entry"]
    for dt in payroll_doctypes:
        status, resp = api_call("GET", dt, params={"limit_page_length": 1})
        if status == 200:
            add_test("HR", f"{dt} Accessible", True)
        else:
            add_test("HR", f"{dt} Accessible", False, str(resp)[:200])
            add_issue("HIGH", "HR", f"{dt} DocType does NOT EXIST",
                      str(resp)[:200], f"GET {dt}", "Payroll module (HRMS) not installed",
                      "Install HRMS module via bench")

    # ============================================================
    # 7. MANUFACTURING MODULE
    # ============================================================
    print("\n[7] Testing Manufacturing Module...")

    for dt in ["BOM", "Work Order", "Job Card", "Operation", "Routing"]:
        status, resp = api_call("GET", dt, params={"limit_page_length": 5})
        if status == 200:
            count = len(resp.get("data", []))
            add_test("Manufacturing", f"{dt} List", True, f"{count} records")
            if count == 0 and dt in ["BOM", "Work Order"]:
                add_issue("MEDIUM", "Manufacturing", f"No {dt}s exist",
                          f"Count: 0", f"GET {dt}", "No master data seeded",
                          f"Create at least 1 {dt} via Manufacturing module")
        else:
            add_test("Manufacturing", f"{dt} List", False, str(resp)[:200])
            add_issue("HIGH", "Manufacturing", f"{dt} list failed", str(resp)[:300], f"GET {dt}", "Unknown", "Check module access")

    # ============================================================
    # 8. VEHICLE MANAGEMENT MODULE (Custom App)
    # ============================================================
    print("\n[8] Testing Vehicle Management Module...")

    vm_doctypes = ["Vehicle Job Order", "Customer Vehicle", "Vehicle Service Item"]
    for dt in vm_doctypes:
        status, resp = api_call("GET", dt, params={"limit_page_length": 5})
        if status == 200:
            add_test("Vehicle Mgmt", f"{dt} List", True, f"{len(resp.get('data', []))} records")
        else:
            add_test("Vehicle Mgmt", f"{dt} List", False, str(resp)[:200])
            add_issue("MEDIUM", "Vehicle Mgmt", f"{dt} not accessible",
                      str(resp)[:200], f"GET {dt}", "DocType may not exist or app not deployed",
                      "Verify vehicle_management app is deployed")

    # Test Vehicle Management APIs
    vm_apis = [
        ("/api/method/vehicle_management.api.get_analytics", "Vehicle Analytics API"),
        ("/api/method/vehicle_management.api.get_executive_dashboard", "Executive Dashboard API"),
        ("/api/method/vehicle_management.api.get_pos_meta", "POS Meta API"),
    ]
    for api_path, api_name in vm_apis:
        url = f"{BASE_URL}{api_path}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Basic {json.dumps(AUTH).encode().decode()}")
        req.add_header("User-Agent", "ERPNext-Audit/2.0")
        try:
            response = urllib.request.urlopen(req, timeout=15, context=ssl_context)
            add_test("Vehicle Mgmt", api_name, True, f"Status: {response.status}")
        except urllib.error.HTTPError as e:
            add_test("Vehicle Mgmt", api_name, False, f"Status: {e.code}")
            if e.code == 404:
                add_issue("CRITICAL", "Vehicle Mgmt", f"{api_name} returns 404",
                          f"Status: {e.code}", f"GET {api_path}", "vehicle_management.api module not deployed",
                          "Deploy vehicle_management app from local repo to VPS")
            else:
                add_issue("HIGH", "Vehicle Mgmt", f"{api_name} failed",
                          f"Status: {e.code}", f"GET {api_path}", "Unknown", "Check error log")
        except Exception as e:
            add_test("Vehicle Mgmt", api_name, False, str(e)[:200])
            add_issue("HIGH", "Vehicle Mgmt", f"{api_name} unreachable",
                      str(e)[:200], f"GET {api_path}", "Connection error", "Check VPS status")

    # ============================================================
    # 9. WEB PAGES / ROUTES
    # ============================================================
    print("\n[9] Testing Web Pages...")

    pages = [
        ("/", "Home"),
        ("/desk", "Desk"),
        ("/login", "Login"),
        ("/pos", "POS"),
        ("/pos-terminal", "POS Terminal"),
        ("/executive", "Executive Dashboard"),
        ("/assets/vehicle_management/js/pos.js", "Vehicle POS JS"),
        ("/assets/erpnext/js/erpnext-web.js", "ERPNext Web JS"),
    ]
    for path, name in pages:
        status, body = web_get(path)
        if status == 200:
            add_test("Web Pages", name, True, f"{path} → 200")
        elif status == 404:
            add_test("Web Pages", name, False, f"{path} → 404")
            if "assets" in path:
                add_issue("MEDIUM", "Web Pages", f"{name} returns 404",
                          f"Path: {path}", f"GET {path}", "Static assets not built/deployed",
                          "Run bench build to deploy JS/CSS assets")
            else:
                add_issue("HIGH", "Web Pages", f"{name} returns 404",
                          f"Path: {path}", f"GET {path}", "Web Page route not defined",
                          f"Create Web Page with route '{path}'")
        else:
            add_test("Web Pages", name, False, f"{path} → {status}")
            add_issue("MEDIUM", "Web Pages", f"{name} returns {status}",
                      f"Path: {path}", f"GET {path}", "Unexpected status", "Check web server config")

    # ============================================================
    # 10. SERVER SCRIPTS
    # ============================================================
    print("\n[10] Testing Server Scripts...")

    status, resp = api_call("GET", "Server Script", params={"limit_page_length": 100})
    if status == 200:
        scripts = resp.get("data", [])
        add_test("Server Scripts", "List", True, f"{len(scripts)} scripts")
        active_scripts = [s for s in scripts if not s.get("disabled", 0)]
        print(f"  Total: {len(scripts)}, Active: {len(active_scripts)}")
        
        # Check for VM Stock Entry Safety Check
        safety_scripts = [s for s in scripts if "safety" in s.get("name", "").lower() or "VM" in s.get("name", "") or "vehicle" in s.get("name", "").lower()]
        if safety_scripts:
            for s in safety_scripts:
                add_issue("HIGH", "Server Scripts", f"Active Server Script: {s['name']}",
                          f"Script: {s['name']}, Disabled: {s.get('disabled', 0)}",
                          f"Server Script '{s['name']}' is active",
                          "May block transactions (e.g., Material Issue requires QR badge)",
                          "Review if script should have API bypass")
    else:
        add_test("Server Scripts", "List", False, str(resp)[:200])
        add_issue("MEDIUM", "Server Scripts", "Cannot list Server Scripts",
                  str(resp)[:200], "GET Server Script", "Unknown", "Check permissions")

    # ============================================================
    # 11. ERROR LOG
    # ============================================================
    print("\n[11] Checking Error Log...")

    status, resp = api_call("GET", "Error Log", params={
        "limit_page_length": 10,
        "fields": '["name","method","error","creation"]'
    })
    if status == 200:
        errors = resp.get("data", [])
        add_test("Error Log", "List", True, f"{len(errors)} recent errors")
        for err in errors[:5]:
            method = err.get("method", "unknown")
            error_text = err.get("error", "")[:150]
            if "LIMIT" in error_text and "syntax" in error_text:
                add_issue("CRITICAL", "System", "PostgreSQL LIMIT syntax error in search",
                          error_text, method, "PostgreSQL LIMIT #,# syntax not supported",
                          "Patch search query builder for PostgreSQL")
            elif "DatatypeMismatch" in error_text:
                add_issue("CRITICAL", "System", "PostgreSQL DatatypeMismatch error",
                          error_text, method, "Integer used in CASE WHEN instead of boolean",
                          "Cast to boolean in SQL query")
            else:
                add_issue("LOW", "System", f"Error: {method}", error_text, method, "Various", "Review error log")
    else:
        add_test("Error Log", "List", False, str(resp)[:200])
        add_issue("MEDIUM", "System", "Cannot read Error Log",
                  str(resp)[:200], "GET Error Log", "Unknown", "Check permissions")

    # ============================================================
    # 12. CROSS-CUTTING ISSUES
    # ============================================================
    print("\n[12] Checking cross-cutting issues...")

    # Company mismatch
    if len(ultra_mrf_cust) == 0 and len(customers) > 0:
        add_issue("CRITICAL", "Cross-Cutting", "Company mismatch: No customers linked to ULTRA MRF",
                  f"Total customers: {len(customers)}, ULTRA MRF customers: {len(ultra_mrf_cust)}",
                  "Check customer company field", "Default company is ULTRA MRF but master data belongs to MC",
                  "Link existing customers/items to ULTRA MRF or change default company")

    if len(ultra_mrf_items) == 0 and len(items) > 0:
        add_issue("CRITICAL", "Cross-Cutting", "Company mismatch: No items linked to ULTRA MRF",
                  f"Total items: {len(items)}, ULTRA MRF items: {len(ultra_mrf_items)}",
                  "Check item company field", "Default company is ULTRA MRF but items belong to MC",
                  "Link existing items to ULTRA MRF or change default company")

    # Missing modules
    status, resp = api_call("GET", "Salary Structure", params={"limit_page_length": 1})
    if status != 200:
        add_issue("MEDIUM", "Cross-Cutting", "Payroll (HRMS) module not installed",
                  str(resp)[:200], "GET Salary Structure", "HRMS module not installed",
                  "Install HRMS via bench: bench --site site1.local install-app hrms")

    # Missing manufacturing data
    status, resp = api_call("GET", "BOM", params={"limit_page_length": 1})
    if status == 200 and len(resp.get("data", [])) == 0:
        add_issue("MEDIUM", "Cross-Cutting", "No BOMs exist — Manufacturing cannot function",
                  "BOM count: 0", "GET BOM", "No manufacturing master data seeded",
                  "Create at least 1 BOM for an item")

    # Vehicle Management API missing
    status, resp = api_call("GET", "Vehicle Job Order", params={"limit_page_length": 1})
    if status == 200:
        # DocType exists, check if API module exists
        url = f"{BASE_URL}/api/method/vehicle_management.api.get_analytics"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Basic {json.dumps(AUTH).encode().decode()}")
        req.add_header("User-Agent", "ERPNext-Audit/2.0")
        try:
            response = urllib.request.urlopen(req, timeout=10, context=ssl_context)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                add_issue("CRITICAL", "Cross-Cutting", "vehicle_management.api Python module not deployed",
                          "API returns 404", "GET /api/method/vehicle_management.api.get_analytics",
                          "Python module vehicle_management/api.py missing from VPS deployment",
                          "Deploy vehicle_management app from local repo to VPS")

    return timestamp, issues, test_results


def generate_issue_logs(timestamp, issues, test_results):
    """Generate Issue_Logs.md content"""
    
    # Count by severity
    critical = len([i for i in issues if i["severity"] == "CRITICAL"])
    high = len([i for i in issues if i["severity"] == "HIGH"])
    medium = len([i for i in issues if i["severity"] == "MEDIUM"])
    low = len([i for i in issues if i["severity"] == "LOW"])
    
    # Count test results
    passed = len([t for t in test_results if t["passed"]])
    failed = len([t for t in test_results if not t["passed"]])
    total = len(test_results)
    
    # Group issues by module
    modules = {}
    for issue in issues:
        mod = issue["module"]
        if mod not in modules:
            modules[mod] = []
        modules[mod].append(issue)
    
    # Build markdown
    md = f"""# Issue Logs — ERPNext System Audit

> **Audit Date:** {timestamp} (Malay Peninsula Standard Time, UTC+08:00)
> **Auditor:** Hermes Agent (automated cron sweep)
> **Target:** VPS `38.247.138.224:10017` (ULTRA MRF demo site)
> **Role:** Test / Debug / Audit ONLY — no fixes applied
> **Format:** Each issue has ID | Severity | Status | Module | Description | Repro | Root Cause | Suggested Fix

---

## EXECUTIVE SUMMARY

| Metric | Count |
|--------|-------|
| Total Issues | {len(issues)} |
| CRITICAL | {critical} |
| HIGH | {high} |
| MEDIUM | {medium} |
| LOW | {low} |
| Tests Run | {total} |
| Tests Passed | {passed} |
| Tests Failed | {failed} |
| Pass Rate | {passed/total*100:.1f}% |

---

## ISSUE DETAILS (Numbered)

"""
    
    # Number all issues
    numbered_issues = []
    for i, issue in enumerate(issues, 1):
        issue["id"] = f"ISS-{i:03d}"
        numbered_issues.append(issue)
    
    # Sort by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    numbered_issues.sort(key=lambda x: severity_order.get(x["severity"], 99))
    
    for issue in numbered_issues:
        md += f"""### {issue['id']} [{issue['severity']}] — {issue['module']}

| Field | Value |
|-------|-------|
| **Title** | {issue['title']} |
| **Detail** | {issue['detail'][:300]} |
| **Repro** | {issue['repro']} |
| **Root Cause** | {issue['root_cause']} |
| **Suggested Fix** | {issue['fix']} |
| **Status** | OPEN |

"""
    
    # Module summaries
    md += """---

## MODULE SUMMARIES

"""
    for mod, mod_issues in sorted(modules.items()):
        mod_critical = len([i for i in mod_issues if i["severity"] == "CRITICAL"])
        mod_high = len([i for i in mod_issues if i["severity"] == "HIGH"])
        mod_medium = len([i for i in mod_issues if i["severity"] == "MEDIUM"])
        mod_low = len([i for i in mod_issues if i["severity"] == "LOW"])
        md += f"""### {mod}

| Severity | Count |
|----------|-------|
| CRITICAL | {mod_critical} |
| HIGH | {mod_high} |
| MEDIUM | {mod_medium} |
| LOW | {mod_low} |

"""
        for issue in mod_issues:
            md += f"- **{issue['id']}** [{issue['severity']}] {issue['title']}\n"
        md += "\n"
    
    # Test results
    md += """---

## TEST RESULTS

| Module | Test | Result | Detail |
|--------|------|--------|--------|
"""
    for t in test_results:
        result = "✅ PASS" if t["passed"] else "❌ FAIL"
        md += f"| {t['module']} | {t['test']} | {result} | {t['detail'][:100]} |\n"
    
    # Priority matrix
    md += """

---

## ISSUE PRIORITY MATRIX

### Immediate (breaks core workflow)
"""
    immediate = [i for i in numbered_issues if i["severity"] == "CRITICAL"]
    for i, issue in enumerate(immediate, 1):
        md += f"{i}. **{issue['id']}** — {issue['title']}\n"

    md += "\n### High (blocks module functionality)\n"
    high_issues = [i for i in numbered_issues if i["severity"] == "HIGH"]
    for i, issue in enumerate(high_issues, 1):
        md += f"{i}. **{issue['id']}** — {issue['title']}\n"

    md += "\n### Medium (missing configuration / minor bugs)\n"
    med_issues = [i for i in numbered_issues if i["severity"] == "MEDIUM"]
    for i, issue in enumerate(med_issues, 1):
        md += f"{i}. **{issue['id']}** — {issue['title']}\n"

    md += "\n### Low (cosmetic / known)\n"
    low_issues = [i for i in numbered_issues if i["severity"] == "LOW"]
    for i, issue in enumerate(low_issues, 1):
        md += f"{i}. **{issue['id']}** — {issue['title']}\n"

    md += f"""

---

## RECOMMENDED ACTIONS

1. Fix all CRITICAL issues first (PostgreSQL compatibility, company mismatch, missing modules)
2. Address HIGH issues (warehouse mandatory fields, missing DocTypes)
3. Resolve MEDIUM issues (missing master data, static assets)
4. LOW issues can be addressed in maintenance windows

---

*This file is auto-generated by the hourly audit cron job. Do not edit manually — it will be overwritten.*
*Last updated: {timestamp}*
"""
    
    return md


if __name__ == "__main__":
    print("=" * 70)
    print("ERPNext Comprehensive Audit")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 70)
    
    timestamp, issues, test_results = run_full_audit()
    
    # Generate Issue Logs
    md_content = generate_issue_logs(timestamp, issues, test_results)
    
    # Save to file
    output_path = "C:/Users/josem/erpnext-system/Issue_Logs.md"
    with open(output_path, "w") as f:
        f.write(md_content)
    
    # Also save raw results as JSON
    json_path = "C:/Users/josem/erpnext-system/audit_results.json"
    with open(json_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "issues": issues,
            "test_results": test_results,
            "summary": {
                "total_issues": len(issues),
                "critical": len([i for i in issues if i["severity"] == "CRITICAL"]),
                "high": len([i for i in issues if i["severity"] == "HIGH"]),
                "medium": len([i for i in issues if i["severity"] == "MEDIUM"]),
                "low": len([i for i in issues if i["severity"] == "LOW"]),
                "tests_total": len(test_results),
                "tests_passed": len([t for t in test_results if t["passed"]]),
                "tests_failed": len([t for t in test_results if not t["passed"]]),
            }
        }, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print(f"Total Issues: {len(issues)}")
    print(f"  CRITICAL: {len([i for i in issues if i['severity'] == 'CRITICAL'])}")
    print(f"  HIGH: {len([i for i in issues if i['severity'] == 'HIGH'])}")
    print(f"  MEDIUM: {len([i for i in issues if i['severity'] == 'MEDIUM'])}")
    print(f"  LOW: {len([i for i in issues if i['severity'] == 'LOW'])}")
    print(f"Tests: {len(test_results)} run, {len([t for t in test_results if t['passed']])} passed, {len([t for t in test_results if not t['passed']])} failed")
    print(f"Issue Logs saved to: {output_path}")
    print(f"Raw results saved to: {json_path}")
    print("=" * 70)
