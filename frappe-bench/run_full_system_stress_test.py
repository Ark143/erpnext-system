import sys, os, time, random
from datetime import datetime, timedelta

sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')

import frappe
from frappe.utils import nowdate, flt, cint, getdate, add_days

frappe.init('site1.local')
frappe.connect()

print("=" * 75, flush=True)
print("  AUTOMOTIVE ERP ENTERPRISE PERFORMANCE BENCHMARK & LOAD ENGINE", flush=True)
print("=" * 75, flush=True)

# Fetch master pools
customers = frappe.get_all('Customer', fields=['name', 'customer_name'])
suppliers = frappe.get_all('Supplier', fields=['name', 'supplier_name'])
items = frappe.get_all('Item', filters={'disabled': 0}, fields=['name', 'item_name', 'item_group', 'stock_uom', 'is_sales_item', 'is_purchase_item', 'is_stock_item'])
sales_items = [it for it in items if it.get('is_sales_item')] or items[:50]
purchase_items = [it for it in items if it.get('is_purchase_item')] or items[:50]
vehicles = frappe.get_all('Customer Vehicle', fields=['name', 'plate_no', 'make', 'model', 'customer']) if frappe.db.table_exists('Customer Vehicle') else []

companies = [c['name'] for c in frappe.get_all('Company', filters={'name': ['!=', 'My Company']})]

print(f"Master Pools loaded:", flush=True)
print(f"  - Customers:         {len(customers):,}", flush=True)
print(f"  - Suppliers:         {len(suppliers):,}", flush=True)
print(f"  - Sales Items:       {len(sales_items):,}", flush=True)
print(f"  - Purchase Items:    {len(purchase_items):,}", flush=True)
print(f"  - Customer Vehicles: {len(vehicles):,}", flush=True)
print(f"  - Companies:         {len(companies)}", flush=True)
print("=" * 75, flush=True)

bench_stats = {
    "sales_invoices": {"count": 0, "total_time": 0.0, "total_value": 0.0},
    "payment_received": {"count": 0, "total_time": 0.0, "total_value": 0.0},
    "purchase_invoices": {"count": 0, "total_time": 0.0, "total_value": 0.0},
    "payment_paid": {"count": 0, "total_time": 0.0, "total_value": 0.0},
    "job_orders": {"count": 0, "total_time": 0.0, "total_value": 0.0},
    "inspections": {"count": 0, "total_time": 0.0, "total_value": 0.0},
}

TARGET_PER_COMPANY = 100  # 100 transactions per company per module

start_all = time.time()

for comp_idx, comp in enumerate(companies, 1):
    print(f"\n[{comp_idx:02d}/{len(companies):02d}] Processing 100 Transactions per module for: {comp}", flush=True)
    
    # Retrieve company defaults
    abbr = frappe.db.get_value('Company', comp, 'abbr')
    income_acc = frappe.db.get_value('Company', comp, 'default_income_account') or f"Sales - {abbr}"
    expense_acc = frappe.db.get_value('Company', comp, 'default_expense_account') or f"Cost of Goods Sold - {abbr}"
    recv_acc = frappe.db.get_value('Company', comp, 'default_receivable_account') or f"Debtors - {abbr}"
    pay_acc = frappe.db.get_value('Company', comp, 'default_payable_account') or f"Creditors - {abbr}"
    cash_acc = frappe.db.get_value('Company', comp, 'default_cash_account') or f"Cash - {abbr}"
    cost_center = frappe.db.get_value('Company', comp, 'cost_center') or f"Main - {abbr}"
    
    # -------------------------------------------------------------
    # 1. SALES INVOICES & PAYMENTS RECEIVED (100 per company)
    # -------------------------------------------------------------
    print(f"  [1/3] Sales & Accounts Receivable: 100 Invoices + 100 Customer Payments...", end="", flush=True)
    si_t0 = time.time()
    comp_si_created = 0
    comp_pay_rcv_created = 0
    
    for i in range(TARGET_PER_COMPANY):
        cust = random.choice(customers)
        sel_items = random.sample(sales_items, k=random.randint(1, 2))
        posting_date = add_days(nowdate(), -random.randint(0, 27))
        due_date = add_days(posting_date, 15)
        
        try:
            t_doc0 = time.time()
            si = frappe.get_doc({
                "doctype": "Sales Invoice",
                "company": comp,
                "customer": cust['name'],
                "posting_date": posting_date,
                "due_date": due_date,
                "currency": "PHP",
                "debit_to": recv_acc,
                "cost_center": cost_center,
                "update_stock": 0,
                "items": [
                    {
                        "item_code": it['name'],
                        "qty": random.randint(1, 4),
                        "rate": random.choice([450.0, 850.0, 1200.0, 2800.0, 3500.0, 4800.0]),
                        "income_account": income_acc,
                        "cost_center": cost_center
                    }
                    for it in sel_items
                ]
            })
            si.insert(ignore_permissions=True)
            si.submit()
            t_doc_end = time.time()
            
            comp_si_created += 1
            bench_stats["sales_invoices"]["count"] += 1
            bench_stats["sales_invoices"]["total_value"] += flt(si.grand_total)
            bench_stats["sales_invoices"]["total_time"] += (t_doc_end - t_doc0)
            
            # Payment Entry (Receive)
            t_pe0 = time.time()
            pe = frappe.get_doc({
                "doctype": "Payment Entry",
                "payment_type": "Receive",
                "party_type": "Customer",
                "party": cust['name'],
                "company": comp,
                "posting_date": posting_date,
                "paid_from": recv_acc,
                "paid_to": cash_acc,
                "paid_amount": si.grand_total,
                "received_amount": si.grand_total,
                "target_exchange_rate": 1.0,
                "references": [
                    {
                        "reference_doctype": "Sales Invoice",
                        "reference_name": si.name,
                        "total_amount": si.grand_total,
                        "outstanding_amount": si.grand_total,
                        "allocated_amount": si.grand_total
                    }
                ]
            })
            pe.insert(ignore_permissions=True)
            pe.submit()
            t_pe_end = time.time()
            
            comp_pay_rcv_created += 1
            bench_stats["payment_received"]["count"] += 1
            bench_stats["payment_received"]["total_value"] += flt(si.grand_total)
            bench_stats["payment_received"]["total_time"] += (t_pe_end - t_pe0)
            
            if (i + 1) % 25 == 0:
                frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            continue
            
    frappe.db.commit()
    print(f" Done ({comp_si_created} SI, {comp_pay_rcv_created} PE in {time.time() - si_t0:.2f}s)", flush=True)

    # -------------------------------------------------------------
    # 2. PURCHASE INVOICES & PAYMENTS PAID (100 per company)
    # -------------------------------------------------------------
    print(f"  [2/3] Procurement & Accounts Payable: 100 Bills + 100 Supplier Payments...", end="", flush=True)
    pi_t0 = time.time()
    comp_pi_created = 0
    comp_pay_paid_created = 0
    
    for i in range(TARGET_PER_COMPANY):
        supp = random.choice(suppliers)
        sel_items = random.sample(purchase_items, k=random.randint(1, 2))
        posting_date = add_days(nowdate(), -random.randint(0, 27))
        due_date = add_days(posting_date, 15)
        
        try:
            t_pi0 = time.time()
            pi = frappe.get_doc({
                "doctype": "Purchase Invoice",
                "company": comp,
                "supplier": supp['name'],
                "posting_date": posting_date,
                "due_date": due_date,
                "currency": "PHP",
                "credit_to": pay_acc,
                "cost_center": cost_center,
                "items": [
                    {
                        "item_code": it['name'],
                        "qty": random.randint(2, 8),
                        "rate": random.choice([350.0, 650.0, 950.0, 1800.0, 2400.0]),
                        "expense_account": expense_acc,
                        "cost_center": cost_center
                    }
                    for it in sel_items
                ]
            })
            pi.insert(ignore_permissions=True)
            pi.submit()
            t_pi_end = time.time()
            
            comp_pi_created += 1
            bench_stats["purchase_invoices"]["count"] += 1
            bench_stats["purchase_invoices"]["total_value"] += flt(pi.grand_total)
            bench_stats["purchase_invoices"]["total_time"] += (t_pi_end - t_pi0)
            
            # Payment Entry (Pay to Supplier)
            t_pe0 = time.time()
            pe_paid = frappe.get_doc({
                "doctype": "Payment Entry",
                "payment_type": "Pay",
                "party_type": "Supplier",
                "party": supp['name'],
                "company": comp,
                "posting_date": posting_date,
                "paid_from": cash_acc,
                "paid_to": pay_acc,
                "paid_amount": pi.grand_total,
                "received_amount": pi.grand_total,
                "target_exchange_rate": 1.0,
                "references": [
                    {
                        "reference_doctype": "Purchase Invoice",
                        "reference_name": pi.name,
                        "total_amount": pi.grand_total,
                        "outstanding_amount": pi.grand_total,
                        "allocated_amount": pi.grand_total
                    }
                ]
            })
            pe_paid.insert(ignore_permissions=True)
            pe_paid.submit()
            t_pe_end = time.time()
            
            comp_pay_paid_created += 1
            bench_stats["payment_paid"]["count"] += 1
            bench_stats["payment_paid"]["total_value"] += flt(pi.grand_total)
            bench_stats["payment_paid"]["total_time"] += (t_pe_end - t_pe0)
            
            if (i + 1) % 25 == 0:
                frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            continue
            
    frappe.db.commit()
    print(f" Done ({comp_pi_created} PI, {comp_pay_paid_created} PE in {time.time() - pi_t0:.2f}s)", flush=True)

    # -------------------------------------------------------------
    # 3. VEHICLE JOB ORDERS & INSPECTIONS (100 per company)
    # -------------------------------------------------------------
    if frappe.db.table_exists("Vehicle Job Order"):
        print(f"  [3/3] Vehicle Operations: 100 Job Orders + 100 Inspections...", end="", flush=True)
        jo_t0 = time.time()
        comp_jo_created = 0
        comp_insp_created = 0
        
        for i in range(TARGET_PER_COMPANY):
            cust = random.choice(customers)
            veh = random.choice(vehicles) if vehicles else None
            
            try:
                t_jo0 = time.time()
                jo = frappe.get_doc({
                    "doctype": "Vehicle Job Order",
                    "company": comp,
                    "customer": cust['name'],
                    "vehicle": veh['name'] if veh else None,
                    "plate_no": veh.get('plate_no') if veh else None,
                    "service_type": random.choice(["Periodic Maintenance (PMS)", "Brake Service & Overhaul", "Tire Replacement & Balancing", "Engine Diagnostic & Tuning", "Suspension & Underchassis"]),
                    "status": random.choice(["In Progress", "Completed", "Pending Parts"]),
                    "cost_center": cost_center,
                    "creation": add_days(nowdate(), -random.randint(0, 20)),
                    "tasks": [
                        {
                            "task_name": "Multi-point Automotive Health Check",
                            "status": "Completed",
                            "labor_cost": random.choice([600.0, 1200.0, 1800.0, 2500.0])
                        }
                    ],
                    "parts": [
                        {
                            "item_code": random.choice(sales_items)['name'],
                            "qty": random.randint(1, 4),
                            "rate": random.choice([450.0, 850.0, 1600.0, 2800.0]),
                            "uom": "PC"
                        }
                    ]
                })
                jo.insert(ignore_permissions=True)
                t_jo_end = time.time()
                
                comp_jo_created += 1
                bench_stats["job_orders"]["count"] += 1
                bench_stats["job_orders"]["total_time"] += (t_jo_end - t_jo0)
                
                # Inspection
                if frappe.db.table_exists("Vehicle Inspection"):
                    t_in0 = time.time()
                    insp = frappe.get_doc({
                        "doctype": "Vehicle Inspection",
                        "company": comp,
                        "customer": cust['name'],
                        "vehicle": veh['name'] if veh else None,
                        "job_order": jo.name,
                        "inspection_type": "Pre-Service Intake Inspection",
                        "status": "Passed"
                    })
                    insp.insert(ignore_permissions=True)
                    t_in_end = time.time()
                    
                    comp_insp_created += 1
                    bench_stats["inspections"]["count"] += 1
                    bench_stats["inspections"]["total_time"] += (t_in_end - t_in0)
                    
                if (i + 1) % 25 == 0:
                    frappe.db.commit()
            except Exception:
                frappe.db.rollback()
                continue
                
        frappe.db.commit()
        print(f" Done ({comp_jo_created} JO, {comp_insp_created} Insp in {time.time() - jo_t0:.2f}s)", flush=True)

total_elapsed = time.time() - start_all
total_transactions = sum(s["count"] for s in bench_stats.values())
tps = (total_transactions / total_elapsed) if total_elapsed > 0 else 0

print("\n" + "=" * 75, flush=True)
print("  ENTERPRISE STRESS TEST & PERFORMANCE BENCHMARK RESULTS", flush=True)
print("=" * 75, flush=True)
print(f"Total Transactions Processed & Committed: {total_transactions:,}", flush=True)
print(f"Total Elapsed Execution Time:            {total_elapsed:.2f} seconds ({total_elapsed/60.0:.2f} mins)", flush=True)
print(f"Average Throughput Rate:                 {tps:.2f} transactions/sec", flush=True)
print("-" * 75, flush=True)
print(f"{'Module / Transaction Type':35s} | {'Count':8s} | {'Total Value (PHP)':18s} | {'Avg Latency (ms)':16s}", flush=True)
print("-" * 75, flush=True)

for k, v in bench_stats.items():
    cnt = v["count"]
    val_str = f"PHP {v['total_value']:,.2f}" if v['total_value'] > 0 else "—"
    avg_ms = (v["total_time"] / cnt * 1000.0) if cnt > 0 else 0.0
    lbl = k.replace("_", " ").title()
    print(f"{lbl:35s} | {cnt:8,d} | {val_str:18s} | {avg_ms:14.2f} ms", flush=True)

print("=" * 75, flush=True)

# Verify updated ledger counts
gl_count = frappe.db.count('GL Entry')
si_count = frappe.db.count('Sales Invoice')
pi_count = frappe.db.count('Purchase Invoice')
pe_count = frappe.db.count('Payment Entry')
jo_count = frappe.db.count('Vehicle Job Order') if frappe.db.table_exists('Vehicle Job Order') else 0
vi_count = frappe.db.count('Vehicle Inspection') if frappe.db.table_exists('Vehicle Inspection') else 0

print("\nUpdated Live System Ledger Counters:", flush=True)
print(f"  - General Ledger (GL) Entries: {gl_count:,}", flush=True)
print(f"  - Sales Invoices:              {si_count:,}", flush=True)
print(f"  - Purchase Invoices:           {pi_count:,}", flush=True)
print(f"  - Payment Entries (Pay/Recv):  {pe_count:,}", flush=True)
print(f"  - Vehicle Job Orders:          {jo_count:,}", flush=True)
print(f"  - Vehicle Inspections:         {vi_count:,}", flush=True)
print("=" * 75, flush=True)
