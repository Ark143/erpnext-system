import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

# 1. Fetch all submitted Sales Invoices for Automan
sinvs = s.get(f"{VPS_BASE}/api/resource/Sales Invoice?filters=[[\"company\",\"=\",\"Automan Car Care Center\"],[\"docstatus\",\"=\",1]]&fields=[\"name\",\"customer\",\"posting_date\",\"grand_total\",\"status\",\"remarks\"]&limit_page_length=100&order_by=creation desc").json().get("data", [])

print(f"=== TOTAL SUBMITTED AUTOMAN SALES INVOICES: {len(sinvs)} ===")
recent_30 = sinvs[:30]
total_30_amt = 0.0
for idx, inv in enumerate(reversed(recent_30), 1):
    amt = float(inv.get("grand_total") or 0.0)
    total_30_amt += amt
    print(f"Tx #{idx:02d} | Invoice: {inv.get('name')} | Customer: {inv.get('customer')[:22]:22s} | Amount: PHP {amt:9.2f} | Status: {inv.get('status')}")

print(f"\nTotal Revenue for 30 Service Transactions: PHP {total_30_amt:,.2f}")

# 2. Check BIR Sales Journal for Automan
res_sj = s.post(f"{VPS_BASE}/api/resource/BIR Sales Journal", json={
    "company": "Automan Car Care Center",
    "posting_date": "2026-09-08",
    "from_date": "2026-09-01",
    "to_date": "2026-09-08"
}).json()
sj_name = res_sj.get("data", {}).get("name")
print(f"\nGenerated BIR Sales Journal for Automan: {sj_name}")

# 3. Check BIR Cash Receipt Journal for Automan
res_crj = s.post(f"{VPS_BASE}/api/resource/BIR Cash Receipt Journal", json={
    "company": "Automan Car Care Center",
    "posting_date": "2026-09-08",
    "from_date": "2026-09-01",
    "to_date": "2026-09-08"
}).json()
crj_name = res_crj.get("data", {}).get("name")
print(f"Generated BIR Cash Receipt Journal for Automan: {crj_name}")

# 4. Check BIR General Ledger for Automan
res_gl = s.post(f"{VPS_BASE}/api/resource/BIR General Ledger", json={
    "company": "Automan Car Care Center",
    "posting_date": "2026-09-08",
    "from_date": "2026-09-01",
    "to_date": "2026-09-08"
}).json()
gl_name = res_gl.get("data", {}).get("name")
print(f"Generated BIR General Ledger for Automan: {gl_name}")

# Save detailed report
report_data = {
    "company": "Automan Car Care Center",
    "total_transactions": len(recent_30),
    "total_revenue": total_30_amt,
    "transactions": recent_30,
    "bir_reports": {
        "sales_journal": sj_name,
        "cash_receipt_journal": crj_name,
        "general_ledger": gl_name
    }
}
with open("tools/automan_30_services_report.json", "w") as f:
    json.dump(report_data, f, indent=2)
print("\nSaved detailed audit report to tools/automan_30_services_report.json")
