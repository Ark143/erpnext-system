import urllib.request, urllib.parse, json, http.cookiejar, os

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)
print("Logged in successfully as Administrator.")

# -------------------------------------------------------------
# Clean, robust Server Script for VM SAP Relationship Map API
# -------------------------------------------------------------
server_script_code = """
try:
    doctype = frappe.form_dict.get('doctype')
    docname = frappe.form_dict.get('docname')
    vehicle = frappe.form_dict.get('vehicle')
    customer = frappe.form_dict.get('customer')

    if not doctype and not docname and not vehicle and not customer:
        latest_jo = frappe.get_all("Vehicle Job Order", fields=["name"], order_by="creation desc", limit=1)
        if latest_jo:
            doctype = "Vehicle Job Order"
            docname = latest_jo[0].get("name")

    if vehicle and not doctype:
        doctype = "Customer Vehicle"
        docname = vehicle
    elif customer and not doctype:
        doctype = "Customer"
        docname = customer

    nodes_dict = {}
    edges = []

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
        paid = float(doc.get("paid_amount") or doc.get("total_allocated_amount") or 0)
        outst = float(doc.get("outstanding_amount") or (gt - paid if gt > paid else 0))
        p_date = str(doc.get("posting_date") or doc.get("job_order_date") or doc.get("estimate_date") or doc.get("inspection_date") or doc.get("transaction_date") or doc.get("creation") or "")[:10]
        p_time = str(doc.get("posting_time") or "")

        v_plate = doc.get("plate_no") or doc.get("vehicle") or doc.get("custom_vehicle_plate") or ""
        c_name = doc.get("customer_name") or doc.get("customer") or doc.get("party_name") or ""
        comp = doc.get("company") or ""

        items_list = []
        if doc.get("services"):
            for s in doc.get("services"):
                items_list.append({
                    "type": "Labor / Service",
                    "item_code": s.get("service_name") or s.get("description") or "Service",
                    "description": s.get("description") or "",
                    "qty": s.get("hours") or 1,
                    "rate": s.get("rate") or 0,
                    "amount": s.get("total_amount") or 0
                })
        if doc.get("parts"):
            for p in doc.get("parts"):
                items_list.append({
                    "type": "Part / Material",
                    "item_code": p.get("part_no") or p.get("item_code") or p.get("item_name") or "Part",
                    "description": p.get("item_name") or p.get("description") or "",
                    "qty": p.get("qty") or 1,
                    "rate": p.get("rate") or 0,
                    "amount": p.get("amount") or 0
                })
        if doc.get("items"):
            for it in doc.get("items"):
                items_list.append({
                    "type": "Item",
                    "item_code": it.get("item_code") or it.get("item_name") or "Item",
                    "description": it.get("description") or it.get("item_name") or "",
                    "qty": it.get("qty") or 1,
                    "rate": it.get("rate") or 0,
                    "amount": it.get("amount") or 0
                })

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
                for idx, gl in enumerate(frappe.get_all("GL Entry", filters={"voucher_no": jo.get("sales_invoice")}, fields=["account", "debit", "credit"], limit=3)):
                    gl_id = "GL-" + str(jo.get("sales_invoice")) + "-" + str(idx)
                    nodes_dict["GL Entry::" + gl_id] = {
                        "id": "GL Entry::" + gl_id,
                        "doctype": "GL Entry",
                        "name": gl.get("account"),
                        "title": str(gl.get("account")),
                        "status": "Posted",
                        "docstatus": 1,
                        "grand_total": float(gl.get("debit") or gl.get("credit") or 0),
                        "currency": "PHP",
                        "level": 4,
                        "remarks": "Accounting ledger impact for " + str(jo.get("sales_invoice"))
                    }
                    link_nodes("Sales Invoice", jo.get("sales_invoice"), "GL Entry", gl_id, "GL Posting", "accounting")

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
            for j in frappe.get_all("Vehicle Job Order", filters={"sales_invoice": docname}, fields=["name"]):
                get_node("Vehicle Job Order", j.get("name"), False, 2)
                link_nodes("Vehicle Job Order", j.get("name"), "Sales Invoice", docname, "Billed via SI", "flow")
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

    tot_val = 0.0
    tot_paid = 0.0
    tot_outst = 0.0
    for n in nodes_dict.values():
        if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Vehicle POS Invoice", "POS Invoice"):
            tot_val = tot_val + float(n.get("grand_total") or 0)
            tot_outst = tot_outst + float(n.get("outstanding_amount") or 0)
        if n.get("doctype") in ("Vehicle Job Order", "Sales Invoice", "Payment Entry", "Vehicle POS Invoice"):
            tot_paid = tot_paid + float(n.get("paid_amount") or 0)

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
        "summary": summary_obj
    }
except Exception as e:
    frappe.response['message'] = {
        "nodes": [],
        "edges": [],
        "summary": {"error": str(e)}
    }
"""

script_name = "VM SAP Relationship Map API"
script_payload = {
    "name": script_name,
    "script_type": "API",
    "api_method": "vm_relationship_map",
    "disabled": 0,
    "script": server_script_code
}

check_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(script_name)}', headers=H)
try:
    op.open(check_req, timeout=10)
    up_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(script_name)}', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    res = op.open(up_req, timeout=15)
    print("Server Script updated successfully.")
except urllib.error.HTTPError as e:
    if e.code == 404:
        create_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script', data=json.dumps(script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
        res = op.open(create_req, timeout=15)
        print("Server Script created successfully.")
    else:
        raise

# Test API call
test_req = urllib.request.Request(f'{URL}/api/method/vm_relationship_map?doctype=Vehicle%20Job%20Order&docname=JO-2026-00028', headers=H)
res = op.open(test_req, timeout=15)
data = json.loads(res.read().decode())
print("API Test result for JO-2026-00028:")
print("Summary:", json.dumps(data.get('message', {}).get('summary', {}), indent=2))
print("Nodes count:", len(data.get('message', {}).get('nodes', [])))
for n in data.get('message', {}).get('nodes', []):
    print(f"  [{n['doctype']}] {n['name']} | Status: {n['status']} | Amount: {n['grand_total']} | Current: {n.get('is_current')}")
print("Edges count:", len(data.get('message', {}).get('edges', [])))
for e in data.get('message', {}).get('edges', []):
    print(f"  {e['from']}  ---({e['label']})--->  {e['to']}")
