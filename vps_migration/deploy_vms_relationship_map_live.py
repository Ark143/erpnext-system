import requests
import json
import os

URL = 'http://38.247.138.224:10017'
s = requests.Session()
login_res = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=45)
if login_res.status_code != 200:
    print("Login failed:", login_res.text)
    exit(1)
print("[OK] Logged in as Administrator.")

# 1. Server Script Code
server_script_code = """
doctype = frappe.form_dict.get('doctype')
docname = frappe.form_dict.get('docname')
vehicle = frappe.form_dict.get('vehicle')
customer = frappe.form_dict.get('customer')

if not doctype and not docname and not vehicle and not customer:
    jos = frappe.get_all("Vehicle Job Order", fields=["name"], order_by="creation desc", limit=1)
    if jos:
        doctype = "Vehicle Job Order"
        docname = jos[0].get("name")
    else:
        frappe.response['message'] = {"nodes": [], "edges": [], "summary": {}, "items": [], "accounting": {}}

if vehicle and not doctype:
    doctype = "Customer Vehicle"
    docname = vehicle
elif customer and not doctype:
    doctype = "Customer"
    docname = customer

try:
    nodes_dict = {}
    edges = []
    all_items = []

    def get_node(dt, name, is_curr, lvl):
        key = str(dt) + "::" + str(name)
        if key in nodes_dict:
            if is_curr:
                nodes_dict[key]["is_current"] = True
            return nodes_dict[key]

        if not frappe.db.exists(dt, name):
            return None

        doc = frappe.get_doc(dt, name)
        st = doc.get("status") or doc.get("workflow_state") or "Active"
        ds = doc.get("docstatus") or 0
        if ds == 0:
            st_disp = st if st != "Active" else "Draft"
        elif ds == 1:
            st_disp = st if st not in ("Draft", "Active") else "Submitted"
        elif ds == 2:
            st_disp = "Cancelled"
        else:
            st_disp = st

        gt = float(doc.get("grand_total") or doc.get("total_amount") or doc.get("paid_amount") or doc.get("received_amount") or 0)
        
        if dt == "Sales Invoice":
            si_out = doc.get("outstanding_amount")
            if si_out is not None:
                outst = max(0.0, float(si_out))
            else:
                ples = frappe.get_all("Payment Ledger Entry", filters={"against_voucher_no": name, "delinked": 0}, fields=["amount"])
                if ples:
                    outst = max(0.0, sum([float(p.get("amount") or 0) for p in ples]))
                else:
                    outst = gt
            paid = max(0.0, gt - outst)
            if outst <= 0.001:
                outst = 0.0
                paid = gt
                st_disp = "Paid"
        elif dt == "Payment Entry":
            paid = gt
            outst = 0.0
        elif dt == "Vehicle Job Order":
            si_no = doc.get("sales_invoice")
            if si_no and frappe.db.exists("Sales Invoice", si_no):
                outst = 0.0
                si_doc = frappe.get_doc("Sales Invoice", si_no)
                si_out = si_doc.get("outstanding_amount")
                if (si_out is not None and float(si_out) <= 0.001) or si_doc.get("status") == "Paid":
                    paid = gt
                else:
                    paid = float(doc.get("paid_amount") or 0)
            else:
                paid = float(doc.get("paid_amount") or 0)
                outst = max(0.0, gt - paid)
        elif dt in ("Vehicle POS Invoice", "POS Invoice"):
            paid = float(doc.get("paid_amount") or gt)
            outst = max(0.0, gt - paid)
        else:
            paid = float(doc.get("paid_amount") or doc.get("total_allocated_amount") or 0)
            doc_out = doc.get("outstanding_amount")
            if doc_out is not None:
                outst = max(0.0, float(doc_out))
            else:
                outst = max(0.0, gt - paid)

        p_date = str(doc.get("posting_date") or doc.get("job_order_date") or doc.get("estimate_date") or doc.get("inspection_date") or doc.get("transaction_date") or doc.get("creation") or "")[:10]
        p_time = str(doc.get("posting_time") or "")

        v_plate = doc.get("plate_no") or doc.get("vehicle") or doc.get("custom_vehicle_plate") or ""
        c_name = doc.get("customer_name") or doc.get("customer") or doc.get("party_name") or ""
        comp = doc.get("company") or "ULTRA MRF"

        items_list = []
        if doc.get("services"):
            for s in doc.get("services"):
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Labor / Service",
                    "item_code": s.get("service_name") or s.get("description") or "Service",
                    "description": s.get("description") or s.get("service_name") or "",
                    "qty": float(s.get("hours") or 1),
                    "uom": "Hrs",
                    "rate": float(s.get("rate") or 0),
                    "amount": float(s.get("total_amount") or 0),
                    "account": "Service Revenue"
                }
                items_list.append(it_obj)
                all_items.append(it_obj)
        if doc.get("parts"):
            for p in doc.get("parts"):
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Spare Part / Material",
                    "item_code": p.get("part_no") or p.get("item_code") or p.get("item_name") or "Part",
                    "description": p.get("item_name") or p.get("description") or "",
                    "qty": float(p.get("qty") or 1),
                    "uom": p.get("uom") or "PC",
                    "rate": float(p.get("rate") or 0),
                    "amount": float(p.get("amount") or 0),
                    "account": "Parts & Inventory"
                }
                items_list.append(it_obj)
                all_items.append(it_obj)
        if doc.get("items"):
            for it in doc.get("items"):
                grp = str(it.get("item_group") or "").lower()
                nm = str(it.get("item_name") or "").lower()
                cat = "Billed Service / Labor" if ("service" in grp or "labor" in grp or "service" in nm or "labor" in nm) else "Billed Spare Part / Product"
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": cat,
                    "item_code": it.get("item_code") or it.get("item_name") or "Item",
                    "description": it.get("description") or it.get("item_name") or "",
                    "qty": float(it.get("qty") or 1),
                    "uom": it.get("uom") or "PC",
                    "rate": float(it.get("rate") or 0),
                    "amount": float(it.get("amount") or 0),
                    "account": it.get("income_account") or it.get("expense_account") or "Sales Revenue"
                }
                items_list.append(it_obj)
                all_items.append(it_obj)
        if doc.get("references"):
            for ref in doc.get("references"):
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Payment Allocation",
                    "item_code": ref.get("reference_name") or "",
                    "description": "Allocated Payment for " + str(ref.get("reference_doctype") or "") + " " + str(ref.get("reference_name") or ""),
                    "qty": 1.0,
                    "uom": "Voucher",
                    "rate": float(ref.get("allocated_amount") or 0),
                    "amount": float(ref.get("allocated_amount") or 0),
                    "account": "Accounts Receivable Offset"
                }
                items_list.append(it_obj)
                all_items.append(it_obj)

        node_obj = {
            "id": key,
            "doctype": dt,
            "name": name,
            "title": str(dt) + ": " + str(name),
            "status": st_disp,
            "raw_status": st,
            "docstatus": ds,
            "grand_total": gt,
            "paid_amount": paid,
            "outstanding_amount": outst,
            "currency": doc.get("currency") or "PHP",
            "posting_date": p_date,
            "posting_time": p_time,
            "vehicle": v_plate,
            "customer": c_name,
            "company": comp,
            "is_current": is_curr,
            "level": lvl,
            "items_count": len(items_list),
            "items": items_list[:25],
            "remarks": doc.get("remarks") or doc.get("customer_complaint") or doc.get("general_remarks") or ""
        }
        nodes_dict[key] = node_obj
        return node_obj

    def link_nodes(from_dt, from_name, to_dt, to_name, lbl, e_type):
        if not from_name or not to_name:
            return
        f_id = str(from_dt) + "::" + str(from_name)
        t_id = str(to_dt) + "::" + str(to_name)
        for e in edges:
            if e.get("from") == f_id and e.get("to") == t_id and e.get("label") == lbl:
                return
        edges.append({"from": f_id, "to": t_id, "label": lbl, "type": e_type})

    focal = None
    plate = ""
    cust = ""
    if doctype and docname and frappe.db.exists(doctype, docname):
        focal = get_node(doctype, docname, True, 2)
    
    if focal:
        plate = focal.get("vehicle") or ""
        cust = focal.get("customer") or ""

        if doctype == "Customer Vehicle":
            plate = docname
            v_doc = frappe.get_doc("Customer Vehicle", docname)
            if v_doc.get("customer") and frappe.db.exists("Customer", v_doc.get("customer")):
                get_node("Customer", v_doc.get("customer"), False, 0)
                link_nodes("Customer", v_doc.get("customer"), "Customer Vehicle", docname, "Owns Vehicle", "reference")

        if plate and frappe.db.exists("Customer Vehicle", plate):
            get_node("Customer Vehicle", plate, False, 0)
            if doctype not in ("Customer Vehicle", "Customer"):
                link_nodes("Customer Vehicle", plate, doctype, docname, "Vehicle", "reference")
            v_doc = frappe.get_doc("Customer Vehicle", plate)
            if v_doc.get("customer") and frappe.db.exists("Customer", v_doc.get("customer")):
                get_node("Customer", v_doc.get("customer"), False, 0)
                link_nodes("Customer", v_doc.get("customer"), "Customer Vehicle", plate, "Owns Vehicle", "reference")

        if cust and frappe.db.exists("Customer", cust):
            get_node("Customer", cust, False, 0)
            if doctype not in ("Customer Vehicle", "Customer"):
                link_nodes("Customer", cust, doctype, docname, "Customer", "reference")

        if doctype == "Vehicle Job Order":
            jo = frappe.get_doc("Vehicle Job Order", docname)
            if jo.get("estimate") and frappe.db.exists("Vehicle Estimate", jo.get("estimate")):
                get_node("Vehicle Estimate", jo.get("estimate"), False, 1)
                link_nodes("Vehicle Estimate", jo.get("estimate"), "Vehicle Job Order", docname, "Converted to JO", "flow")
            elif plate:
                for est in frappe.get_all("Vehicle Estimate", filters={"vehicle": plate}, fields=["name"], order_by="creation desc", limit=2):
                    get_node("Vehicle Estimate", est.get("name"), False, 1)
                    link_nodes("Vehicle Estimate", est.get("name"), "Vehicle Job Order", docname, "Quotation", "reference")

            if plate:
                for insp in frappe.get_all("Vehicle Inspection", filters={"vehicle": plate}, fields=["name"], order_by="creation desc", limit=2):
                    get_node("Vehicle Inspection", insp.get("name"), False, 1)
                    link_nodes("Vehicle Inspection", insp.get("name"), "Vehicle Job Order", docname, "Diagnostic", "flow")

            if jo.get("sales_invoice") and frappe.db.exists("Sales Invoice", jo.get("sales_invoice")):
                get_node("Sales Invoice", jo.get("sales_invoice"), False, 3)
                link_nodes("Vehicle Job Order", docname, "Sales Invoice", jo.get("sales_invoice"), "Billed via SI", "flow")
                for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": jo.get("sales_invoice")}, fields=["parent"]):
                    if frappe.db.exists("Payment Entry", p.get("parent")):
                        get_node("Payment Entry", p.get("parent"), False, 4)
                        link_nodes("Sales Invoice", jo.get("sales_invoice"), "Payment Entry", p.get("parent"), "Payment Received", "accounting")

            if plate:
                for vp in frappe.get_all("Vehicle POS Invoice", filters={"vehicle": plate}, fields=["name", "pos_invoice"], order_by="creation desc", limit=2):
                    get_node("Vehicle POS Invoice", vp.get("name"), False, 3)
                    link_nodes("Vehicle Job Order", docname, "Vehicle POS Invoice", vp.get("name"), "POS Bill", "flow")
                    if vp.get("pos_invoice") and frappe.db.exists("POS Invoice", vp.get("pos_invoice")):
                        get_node("POS Invoice", vp.get("pos_invoice"), False, 3)
                        link_nodes("Vehicle POS Invoice", vp.get("name"), "POS Invoice", vp.get("pos_invoice"), "POS Record", "flow")

        elif doctype == "Vehicle Estimate":
            est = frappe.get_doc("Vehicle Estimate", docname)
            if est.get("job_order") and frappe.db.exists("Vehicle Job Order", est.get("job_order")):
                get_node("Vehicle Job Order", est.get("job_order"), False, 2)
                link_nodes("Vehicle Estimate", docname, "Vehicle Job Order", est.get("job_order"), "Converted to JO", "flow")
                jo = frappe.get_doc("Vehicle Job Order", est.get("job_order"))
                if jo.get("sales_invoice") and frappe.db.exists("Sales Invoice", jo.get("sales_invoice")):
                    get_node("Sales Invoice", jo.get("sales_invoice"), False, 3)
                    link_nodes("Vehicle Job Order", est.get("job_order"), "Sales Invoice", jo.get("sales_invoice"), "Billed via SI", "flow")
                    for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": jo.get("sales_invoice")}, fields=["parent"]):
                        if frappe.db.exists("Payment Entry", p.get("parent")):
                            get_node("Payment Entry", p.get("parent"), False, 4)
                            link_nodes("Sales Invoice", jo.get("sales_invoice"), "Payment Entry", p.get("parent"), "Payment Received", "accounting")
            elif plate:
                for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate}, fields=["name"], order_by="creation desc", limit=2):
                    get_node("Vehicle Job Order", j.get("name"), False, 2)
                    link_nodes("Vehicle Estimate", docname, "Vehicle Job Order", j.get("name"), "Vehicle JO", "flow")

        elif doctype == "Vehicle Inspection":
            if plate:
                for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate}, fields=["name", "estimate", "sales_invoice"], order_by="creation desc", limit=2):
                    get_node("Vehicle Job Order", j.get("name"), False, 2)
                    link_nodes("Vehicle Inspection", docname, "Vehicle Job Order", j.get("name"), "Work Executed", "flow")
                    if j.get("estimate") and frappe.db.exists("Vehicle Estimate", j.get("estimate")):
                        get_node("Vehicle Estimate", j.get("estimate"), False, 1)
                        link_nodes("Vehicle Inspection", docname, "Vehicle Estimate", j.get("estimate"), "Estimate Quoted", "flow")
                    if j.get("sales_invoice") and frappe.db.exists("Sales Invoice", j.get("sales_invoice")):
                        get_node("Sales Invoice", j.get("sales_invoice"), False, 3)
                        link_nodes("Vehicle Job Order", j.get("name"), "Sales Invoice", j.get("sales_invoice"), "Billed SI", "flow")

        elif doctype in ("Vehicle POS Invoice", "POS Invoice"):
            if doctype == "Vehicle POS Invoice":
                vp = frappe.get_doc("Vehicle POS Invoice", docname)
                if vp.get("pos_invoice") and frappe.db.exists("POS Invoice", vp.get("pos_invoice")):
                    get_node("POS Invoice", vp.get("pos_invoice"), False, 3)
                    link_nodes("Vehicle POS Invoice", docname, "POS Invoice", vp.get("pos_invoice"), "Fiscal POS Record", "flow")
            if plate:
                for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate}, fields=["name"], order_by="creation desc", limit=2):
                    get_node("Vehicle Job Order", j.get("name"), False, 2)
                    link_nodes("Vehicle Job Order", j.get("name"), doctype, docname, "Workshop Billing", "flow")

        elif doctype == "Sales Invoice":
            for j in frappe.get_all("Vehicle Job Order", filters={"sales_invoice": docname}, fields=["name", "estimate"]):
                get_node("Vehicle Job Order", j.get("name"), False, 2)
                link_nodes("Vehicle Job Order", j.get("name"), "Sales Invoice", docname, "Billed via SI", "flow")
                if j.get("estimate") and frappe.db.exists("Vehicle Estimate", j.get("estimate")):
                    get_node("Vehicle Estimate", j.get("estimate"), False, 1)
                    link_nodes("Vehicle Estimate", j.get("estimate"), "Vehicle Job Order", j.get("name"), "Converted to JO", "flow")
            for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": docname}, fields=["parent"]):
                if frappe.db.exists("Payment Entry", p.get("parent")):
                    get_node("Payment Entry", p.get("parent"), False, 4)
                    link_nodes("Sales Invoice", docname, "Payment Entry", p.get("parent"), "Payment Received", "accounting")

        elif doctype == "Customer Vehicle":
            for i in frappe.get_all("Vehicle Inspection", filters={"vehicle": docname}, fields=["name"], limit=3):
                get_node("Vehicle Inspection", i.get("name"), False, 1)
                link_nodes("Customer Vehicle", docname, "Vehicle Inspection", i.get("name"), "Inspection", "flow")
            for e in frappe.get_all("Vehicle Estimate", filters={"vehicle": docname}, fields=["name"], limit=3):
                get_node("Vehicle Estimate", e.get("name"), False, 1)
                link_nodes("Customer Vehicle", docname, "Vehicle Estimate", e.get("name"), "Estimate", "flow")
            for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": docname}, fields=["name", "sales_invoice"], limit=4):
                get_node("Vehicle Job Order", j.get("name"), False, 2)
                link_nodes("Customer Vehicle", docname, "Vehicle Job Order", j.get("name"), "Job Order", "flow")
                if j.get("sales_invoice") and frappe.db.exists("Sales Invoice", j.get("sales_invoice")):
                    get_node("Sales Invoice", j.get("sales_invoice"), False, 3)
                    link_nodes("Vehicle Job Order", j.get("name"), "Sales Invoice", j.get("sales_invoice"), "Invoice", "flow")
            for vp in frappe.get_all("Vehicle POS Invoice", filters={"vehicle": docname}, fields=["name"], limit=3):
                get_node("Vehicle POS Invoice", vp.get("name"), False, 3)
                link_nodes("Customer Vehicle", docname, "Vehicle POS Invoice", vp.get("name"), "POS Receipt", "flow")

    # Deduplicate transaction value and calculate true net outstanding
    invoices = [n for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "POS Invoice", "Vehicle POS Invoice")]
    invoiced_jo_names = []
    for inv in invoices:
        for j in frappe.get_all("Vehicle Job Order", filters={"sales_invoice": inv.get("name")}, fields=["name"]):
            invoiced_jo_names.append(j.get("name"))

    unbilled_jos = [n for n in nodes_dict.values() if n.get("doctype") == "Vehicle Job Order" and n.get("name") not in invoiced_jo_names]
    billable_nodes = invoices + unbilled_jos

    if billable_nodes:
        tot_val = sum([float(n.get("grand_total") or 0) for n in billable_nodes])
        payment_entries = [n for n in nodes_dict.values() if n.get("doctype") == "Payment Entry"]
        if payment_entries:
            pe_paid = sum([float(n.get("grand_total") or 0) for n in payment_entries])
            pos_paid = sum([float(n.get("paid_amount") or 0) for n in billable_nodes if n.get("doctype") in ("POS Invoice", "Vehicle POS Invoice")])
            tot_paid = pe_paid + pos_paid
        else:
            tot_paid = sum([float(n.get("paid_amount") or 0) for n in billable_nodes])
        tot_paid = min(tot_val, tot_paid) if tot_val > 0 else tot_paid
        tot_outst = max(0.0, tot_val - tot_paid)
    else:
        tot_val = sum([float(n.get("grand_total") or 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Vehicle POS Invoice", "POS Invoice")])
        tot_paid = sum([float(n.get("paid_amount") or 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Payment Entry", "Vehicle POS Invoice")])
        tot_outst = max(0.0, tot_val - tot_paid)

    # -------------------------------------------------------------
    # Full Accounting & General Ledger Double-Entry Extraction
    # -------------------------------------------------------------
    accounting_vouchers = [n.get("name") for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "Payment Entry", "POS Invoice", "Vehicle POS Invoice", "Journal Entry")]
    gl_entries_list = []
    
    if accounting_vouchers:
        gles = frappe.get_all("GL Entry", 
            filters={"voucher_no": ["in", accounting_vouchers], "is_cancelled": 0}, 
            fields=["name", "voucher_type", "voucher_no", "account", "debit", "credit", "posting_date", "cost_center", "remarks"],
            order_by="posting_date asc, creation asc"
        )
        for gl in gles:
            gl_entries_list.append({
                "id": gl.get("name"),
                "voucher_type": gl.get("voucher_type"),
                "voucher_no": gl.get("voucher_no"),
                "account": gl.get("account"),
                "debit": float(gl.get("debit") or 0),
                "credit": float(gl.get("credit") or 0),
                "posting_date": str(gl.get("posting_date") or ""),
                "cost_center": gl.get("cost_center") or "",
                "remarks": gl.get("remarks") or ""
            })

    total_debit = sum([g.get("debit") or 0 for g in gl_entries_list])
    total_credit = sum([g.get("credit") or 0 for g in gl_entries_list])

    ple_list = []
    if accounting_vouchers:
        ples = frappe.get_all("Payment Ledger Entry",
            filters={"voucher_no": ["in", accounting_vouchers], "delinked": 0},
            fields=["name", "voucher_type", "voucher_no", "against_voucher_type", "against_voucher_no", "account", "party_type", "party", "amount"],
            order_by="creation asc"
        )
        for p in ples:
            ple_list.append({
                "name": p.get("name"),
                "voucher_type": p.get("voucher_type"),
                "voucher_no": p.get("voucher_no"),
                "against_voucher_type": p.get("against_voucher_type") or "",
                "against_voucher_no": p.get("against_voucher_no") or "",
                "account": p.get("account") or "",
                "party": p.get("party") or "",
                "amount": float(p.get("amount") or 0)
            })

    vouchers_gl_map = {}
    for g in gl_entries_list:
        v_key = str(g.get("voucher_type")) + "::" + str(g.get("voucher_no"))
        if v_key not in vouchers_gl_map:
            vouchers_gl_map[v_key] = []
        vouchers_gl_map[v_key].append(g)

    accounting_summary = {
        "gl_entries": gl_entries_list,
        "payment_ledger": ple_list,
        "vouchers_gl_map": vouchers_gl_map,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "is_balanced": bool(round(total_debit, 2) == round(total_credit, 2)),
        "vouchers_count": len(accounting_vouchers)
    }

    summary_obj = {
        "focal_doctype": doctype,
        "focal_docname": docname,
        "vehicle_plate": plate,
        "customer_name": cust,
        "total_nodes": len(nodes_dict),
        "total_edges": len(edges),
        "total_transaction_value": tot_val,
        "total_paid_value": tot_paid,
        "total_outstanding_value": tot_outst,
        "status_flow_complete": bool(tot_outst == 0 and tot_val > 0)
    }

    frappe.response['message'] = {
        "nodes": list(nodes_dict.values()),
        "edges": edges,
        "summary": summary_obj,
        "items": all_items,
        "accounting": accounting_summary
    }
except Exception as e:
    frappe.response['message'] = {
        "nodes": [],
        "edges": [],
        "summary": {"error": str(e)},
        "items": [],
        "accounting": {}
    }
"""

res = s.put(f'{URL}/api/resource/Server%20Script/VM%20SAP%20Relationship%20Map%20API', json={
    "name": "VM SAP Relationship Map API",
    "script_type": "API",
    "api_method": "vm_relationship_map",
    "disabled": 0,
    "script": server_script_code
}, timeout=45)
print("Updated Server Script:", res.status_code)

# 2. Client Script
with open('c:/Users/josem/erpnext-system/frappe-bench/apps/vehicle_management/vehicle_management/public/js/vehicle_relationship_map.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

with open('c:/Users/josem/erpnext-system/frappe-bench/apps/vehicle_management/vehicle_management/public/css/vehicle_management_desk.css', 'r', encoding='utf-8') as f:
    css_code = f.read()

css_clean = css_code.replace('`', '\\`')

full_client_script = f"""
frappe.provide('frappe.ui.form');

if (!$('#sap-rel-map-styles').length) {{
  $('head').append(`<style id="sap-rel-map-styles">{css_clean}</style>`);
}}

{js_code}
"""

client_script_payload = {
    "name": "VM SAP Relationship Map Client",
    "dt": "Vehicle Job Order",
    "view": "Form",
    "script_type": "DocType Event",
    "enabled": 1,
    "script": full_client_script
}

try:
    check_cs = s.get(f'{URL}/api/resource/Client%20Script/VM%20SAP%20Relationship%20Map%20Client', timeout=45)
    if check_cs.status_code == 200:
        cs_res = s.put(f'{URL}/api/resource/Client%20Script/VM%20SAP%20Relationship%20Map%20Client', json=client_script_payload, timeout=45)
        print("Updated Client Script:", cs_res.status_code)
    else:
        cs_res = s.post(f'{URL}/api/resource/Client%20Script', json=client_script_payload, timeout=45)
        print("Created Client Script:", cs_res.status_code)
except Exception as e:
    print("Client Script error:", str(e))

# 3. Test API Call
test_res = s.get(f'{URL}/api/method/vm_relationship_map', params={'doctype': 'Sales Invoice', 'docname': 'ACC-SINV-2026-00166'}, timeout=45)
data = test_res.json().get('message', {})
print("\n=== TEST ACC-SINV-2026-00166 ===")
print("Summary:", json.dumps(data.get('summary', {}), indent=2))
print(f"Total Nodes: {len(data.get('nodes', []))}")
print(f"Total Items: {len(data.get('items', []))}")
for it in data.get('items', []):
    print(f"  [{it.get('doc_type')}] {it.get('type')}: {it.get('item_code')} | Qty: {it.get('qty')} | Amount: {it.get('amount')}")
print(f"Accounting GL Entries: {len(data.get('accounting', {}).get('gl_entries', []))}")
for gl in data.get('accounting', {}).get('gl_entries', []):
    print(f"  [{gl.get('voucher_type')} {gl.get('voucher_no')}] {gl.get('account')} | Dr: {gl.get('debit')} | Cr: {gl.get('credit')}")
