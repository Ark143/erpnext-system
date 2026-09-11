import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    with op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
            method="POST",
        ),
        timeout=30,
    ) as r:
        pass

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body[:400]}")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body}

login()

# 1. Server Script: VM Get Bank Clearance Entries
get_clearance_script = """
account = frappe.form_dict.get("account")
from_date = frappe.form_dict.get("from_date")
to_date = frappe.form_dict.get("to_date")
include_reconciled = frappe.utils.cint(frappe.form_dict.get("include_reconciled_entries"))
include_pos = frappe.utils.cint(frappe.form_dict.get("include_pos_transactions"))

if not account or not from_date or not to_date:
    frappe.response["message"] = []
else:
    entries = []
    
    # 1. Payment Entries
    pe_sql = \"\"\"
        SELECT 
            'Payment Entry' as payment_document,
            pe.name as payment_entry,
            pe.reference_no as cheque_number,
            pe.reference_date as cheque_date,
            pe.posting_date,
            pe.clearance_date,
            CASE 
                WHEN pe.paid_from = %(account)s THEN (pe.paid_amount + COALESCE(pe.total_taxes_and_charges, 0))
                ELSE 0.0 
            END as credit,
            CASE 
                WHEN pe.paid_to = %(account)s THEN (pe.received_amount + COALESCE(pe.total_taxes_and_charges, 0))
                ELSE 0.0 
            END as debit,
            COALESCE(pe.party, CASE WHEN pe.paid_from = %(account)s THEN pe.paid_to ELSE pe.paid_from END) as against_account,
            CASE 
                WHEN pe.paid_to = %(account)s THEN pe.paid_to_account_currency 
                ELSE pe.paid_from_account_currency 
            END as account_currency
        FROM "tabPayment Entry" pe
        WHERE pe.docstatus = 1
          AND (pe.paid_from = %(account)s OR pe.paid_to = %(account)s)
          AND pe.posting_date >= %(from_date)s
          AND pe.posting_date <= %(to_date)s
    \"\"\"
    if not include_reconciled:
        pe_sql = pe_sql + " AND pe.clearance_date IS NULL"
    pe_sql = pe_sql + " ORDER BY pe.posting_date ASC, pe.name DESC"
    
    pe_rows = frappe.db.sql(pe_sql, {"account": account, "from_date": from_date, "to_date": to_date}, as_dict=True)
    for r in pe_rows:
        entries.append(r)
        
    # 2. Journal Entries
    je_sql = \"\"\"
        SELECT 
            'Journal Entry' as payment_document,
            je.name as payment_entry,
            je.cheque_no as cheque_number,
            je.cheque_date,
            je.posting_date,
            je.clearance_date,
            SUM(jea.debit_in_account_currency) as debit,
            SUM(jea.credit_in_account_currency) as credit,
            MAX(jea.against_account) as against_account,
            MAX(jea.account_currency) as account_currency
        FROM "tabJournal Entry Account" jea
        JOIN "tabJournal Entry" je ON jea.parent = je.name
        WHERE je.docstatus = 1
          AND jea.account = %(account)s
          AND je.is_opening = 'No'
          AND je.posting_date >= %(from_date)s
          AND je.posting_date <= %(to_date)s
    \"\"\"
    if not include_reconciled:
        je_sql = je_sql + " AND je.clearance_date IS NULL"
    je_sql = je_sql + " GROUP BY je.name, je.cheque_no, je.cheque_date, je.posting_date, je.clearance_date ORDER BY je.posting_date ASC, je.name DESC"
    
    je_rows = frappe.db.sql(je_sql, {"account": account, "from_date": from_date, "to_date": to_date}, as_dict=True)
    for r in je_rows:
        entries.append(r)
        
    # 3. Paid Purchase Invoices
    pi_sql = \"\"\"
        SELECT 
            'Purchase Invoice' as payment_document,
            pi.name as payment_entry,
            pi.bill_no as cheque_number,
            NULL as cheque_date,
            pi.posting_date,
            pi.clearance_date,
            0.0 as debit,
            pi.paid_amount as credit,
            pi.supplier as against_account,
            acc.account_currency
        FROM "tabPurchase Invoice" pi
        JOIN "tabAccount" acc ON pi.cash_bank_account = acc.name
        WHERE pi.docstatus = 1
          AND pi.is_paid = 1
          AND pi.cash_bank_account = %(account)s
          AND pi.posting_date >= %(from_date)s
          AND pi.posting_date <= %(to_date)s
    \"\"\"
    if not include_reconciled:
        pi_sql = pi_sql + " AND pi.clearance_date IS NULL"
    pi_sql = pi_sql + " ORDER BY pi.posting_date ASC, pi.name DESC"
    
    pi_rows = frappe.db.sql(pi_sql, {"account": account, "from_date": from_date, "to_date": to_date}, as_dict=True)
    for r in pi_rows:
        entries.append(r)
        
    # 4. POS Sales Invoices
    if include_pos:
        si_sql = \"\"\"
            SELECT 
                'Sales Invoice' as payment_document,
                si.name as payment_entry,
                sip.reference_no as cheque_number,
                NULL as cheque_date,
                si.posting_date,
                sip.clearance_date,
                sip.amount as debit,
                0.0 as credit,
                si.customer as against_account,
                acc.account_currency
            FROM "tabSales Invoice Payment" sip
            JOIN "tabSales Invoice" si ON sip.parent = si.name
            JOIN "tabAccount" acc ON sip.account = acc.name
            WHERE si.docstatus = 1
              AND sip.account = %(account)s
              AND si.posting_date >= %(from_date)s
              AND si.posting_date <= %(to_date)s
        \"\"\"
        if not include_reconciled:
            si_sql = si_sql + " AND sip.clearance_date IS NULL"
        si_sql = si_sql + " ORDER BY si.posting_date ASC, si.name DESC"
        
        si_rows = frappe.db.sql(si_sql, {"account": account, "from_date": from_date, "to_date": to_date}, as_dict=True)
        for r in si_rows:
            entries.append(r)
            
    # Format amount and labels
    formatted_entries = []
    for d in entries:
        amt = frappe.utils.flt(d.get("debit", 0)) - frappe.utils.flt(d.get("credit", 0))
        curr = d.get("account_currency") or "PHP"
        dr_cr = " Dr" if amt > 0 else " Cr"
        d["amount"] = frappe.utils.fmt_money(abs(amt), currency=curr) + dr_cr
        d["posting_date"] = str(d.get("posting_date"))
        if d.get("cheque_date"):
            d["cheque_date"] = str(d.get("cheque_date"))
        if d.get("clearance_date"):
            d["clearance_date"] = str(d.get("clearance_date"))
        formatted_entries.append(d)
        
    frappe.response["message"] = formatted_entries
"""

ss1 = {
    "name": "VM Get Bank Clearance Entries",
    "doctype": "Server Script",
    "script_type": "API",
    "api_method": "vm_get_bank_clearance_entries",
    "allow_guest": 0,
    "disabled": 0,
    "script": get_clearance_script
}

chk1 = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Get Bank Clearance Entries')}", "GET")
if chk1.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Get Bank Clearance Entries')}", "PUT", {"script": get_clearance_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss1)
print("[OK] Deployed Server Script: VM Get Bank Clearance Entries")

# 2. Server Script: VM Update Bank Clearance Dates
update_clearance_script = """
entries = frappe.form_dict.get("entries")
if isinstance(entries, str):
    entries = frappe.parse_json(entries)

updated_count = 0
if entries:
    for d in entries:
        dt = d.get("payment_document")
        dn = d.get("payment_entry")
        cdate = d.get("clearance_date") or None
        
        if dt and dn:
            if dt == "Sales Invoice":
                frappe.db.set_value("Sales Invoice Payment", {"parent": dn}, "clearance_date", cdate)
                updated_count = updated_count + 1
            elif dt in ["Journal Entry", "Payment Entry", "Purchase Invoice"]:
                frappe.db.set_value(dt, dn, "clearance_date", cdate)
                updated_count = updated_count + 1

frappe.response["message"] = {
    "status": "success",
    "updated_count": updated_count
}
"""

ss2 = {
    "name": "VM Update Bank Clearance Dates",
    "doctype": "Server Script",
    "script_type": "API",
    "api_method": "vm_update_bank_clearance_dates",
    "allow_guest": 0,
    "disabled": 0,
    "script": update_clearance_script
}


chk2 = call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Update Bank Clearance Dates')}", "GET")
if chk2.get("data"):
    call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Update Bank Clearance Dates')}", "PUT", {"script": update_clearance_script, "disabled": 0})
else:
    call("/api/resource/Server%20Script", "POST", ss2)
print("[OK] Deployed Server Script: VM Update Bank Clearance Dates")

# 3. Client Script: Bank Clearance PG Fix
client_script_code = """
frappe.ui.form.on("Bank Clearance", {
    get_payment_entries: function(frm) {
        if (!frm.doc.from_date || !frm.doc.to_date) {
            frappe.msgprint(__("From Date and To Date are Mandatory"));
            return;
        }
        if (!frm.doc.account) {
            frappe.msgprint(__("Account is mandatory to get payment entries"));
            return;
        }
        frappe.call({
            method: "vm_get_bank_clearance_entries",
            args: {
                account: frm.doc.account,
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date,
                bank_account: frm.doc.bank_account,
                include_reconciled_entries: frm.doc.include_reconciled_entries || 0,
                include_pos_transactions: frm.doc.include_pos_transactions || 0
            },
            freeze: true,
            freeze_message: __("Fetching Payment Entries..."),
            callback: function(r) {
                frm.clear_table("payment_entries");
                if (r.message && r.message.length) {
                    r.message.forEach(function(d) {
                        let row = frm.add_child("payment_entries");
                        Object.assign(row, d);
                    });
                }
                frm.refresh_field("payment_entries");
                frm.refresh();
            }
        });
    },
    update_clearance_date: function(frm) {
        if (!frm.doc.payment_entries || !frm.doc.payment_entries.length) {
            frappe.msgprint(__("No payment entries to update"));
            return;
        }
        frappe.call({
            method: "vm_update_bank_clearance_dates",
            args: {
                entries: frm.doc.payment_entries
            },
            freeze: true,
            freeze_message: __("Updating Clearance Dates..."),
            callback: function(r) {
                frappe.show_alert({message: __("Clearance Date updated successfully"), indicator: "green"});
                frm.trigger("get_payment_entries");
            }
        });
    }
});
"""

cs = {
    "name": "Bank Clearance PG Fix",
    "dt": "Bank Clearance",
    "doctype": "Client Script",
    "view": "Form",
    "enabled": 1,
    "script": client_script_code
}

chk3 = call(f"/api/resource/Client%20Script/{urllib.parse.quote('Bank Clearance PG Fix')}", "GET")
if chk3.get("data"):
    call(f"/api/resource/Client%20Script/{urllib.parse.quote('Bank Clearance PG Fix')}", "PUT", {"script": client_script_code, "enabled": 1})
else:
    call("/api/resource/Client%20Script", "POST", cs)
print("[OK] Deployed Client Script: Bank Clearance PG Fix")
