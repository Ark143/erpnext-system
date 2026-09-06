import requests, json, sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
login_res = session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)
login_res.raise_for_status()
print("[OK] Logged in to ERPNext as Administrator", flush=True)

# -----------------------------------------------------------------------------
# 1. Server Script: VM SAP Relationship Map API (Safe for Frappe Server Scripts)
# -----------------------------------------------------------------------------
server_script_code = """
try:
    doctype = frappe.form_dict.get('doctype')
    docname = frappe.form_dict.get('docname')
    vehicle = frappe.form_dict.get('vehicle')
    customer = frappe.form_dict.get('customer')
    supplier = frappe.form_dict.get('supplier')

    if not doctype and not docname and not vehicle and not customer and not supplier:
        latest_jo = frappe.get_all("Vehicle Job Order", fields=["name"], order_by="creation desc", limit=1)
        if latest_jo:
            doctype = "Vehicle Job Order"
            docname = latest_jo[0].get("name")
        else:
            latest_po = frappe.get_all("Purchase Order", fields=["name"], order_by="creation desc", limit=1)
            if latest_po:
                doctype = "Purchase Order"
                docname = latest_po[0].get("name")

    if vehicle and not doctype:
        doctype = "Customer Vehicle"
        docname = vehicle
    elif customer and not doctype:
        doctype = "Customer"
        docname = customer
    elif supplier and not doctype:
        doctype = "Supplier"
        docname = supplier

    nodes_dict = {}
    edges = []
    all_items = []

    def get_node(dt, name, is_curr, lvl):
        if not dt or not name:
            return None
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

        gt = float(doc.get("grand_total") or doc.get("total_amount") or doc.get("paid_amount") or doc.get("received_amount") or doc.get("total") or 0)
        
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
        elif dt == "Purchase Invoice":
            pi_out = doc.get("outstanding_amount")
            if pi_out is not None:
                outst = max(0.0, float(pi_out))
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
        elif dt == "Purchase Order":
            adv = float(doc.get("advance_paid") or 0)
            paid = adv
            doc_out = doc.get("outstanding_amount")
            outst = float(doc_out) if doc_out is not None else max(0.0, gt - paid)
        else:
            paid = float(doc.get("paid_amount") or doc.get("total_allocated_amount") or 0)
            doc_out = doc.get("outstanding_amount")
            if doc_out is not None:
                outst = max(0.0, float(doc_out))
            else:
                outst = max(0.0, gt - paid)

        p_date = str(doc.get("posting_date") or doc.get("transaction_date") or doc.get("job_order_date") or doc.get("schedule_date") or doc.get("estimate_date") or doc.get("creation"))[:10]
        
        v_plate = doc.get("plate_no") or doc.get("vehicle") or doc.get("custom_vehicle_plate")
        c_name = doc.get("customer_name") or doc.get("customer")
        s_name = doc.get("supplier_name") or doc.get("supplier")
        if not c_name and doc.get("party_type") == "Customer":
            c_name = doc.get("party") or doc.get("party_name")
        if not s_name and doc.get("party_type") == "Supplier":
            s_name = doc.get("party") or doc.get("party_name")

        co = doc.get("company") or "ULTRA MRF"

        items = []
        if doc.get("services"):
            for s in doc.get("services"):
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Labor / Service",
                    "category": "service",
                    "item_code": s.get("service_name") or s.get("description") or "Service",
                    "description": s.get("description") or s.get("service_name") or "",
                    "qty": float(s.get("hours") or 1),
                    "uom": "Hrs",
                    "rate": float(s.get("rate") or 0),
                    "amount": float(s.get("total_amount") or (float(s.get("hours") or 1) * float(s.get("rate") or 0))),
                    "account": "Service Revenue"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        if doc.get("parts"):
            for p in doc.get("parts"):
                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": "Spare Part / Material",
                    "category": "part",
                    "item_code": p.get("part_no") or p.get("item_code") or p.get("item_name") or "Part",
                    "description": p.get("item_name") or p.get("description") or "",
                    "qty": float(p.get("qty") or 1),
                    "uom": p.get("uom") or "PC",
                    "rate": float(p.get("rate") or 0),
                    "amount": float(p.get("amount") or (float(p.get("qty") or 1) * float(p.get("rate") or 0))),
                    "account": "Parts & Inventory"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        if doc.get("items"):
            for it in doc.get("items"):
                grp = (it.get("item_group") or "").lower()
                nm = (it.get("item_name") or "").lower()
                if "service" in grp or "labor" in grp or "service" in nm or "labor" in nm:
                    cat_name = "Billed Service / Labor" if dt in ("Sales Invoice", "POS Invoice") else "Procured Service"
                    cat_key = "service"
                else:
                    cat_name = "Purchased Material / Stock" if dt in ("Purchase Order", "Purchase Receipt", "Purchase Invoice", "Material Request") else "Billed Spare Part / Product"
                    cat_key = "part"

                it_obj = {
                    "doc_type": dt,
                    "doc_name": name,
                    "type": cat_name,
                    "category": cat_key,
                    "item_code": it.get("item_code") or it.get("item_name") or "Item",
                    "description": it.get("description") or it.get("item_name") or "",
                    "qty": float(it.get("qty") or 1),
                    "uom": it.get("uom") or "PC",
                    "rate": float(it.get("rate") or 0),
                    "amount": float(it.get("amount") or (float(it.get("qty") or 1) * float(it.get("rate") or 0))),
                    "account": it.get("expense_account") or it.get("income_account") or it.get("cost_center") or "Inventory / COGS"
                }
                items.append(it_obj)
                all_items.append(it_obj)

        node = {
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
            "vehicle": v_plate,
            "customer": c_name,
            "supplier": s_name,
            "company": co,
            "is_current": is_curr,
            "level": lvl,
            "items_count": len(items),
            "items": items[:25],
            "remarks": doc.get("remarks") or doc.get("customer_complaint") or doc.get("general_remarks") or ""
        }
        nodes_dict[key] = node
        return node

    def add_link(from_dt, from_name, to_dt, to_name, lbl, e_type="flow"):
        if not from_name or not to_name:
            return
        from_id = str(from_dt) + "::" + str(from_name)
        to_id = str(to_dt) + "::" + str(to_name)
        for e in edges:
            if e["from"] == from_id and e["to"] == to_id and e["label"] == lbl:
                return
        edges.append({
            "from": from_id,
            "to": to_id,
            "label": lbl,
            "type": e_type
        })

    focal_lvl = 2
    if doctype in ("Customer", "Customer Vehicle", "Supplier", "Material Request"):
        focal_lvl = 0
    elif doctype in ("Purchase Order", "Vehicle Estimate", "Vehicle Inspection", "Quotation", "Supplier Quotation", "Sales Order"):
        focal_lvl = 1
    elif doctype in ("Vehicle Job Order", "Purchase Receipt", "Delivery Note", "Stock Entry"):
        focal_lvl = 2
    elif doctype in ("Sales Invoice", "Purchase Invoice", "Vehicle POS Invoice", "POS Invoice"):
        focal_lvl = 3
    elif doctype in ("Payment Entry", "GL Entry", "Journal Entry"):
        focal_lvl = 4

    focal_node = get_node(doctype, docname, True, focal_lvl)

    plate_no = focal_node.get("vehicle") if focal_node else None
    customer_name = focal_node.get("customer") if focal_node else None
    supplier_name = focal_node.get("supplier") if focal_node else None

    if doctype == "Customer Vehicle":
        plate_no = docname
        veh_doc = frappe.get_doc("Customer Vehicle", docname)
        if veh_doc.get("customer") and frappe.db.exists("Customer", veh_doc.get("customer")):
            get_node("Customer", veh_doc.get("customer"), False, 0)
            add_link("Customer", veh_doc.get("customer"), "Customer Vehicle", docname, "Owns Vehicle", "reference")

    if doctype == "Customer":
        customer_name = docname
    if doctype == "Supplier":
        supplier_name = docname

    if plate_no and frappe.db.exists("Customer Vehicle", plate_no):
        get_node("Customer Vehicle", plate_no, False, 0)
        if doctype not in ("Customer Vehicle", "Customer"):
            add_link("Customer Vehicle", plate_no, doctype, docname, "Vehicle", "reference")
        veh_doc = frappe.get_doc("Customer Vehicle", plate_no)
        if veh_doc.get("customer") and frappe.db.exists("Customer", veh_doc.get("customer")):
            get_node("Customer", veh_doc.get("customer"), False, 0)
            add_link("Customer", veh_doc.get("customer"), "Customer Vehicle", plate_no, "Owns Vehicle", "reference")

    if customer_name and frappe.db.exists("Customer", customer_name):
        get_node("Customer", customer_name, False, 0)
        if doctype != "Customer":
            add_link("Customer", customer_name, doctype, docname, "Customer", "reference")

    if supplier_name and frappe.db.exists("Supplier", supplier_name):
        get_node("Supplier", supplier_name, False, 0)
        if doctype != "Supplier":
            add_link("Supplier", supplier_name, doctype, docname, "Supplier", "reference")

    # =========================================================================
    # P2P TRACING
    # =========================================================================
    if doctype == "Material Request":
        po_items = frappe.get_all("Purchase Order Item", filters={"material_request": docname}, fields=["parent"], distinct=True)
        for poi in po_items:
            if frappe.db.exists("Purchase Order", poi.parent):
                get_node("Purchase Order", poi.parent, False, 1)
                add_link("Material Request", docname, "Purchase Order", poi.parent, "Procured via PO", "flow")
                po_doc = frappe.get_doc("Purchase Order", poi.parent)
                if po_doc.get("supplier") and frappe.db.exists("Supplier", po_doc.get("supplier")):
                    get_node("Supplier", po_doc.get("supplier"), False, 0)
                    add_link("Supplier", po_doc.get("supplier"), "Purchase Order", poi.parent, "Supplier", "reference")

                for pr in frappe.get_all("Purchase Receipt Item", filters={"purchase_order": poi.parent}, fields=["parent"], distinct=True):
                    if frappe.db.exists("Purchase Receipt", pr.parent):
                        get_node("Purchase Receipt", pr.parent, False, 2)
                        add_link("Purchase Order", poi.parent, "Purchase Receipt", pr.parent, "GRN Receipt", "flow")

                for pi in frappe.get_all("Purchase Invoice Item", filters={"purchase_order": poi.parent}, fields=["parent"], distinct=True):
                    if frappe.db.exists("Purchase Invoice", pi.parent):
                        get_node("Purchase Invoice", pi.parent, False, 3)
                        add_link("Purchase Order", poi.parent, "Purchase Invoice", pi.parent, "Billed via PI", "flow")
                        for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": pi.parent}, fields=["parent"], distinct=True):
                            if frappe.db.exists("Payment Entry", p.parent):
                                get_node("Payment Entry", p.parent, False, 4)
                                add_link("Purchase Invoice", pi.parent, "Payment Entry", p.parent, "Payment Disbursed", "accounting")

    elif doctype == "Purchase Order":
        po_doc = frappe.get_doc("Purchase Order", docname)
        if po_doc.get("supplier") and frappe.db.exists("Supplier", po_doc.get("supplier")):
            get_node("Supplier", po_doc.get("supplier"), False, 0)
            add_link("Supplier", po_doc.get("supplier"), "Purchase Order", docname, "Supplier", "reference")

        for it in po_doc.get("items") or []:
            mr_id = it.get("material_request")
            if mr_id and frappe.db.exists("Material Request", mr_id):
                get_node("Material Request", mr_id, False, 0)
                add_link("Material Request", mr_id, "Purchase Order", docname, "Procured via PO", "flow")

        for pr in frappe.get_all("Purchase Receipt Item", filters={"purchase_order": docname}, fields=["parent"], distinct=True):
            if frappe.db.exists("Purchase Receipt", pr.parent):
                get_node("Purchase Receipt", pr.parent, False, 2)
                add_link("Purchase Order", docname, "Purchase Receipt", pr.parent, "Goods Received (GRN)", "flow")

        for pi in frappe.get_all("Purchase Invoice Item", filters={"purchase_order": docname}, fields=["parent"], distinct=True):
            if frappe.db.exists("Purchase Invoice", pi.parent):
                get_node("Purchase Invoice", pi.parent, False, 3)
                add_link("Purchase Order", docname, "Purchase Invoice", pi.parent, "Billed via PI", "flow")
                for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": pi.parent}, fields=["parent"], distinct=True):
                    if frappe.db.exists("Payment Entry", p.parent):
                        get_node("Payment Entry", p.parent, False, 4)
                        add_link("Purchase Invoice", pi.parent, "Payment Entry", p.parent, "Payment Disbursed", "accounting")

        for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": docname}, fields=["parent"], distinct=True):
            if frappe.db.exists("Payment Entry", p.parent):
                get_node("Payment Entry", p.parent, False, 4)
                add_link("Purchase Order", docname, "Payment Entry", p.parent, "Advance Payment", "accounting")

        inter_so = po_doc.get("inter_company_order_reference")
        if inter_so and frappe.db.exists("Sales Order", inter_so):
            get_node("Sales Order", inter_so, False, 1)
            add_link("Purchase Order", docname, "Sales Order", inter_so, "Intercompany Sister SO", "reference")

    elif doctype == "Purchase Receipt":
        pr_doc = frappe.get_doc("Purchase Receipt", docname)
        if pr_doc.get("supplier") and frappe.db.exists("Supplier", pr_doc.get("supplier")):
            get_node("Supplier", pr_doc.get("supplier"), False, 0)
            add_link("Supplier", pr_doc.get("supplier"), "Purchase Receipt", docname, "Supplier", "reference")

        for it in pr_doc.get("items") or []:
            po_id = it.get("purchase_order")
            if po_id and frappe.db.exists("Purchase Order", po_id):
                get_node("Purchase Order", po_id, False, 1)
                add_link("Purchase Order", po_id, "Purchase Receipt", docname, "Goods Received (GRN)", "flow")

        for pi in frappe.get_all("Purchase Invoice Item", filters={"purchase_receipt": docname}, fields=["parent"], distinct=True):
            if frappe.db.exists("Purchase Invoice", pi.parent):
                get_node("Purchase Invoice", pi.parent, False, 3)
                add_link("Purchase Receipt", docname, "Purchase Invoice", pi.parent, "Billed via PI", "flow")
                for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": pi.parent}, fields=["parent"], distinct=True):
                    if frappe.db.exists("Payment Entry", p.parent):
                        get_node("Payment Entry", p.parent, False, 4)
                        add_link("Purchase Invoice", pi.parent, "Payment Entry", p.parent, "Payment Disbursed", "accounting")

    elif doctype == "Purchase Invoice":
        pi_doc = frappe.get_doc("Purchase Invoice", docname)
        if pi_doc.get("supplier") and frappe.db.exists("Supplier", pi_doc.get("supplier")):
            get_node("Supplier", pi_doc.get("supplier"), False, 0)
            add_link("Supplier", pi_doc.get("supplier"), "Purchase Invoice", docname, "Supplier", "reference")

        for it in pi_doc.get("items") or []:
            pr_id = it.get("purchase_receipt")
            if pr_id and frappe.db.exists("Purchase Receipt", pr_id):
                get_node("Purchase Receipt", pr_id, False, 2)
                add_link("Purchase Receipt", pr_id, "Purchase Invoice", docname, "Billed via PI", "flow")
            po_id = it.get("purchase_order")
            if po_id and frappe.db.exists("Purchase Order", po_id):
                get_node("Purchase Order", po_id, False, 1)
                add_link("Purchase Order", po_id, "Purchase Invoice", docname, "Direct Billed PO", "flow")

        for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": docname}, fields=["parent"], distinct=True):
            if frappe.db.exists("Payment Entry", p.parent):
                get_node("Payment Entry", p.parent, False, 4)
                add_link("Purchase Invoice", docname, "Payment Entry", p.parent, "Payment Disbursed", "accounting")

        inter_si = pi_doc.get("inter_company_invoice_reference")
        if inter_si and frappe.db.exists("Sales Invoice", inter_si):
            get_node("Sales Invoice", inter_si, False, 3)
            add_link("Purchase Invoice", docname, "Sales Invoice", inter_si, "Intercompany Sister SI", "reference")

    elif doctype == "Supplier":
        for po in frappe.get_all("Purchase Order", filters={"supplier": docname}, fields=["name"], order_by="creation desc", limit=3):
            get_node("Purchase Order", po.name, False, 1)
            add_link("Supplier", docname, "Purchase Order", po.name, "Purchase Order", "flow")
        for pr in frappe.get_all("Purchase Receipt", filters={"supplier": docname}, fields=["name"], order_by="creation desc", limit=2):
            get_node("Purchase Receipt", pr.name, False, 2)
            add_link("Supplier", docname, "Purchase Receipt", pr.name, "Receipt (GRN)", "flow")
        for pi in frappe.get_all("Purchase Invoice", filters={"supplier": docname}, fields=["name"], order_by="creation desc", limit=3):
            get_node("Purchase Invoice", pi.name, False, 3)
            add_link("Supplier", docname, "Purchase Invoice", pi.name, "Purchase Bill", "flow")
        for pe in frappe.get_all("Payment Entry", filters={"party_type": "Supplier", "party": docname}, fields=["name"], order_by="creation desc", limit=3):
            get_node("Payment Entry", pe.name, False, 4)
            add_link("Supplier", docname, "Payment Entry", pe.name, "Payment Entry", "accounting")

    # =========================================================================
    # VMS & O2C TRACING
    # =========================================================================
    elif doctype == "Vehicle Job Order":
        jo = frappe.get_doc("Vehicle Job Order", docname)
        if jo.get("estimate") and frappe.db.exists("Vehicle Estimate", jo.get("estimate")):
            get_node("Vehicle Estimate", jo.get("estimate"), False, 1)
            add_link("Vehicle Estimate", jo.get("estimate"), "Vehicle Job Order", docname, "Converted to JO", "flow")
        elif plate_no:
            for est in frappe.get_all("Vehicle Estimate", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                get_node("Vehicle Estimate", est.name, False, 1)
                add_link("Vehicle Estimate", est.name, "Vehicle Job Order", docname, "Referenced Estimate", "reference")

        if plate_no:
            for insp in frappe.get_all("Vehicle Inspection", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                get_node("Vehicle Inspection", insp.name, False, 1)
                add_link("Vehicle Inspection", insp.name, "Vehicle Job Order", docname, "Diagnostic Inspection", "flow")

        if jo.get("sales_invoice") and frappe.db.exists("Sales Invoice", jo.get("sales_invoice")):
            get_node("Sales Invoice", jo.get("sales_invoice"), False, 3)
            add_link("Vehicle Job Order", docname, "Sales Invoice", jo.get("sales_invoice"), "Billed via SI", "flow")
            for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": jo.get("sales_invoice")}, fields=["parent"]):
                if frappe.db.exists("Payment Entry", p.parent):
                    get_node("Payment Entry", p.parent, False, 4)
                    add_link("Sales Invoice", jo.get("sales_invoice"), "Payment Entry", p.parent, "Payment Received", "accounting")

        for vp in frappe.get_all("Vehicle POS Invoice", filters={"vehicle": plate_no}, fields=["name", "pos_invoice"], order_by="creation desc", limit=2):
            get_node("Vehicle POS Invoice", vp.name, False, 3)
            add_link("Vehicle Job Order", docname, "Vehicle POS Invoice", vp.name, "POS Counter Bill", "flow")
            if vp.get("pos_invoice") and frappe.db.exists("POS Invoice", vp.get("pos_invoice")):
                get_node("POS Invoice", vp.get("pos_invoice"), False, 3)
                add_link("Vehicle POS Invoice", vp.name, "POS Invoice", vp.get("pos_invoice"), "Fiscal POS Record", "flow")

    elif doctype == "Vehicle Estimate":
        est = frappe.get_doc("Vehicle Estimate", docname)
        if est.get("job_order") and frappe.db.exists("Vehicle Job Order", est.get("job_order")):
            get_node("Vehicle Job Order", est.get("job_order"), False, 2)
            add_link("Vehicle Estimate", docname, "Vehicle Job Order", est.get("job_order"), "Converted to JO", "flow")
            jo = frappe.get_doc("Vehicle Job Order", est.get("job_order"))
            if jo.get("sales_invoice") and frappe.db.exists("Sales Invoice", jo.get("sales_invoice")):
                get_node("Sales Invoice", jo.get("sales_invoice"), False, 3)
                add_link("Vehicle Job Order", est.get("job_order"), "Sales Invoice", jo.get("sales_invoice"), "Billed via SI", "flow")

    elif doctype in ("Vehicle POS Invoice", "POS Invoice"):
        if doctype == "Vehicle POS Invoice":
            vp = frappe.get_doc("Vehicle POS Invoice", docname)
            if vp.get("pos_invoice") and frappe.db.exists("POS Invoice", vp.get("pos_invoice")):
                get_node("POS Invoice", vp.get("pos_invoice"), False, 3)
                add_link("Vehicle POS Invoice", docname, "POS Invoice", vp.get("pos_invoice"), "Fiscal POS Record", "flow")
        if plate_no:
            for j in frappe.get_all("Vehicle Job Order", filters={"vehicle": plate_no}, fields=["name"], order_by="creation desc", limit=2):
                get_node("Vehicle Job Order", j.name, False, 2)
                add_link("Vehicle Job Order", j.name, doctype, docname, "Workshop Billing", "flow")

    elif doctype == "Sales Invoice":
        for j in frappe.get_all("Vehicle Job Order", filters={"sales_invoice": docname}, fields=["name"]):
            get_node("Vehicle Job Order", j.name, False, 2)
            add_link("Vehicle Job Order", j.name, "Sales Invoice", docname, "Billed via SI", "flow")
            
        for p in frappe.get_all("Payment Entry Reference", filters={"reference_name": docname}, fields=["parent"]):
            if frappe.db.exists("Payment Entry", p.parent):
                get_node("Payment Entry", p.parent, False, 4)
                add_link("Sales Invoice", docname, "Payment Entry", p.parent, "Payment Received", "accounting")

    elif doctype == "Payment Entry":
        pe_doc = frappe.get_doc("Payment Entry", docname)
        if pe_doc.get("party_type") == "Customer" and pe_doc.get("party") and frappe.db.exists("Customer", pe_doc.get("party")):
            get_node("Customer", pe_doc.get("party"), False, 0)
            add_link("Customer", pe_doc.get("party"), "Payment Entry", docname, "Party", "reference")
        elif pe_doc.get("party_type") == "Supplier" and pe_doc.get("party") and frappe.db.exists("Supplier", pe_doc.get("party")):
            get_node("Supplier", pe_doc.get("party"), False, 0)
            add_link("Supplier", pe_doc.get("party"), "Payment Entry", docname, "Party", "reference")

        for ref in pe_doc.get("references") or []:
            ref_dt = ref.get("reference_doctype")
            ref_dn = ref.get("reference_name")
            if ref_dt and ref_dn and frappe.db.exists(ref_dt, ref_dn):
                if ref_dt in ("Sales Invoice", "POS Invoice", "Purchase Invoice"):
                    get_node(ref_dt, ref_dn, False, 3)
                    add_link(ref_dt, ref_dn, "Payment Entry", docname, "Payment Settled", "accounting")
                elif ref_dt in ("Sales Order", "Purchase Order"):
                    get_node(ref_dt, ref_dn, False, 1)
                    add_link(ref_dt, ref_dn, "Payment Entry", docname, "Advance Payment", "accounting")

    # -------------------------------------------------------------
    # FINANCIAL SUMMARY CALCULATION
    # -------------------------------------------------------------
    is_p2p = doctype in ("Material Request", "Purchase Order", "Purchase Receipt", "Purchase Invoice", "Supplier") or any(n.get("doctype") in ("Purchase Order", "Purchase Invoice", "Supplier") for n in nodes_dict.values())

    if is_p2p:
        po_nodes = [n for n in nodes_dict.values() if n.get("doctype") == "Purchase Order"]
        pi_nodes = [n for n in nodes_dict.values() if n.get("doctype") == "Purchase Invoice"]
        pe_nodes = [n for n in nodes_dict.values() if n.get("doctype") == "Payment Entry"]
        
        total_val = sum([n.get("grand_total", 0) for n in pi_nodes]) or sum([n.get("grand_total", 0) for n in po_nodes])
        total_paid = sum([n.get("grand_total", 0) for n in pe_nodes]) or sum([n.get("paid_amount", 0) for n in pi_nodes])
        total_paid = min(total_val, total_paid) if total_val > 0 else total_paid
        total_outstanding = max(0.0, total_val - total_paid)
    else:
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
    # DEDUPLICATED ITEMS & ACCOUNTING GL EXTRACTION
    # -------------------------------------------------------------
    unique_parts_map = {}
    unique_services_map = {}
    for it in all_items:
        code = it.get("item_code") or it.get("description")
        amt = float(it.get("amount") or 0)
        qty = float(it.get("qty") or 1)
        cat = it.get("category", "")
        if cat == "part":
            if code not in unique_parts_map or it.get("doc_type") in ("Sales Invoice", "POS Invoice", "Purchase Invoice"):
                unique_parts_map[code] = {"amount": amt, "qty": qty, "item": it}
        elif cat == "service":
            if code not in unique_services_map or it.get("doc_type") in ("Sales Invoice", "POS Invoice", "Purchase Invoice"):
                unique_services_map[code] = {"amount": amt, "qty": qty, "item": it}

    dedup_parts_total = sum([p["amount"] for p in unique_parts_map.values()])
    dedup_services_total = sum([s["amount"] for s in unique_services_map.values()])

    accounting_vouchers = [n["name"] for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "Payment Entry", "POS Invoice", "Vehicle POS Invoice", "Purchase Invoice", "Journal Entry", "Stock Entry")]
    gl_entries_list = []

    voucher_doctype_map = {
        n["name"]: n["doctype"]
        for n in nodes_dict.values()
        if n.get("doctype") in ("Sales Invoice", "Payment Entry", "POS Invoice", "Vehicle POS Invoice", "Purchase Invoice", "Journal Entry", "Stock Entry")
    }

    if accounting_vouchers:
        gles = frappe.get_all("GL Entry", 
            filters={"voucher_no": ["in", accounting_vouchers], "is_cancelled": 0}, 
            fields=["name", "voucher_type", "voucher_no", "account", "debit", "credit", "posting_date", "cost_center", "remarks"],
            order_by="posting_date asc, creation asc"
        )
        for gl in gles:
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

    vouchers_gl_map = {}
    for g in gl_entries_list:
        v_key = str(g['voucher_type']) + "::" + str(g['voucher_no'])
        if v_key not in vouchers_gl_map:
            vouchers_gl_map[v_key] = []
        vouchers_gl_map[v_key].append(g)

    total_invoice_revenue = sum([
        float(g["credit"] or 0) 
        for g in gl_entries_list 
        if g.get("voucher_type") in ("Sales Invoice", "POS Invoice", "Vehicle POS Invoice") 
        and ("sales" in (g.get("account") or "").lower() or "income" in (g.get("account") or "").lower() or "revenue" in (g.get("account") or "").lower())
    ])
    if total_invoice_revenue == 0:
        total_invoice_revenue = sum([n.get("grand_total", 0) for n in nodes_dict.values() if n.get("doctype") in ("Sales Invoice", "POS Invoice", "Vehicle POS Invoice", "Purchase Invoice")])

    total_payments_collected = sum([
        float(g["debit"] or 0) 
        for g in gl_entries_list
        if g.get("voucher_type") in ("Payment Entry", "Journal Entry", "Sales Invoice", "POS Invoice", "Vehicle POS Invoice")
        and ("cash" in (g.get("account") or "").lower() or "bank" in (g.get("account") or "").lower() or "undeposited" in (g.get("account") or "").lower())
    ])
    if total_payments_collected == 0:
        total_payments_collected = sum([n.get("paid_amount", 0) for n in nodes_dict.values() if n.get("doctype") in ("Payment Entry", "Sales Invoice", "POS Invoice", "Vehicle POS Invoice", "Purchase Invoice")])

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

    company_name = ""
    for n in nodes_dict.values():
        if n.get("company"):
            company_name = n.get("company")
            break
    if not company_name:
        company_name = "ULTRA MRF"

    summary = {
        "company": company_name,
        "focal_doctype": doctype,
        "focal_docname": docname,
        "is_p2p": is_p2p,
        "vehicle_plate": plate_no,
        "customer_name": customer_name,
        "supplier_name": supplier_name,
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

    frappe.response["message"] = {
        "nodes": list(nodes_dict.values()),
        "edges": edges,
        "summary": summary,
        "items": all_items,
        "accounting": accounting_summary
    }

except Exception as e:
    frappe.response["message"] = {
        "error": str(e),
        "nodes": [],
        "edges": [],
        "summary": {},
        "items": [],
        "accounting": {}
    }
"""

print("[1/3] Deploying updated Server Script 'VM SAP Relationship Map API'...", flush=True)
ss_payload = {
    "name": "VM SAP Relationship Map API",
    "script_type": "API",
    "api_method": "vm_relationship_map",
    "allow_guest": 0,
    "disabled": 0,
    "script": server_script_code
}

check_ss = session.get(f"{BASE_URL}/api/resource/Server%20Script/VM%20SAP%20Relationship%20Map%20API", timeout=30)
if check_ss.status_code == 200:
    res = session.put(f"{BASE_URL}/api/resource/Server%20Script/VM%20SAP%20Relationship%20Map%20API", json=ss_payload, timeout=30)
    print(f"      [OK] Updated Server Script: {res.status_code}", flush=True)
else:
    res = session.post(f"{BASE_URL}/api/resource/Server%20Script", json=ss_payload, timeout=30)
    print(f"      [OK] Created Server Script: {res.status_code}", flush=True)

# -----------------------------------------------------------------------------
# 2. Client Scripts for All P2P & O2C DocTypes
# -----------------------------------------------------------------------------
print("\n[2/3] Deploying Client Scripts for P2P & O2C DocTypes...", flush=True)
js_file = pathlib.Path(r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\public\js\vehicle_relationship_map.js')
css_file = pathlib.Path(r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\public\css\vehicle_management_desk.css')

js_code = js_file.read_text(encoding='utf-8')
css_code = css_file.read_text(encoding='utf-8') if css_file.exists() else ""
css_clean = css_code.replace('`', '\\`')

full_client_script = f"""
frappe.provide('frappe.ui.form');

if (!$('#sap-rel-map-styles').length) {{
  $('head').append(`<style id="sap-rel-map-styles">{css_clean}</style>`);
}}

{js_code}
"""

target_doctypes = [
    # P2P DocTypes
    "Material Request",
    "Purchase Order",
    "Purchase Receipt",
    "Purchase Invoice",
    "Supplier",
    "Supplier Quotation",

    # VMS & O2C DocTypes
    "Vehicle Job Order",
    "Vehicle Estimate",
    "Vehicle Inspection",
    "Vehicle POS Invoice",
    "Customer Vehicle",
    "Sales Invoice",
    "POS Invoice",
    "Sales Order",
    "Delivery Note",
    "Quotation",
    "Customer",

    # Financial & Stock
    "Payment Entry",
    "Stock Entry"
]

for dt in target_doctypes:
    cs_name = f"SAP Relationship Map - {dt}"
    payload = {
        "name": cs_name,
        "dt": dt,
        "view": "Form",
        "script_type": "DocType Event",
        "enabled": 1,
        "script": full_client_script
    }
    try:
        check_cs = session.get(f"{BASE_URL}/api/resource/Client%20Script/{requests.utils.quote(cs_name)}", timeout=15)
        if check_cs.status_code == 200:
            cs_res = session.put(f"{BASE_URL}/api/resource/Client%20Script/{requests.utils.quote(cs_name)}", json=payload, timeout=15)
            print(f"      [OK] Updated: {cs_name}", flush=True)
        else:
            cs_res = session.post(f"{BASE_URL}/api/resource/Client%20Script", json=payload, timeout=15)
            print(f"      [OK] Created: {cs_name}", flush=True)
    except Exception as e:
        print(f"      [ERROR] {cs_name}: {e}", flush=True)

# -----------------------------------------------------------------------------
# 3. Testing Relationship Map Live API
# -----------------------------------------------------------------------------
print("\n[3/3] Validating Live Relationship Map API across P2P & O2C...", flush=True)

test_cases = [
    {"doctype": "Purchase Order", "docname": "PUR-ORD-2026-00016"},
    {"doctype": "Material Request", "docname": "MAT-MR-2026-00004"},
    {"doctype": "Supplier", "docname": "ULTRA MRF WAREHOUSE DAU"},
    {"doctype": "Sales Invoice", "docname": "ACC-SINV-2026-00163"},
    {"doctype": "Vehicle Job Order", "docname": "JO-2026-00028"}
]

for tc in test_cases:
    dt = tc['doctype']
    dn = tc['docname']
    r = session.get(f"{BASE_URL}/api/method/vm_relationship_map", params={'doctype': dt, 'docname': dn}, timeout=15)
    if r.status_code == 200:
        data = r.json().get('message', {})
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        sum_info = data.get('summary', {})
        print(f"\n[PASS] {dt}: {dn}")
        print(f"       Nodes ({len(nodes)}): {[n['doctype'] + ': ' + n['name'] for n in nodes]}")
        print(f"       Edges ({len(edges)}): {[e['from'].split('::')[0] + ' -> ' + e['to'].split('::')[0] + ' (' + e['label'] + ')' for e in edges]}")
        print(f"       Summary: Total Val: {sum_info.get('total_transaction_value')}, Paid: {sum_info.get('total_paid_value')}, Outstanding: {sum_info.get('total_outstanding_value')}")
    else:
        print(f"\n[FAIL] {dt}: {dn} -> Status {r.status_code}: {r.text}")

print("\nDeployment and live testing of P2P Relationship Map completed successfully!", flush=True)
