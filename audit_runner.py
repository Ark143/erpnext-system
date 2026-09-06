#!/usr/bin/env python3
"""
ERPNext System Audit Script
Tests all modules end-to-end on VPS http://38.247.138.224:10017
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
import time
import sys
from datetime import datetime

# Disable SSL verification for testing
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

BASE_URL = "http://38.247.138.224:10017"
API_BASE = f"{BASE_URL}/api/resource"

# Test credentials
AUTH = {"usr": "administrator", "pwd": "admin"}

def api_call(method, endpoint, data=None, params=None):
    """Make API call to ERPNext"""
    url = f"{API_BASE}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    if method == "GET":
        req = urllib.request.Request(url, method="GET")
    else:
        req = urllib.request.Request(url, method=method, data=json.dumps(data).encode() if data else None)
        req.add_header("Content-Type", "application/json")
    
    # Add auth
    auth_data = json.dumps(AUTH).encode()
    req.add_header("Authorization", f"Basic {auth_data.decode()}")
    req.add_header("User-Agent", "ERPNext-Audit/1.0")
    
    try:
        response = urllib.request.urlopen(req, timeout=30, context=ssl_context)
        return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            return e.code, json.loads(body)
        except:
            return e.code, {"error": body[:500]}
    except Exception as e:
        return 0, {"error": str(e)[:500]}

def get_list(doctype, fields=None, limit=5):
    """Get list of documents"""
    params = {"limit_page_length": limit}
    if fields:
        params["fields"] = json.dumps(fields)
    return api_call("GET", doctype, params=params)

def create_doc(doctype, data):
    """Create a new document"""
    return api_call("POST", doctype, data=data)

def submit_doc(doctype, name):
    """Submit a document"""
    return api_call("POST", f"{doctype}/{name}", data={"docstatus": 1})

def run_audit():
    """Run full audit"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "target": BASE_URL,
        "modules": {},
        "issues": [],
        "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0}
    }
    
    def add_issue(severity, module, issue, detail=""):
        results["issues"].append({
            "id": f"ISS-{results['summary']['total']+1:03d}",
            "severity": severity,
            "module": module,
            "issue": issue,
            "detail": detail
        })
        results["summary"]["total"] += 1
        if severity in ["CRITICAL", "HIGH"]:
            results["summary"]["failed"] += 1
        elif severity == "MEDIUM":
            results["summary"]["warnings"] += 1
        else:
            results["summary"]["passed"] += 1
    
    # Test 1: Connectivity
    print("Testing connectivity...")
    status, body = api_call("GET", "Company", params={"limit_page_length": 1})
    if status == 200:
        print(f"  ✓ Connected ({status})")
    else:
        add_issue("CRITICAL", "System", "Cannot connect to VPS", f"Status: {status}")
        return results
    
    # Test 2: Selling Module
    print("\nTesting Selling Module...")
    selling = {"tests": []}
    
    # Quotation
    status, resp = create_doc("Quotation", {
        "quotation_to": "Customer",
        "customer": "Test Customer",
        "items": [{"item_code": "Test Item", "qty": 1, "rate": 100}]
    })
    selling["tests"].append({"name": "Quotation Create", "status": status, "response": resp})
    if status == 200:
        print("  ✓ Quotation created")
    else:
        add_issue("HIGH", "Selling", "Quotation creation failed", str(resp))
    
    # Sales Order
    status, resp = create_doc("Sales Order", {
        "customer": "Test Customer",
        "delivery_date": "2026-09-10",
        "items": [{"item_code": "Test Item", "qty": 1, "rate": 100}]
    })
    selling["tests"].append({"name": "Sales Order Create", "status": status, "response": resp})
    if status == 200:
        so_name = resp.get("data", {}).get("name", "")
        print(f"  ✓ Sales Order created: {so_name}")
        # Try submit
        status2, resp2 = submit_doc("Sales Order", so_name)
        selling["tests"].append({"name": "Sales Order Submit", "status": status2, "response": resp2})
        if status2 == 200:
            print(f"  ✓ Sales Order submitted")
        else:
            add_issue("CRITICAL", "Selling", "Sales Order submit failed", str(resp2))
    else:
        add_issue("HIGH", "Selling", "Sales Order creation failed", str(resp))
    
    # Sales Invoice
    status, resp = create_doc("Sales Invoice", {
        "customer": "Test Customer",
        "due_date": "2026-09-10",
        "items": [{"item_code": "Test Item", "qty": 1, "rate": 100}]
    })
    selling["tests"].append({"name": "Sales Invoice Create", "status": status, "response": resp})
    if status == 200:
        inv_name = resp.get("data", {}).get("name", "")
        status2, resp2 = submit_doc("Sales Invoice", inv_name)
        if status2 == 200:
            print(f"  ✓ Sales Invoice created + submitted")
        else:
            add_issue("HIGH", "Selling", "Sales Invoice submit failed", str(resp2))
    else:
        add_issue("HIGH", "Selling", "Sales Invoice creation failed", str(resp))
    
    results["modules"]["selling"] = selling
    
    # Test 3: Buying Module
    print("\nTesting Buying Module...")
    buying = {"tests": []}
    
    status, resp = create_doc("Purchase Order", {
        "supplier": "Test Supplier",
        "items": [{"item_code": "Test Item", "qty": 1, "rate": 100, "schedule_date": "2026-09-10"}]
    })
    buying["tests"].append({"name": "Purchase Order Create", "status": status, "response": resp})
    if status == 200:
        po_name = resp.get("data", {}).get("name", "")
        status2, resp2 = submit_doc("Purchase Order", po_name)
        if status2 == 200:
            print(f"  ✓ Purchase Order created + submitted")
        else:
            add_issue("HIGH", "Buying", "Purchase Order submit failed", str(resp2))
    else:
        add_issue("HIGH", "Buying", "Purchase Order creation failed", str(resp))
    
    results["modules"]["buying"] = buying
    
    # Test 4: Stock Module
    print("\nTesting Stock Module...")
    stock = {"tests": []}
    
    status, resp = create_doc("Stock Entry", {
        "stock_entry_type": "Material Receipt",
        "items": [{
            "item_code": "Test Item",
            "qty": 10,
            "t_warehouse": "Stores - ULTRA MRF",
            "rate": 100
        }]
    })
    stock["tests"].append({"name": "Stock Entry (Receipt) Create", "status": status, "response": resp})
    if status == 200:
        se_name = resp.get("data", {}).get("name", "")
        status2, resp2 = submit_doc("Stock Entry", se_name)
        if status2 == 200:
            print(f"  ✓ Stock Entry (Receipt) created + submitted")
        else:
            add_issue("CRITICAL", "Stock", "Stock Entry (Receipt) submit failed", str(resp2))
    else:
        add_issue("HIGH", "Stock", "Stock Entry creation failed", str(resp))
    
    # Material Issue
    status, resp = create_doc("Stock Entry", {
        "stock_entry_type": "Material Issue",
        "items": [{
            "item_code": "Test Item",
            "qty": 1,
            "s_warehouse": "Stores - ULTRA MRF"
        }]
    })
    stock["tests"].append({"name": "Stock Entry (Issue) Create", "status": status, "response": resp})
    if status == 200:
        se_name = resp.get("data", {}).get("name", "")
        status2, resp2 = submit_doc("Stock Entry", se_name)
        if status2 == 200:
            print(f"  ✓ Stock Entry (Issue) created + submitted")
        else:
            add_issue("CRITICAL", "Stock", "Stock Entry (Issue) submit failed", str(resp2))
    else:
        add_issue("HIGH", "Stock", "Stock Entry (Issue) creation failed", str(resp))
    
    results["modules"]["stock"] = stock
    
    # Test 5: Accounts Module
    print("\nTesting Accounts Module...")
    accounts = {"tests": []}
    
    status, resp = create_doc("Payment Entry", {
        "payment_type": "Receive",
        "party_type": "Customer",
        "party": "Test Customer",
        "paid_amount": 100,
        "received_amount": 100
    })
    accounts["tests"].append({"name": "Payment Entry Create", "status": status, "response": resp})
    if status == 200:
        pe_name = resp.get("data", {}).get("name", "")
        status2, resp2 = submit_doc("Payment Entry", pe_name)
        if status2 == 200:
            print(f"  ✓ Payment Entry created + submitted")
        else:
            add_issue("HIGH", "Accounts", "Payment Entry submit failed", str(resp2))
    else:
        add_issue("HIGH", "Accounts", "Payment Entry creation failed", str(resp))
    
    results["modules"]["accounts"] = accounts
    
    # Test 6: HR Module
    print("\nTesting HR Module...")
    hr = {"tests": []}
    
    status, resp = get_list("Employee", limit=5)
    hr["tests"].append({"name": "Employee List", "status": status, "response": resp})
    if status == 200:
        print(f"  ✓ Employee list retrieved")
    else:
        add_issue("HIGH", "HR", "Employee list failed", str(resp))
    
    # Check payroll doctypes
    for dt in ["Salary Structure", "Salary Slip", "Expense Claim", "Leave Application", "Attendance"]:
        status, resp = get_list(dt, limit=1)
        hr["tests"].append({"name": f"{dt} List", "status": status, "response": resp})
        if status == 200:
            print(f"  ✓ {dt} accessible")
        else:
            add_issue("HIGH", "HR", f"{dt} not accessible", str(resp)[:200])
    
    results["modules"]["hr"] = hr
    
    # Test 7: Manufacturing Module
    print("\nTesting Manufacturing Module...")
    mfg = {"tests": []}
    
    for dt in ["BOM", "Work Order", "Job Card", "Operation"]:
        status, resp = get_list(dt, limit=5)
        mfg["tests"].append({"name": f"{dt} List", "status": status, "response": resp})
        if status == 200:
            count = len(resp.get("data", []))
            print(f"  ✓ {dt} list: {count} records")
            if count == 0 and dt in ["BOM", "Work Order"]:
                add_issue("MEDIUM", "Manufacturing", f"No {dt}s exist", "Manufacturing cannot function without master data")
        else:
            add_issue("HIGH", "Manufacturing", f"{dt} list failed", str(resp))
    
    results["modules"]["manufacturing"] = mfg
    
    # Test 8: Vehicle Management Module
    print("\nTesting Vehicle Management Module...")
    vm = {"tests": []}
    
    for dt in ["Vehicle Job Order", "Customer Vehicle"]:
        status, resp = get_list(dt, limit=5)
        vm["tests"].append({"name": f"{dt} List", "status": status, "response": resp})
        if status == 200:
            print(f"  ✓ {dt} accessible")
        else:
            add_issue("MEDIUM", "Vehicle Management", f"{dt} not accessible", str(resp)[:200])
    
    results["modules"]["vehicle_management"] = vm
    
    # Test 9: Web Pages
    print("\nTesting Web Pages...")
    web = {"tests": []}
    
    pages = ["/", "/desk", "/login", "/pos", "/pos-terminal", "/executive"]
    for page in pages:
        url = f"{BASE_URL}{page}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "ERPNext-Audit/1.0")
        try:
            response = urllib.request.urlopen(req, timeout=15, context=ssl_context)
            web["tests"].append({"page": page, "status": response.status})
            print(f"  ✓ {page} → {response.status}")
        except urllib.error.HTTPError as e:
            web["tests"].append({"page": page, "status": e.code})
            if e.code == 404:
                add_issue("MEDIUM", "Web Pages", f"{page} returns 404", "Page not found")
            else:
                print(f"  ⚠ {page} → {e.code}")
        except Exception as e:
            web["tests"].append({"page": page, "status": 0, "error": str(e)})
            add_issue("HIGH", "Web Pages", f"{page} unreachable", str(e)[:200])
    
    results["modules"]["web_pages"] = web
    
    # Test 10: System Health
    print("\nTesting System Health...")
    system = {"tests": []}
    
    # Check error log
    status, resp = api_call("GET", "Error Log", params={"limit_page_length": 5, "fields": '["name","method","error","creation"]'})
    system["tests"].append({"name": "Error Log", "status": status, "response": resp})
    if status == 200:
        errors = resp.get("data", [])
        print(f"  ✓ Error Log: {len(errors)} recent errors")
        for err in errors[:3]:
            add_issue("LOW", "System", f"Error: {err.get('method', 'unknown')}", err.get('error', '')[:100])
    else:
        add_issue("MEDIUM", "System", "Cannot read Error Log", str(resp))
    
    results["modules"]["system"] = system
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("ERPNext System Audit")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = run_audit()
    
    # Save results
    output_path = "/c/Users/josem/erpnext-system/audit_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print(f"Total Issues: {results['summary']['total']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Warnings: {results['summary']['warnings']}")
    print(f"Results saved to: {output_path}")
    print("=" * 60)
