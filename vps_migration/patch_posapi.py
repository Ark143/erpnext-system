#!/usr/bin/env python3
"""Patch pos_api.py: enhance get_history (timestamp), add receipt + shift open/close."""
import frappe

PATH = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/pos_api.py"
src = open(PATH).read()

# 1. Replace get_history with timestamp-aware version
old_hist = '''@frappe.whitelist()
def get_history():
\t"""Recent Vehicle POS Invoices created by the logged-in cashier."""
\tuser = frappe.session.user
\trows = frappe.get_all(
\t\t"Vehicle POS Invoice",
\t\tfilters=[["Vehicle POS Invoice", "cashier", "=", user], ["Vehicle POS Invoice", "docstatus", "=", 1]],
\t\tfields=["name", "posting_date", "customer_name", "vehicle", "total_amount", "paid_amount",
\t\t        "payment_method", "company", "creation"],
\t\torder_by="creation desc",
\t\tlimit_page_length=50,
\t)
\treturn rows
'''

new_hist = '''@frappe.whitelist()
def get_history():
\t"""Recent Vehicle POS Invoices created by the logged-in cashier (real-time)."""
\tuser = frappe.session.user
\trows = frappe.get_all(
\t\t"Vehicle POS Invoice",
\t\tfilters=[["Vehicle POS Invoice", "cashier", "=", user], ["Vehicle POS Invoice", "docstatus", "=", 1]],
\t\tfields=["name", "posting_date", "customer_name", "vehicle", "plate_no", "total_amount", "paid_amount",
\t\t        "payment_method", "company", "pos_invoice", "creation"],
\t\torder_by="creation desc",
\t\tlimit_page_length=200,
\t)
\tfor r in rows:
\t\tr["timestamp"] = _fmt_ts(r)
\treturn rows


def _fmt_ts(r):
\t"""Human timestamp: YYYY-MM-DD HH:MM:SS from creation, fallback to posting_date."""
\tc = r.get("creation") or ""
\tif c:
\t\treturn str(c)[:19]
\treturn str(r.get("posting_date") or "")


@frappe.whitelist()
def get_receipt(name):
\t"""Full receipt detail for a single Vehicle POS Invoice (for receipt printing)."""
\tif not name:
\t\treturn {}
\tdoc = frappe.get_doc("Vehicle POS Invoice", name)
\troles = frappe.get_roles(frappe.session.user)
\tif doc.cashier and doc.cashier != frappe.session.user and "System Manager" not in roles:
\t\tfrappe.throw("Not permitted", frappe.PermissionError)
\titems = []
\tfor it in doc.get("items") or []:
\t\titems.append({
\t\t\t"item_code": it.item_code,
\t\t\t"item_name": it.item_name,
\t\t\t"uom": it.uom,
\t\t\t"qty": flt(it.qty),
\t\t\t"rate": flt(it.rate),
\t\t\t"discount_amount": flt(it.discount_amount),
\t\t\t"amount": flt(it.amount),
\t\t})
\treturn {
\t\t"name": doc.name,
\t\t"posting_date": str(doc.posting_date or ""),
\t\t"timestamp": str(doc.creation or "")[:19],
\t\t"customer": doc.customer,
\t\t"customer_name": doc.customer_name,
\t\t"vehicle": doc.vehicle,
\t\t"plate_no": doc.plate_no,
\t\t"company": doc.company,
\t\t"cashier": doc.cashier,
\t\t"payment_method": doc.payment_method,
\t\t"paid_amount": flt(doc.paid_amount),
\t\t"total_amount": flt(doc.total_amount),
\t\t"total_discount": flt(doc.total_discount),
\t\t"balance_amount": flt(doc.balance_amount),
\t\t"pos_invoice": doc.pos_invoice,
\t\t"items": items,
\t}


@frappe.whitelist()
def get_cashier_shift():
\t"""Current open POS Opening Entry for the logged-in cashier (or closed)."""
\tuser = frappe.session.user
\te = frappe.db.get_value(
\t\t"POS Opening Entry",
\t\t{"user": user, "status": "Open", "docstatus": 1},
\t\t["name", "pos_profile", "company", "period_start_date"],
\t\tas_dict=True,
\t)
\tif e:
\t\treturn {"open": True, "name": e.name, "pos_profile": e.pos_profile,
\t\t        "company": e.company, "period_start_date": str(e.period_start_date or "")}
\treturn {"open": False, "name": None}


@frappe.whitelist()
def open_cashier(company=None, opening_amount=0):
\t"""Open a POS Opening Entry for the logged-in cashier."""
\tuser = frappe.session.user
\texisting = frappe.db.get_value(
\t\t"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
\t)
\tif existing:
\t\treturn {"status": "already_open", "name": existing}
\tif not company:
\t\tcompany = (get_cashier() or {}).get("company")
\tif not company:
\t\tfrappe.throw("Could not resolve a company for this cashier.")
\tfrom vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice import VehiclePOSInvoice
\tvpi = VehiclePOSInvoice({"doctype": "Vehicle POS Invoice"})
\tpos_profile = vpi.ensure_pos_profile(company)
\tcash = vpi.get_mode_of_payment("Cash", company)
\tentry = frappe.get_doc({
\t\t"doctype": "POS Opening Entry",
\t\t"company": company,
\t\t"pos_profile": pos_profile,
\t\t"user": user,
\t\t"posting_date": frappe.utils.nowdate(),
\t\t"period_start_date": frappe.utils.now_datetime(),
\t\t"balance_details": [{"mode_of_payment": cash, "opening_amount": flt(opening_amount)}],
\t})
\tentry.insert()
\tentry.submit()
\tfrappe.db.commit()
\treturn {"status": "opened", "name": entry.name}


@frappe.whitelist()
def close_cashier():
\t"""Close the cashier's open POS Opening Entry via a POS Closing Entry."""
\tuser = frappe.session.user
\topening_name = frappe.db.get_value(
\t\t"POS Opening Entry", {"user": user, "status": "Open", "docstatus": 1}, "name"
\t)
\tif not opening_name:
\t\treturn {"status": "no_open_entry", "message": "No open POS Opening Entry found."}
\tfrom erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
\topening = frappe.get_doc("POS Opening Entry", opening_name)
\tclosing = make_closing_entry_from_opening(opening)
\tclosing.insert()
\tclosing.submit()
\tfrappe.db.commit()
\treturn {"status": "closed", "name": closing.name}
'''

if old_hist not in src:
    print("!! get_history old body NOT FOUND — checking exact form")
    # try without the docstring variant
    i = src.find("def get_history():")
    print("get_history at", i)
    print(repr(src[i:i+600]))
    raise SystemExit(1)

src = src.replace(old_hist, new_hist, 1)
open(PATH, "w").write(src)
print("patched pos_api.py. new length", len(src))
print("has get_receipt:", "def get_receipt" in src)
print("has open_cashier:", "def open_cashier" in src)
print("has close_cashier:", "def close_cashier" in src)
print("has get_cashier_shift:", "def get_cashier_shift" in src)
