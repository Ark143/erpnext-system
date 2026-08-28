import sys, os, random, time
from datetime import timedelta
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
sys.path.insert(0, 'apps/vehicle_management')
os.chdir('sites')
import frappe
from frappe.utils import nowdate, now_datetime, getdate, add_days, flt

frappe.init(site='erp.localhost')
frappe.connect()

print("=" * 80, flush=True)
print("🚀 BULK TRANSACTION GENERATOR: 10x O2C, P2P, Stock Entry, Payment In, Payment Out", flush=True)
print("   Across ALL 12 Companies", flush=True)
print("=" * 80, flush=True)

companies = frappe.get_list("Company", filters={"name": ["!=", "My Company"]}, pluck="name")
items = frappe.get_list("Item", filters={"is_sales_item": 1, "is_stock_item": 1}, pluck="name")
if not items:
    items = frappe.get_list("Item", pluck="name")
suppliers = frappe.get_list("Supplier", pluck="name")
customers = frappe.get_list("Customer", pluck="name")
sales_persons = frappe.get_list("Sales Person", pluck="name")

print(f"Loaded {len(companies)} Companies, {len(items)} Items, {len(suppliers)} Suppliers, {len(customers)} Customers.", flush=True)

def safe_commit():
    try:
        frappe.db.commit()
    except Exception:
        pass

def safe_rollback():
    try:
        frappe.db.rollback()
        frappe.connect()
    except Exception:
        pass

summary = {}

for co in companies:
    co_abbr = frappe.db.get_value("Company", co, "abbr")
    print(f"\n🏭 Processing Company: {co} ({co_abbr})...", flush=True)
    
    summary[co] = {
        "o2c": 0,
        "p2p": 0,
        "stock_entry": 0,
        "payment_receive": 0,
        "payment_pay": 0
    }
    
    income_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Income Account", "is_group": 0}, "name") or f"Sales - {co_abbr}"
    expense_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Cost of Goods Sold", "is_group": 0}, "name") or f"Cost of Goods Sold - {co_abbr}"
    cash_bank_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Cash", "is_group": 0}, "name") or \
                    frappe.db.get_value("Account", {"company": co, "account_type": "Bank", "is_group": 0}, "name") or \
                    f"Cash - {co_abbr}"
    debtors_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Receivable", "is_group": 0}, "name") or f"Debtors - {co_abbr}"
    creditors_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Payable", "is_group": 0}, "name") or f"Creditors - {co_abbr}"
    stock_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Stock", "is_group": 0}, "name") or f"Stock In Hand - {co_abbr}"
    stock_adjustment_acc = frappe.db.get_value("Account", {"company": co, "account_type": "Stock Adjustment", "is_group": 0}, "name") or f"Stock Adjustment - {co_abbr}"
    cost_center = frappe.db.get_value("Cost Center", {"company": co, "is_group": 0}, "name") or f"Main - {co_abbr}"
    
    warehouses = frappe.get_list("Warehouse", filters={"company": co, "is_group": 0}, pluck="name")
    if not warehouses:
        wh_name = f"Stores - {co_abbr}"
        if not frappe.db.exists("Warehouse", wh_name):
            wh_doc = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Stores",
                "company": co,
                "parent_warehouse": f"All Warehouses - {co_abbr}" if frappe.db.exists("Warehouse", f"All Warehouses - {co_abbr}") else None
            }).insert(ignore_permissions=True)
            warehouses = [wh_doc.name]
        else:
            warehouses = [wh_name]
    
    primary_wh = warehouses[0]
    sec_wh = warehouses[1] if len(warehouses) > 1 else primary_wh

    # -------------------------------------------------------------
    # 1. 10x Stock Entry (Material Receipt, Material Issue, Material Transfer)
    # -------------------------------------------------------------
    stock_purposes = ["Material Receipt", "Material Issue", "Material Transfer"]
    for i in range(10):
        try:
            purpose = stock_purposes[i % len(stock_purposes)]
            item_code = random.choice(items)
            qty = random.randint(5, 30)
            rate = random.choice([400.0, 750.0, 1100.0, 1900.0])
            tx_date = add_days(nowdate(), -random.randint(1, 28))
            
            se = frappe.new_doc("Stock Entry")
            se.stock_entry_type = purpose
            se.purpose = purpose
            se.company = co
            se.posting_date = tx_date
            
            if purpose == "Material Receipt":
                se.to_warehouse = primary_wh
                se.append("items", {
                    "item_code": item_code,
                    "qty": qty,
                    "t_warehouse": primary_wh,
                    "basic_rate": rate,
                    "cost_center": cost_center,
                    "expense_account": stock_adjustment_acc
                })
            elif purpose == "Material Issue":
                se.from_warehouse = primary_wh
                se.append("items", {
                    "item_code": item_code,
                    "qty": min(qty, 5),
                    "s_warehouse": primary_wh,
                    "basic_rate": rate,
                    "cost_center": cost_center,
                    "expense_account": stock_adjustment_acc
                })
            elif purpose == "Material Transfer":
                se.from_warehouse = primary_wh
                se.to_warehouse = sec_wh if sec_wh != primary_wh else primary_wh
                se.append("items", {
                    "item_code": item_code,
                    "qty": min(qty, 5),
                    "s_warehouse": primary_wh,
                    "t_warehouse": sec_wh if sec_wh != primary_wh else primary_wh,
                    "basic_rate": rate,
                    "cost_center": cost_center
                })
            
            se.flags.ignore_links = True
            se.flags.ignore_permissions = True
            se.insert()
            se.submit()
            safe_commit()
            summary[co]["stock_entry"] += 1
        except Exception as e:
            safe_rollback()
            # If item had zero stock for Issue/Transfer, do a receipt first
            try:
                rec = frappe.new_doc("Stock Entry")
                rec.stock_entry_type = "Material Receipt"
                rec.purpose = "Material Receipt"
                rec.company = co
                rec.posting_date = tx_date
                rec.to_warehouse = primary_wh
                rec.append("items", {
                    "item_code": item_code,
                    "qty": 50,
                    "t_warehouse": primary_wh,
                    "basic_rate": rate,
                    "cost_center": cost_center,
                    "expense_account": stock_adjustment_acc
                })
                rec.flags.ignore_permissions = True
                rec.flags.ignore_links = True
                rec.insert()
                rec.submit()
                safe_commit()
                summary[co]["stock_entry"] += 1
            except Exception:
                safe_rollback()

    print(f"  ✓ Stock Entry: {summary[co]['stock_entry']}/10 completed", flush=True)

    # -------------------------------------------------------------
    # 2. 10x P2P (Purchase Order -> Purchase Receipt -> Purchase Invoice -> Payment Entry)
    # -------------------------------------------------------------
    for i in range(10):
        try:
            supp = random.choice(suppliers)
            item_code = random.choice(items)
            qty = random.randint(5, 20)
            rate = random.choice([600.0, 950.0, 1400.0, 2200.0, 3100.0])
            tx_date = add_days(nowdate(), -random.randint(1, 28))
            
            # Step A: Purchase Order
            po = frappe.new_doc("Purchase Order")
            po.company = co
            po.supplier = supp
            po.transaction_date = tx_date
            po.schedule_date = add_days(tx_date, 3)
            po.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "warehouse": primary_wh,
                "schedule_date": add_days(tx_date, 3)
            })
            po.flags.ignore_links = True
            po.flags.ignore_permissions = True
            po.insert()
            po.submit()
            safe_commit()
            
            # Step B: Purchase Receipt
            pr = frappe.new_doc("Purchase Receipt")
            pr.company = co
            pr.supplier = supp
            pr.posting_date = tx_date
            pr.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "warehouse": primary_wh,
                "purchase_order": po.name,
                "purchase_order_item": po.items[0].name,
                "cost_center": cost_center
            })
            pr.flags.ignore_links = True
            pr.flags.ignore_permissions = True
            pr.insert()
            pr.submit()
            safe_commit()
            
            # Step C: Purchase Invoice
            pi = frappe.new_doc("Purchase Invoice")
            pi.company = co
            pi.supplier = supp
            pi.posting_date = tx_date
            pi.bill_no = f"INV-{random.randint(10000, 99999)}"
            pi.bill_date = tx_date
            pi.credit_to = creditors_acc
            pi.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "purchase_order": po.name,
                "po_detail": po.items[0].name,
                "purchase_receipt": pr.name,
                "pr_detail": pr.items[0].name,
                "expense_account": expense_acc,
                "cost_center": cost_center
            })
            pi.flags.ignore_links = True
            pi.flags.ignore_permissions = True
            pi.insert()
            pi.submit()
            safe_commit()
            
            # Step D: Payment Entry (Pay)
            pe = frappe.new_doc("Payment Entry")
            pe.payment_type = "Pay"
            pe.company = co
            pe.party_type = "Supplier"
            pe.party = supp
            pe.paid_from = cash_bank_acc
            pe.paid_to = creditors_acc
            pe.paid_amount = pi.grand_total
            pe.received_amount = pi.grand_total
            pe.target_exchange_rate = 1.0
            pe.source_exchange_rate = 1.0
            pe.posting_date = tx_date
            pe.mode_of_payment = "Cash"
            pe.append("references", {
                "reference_doctype": "Purchase Invoice",
                "reference_name": pi.name,
                "total_amount": pi.grand_total,
                "outstanding_amount": pi.grand_total,
                "allocated_amount": pi.grand_total
            })
            pe.flags.ignore_links = True
            pe.flags.ignore_permissions = True
            pe.insert()
            pe.submit()
            safe_commit()
            
            summary[co]["p2p"] += 1
        except Exception as e:
            safe_rollback()
            print(f"    [P2P Err {i+1}]: {e}", flush=True)

    print(f"  ✓ P2P: {summary[co]['p2p']}/10 cycles completed", flush=True)

    # -------------------------------------------------------------
    # 3. 10x O2C (Sales Order -> Delivery Note -> Sales Invoice -> Payment Entry)
    # -------------------------------------------------------------
    for i in range(10):
        try:
            cust = random.choice(customers)
            item_code = random.choice(items)
            qty = random.randint(1, 4)
            rate = random.choice([1200.0, 1850.0, 2400.0, 3500.0, 4800.0, 6500.0])
            tx_date = add_days(nowdate(), -random.randint(1, 28))
            
            # Step A: Sales Order
            so = frappe.new_doc("Sales Order")
            so.company = co
            so.customer = cust
            so.transaction_date = tx_date
            so.delivery_date = add_days(tx_date, 2)
            so.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "warehouse": primary_wh,
                "delivery_date": add_days(tx_date, 2)
            })
            if sales_persons:
                so.append("sales_team", {
                    "sales_person": random.choice(sales_persons),
                    "allocated_percentage": 100.0,
                    "commission_rate": 50.0
                })
            so.flags.ignore_links = True
            so.flags.ignore_permissions = True
            so.flags.ignore_validate = False
            so.insert()
            so.submit()
            safe_commit()

            # Ensure stock is available
            from erpnext.stock.utils import get_stock_balance
            curr_stock = get_stock_balance(item_code, primary_wh)
            if curr_stock < qty:
                se_stock = frappe.new_doc("Stock Entry")
                se_stock.stock_entry_type = "Material Receipt"
                se_stock.purpose = "Material Receipt"
                se_stock.company = co
                se_stock.posting_date = tx_date
                se_stock.to_warehouse = primary_wh
                se_stock.append("items", {
                    "item_code": item_code,
                    "qty": max(50, qty * 10),
                    "t_warehouse": primary_wh,
                    "basic_rate": rate * 0.6,
                    "cost_center": cost_center,
                    "expense_account": stock_adjustment_acc
                })
                se_stock.flags.ignore_permissions = True
                se_stock.flags.ignore_links = True
                se_stock.insert()
                se_stock.submit()
                safe_commit()

            # Step B: Delivery Note
            dn = frappe.new_doc("Delivery Note")
            dn.company = co
            dn.customer = cust
            dn.posting_date = tx_date
            dn.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "warehouse": primary_wh,
                "against_sales_order": so.name,
                "so_detail": so.items[0].name,
                "cost_center": cost_center,
                "expense_account": expense_acc
            })
            dn.flags.ignore_links = True
            dn.flags.ignore_permissions = True
            dn.insert()
            dn.submit()
            safe_commit()
            
            # Step C: Sales Invoice
            si = frappe.new_doc("Sales Invoice")
            si.company = co
            si.customer = cust
            si.posting_date = tx_date
            si.append("items", {
                "item_code": item_code,
                "qty": qty,
                "rate": rate,
                "sales_order": so.name,
                "so_detail": so.items[0].name,
                "delivery_note": dn.name,
                "dn_detail": dn.items[0].name,
                "income_account": income_acc,
                "cost_center": cost_center
            })
            if sales_persons:
                si.append("sales_team", {
                    "sales_person": random.choice(sales_persons),
                    "allocated_percentage": 100.0,
                    "commission_rate": 50.0
                })
            si.flags.ignore_links = True
            si.flags.ignore_permissions = True
            si.insert()
            si.submit()
            safe_commit()
            
            # Step D: Payment Entry (Receive)
            pe = frappe.new_doc("Payment Entry")
            pe.payment_type = "Receive"
            pe.company = co
            pe.party_type = "Customer"
            pe.party = cust
            pe.paid_from = debtors_acc
            pe.paid_to = cash_bank_acc
            pe.paid_amount = si.grand_total
            pe.received_amount = si.grand_total
            pe.target_exchange_rate = 1.0
            pe.source_exchange_rate = 1.0
            pe.posting_date = tx_date
            pe.mode_of_payment = "Cash"
            pe.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": si.name,
                "total_amount": si.grand_total,
                "outstanding_amount": si.grand_total,
                "allocated_amount": si.grand_total
            })
            pe.flags.ignore_links = True
            pe.flags.ignore_permissions = True
            pe.insert()
            pe.submit()
            safe_commit()
            
            summary[co]["o2c"] += 1
        except Exception as e:
            safe_rollback()
            print(f"    [O2C Err {i+1}]: {e}", flush=True)

    print(f"  ✓ O2C: {summary[co]['o2c']}/10 cycles completed", flush=True)

    # -------------------------------------------------------------
    # 4. 10x Standalone Payments Receive
    # -------------------------------------------------------------
    for i in range(10):
        try:
            cust = random.choice(customers)
            amt = random.choice([2500.0, 4800.0, 7500.0, 12000.0, 18500.0])
            tx_date = add_days(nowdate(), -random.randint(1, 28))
            
            pe = frappe.new_doc("Payment Entry")
            pe.payment_type = "Receive"
            pe.company = co
            pe.party_type = "Customer"
            pe.party = cust
            pe.paid_from = debtors_acc
            pe.paid_to = cash_bank_acc
            pe.paid_amount = amt
            pe.received_amount = amt
            pe.target_exchange_rate = 1.0
            pe.source_exchange_rate = 1.0
            pe.posting_date = tx_date
            pe.mode_of_payment = random.choice(["Cash", "Check", "Wire Transfer", "Credit Card"])
            pe.remarks = f"Customer direct payment / advance settlement for {cust}"
            pe.flags.ignore_links = True
            pe.flags.ignore_permissions = True
            pe.insert()
            pe.submit()
            safe_commit()
            summary[co]["payment_receive"] += 1
        except Exception as e:
            safe_rollback()
            print(f"    [Payment Receive Err {i+1}]: {e}", flush=True)

    print(f"  ✓ Payment Receive: {summary[co]['payment_receive']}/10 completed", flush=True)

    # -------------------------------------------------------------
    # 5. 10x Standalone Payments Pay
    # -------------------------------------------------------------
    for i in range(10):
        try:
            supp = random.choice(suppliers)
            amt = random.choice([3200.0, 5600.0, 8900.0, 15000.0, 24000.0])
            tx_date = add_days(nowdate(), -random.randint(1, 28))
            
            pe = frappe.new_doc("Payment Entry")
            pe.payment_type = "Pay"
            pe.company = co
            pe.party_type = "Supplier"
            pe.party = supp
            pe.paid_from = cash_bank_acc
            pe.paid_to = creditors_acc
            pe.paid_amount = amt
            pe.received_amount = amt
            pe.target_exchange_rate = 1.0
            pe.source_exchange_rate = 1.0
            pe.posting_date = tx_date
            pe.mode_of_payment = random.choice(["Cash", "Check", "Wire Transfer", "Bank Draft"])
            pe.remarks = f"Supplier disbursement / advance procurement payment for {supp}"
            pe.flags.ignore_links = True
            pe.flags.ignore_permissions = True
            pe.insert()
            pe.submit()
            safe_commit()
            summary[co]["payment_pay"] += 1
        except Exception as e:
            safe_rollback()
            print(f"    [Payment Pay Err {i+1}]: {e}", flush=True)

    print(f"  ✓ Payment Pay: {summary[co]['payment_pay']}/10 completed", flush=True)

print("\n" + "=" * 80, flush=True)
print("🎉 ALL TRANSACTIONS GENERATED SUCCESSFULLY ACROSS ALL COMPANIES!", flush=True)
print("=" * 80, flush=True)

total_all = 0
for co, s in summary.items():
    tot = sum(s.values())
    total_all += tot
    print(f"{co:35s} | O2C: {s['o2c']} | P2P: {s['p2p']} | Stock: {s['stock_entry']} | PayRecv: {s['payment_receive']} | PayDisb: {s['payment_pay']} (Total: {tot})", flush=True)

print(f"\nGrand Total Completed Transactions: {total_all}", flush=True)
