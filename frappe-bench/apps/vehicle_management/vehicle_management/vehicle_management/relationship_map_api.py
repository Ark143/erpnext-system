import frappe
from frappe import _

@frappe.whitelist()
def get_relationship_map(doctype=None, docname=None, vehicle=None, customer=None):
    """
    VMS Relationship Map backend engine.
    Given a starting document (or vehicle/customer), traces upstream and downstream
    transactions across Vehicle Management and ERPNext accounting/inventory modules.
    """
    if not doctype and not docname and not vehicle and not customer:
        # Return latest active Job Order or Vehicle as default sample
        latest_jo = frappe.get_all("Vehicle Job Order", fields=["name"], order_by="creation desc", limit=1)
        if latest_jo:
            doctype = "Vehicle Job Order"
            docname = latest_jo[0].name
        else:
            return {"nodes": [], "edges": [], "summary": {}}

    # If vehicle or customer is provided without doctype
    if vehicle and not doctype:
        doctype = "Customer Vehicle"
        docname = vehicle
    elif customer and not doctype:
        doctype = "Customer"
        docname = customer

    nodes_dict = {}
    edges = []
    visited_docs = set()

    def add_node(dt, name, is_current=False, level=0):
        key = f"{dt}::{name}"
        if key in nodes_dict:
            if is_current:
                nodes_dict[key]["is_current"] = True
            return nodes_dict[key]

        if not frappe.db.exists(dt, name):
            return None

        doc = frappe.get_doc(dt, name)
        
        # Build document data
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

        # Amount formatting
        grand_total = float(getattr(doc, "grand_total", 0) or getattr(doc, "total_amount", 0) or getattr(doc, "paid_amount", 0) or getattr(doc, "received_amount", 0) or 0)
        paid_amount = float(getattr(doc, "paid_amount", 0) or getattr(doc, "total_allocated_amount", 0) or 0)
        outstanding = float(getattr(doc, "outstanding_amount", 0) or (grand_total - paid_amount if grand_total > paid_amount else 0))
        
        # Date & Time
        posting_date = str(getattr(doc, "posting_date", "") or getattr(doc, "job_order_date", "") or getattr(doc, "estimate_date", "") or getattr(doc, "inspection_date", "") or getattr(doc, "transaction_date", "") or getattr(doc, "creation", ""))[:10]
        posting_time = str(getattr(doc, "posting_time", "") or "")

        # Vehicle & Customer Info
        veh_plate = getattr(doc, "plate_no", None) or getattr(doc, "vehicle", None) or getattr(doc, "custom_vehicle_plate", None)
        cust_name = getattr(doc, "customer_name", None) or getattr(doc, "customer", None) or getattr(doc, "party_name", None)
        company = getattr(doc, "company", "")

        # Line items summary
        items = []
        if hasattr(doc, "services") and doc.services:
            for s in doc.services:
                items.append({
                    "type": "Labor / Service",
                    "item_code": getattr(s, "service_name", "") or getattr(s, "description", "Service"),
                    "description": getattr(s, "description", ""),
                    "qty": getattr(s, "hours", 1),
                    "rate": getattr(s, "rate", 0),
                    "amount": getattr(s, "total_amount", 0) or (getattr(s, "hours", 1) * getattr(s, "rate", 0))
                })
        if hasattr(doc, "parts") and doc.parts:
            for p in doc.parts:
                items.append({
                    "type": "Part / Material",
                    "item_code": getattr(p, "part_no", "") or getattr(p, "item_code", "") or getattr(p, "item_name", "Part"),
                    "description": getattr(p, "item_name", "") or getattr(p, "description", ""),
                    "qty": getattr(p, "qty", 1),
                    "rate": getattr(p, "rate", 0),
                    "amount": getattr(p, "amount", 0)
                })
        if hasattr(doc, "items") and doc.items:
            for it in doc.items:
                items.append({
                    "type": "Item",
                    "item_code": getattr(it, "item_code", "") or getattr(it, "item_name", "Item"),
                    "description": getattr(it, "description", "") or getattr(it, "item_name", ""),
                    "qty": getattr(it, "qty", 1),
                    "rate": getattr(it, "rate", 0),
                    "amount": getattr(it, "amount", 0)
                })

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
        edge_key = f"{from_id}->{to_id}"
        
        # Check if already added
        for e in edges:
            if e["from"] == from_id and e["to"] == to_id and e["label"] == label:
                return
        edges.append({
            "from": from_id,
            "to": to_id,
            "label": label,
            "type": edge_type
        })

    # -------------------------------------------------------------
    # Recursive / Relational Graph Traversal
    # -------------------------------------------------------------
    
    # 1. Add focal node
    focal_node = add_node(doctype, docname, is_current=True, level=2)
    if not focal_node:
        return {"nodes": [], "edges": [], "summary": {}}

    plate_no = focal_node.get("vehicle")
    customer_name = focal_node.get("customer")

    # If Customer Vehicle is focal
    if doctype == "Customer Vehicle":
        plate_no = docname
        veh_doc = frappe.get_doc("Customer Vehicle", docname)
        if veh_doc.customer:
            cust_node = add_node("Customer", veh_doc.customer, level=0)
            if cust_node:
                add_edge("Customer", veh_doc.customer, "Customer Vehicle", docname, "Owns Vehicle", "reference")

    # If Customer is focal
    if doctype == "Customer":
        customer_name = docname

    # Discover linked Customer Vehicle
    if plate_no and frappe.db.exists("Customer Vehicle", plate_no):
        veh_node = add_node("Customer Vehicle", plate_no, level=0)
        if doctype not in ("Customer Vehicle", "Customer"):
            add_edge("Customer Vehicle", plate_no, doctype, docname, "Vehicle", "reference")
        
        # Get Customer from Vehicle
        veh_doc = frappe.get_doc("Customer Vehicle", plate_no)
        if veh_doc.customer and frappe.db.exists("Customer", veh_doc.customer):
            add_node("Customer", veh_doc.customer, level=0)
            add_edge("Customer", veh_doc.customer, "Customer Vehicle", plate_no, "Owns Vehicle", "reference")

    # Discover linked Customer
    if customer_name and frappe.db.exists("Customer", customer_name):
        add_node("Customer", customer_name, level=0)
        if doctype not in ("Customer Vehicle", "Customer"):
            add_edge("Customer", customer_name, doctype, docname, "Customer", "reference")

    # -------------------------------------------------------------
    # Document specifics based on target
    # -------------------------------------------------------------

    # If focal is Vehicle Job Order
    if doctype == "Vehicle Job Order":
        jo = frappe.get_doc("Vehicle Job Order", docname)
        
        # 1. Upstream: Vehicle Estimate
        if jo.estimate and frappe.db.exists("Vehicle Estimate", jo.estimate):
            add_node("Vehicle Estimate", jo.estimate, level=1)
            add_edge("Vehicle Estimate", jo.estimate, "Vehicle Job Order", docname, "Converted to JO", "flow")
        elif plate_no:
            estimates = frappe.get_all("Vehicle Estimate", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=3)
            for est in estimates:
                add_node("Vehicle Estimate", est.name, level=1)
                add_edge("Vehicle Estimate", est.name, "Vehicle Job Order", docname, "Referenced Estimate", "reference")

        # 2. Upstream: Vehicle Inspection
        if plate_no:
            inspections = frappe.get_all("Vehicle Inspection", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=3)
            for insp in inspections:
                add_node("Vehicle Inspection", insp.name, level=1)
                add_edge("Vehicle Inspection", insp.name, "Vehicle Job Order", docname, "Diagnostic Inspection", "flow")

        # 3. Downstream: Sales Invoice
        if jo.sales_invoice and frappe.db.exists("Sales Invoice", jo.sales_invoice):
            sinv = add_node("Sales Invoice", jo.sales_invoice, level=3)
            add_edge("Vehicle Job Order", docname, "Sales Invoice", jo.sales_invoice, "Billed via SI", "flow")
            
            # Trace payments for Sales Invoice
            pay_refs = frappe.get_all("Payment Entry Reference", filters={"reference_name": jo.sales_invoice}, fields=["parent"])
            for p in pay_refs:
                if frappe.db.exists("Payment Entry", p.parent):
                    add_node("Payment Entry", p.parent, level=4)
                    add_edge("Sales Invoice", jo.sales_invoice, "Payment Entry", p.parent, "Payment Received", "accounting")
            
            # Trace GL Entries for Sales Invoice
            gl_entries = frappe.get_all("GL Entry", filters={"voucher_no": jo.sales_invoice}, fields=["account", "debit", "credit"], limit=4)
            if gl_entries:
                for idx, gl in enumerate(gl_entries):
                    gl_id = f"GL-{jo.sales_invoice}-{idx}"
                    gl_title = f"{gl.account} (Dr: {gl.debit:,.2f}, Cr: {gl.credit:,.2f})"
                    nodes_dict[f"GL Entry::{gl_id}"] = {
                        "id": f"GL Entry::{gl_id}",
                        "doctype": "GL Entry",
                        "name": gl.account,
                        "title": gl_title,
                        "status": "Posted",
                        "docstatus": 1,
                        "grand_total": gl.debit or gl.credit,
                        "currency": "PHP",
                        "level": 4,
                        "remarks": f"Accounting ledger impact for {jo.sales_invoice}"
                    }
                    add_edge("Sales Invoice", jo.sales_invoice, "GL Entry", gl_id, "GL Posting", "accounting")

        # 4. Downstream: Vehicle POS Invoice & POS Invoice
        vpos_list = frappe.get_all("Vehicle POS Invoice", filters={"vehicle": plate_no}, fields=["name", "pos_invoice"], order_by="creation desc", limit=3)
        for vp in vpos_list:
            add_node("Vehicle POS Invoice", vp.name, level=3)
            add_edge("Vehicle Job Order", docname, "Vehicle POS Invoice", vp.name, "POS Counter Bill", "flow")
            if vp.pos_invoice and frappe.db.exists("POS Invoice", vp.pos_invoice):
                add_node("POS Invoice", vp.pos_invoice, level=3)
                add_edge("Vehicle POS Invoice", vp.name, "POS Invoice", vp.pos_invoice, "Generated POS Doc", "flow")

        # 5. Downstream: Stock Entries
        stock_entries = frappe.get_all("Stock Entry", filters={"docstatus": ["!=", 2]}, fields=["name", "stock_entry_type", "purpose"], limit=50)
        for se in stock_entries:
            se_doc = frappe.get_doc("Stock Entry", se.name)
            if docname in (getattr(se_doc, "remarks", "") or "") or docname in (getattr(se_doc, "work_order", "") or ""):
                add_node("Stock Entry", se.name, level=2)
                add_edge("Vehicle Job Order", docname, "Stock Entry", se.name, "Parts Issued", "inventory")

    # If focal is Vehicle Estimate
    elif doctype == "Vehicle Estimate":
        est = frappe.get_doc("Vehicle Estimate", docname)
        if est.job_order and frappe.db.exists("Vehicle Job Order", est.job_order):
            add_node("Vehicle Job Order", est.job_order, level=2)
            add_edge("Vehicle Estimate", docname, "Vehicle Job Order", est.job_order, "Converted to JO", "flow")
            # Trace downstream from Job Order
            jo = frappe.get_doc("Vehicle Job Order", est.job_order)
            if jo.sales_invoice and frappe.db.exists("Sales Invoice", jo.sales_invoice):
                add_node("Sales Invoice", jo.sales_invoice, level=3)
                add_edge("Vehicle Job Order", est.job_order, "Sales Invoice", jo.sales_invoice, "Billed via SI", "flow")
        elif plate_no:
            # Look up Job Orders for this vehicle
            jos = frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=3)
            for j in jos:
                add_node("Vehicle Job Order", j.name, level=2)
                add_edge("Vehicle Estimate", docname, "Vehicle Job Order", j.name, "Vehicle JO", "flow")

    # If focal is Vehicle Inspection
    elif doctype == "Vehicle Inspection":
        if plate_no:
            jos = frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name", "estimate"], order_by="creation desc", limit=3)
            for j in jos:
                add_node("Vehicle Job Order", j.name, level=2)
                add_edge("Vehicle Inspection", docname, "Vehicle Job Order", j.name, "Work Executed", "flow")
                if j.estimate and frappe.db.exists("Vehicle Estimate", j.estimate):
                    add_node("Vehicle Estimate", j.estimate, level=1)
                    add_edge("Vehicle Inspection", docname, "Vehicle Estimate", j.estimate, "Estimate Quoted", "flow")

    # If focal is Vehicle POS Invoice or POS Invoice
    elif doctype in ("Vehicle POS Invoice", "POS Invoice"):
        if doctype == "Vehicle POS Invoice":
            vp = frappe.get_doc("Vehicle POS Invoice", docname)
            if vp.pos_invoice and frappe.db.exists("POS Invoice", vp.pos_invoice):
                add_node("POS Invoice", vp.pos_invoice, level=3)
                add_edge("Vehicle POS Invoice", docname, "POS Invoice", vp.pos_invoice, "Fiscal POS Record", "flow")
        if plate_no:
            jos = frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2)
            for j in jos:
                add_node("Vehicle Job Order", j.name, level=2)
                add_edge("Vehicle Job Order", j.name, doctype, docname, "Workshop Billing", "flow")

    # If focal is Sales Invoice
    elif doctype == "Sales Invoice":
        sinv = frappe.get_doc("Sales Invoice", docname)
        
        # Upstream Job Order
        jos = frappe.get_all("Vehicle Job Order", filters={"sales_invoice": docname}, fields=["name"])
        for j in jos:
            add_node("Vehicle Job Order", j.name, level=2)
            add_edge("Vehicle Job Order", j.name, "Sales Invoice", docname, "Billed via SI", "flow")
            
        # Downstream Payment Entry
        pay_refs = frappe.get_all("Payment Entry Reference", filters={"reference_name": docname}, fields=["parent"])
        for p in pay_refs:
            if frappe.db.exists("Payment Entry", p.parent):
                add_node("Payment Entry", p.parent, level=4)
                add_edge("Sales Invoice", docname, "Payment Entry", p.parent, "Payment Received", "accounting")

    # If focal is Customer Vehicle
    elif doctype == "Customer Vehicle":
        # Pull all history
        insps = frappe.get_all("Vehicle Inspection", filters={"vehicle": docname}, fields=["name"], limit=5)
        for i in insps:
            add_node("Vehicle Inspection", i.name, level=1)
            add_edge("Customer Vehicle", docname, "Vehicle Inspection", i.name, "Inspection", "flow")

        ests = frappe.get_all("Vehicle Estimate", filters={"vehicle": docname}, fields=["name"], limit=5)
        for e in ests:
            add_node("Vehicle Estimate", e.name, level=1)
            add_edge("Customer Vehicle", docname, "Vehicle Estimate", e.name, "Estimate", "flow")

        jos = frappe.get_all("Vehicle Job Order", filters={"vehicle": docname}, fields=["name", "sales_invoice"], limit=5)
        for j in jos:
            add_node("Vehicle Job Order", j.name, level=2)
            add_edge("Customer Vehicle", docname, "Vehicle Job Order", j.name, "Job Order", "flow")
            if j.sales_invoice and frappe.db.exists("Sales Invoice", j.sales_invoice):
                add_node("Sales Invoice", j.sales_invoice, level=3)
                add_edge("Vehicle Job Order", j.name, "Sales Invoice", j.sales_invoice, "Invoice", "flow")

        vpos = frappe.get_all("Vehicle POS Invoice", filters={"vehicle": docname}, fields=["name"], limit=5)
        for vp in vpos:
            add_node("Vehicle POS Invoice", vp.name, level=3)
            add_edge("Customer Vehicle", docname, "Vehicle POS Invoice", vp.name, "POS Receipt", "flow")

    # -------------------------------------------------------------
    # Calculate Graph Financial Summary
    # -------------------------------------------------------------
    total_val = sum([n.get("grand_total", 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Vehicle POS Invoice", "POS Invoice")])
    total_paid = sum([n.get("paid_amount", 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Payment Entry", "Vehicle POS Invoice")])
    total_outstanding = sum([n.get("outstanding_amount", 0) for n in nodes_dict.values() if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice")])

    summary = {
        "focal_doctype": doctype,
        "focal_docname": docname,
        "vehicle_plate": plate_no,
        "customer_name": customer_name,
        "total_nodes": len(nodes_dict),
        "total_edges": len(edges),
        "total_transaction_value": total_val,
        "total_paid_value": total_paid,
        "total_outstanding_value": total_outstanding,
        "status_flow_complete": total_outstanding == 0 and total_val > 0
    }

    return {
        "nodes": list(nodes_dict.values()),
        "edges": edges,
        "summary": summary
    }


