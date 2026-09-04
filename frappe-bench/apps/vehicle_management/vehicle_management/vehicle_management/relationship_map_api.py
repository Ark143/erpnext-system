import frappe
from frappe import _

@frappe.whitelist()
def get_relationship_map(doctype=None, docname=None, vehicle=None, customer=None):
    """
    VMS Relationship Map backend engine.
    Traces upstream and downstream transactions across Vehicle Management, ERPNext Accounting,
    and Inventory modules. Provides full Document Flow, Related Items Matrix, and Double-Entry Accounting Flow.
    """
    if not doctype and not docname and not vehicle and not customer:
        latest_jo = frappe.get_all("Vehicle Job Order", fields=["name"], order_by="creation desc", limit=1)
        if latest_jo:
            doctype = "Vehicle Job Order"
            docname = latest_jo[0].name
        else:
            return {"nodes": [], "edges": [], "summary": {}, "items": [], "accounting": {}}

    if vehicle and not doctype:
        doctype = "Customer Vehicle"
        docname = vehicle
    elif customer and not doctype:
        doctype = "Customer"
        docname = customer

    nodes_dict = {}
    edges = []
    all_items = []

    def add_node(dt, name, is_current=False, level=0):
        key = f"{dt}::{name}"
        if key in nodes_dict:
            if is_current:
                nodes_dict[key]["is_current"] = True
            return nodes_dict[key]

        if not frappe.db.exists(dt, name):
            return None

        doc = frappe.get_doc(dt, name)
        
        # Status calculation
        status = getattr(doc, "status", None) or getattr(doc, "workflow_state", None) or "Active"
        docstatus = getattr(doc, "docstatus", 0)
        if docstatus == 0:
            status_display = status if status != "Active" else "Draft"
        elif docstatus == 1:
            status_display = status if status not in ("Draft", "Active") else "Submitted"
        elif docstatus == 2:
            status_display = "Cancelled"
        else:
            status_display = status

        grand_total = float(getattr(doc, "grand_total", 0) or getattr(doc, "total_amount", 0) or getattr(doc, "paid_amount", 0) or getattr(doc, "received_amount", 0) or 0)
        
        if dt == "Sales Invoice":
            si_out = getattr(doc, "outstanding_amount", None)
            if si_out is not None:
                outstanding = max(0.0, float(si_out))
            else:
                ples = frappe.get_all("Payment Ledger Entry", filters={"against_voucher_no": name, "delinked": 0}, fields=["amount"])
                if ples:
                    outstanding = max(0.0, sum([float(p.amount) for p in ples]))
                else:
                    outstanding = grand_total
            paid_amount = max(0.0, grand_total - outstanding)
            if outstanding <= 0.001:
                outstanding = 0.0
                paid_amount = grand_total
                status_display = "Paid"
        elif dt == "Payment Entry":
            paid_amount = grand_total
            outstanding = 0.0
        elif dt == "Vehicle Job Order":
            si_no = getattr(doc, "sales_invoice", None)
            if si_no and frappe.db.exists("Sales Invoice", si_no):
                outstanding = 0.0
                si_doc = frappe.get_doc("Sales Invoice", si_no)
                si_out = getattr(si_doc, "outstanding_amount", None)
                if (si_out is not None and float(si_out) <= 0.001) or getattr(si_doc, "status", "") == "Paid":
                    paid_amount = grand_total
                else:
                    paid_amount = float(getattr(doc, "paid_amount", 0) or 0)
            else:
                paid_amount = float(getattr(doc, "paid_amount", 0) or 0)
                outstanding = max(0.0, grand_total - paid_amount)
        elif dt in ("Vehicle POS Invoice", "POS Invoice"):
            paid_amount = float(getattr(doc, "paid_amount", 0) or grand_total)
            outstanding = max(0.0, grand_total - paid_amount)
        else:
            paid_amount = float(getattr(doc, "paid_amount", 0) or getattr(doc, "total_allocated_amount", 0) or 0)
            doc_out = getattr(doc, "outstanding_amount", None)
            if doc_out is not None:
                outstanding = max(0.0, float(doc_out))
            else:
                outstanding = max(0.0, grand_total - paid_amount)
        
        posting_date = str(getattr(doc, "posting_date", "") or getattr(doc, "job_order_date", "") or getattr(doc, "estimate_date", "") or getattr(doc, "inspection_date", "") or getattr(doc, "transaction_date", "") or getattr(doc, "creation", ""))[:10]
        posting_time = str(getattr(doc, "posting_time", "") or "")

        veh_plate = getattr(doc, "plate_no", None) or getattr(doc, "vehicle", None) or getattr(doc, "custom_vehicle_plate", None)
        cust_name = getattr(doc, "customer_name", None) or getattr(doc, "customer", None) or getattr(doc, "party_name", None)
        company = getattr(doc, "company", "") or "ULTRA MRF"

        # Line items extraction
        items = []
        if hasattr(doc, "services") and doc.services:
            for s in doc.services:
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Labor / Service",
                    "category": "service",
                    "item_code": getattr(s, "service_name", "") or getattr(s, "description", "Service"),
                    "description": getattr(s, "description", "") or getattr(s, "service_name", ""),
                    "qty": float(getattr(s, "hours", 1) or 1),
                    "uom": "Hrs",
                    "rate": float(getattr(s, "rate", 0) or 0),
                    "amount": float(getattr(s, "total_amount", 0) or (getattr(s, "hours", 1) * getattr(s, "rate", 0))),
                    "account": "Service Revenue"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        if hasattr(doc, "parts") and doc.parts:
            for p in doc.parts:
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Spare Part / Material",
                    "category": "part",
                    "item_code": getattr(p, "part_no", "") or getattr(p, "item_code", "") or getattr(p, "item_name", "Part"),
                    "description": getattr(p, "item_name", "") or getattr(p, "description", ""),
                    "qty": float(getattr(p, "qty", 1) or 1),
                    "uom": getattr(p, "uom", "PC") or "PC",
                    "rate": float(getattr(p, "rate", 0) or 0),
                    "amount": float(getattr(p, "amount", 0) or (getattr(p, "qty", 1) * getattr(p, "rate", 0))),
                    "account": "Parts & Inventory"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        if hasattr(doc, "items") and doc.items:
            for it in doc.items:
                grp = (getattr(it, "item_group", "") or "").lower()
                nm = (getattr(it, "item_name", "") or "").lower()
                if "service" in grp or "labor" in grp or "service" in nm or "labor" in nm:
                    cat_name = "Billed Service / Labor"
                    cat_key = "service"
                else:
                    cat_name = "Billed Spare Part / Product"
                    cat_key = "part"

                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": cat_name,
                    "category": cat_key,
                    "item_code": getattr(it, "item_code", "") or getattr(it, "item_name", "Item"),
                    "description": getattr(it, "description", "") or getattr(it, "item_name", ""),
                    "qty": float(getattr(it, "qty", 1) or 1),
                    "uom": getattr(it, "uom", "PC") or "PC",
                    "rate": float(getattr(it, "rate", 0) or 0),
                    "amount": float(getattr(it, "amount", 0) or (getattr(it, "qty", 1) * getattr(it, "rate", 0))),
                    "account": getattr(it, "income_account", "") or getattr(it, "expense_account", "") or "Sales Revenue"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        if hasattr(doc, "references") and doc.references:
            for ref in doc.references:
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Payment Allocation",
                    "category": "payment",
                    "item_code": getattr(ref, "reference_name", ""),
                    "description": f"Allocated Payment for {getattr(ref, 'reference_doctype', '')} {getattr(ref, 'reference_name', '')}",
                    "qty": 1.0,
                    "uom": "Voucher",
                    "rate": float(getattr(ref, "allocated_amount", 0) or 0),
                    "amount": float(getattr(ref, "allocated_amount", 0) or 0),
                    "account": "Accounts Receivable Offset"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        node = {
            "id": key,
            "doctype": dt,
            "name": name,
            "title": f"{dt}: {name}",
            "status": status_display,
            "raw_status": status,
            "docstatus": docstatus,
            "grand_total": grand_total,
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding,
            "currency": getattr(doc, "currency", "PHP") or "PHP",
            "posting_date": posting_date,
            "posting_time": posting_time,
            "vehicle": veh_plate,
            "customer": cust_name,
            "company": company,
            "is_current": is_current,
            "level": level,
            "items_count": len(items),
            "items": items[:25],
            "remarks": getattr(doc, "remarks", "") or getattr(doc, "customer_complaint", "") or getattr(doc, "general_remarks", "") or ""
        }
        nodes_dict[key] = node
        return node

    def add_edge(from_dt, from_name, to_dt, to_name, label, edge_type="flow"):
        if not from_name or not to_name:
            return
        from_id = f"{from_dt}::{from_name}"
        to_id = f"{to_dt}::{to_name}"
        for e in edges:
            if e["from"] == from_id and e["to"] == to_id and e["label"] == label:
                return
        edges.append({
            "from": from_id,
            "to": to_id,
            "label": label,
            "type": edge_type
        })

    # 1. Add focal node
    focal_node = add_node(doctype, docname, is_current=True, level=2)
    if not focal_node:
        return {"nodes": [], "edges": [], "summary": {}, "items": [], "accounting": {}}

    plate_no = focal_node.get("vehicle")
    customer_name = focal_node.get("customer")

    if doctype == "Customer Vehicle":
        plate_no = docname
        veh_doc = frappe.get_doc("Customer Vehicle", docname)
        if veh_doc.customer and frappe.db.exists("Customer", veh_doc.customer):
            add_node("Customer", veh_doc.customer, level=0)
            add_edge("Customer", veh_doc.customer, "Customer Vehicle", docname, "Owns Vehicle", "reference")

    if doctype == "Customer":
        customer_name = docname

    if plate_no and frappe.db.exists("Customer Vehicle", plate_no):
        add_node("Customer Vehicle", plate_no, level=0)
        if doctype not in ("Customer Vehicle", "Customer"):
            add_edge("Customer Vehicle", plate_no, doctype, docname, "Vehicle", "reference")
        
        veh_doc = frappe.get_doc("Customer Vehicle", plate_no)
        if veh_doc.customer and frappe.db.exists("Customer", veh_doc.customer):
            add_node("Customer", veh_doc.customer, level=0)
            add_edge("Customer", veh_doc.customer, "Customer Vehicle", plate_no, "Owns Vehicle", "reference")

    if customer_name and frappe.db.exists("Customer", customer_name):
        add_node("Customer", customer_name, level=0)
        if doctype != "Customer":
            add_edge("Customer", customer_name, doctype, docname, "Customer", "reference")

    # Document specifics
    if doctype == "Vehicle Job Order":
        jo = frappe.get_doc("Vehicle Job Order", docname)
        if jo.estimate and frappe.db.exists("Vehicle Estimate", jo.estimate):
            add_node("Vehicle Estimate", jo.estimate, level=1)
            add_edge("Vehicle Estimate", jo.estimate, "Vehicle Job Order", docname, "Converted to JO", "flow")
        elif plate_no:
            for est in frappe.get_all("Vehicle Estimate", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                add_node("Vehicle Estimate", est.name, level=1)
                add_edge("Vehicle Estimate", est.name, "Vehicle Job Order", docname, "Referenced Estimate", "reference")

        # Upstream: Vehicle Inspection
        if plate_no:
            for insp in frappe.get_all("Vehicle Inspection", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                add_node("Vehicle Inspection", insp.name, level=1)
                add_edge("Vehicle Inspection", insp.name, "Vehicle Job Order", docname, "Diagnostic Inspection", "flow")

        # Downstream: Sales Invoice
        if jo.sales_invoice and frappe.db.exists("Sales Invoice", jo.sales_invoice):
            add_node("Sales Invoice", jo.sales_invoice, level=3)
            add_edge("Vehicle Job Order", docname, "Sales Invoice", jo.sales_invoice, "Billed via SI", "flow")
            
            for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": jo.sales_invoice}, fields=["parent"]):
                if frappe.db.exists("Payment Entry", p.parent):
                    add_node("Payment Entry", p.parent, level=4)
                    add_edge("Sales Invoice", jo.sales_invoice, "Payment Entry", p.parent, "Payment Received", "accounting")

        # Downstream: Vehicle POS Invoice & POS Invoice
        for vp in frappe.get_all("Vehicle POS Invoice", filters={"vehicle": plate_no}, fields=["name", "pos_invoice"], order_by="creation desc", limit=2):
            add_node("Vehicle POS Invoice", vp.name, level=3)
            add_edge("Vehicle Job Order", docname, "Vehicle POS Invoice", vp.name, "POS Counter Bill", "flow")
            if vp.pos_invoice and frappe.db.exists("POS Invoice", vp.pos_invoice):
                add_node("POS Invoice", vp.pos_invoice, level=3)
                add_edge("Vehicle POS Invoice", vp.name, "POS Invoice", vp.pos_invoice, "Fiscal POS Record", "flow")

    elif doctype == "Vehicle Estimate":
        est = frappe.get_doc("Vehicle Estimate", docname)
        if est.job_order and frappe.db.exists("Vehicle Job Order", est.job_order):
            add_node("Vehicle Job Order", est.job_order, level=2)
            add_edge("Vehicle Estimate", docname, "Vehicle Job Order", est.job_order, "Converted to JO", "flow")
            jo = frappe.get_doc("Vehicle Job Order", est.job_order)
            if jo.sales_invoice and frappe.db.exists("Sales Invoice", jo.sales_invoice):
                add_node("Sales Invoice", jo.sales_invoice, level=3)
                add_edge("Vehicle Job Order", est.job_order, "Sales Invoice", jo.sales_invoice, "Billed via SI", "flow")
                for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": jo.sales_invoice}, fields=["parent"]):
                    if frappe.db.exists("Payment Entry", p.parent):
                        add_node("Payment Entry", p.parent, level=4)
                        add_edge("Sales Invoice", jo.sales_invoice, "Payment Entry", p.parent, "Payment Received", "accounting")
        elif plate_no:
            for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                add_node("Vehicle Job Order", j.name, level=2)
                add_edge("Vehicle Estimate", docname, "Vehicle Job Order", j.name, "Vehicle JO", "flow")

    elif doctype == "Vehicle Inspection":
        if plate_no:
            for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name", "estimate", "sales_invoice"], order_by="creation desc", limit=2):
                add_node("Vehicle Job Order", j.name, level=2)
                add_edge("Vehicle Inspection", docname, "Vehicle Job Order", j.name, "Work Executed", "flow")
                if j.estimate and frappe.db.exists("Vehicle Estimate", j.estimate):
                    add_node("Vehicle Estimate", j.estimate, level=1)
                    add_edge("Vehicle Inspection", docname, "Vehicle Estimate", j.estimate, "Estimate Quoted", "flow")
                if j.sales_invoice and frappe.db.exists("Sales Invoice", j.sales_invoice):
                    add_node("Sales Invoice", j.sales_invoice, level=3)
                    add_edge("Vehicle Job Order", j.name, "Sales Invoice", j.sales_invoice, "Billed via SI", "flow")

    elif doctype in ("Vehicle POS Invoice", "POS Invoice"):
        if doctype == "Vehicle POS Invoice":
            vp = frappe.get_doc("Vehicle POS Invoice", docname)
            if vp.pos_invoice and frappe.db.exists("POS Invoice", vp.pos_invoice):
                add_node("POS Invoice", vp.pos_invoice, level=3)
                add_edge("Vehicle POS Invoice", docname, "POS Invoice", vp.pos_invoice, "Fiscal POS Record", "flow")
        if plate_no:
            for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                add_node("Vehicle Job Order", j.name, level=2)
                add_edge("Vehicle Job Order", j.name, doctype, docname, "Workshop Billing", "flow")

    elif doctype == "Sales Invoice":
        for j in frappe.get_all("Vehicle Job Order", filters={"sales_invoice": docname}, fields=["name", "estimate"]):
            add_node("Vehicle Job Order", j.name, level=2)
            add_edge("Vehicle Job Order", j.name, "Sales Invoice", docname, "Billed via SI", "flow")
            if j.estimate and frappe.db.exists("Vehicle Estimate", j.estimate):
                add_node("Vehicle Estimate", j.estimate, level=1)
                add_edge("Vehicle Estimate", j.estimate, "Vehicle Job Order", j.name, "Converted to JO", "flow")
            
        for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": docname}, fields=["parent"]):
            if frappe.db.exists("Payment Entry", p.parent):
                add_node("Payment Entry", p.parent, level=4)
                add_edge("Sales Invoice", docname, "Payment Entry", p.parent, "Payment Received", "accounting")

    elif doctype == "Customer Vehicle":
        for i in frappe.get_all("Vehicle Inspection", filters={"vehicle": docname}, fields=["name"], limit=3):
            add_node("Vehicle Inspection", i.name, level=1)
            add_edge("Customer Vehicle", docname, "Vehicle Inspection", i.name, "Inspection", "flow")

        for e in frappe.get_all("Vehicle Estimate", filters={"vehicle": docname}, fields=["name"], limit=3):
            add_node("Vehicle Estimate", e.name, level=1)
            add_edge("Customer Vehicle", docname, "Vehicle Estimate", e.name, "Estimate", "flow")

        for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": docname}, fields=["name", "sales_invoice"], limit=4):
            add_node("Vehicle Job Order", j.name, level=2)
            add_edge("Customer Vehicle", docname, "Vehicle Job Order", j.name, "Job Order", "flow")
            if j.sales_invoice and frappe.db.exists("Sales Invoice", j.sales_invoice):
                add_node("Sales Invoice", j.sales_invoice, level=3)
                add_edge("Vehicle Job Order", j.name, "Sales Invoice", j.sales_invoice, "Invoice", "flow")

        for vp in frappe.get_all("Vehicle POS Invoice", filters={"vehicle": docname}, fields=["name"], limit=3):
            add_node("Vehicle POS Invoice", vp.name, level=3)
            add_edge("Customer Vehicle", docname, "Vehicle POS Invoice", vp.name, "POS Receipt", "flow")

    # -------------------------------------------------------------
    # Calculate Graph Financial Summary (Deduplicating billed JOs)
    # -------------------------------------------------------------
    invoices = [n for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "POS Invoice", "Vehicle POS Invoice")]
    invoiced_jo_names = set()
    for inv in invoices:
        for j in frappe.get_all("Vehicle Job Order", filters={"sales_invoice": inv.get("name")}, fields=["name"]):
            invoiced_jo_names.add(j.name)

    unbilled_jos = [n for n in nodes_dict.values() if n.get("doctype") == "Vehicle Job Order" and n.get("name") not in invoiced_jo_names]
    billable_nodes = invoices + unbilled_jos

    if billable_nodes:
        total_val = sum([n.get("grand_total", 0) for n in billable_nodes])
        payment_entries = [n for n in nodes_dict.values() if n.get("doctype") == "Payment Entry"]
        if payment_entries:
            pe_paid = sum([n.get("grand_total", 0) for n in payment_entries])
            pos_paid = sum([n.get("paid_amount", 0) for n in billable_nodes if n.get("doctype") in ("POS Invoice", "Vehicle POS Invoice")])
            total_paid = pe_paid + pos_paid
        else:
            total_paid = sum([n.get("paid_amount", 0) for n in billable_nodes])
            
        total_paid = min(total_val, total_paid) if total_val > 0 else total_paid
        total_outstanding = max(0.0, total_val - total_paid)
    else:
        total_val = sum([n.get("grand_total", 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Vehicle POS Invoice", "POS Invoice")])
        total_paid = sum([n.get("paid_amount", 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Payment Entry", "Vehicle POS Invoice")])
        total_outstanding = max(0.0, total_val - total_paid)

    # -------------------------------------------------------------
    # Deduplicated Item Matrix & Metrics
    # -------------------------------------------------------------
    unique_parts_map = {}
    unique_services_map = {}
    for it in all_items:
        code = it.get("item_code") or it.get("description")
        amt = float(it.get("amount") or 0)
        qty = float(it.get("qty") or 1)
        cat = it.get("category", "")
        # Deduplicate across Job Order vs Sales Invoice stages
        if cat == "part":
            if code not in unique_parts_map or it.get("doc_type") in ("Sales Invoice", "POS Invoice"):
                unique_parts_map[code] = {"amount": amt, "qty": qty, "item": it}
        elif cat == "service":
            if code not in unique_services_map or it.get("doc_type") in ("Sales Invoice", "POS Invoice"):
                unique_services_map[code] = {"amount": amt, "qty": qty, "item": it}

    dedup_parts_total = sum([p["amount"] for p in unique_parts_map.values()])
    dedup_services_total = sum([s["amount"] for s in unique_services_map.values()])

    # -------------------------------------------------------------
    # Full Accounting & General Ledger Double-Entry Extraction
    # -------------------------------------------------------------
    accounting_vouchers = [n["name"] for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "Payment Entry", "POS Invoice", "Vehicle POS Invoice", "Journal Entry")]
    gl_entries_list = []

    # Build a strict map: voucher_no -> expected doctype from our relationship graph.
    # This is used to discard cross-type GL entries (e.g. Payment Entry clearing rows
    # that ERPNext stores under the Sales Invoice voucher_no).
    voucher_doctype_map = {
        n["name"]: n["doctype"]
        for n in nodes_dict.values()
        if n.get("doctype") in ("Sales Invoice", "Payment Entry", "POS Invoice", "Vehicle POS Invoice", "Journal Entry")
    }

    # -----------------------------------------------------------------------
    # POS Invoice → Sales Invoice consolidation guard
    # -----------------------------------------------------------------------
    # ERPNext posts FULL GL entries on the POS Invoice AND again on the
    # consolidated Sales Invoice (created via POS Closing Entry).
    # Showing both doubles every revenue/receivable line.
    # Rule: if a POS Invoice has already been consolidated into a Sales Invoice
    # that exists in our graph, exclude that POS Invoice from the GL fetch —
    # the Sales Invoice is the authoritative accounting document.
    # Standalone POS Invoices (not yet consolidated) are kept as-is.
    consolidated_pos_to_skip = set()
    si_names_in_graph = {
        n["name"] for n in nodes_dict.values()
        if n.get("doctype") == "Sales Invoice"
    }
    pos_names_in_graph = {
        n["name"] for n in nodes_dict.values()
        if n.get("doctype") in ("POS Invoice", "Vehicle POS Invoice")
    }
    if pos_names_in_graph and si_names_in_graph:
        # Check if any POS Invoice in our graph is referenced by a Sales Invoice
        # in our graph (i.e. it was consolidated already).
        try:
            pos_si_links = frappe.get_all(
                "POS Invoice Merge Log Detail",
                filters={"pos_invoice": ["in", list(pos_names_in_graph)]},
                fields=["pos_invoice", "parent"]
            )
            for link in pos_si_links:
                # 'parent' is the POS Invoice Merge Log; follow to the SI
                merge_log = frappe.db.get_value(
                    "POS Invoice Merge Log", link.parent, "consolidated_invoice"
                )
                if merge_log and merge_log in si_names_in_graph:
                    consolidated_pos_to_skip.add(link.pos_invoice)
        except Exception:
            pass  # Doctype may not exist; safe to skip

    # Remove consolidated POS Invoices from accounting_vouchers
    accounting_vouchers = [v for v in accounting_vouchers if v not in consolidated_pos_to_skip]
    # Also remove them from the type map so the voucher_type filter works correctly
    for pos_name in consolidated_pos_to_skip:
        voucher_doctype_map.pop(pos_name, None)

    if accounting_vouchers:
        gles = frappe.get_all("GL Entry", 
            filters={"voucher_no": ["in", accounting_vouchers], "is_cancelled": 0}, 
            fields=["name", "voucher_type", "voucher_no", "account", "debit", "credit", "posting_date", "cost_center", "remarks"],
            order_by="posting_date asc, creation asc"
        )
        for gl in gles:
            # Skip GL entries whose voucher_type doesn't match the expected doctype
            # for that voucher_no.  ERPNext can store Payment Entry reconciliation
            # rows under the Sales Invoice's voucher_no which would double the total.
            expected_doctype = voucher_doctype_map.get(gl.voucher_no)
            if expected_doctype and gl.voucher_type != expected_doctype:
                continue
            gl_entries_list.append({
                "id": gl.name,
                "voucher_type": gl.voucher_type,
                "voucher_no": gl.voucher_no,
                "account": gl.account,
                "debit": float(gl.debit or 0),
                "credit": float(gl.credit or 0),
                "posting_date": str(gl.posting_date or ""),
                "cost_center": gl.cost_center or "",
                "remarks": gl.remarks or ""
            })

    total_debit = sum([g["debit"] for g in gl_entries_list])
    total_credit = sum([g["credit"] for g in gl_entries_list])

    # Payment Ledger Entries
    ple_list = []
    if accounting_vouchers:
        ples = frappe.get_all("Payment Ledger Entry",
            filters={"voucher_no": ["in", accounting_vouchers], "delinked": 0},
            fields=["name", "voucher_type", "voucher_no", "against_voucher_type", "against_voucher_no", "account", "party_type", "party", "amount"],
            order_by="creation asc"
        )
        for p in ples:
            ple_list.append({
                "name": p.name,
                "voucher_type": p.voucher_type,
                "voucher_no": p.voucher_no,
                "against_voucher_type": p.against_voucher_type or "",
                "against_voucher_no": p.against_voucher_no or "",
                "account": p.account or "",
                "party": p.party or "",
                "amount": float(p.amount or 0)
            })

    # Group GL entries by Voucher for direct accounting breakdown cards
    vouchers_gl_map = {}
    for g in gl_entries_list:
        v_key = f"{g['voucher_type']}::{g['voucher_no']}"
        if v_key not in vouchers_gl_map:
            vouchers_gl_map[v_key] = []
        vouchers_gl_map[v_key].append(g)

    # Net Revenue and Collections for clean accounting KPIs
    total_invoice_revenue = sum([
        float(g["credit"] or 0) 
        for g in gl_entries_list 
        if g.get("voucher_type") in ("Sales Invoice", "POS Invoice", "Vehicle POS Invoice") 
        and ("sales" in (g.get("account") or "").lower() or "income" in (g.get("account") or "").lower() or "revenue" in (g.get("account") or "").lower())
    ])
    if total_invoice_revenue == 0:
        total_invoice_revenue = sum([n.get("grand_total", 0) for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "POS Invoice", "Vehicle POS Invoice")])

    total_payments_collected = sum([
        float(g["debit"] or 0)
        for g in gl_entries_list
        if g.get("voucher_type") in ("Payment Entry", "Journal Entry")
        and ("cash" in (g.get("account") or "").lower() or "bank" in (g.get("account") or "").lower() or "undeposited" in (g.get("account") or "").lower())
    ])
    if total_payments_collected == 0:
        total_payments_collected = sum([n.get("grand_total", 0) for n in nodes_dict.values() if n.get("doctype") == "Payment Entry"])

    accounting_summary = {
        "gl_entries": gl_entries_list,
        "payment_ledger": ple_list,
        "vouchers_gl_map": vouchers_gl_map,
        "total_revenue": total_invoice_revenue,
        "total_collected": total_payments_collected,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "is_balanced": round(total_debit, 2) == round(total_credit, 2),
        "vouchers_count": len(accounting_vouchers)
    }

    # Company Info & Registered Address for Audit / Print
    company_name = ""
    for n in nodes_dict.values():
        if n.get("company"):
            company_name = n.get("company")
            break
    if not company_name:
        try:
            company_name = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company") or "ULTRA MRF"
        except Exception:
            company_name = "ULTRA MRF"

    company_address = ""
    try:
        addr_links = frappe.get_all("Dynamic Link", filters={"link_doctype": "Company", "link_name": company_name, "parenttype": "Address"}, fields=["parent"], limit=1)
        if addr_links:
            addr_doc = frappe.get_doc("Address", addr_links[0].parent)
            addr_parts = [addr_doc.address_line1, addr_doc.address_line2, addr_doc.city, addr_doc.state, addr_doc.pincode, addr_doc.country]
            company_address = ", ".join([p for p in addr_parts if p])
    except Exception:
        company_address = ""

    summary = {
        "company": company_name,
        "company_address": company_address,
        "focal_doctype": doctype,
        "focal_docname": docname,
        "vehicle_plate": plate_no,
        "customer_name": customer_name,
        "total_nodes": len(nodes_dict),
        "total_edges": len(edges),
        "total_transaction_value": total_val,
        "total_paid_value": total_paid,
        "total_outstanding_value": total_outstanding,
        "dedup_parts_total": dedup_parts_total,
        "dedup_services_total": dedup_services_total,
        "unique_parts_count": len(unique_parts_map),
        "unique_services_count": len(unique_services_map),
        "status_flow_complete": total_outstanding == 0 and total_val > 0
    }

    return {
        "nodes": list(nodes_dict.values()),
        "edges": edges,
        "summary": summary,
        "items": all_items,
        "accounting": accounting_summary
    }
