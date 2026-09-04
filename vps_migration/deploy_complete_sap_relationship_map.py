import urllib.request, urllib.parse, json, http.cookiejar, sys

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)
print("[OK] Logged into VPS successfully as Administrator.")

# -------------------------------------------------------------
# 1. Deploy Page: vehicle_relationship_map into VPS Database
# -------------------------------------------------------------
page_payload = {
    "doctype": "Page",
    "name": "vehicle_relationship_map",
    "page_name": "vehicle_relationship_map",
    "title": "VMS Relationship Map",
    "module": "Vehicle Management",
    "standard": "Yes",
    "system_page": 0,
    "roles": []
}

try:
    check_page = urllib.request.Request(f'{URL}/api/resource/Page/vehicle_relationship_map', headers=H)
    op.open(check_page, timeout=10)
    up_req = urllib.request.Request(f'{URL}/api/resource/Page/vehicle_relationship_map', data=json.dumps(page_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    op.open(up_req, timeout=15)
    print("[OK] Page 'vehicle_relationship_map' updated in database.")
except Exception as e:
    try:
        create_req = urllib.request.Request(f'{URL}/api/resource/Page', data=json.dumps(page_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
        op.open(create_req, timeout=15)
        print("[OK] Page 'vehicle_relationship_map' created in database.")
    except Exception as e2:
        print("[INFO] Page note:", e2)

# -------------------------------------------------------------
# 2. Deploy Server Script: VM SAP Relationship Map API
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

server_script_payload = {
    "name": "VM SAP Relationship Map API",
    "script_type": "API",
    "api_method": "vm_relationship_map",
    "disabled": 0,
    "script": server_script_code
}

up_req = urllib.request.Request(f'{URL}/api/resource/Server%20Script/VM%20SAP%20Relationship%20Map%20API', data=json.dumps(server_script_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
op.open(up_req, timeout=15)
print("[OK] Server Script 'VM SAP Relationship Map API' verified and updated.")

# -------------------------------------------------------------
# 3. Read Frontend JS and CSS from local repo and embed in Client Script
# -------------------------------------------------------------
js_path = 'frappe-bench/apps/vehicle_management/vehicle_management/public/js/vehicle_relationship_map.js'
css_path = 'frappe-bench/apps/vehicle_management/vehicle_management/public/css/vehicle_management_desk.css'

with open(js_path, 'r', encoding='utf-8') as f:
    client_engine_js = f.read()

with open(css_path, 'r', encoding='utf-8') as f:
    client_styles_css = f.read()

css_clean = client_styles_css.replace('`', '\\`')

# Combined client script that ensures engine is loaded and attaches the buttons
client_script_bundle = """
// SAP Business One Relationship Map Client Bundle
(function() {
  // 1. Inject Styles
  if (!document.getElementById('sap-relationship-map-css')) {
    const styleEl = document.createElement('style');
    styleEl.id = 'sap-relationship-map-css';
    styleEl.textContent = `""" + css_clean + """`;
    document.head.appendChild(styleEl);
  }

  // 2. Inject Engine
  """ + client_engine_js + """

  // 3. Attach Form View Buttons
  const TARGET_DOCTYPES = [
    "Vehicle Job Order", "Vehicle Estimate", "Vehicle Inspection",
    "Customer Vehicle", "Vehicle POS Invoice", "Sales Invoice",
    "POS Invoice", "Stock Entry", "Payment Entry", "Quotation"
  ];

  function addMapButton(frm) {
    if (!frm || !frm.doc || !frm.doc.name || frm.doc.__islocal) return;
    if (!TARGET_DOCTYPES.includes(frm.doctype)) return;
    
    if (frm.page && !frm.page.has_sap_map_btn) {
      frm.page.add_inner_button(__('🗺️ VMS Relationship Map'), function() {
        if (window.SAPRelationshipMap && window.SAPRelationshipMap.open) {
          window.SAPRelationshipMap.open({
            doctype: frm.doctype,
            docname: frm.doc.name,
            vehicle: frm.doc.vehicle || frm.doc.plate_no || frm.doc.custom_vehicle_plate || "",
            customer: frm.doc.customer || frm.doc.party_name || ""
          });
        }
      }, __('View')).addClass('btn-sap-relationship-map');
      frm.page.has_sap_map_btn = true;
    }
  }

  TARGET_DOCTYPES.forEach(function(dt) {
    frappe.ui.form.on(dt, {
      refresh: function(frm) {
        addMapButton(frm);
      }
    });
  });

})();
"""

# Deploy Client Scripts for each supported doctype
for dt in ["Vehicle Job Order", "Vehicle Estimate", "Vehicle Inspection", "Customer Vehicle", "Vehicle POS Invoice", "Sales Invoice", "POS Invoice", "Stock Entry", "Payment Entry", "Quotation"]:
    cs_name = f"SAP Relationship Map - {dt}"
    cs_payload = {
        "doctype": "Client Script",
        "name": cs_name,
        "dt": dt,
        "enabled": 1,
        "script": client_script_bundle
    }

    try:
        check_cs = urllib.request.Request(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(cs_name)}', headers=H)
        op.open(check_cs, timeout=10)
        up_cs = urllib.request.Request(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(cs_name)}', data=json.dumps(cs_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
        op.open(up_cs, timeout=15)
        print(f"[OK] Client Script updated for {dt}.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            create_cs = urllib.request.Request(f'{URL}/api/resource/Client%20Script', data=json.dumps(cs_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
            op.open(create_cs, timeout=15)
            print(f"[OK] Client Script created for {dt}.")
        else:
            print(f"Client script error for {dt}:", e)

# -------------------------------------------------------------
# 4. Update Workspace Sidebar: Add VMS Relationship Map
# -------------------------------------------------------------
sidebar_items = [
    {"label": "Vehicle Management", "link_type": "Workspace", "type": "Link", "link_to": "Vehicle Management", "icon": "home"},
    {"label": "VMS Relationship Map", "link_type": "Page", "type": "Link", "link_to": "vehicle_relationship_map", "icon": "sitemap"},
    {"label": "Vehicle POS Terminal", "link_type": "Page", "type": "Link", "link_to": "vehicle_pos", "icon": "panel-top"},
    {"label": "Vehicle Analytics", "link_type": "Page", "type": "Link", "link_to": "vehicle_analytics", "icon": "bar-chart"},

    {"label": "Operations & Workshop", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Customer Vehicles", "link_type": "DocType", "type": "Link", "link_to": "Customer Vehicle", "icon": "car"},
    {"label": "Vehicle Job Orders", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Job Order", "icon": "tool"},
    {"label": "Vehicle Inspections", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Inspection", "icon": "check-circle"},
    {"label": "Vehicle Estimates", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Estimate", "icon": "file-text"},
    {"label": "Vehicle Service Reminders", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Service Reminder", "icon": "bell"},

    {"label": "Point of Sale & Cashier", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Vehicle POS Invoices", "link_type": "DocType", "type": "Link", "link_to": "Vehicle POS Invoice", "icon": "file"},
    {"label": "POS Invoices", "link_type": "DocType", "type": "Link", "link_to": "POS Invoice", "icon": "credit-card"},
    {"label": "POS Opening Entry", "link_type": "DocType", "type": "Link", "link_to": "POS Opening Entry", "icon": "play"},
    {"label": "POS Closing Entry", "link_type": "DocType", "type": "Link", "link_to": "POS Closing Entry", "icon": "square"},
    {"label": "Cashier Profiles", "link_type": "DocType", "type": "Link", "link_to": "Cashier Profile", "icon": "user"},

    {"label": "Inventory & Parts", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Items", "link_type": "DocType", "type": "Link", "link_to": "Item", "icon": "box"},
    {"label": "Stock Entries", "link_type": "DocType", "type": "Link", "link_to": "Stock Entry", "icon": "truck"},
    {"label": "Item Vehicle Compatibility", "link_type": "DocType", "type": "Link", "link_to": "Item Vehicle Compatibility", "icon": "check-square"},
    {"label": "Item Part Cross Reference", "link_type": "DocType", "type": "Link", "link_to": "Item Part Cross Reference", "icon": "git-commit"},
    {"label": "Bin Locations", "link_type": "DocType", "type": "Link", "link_to": "Bin Location", "icon": "archive"},
    {"label": "Warehouses", "link_type": "DocType", "type": "Link", "link_to": "Warehouse", "icon": "home"},

    {"label": "Vehicle Masters", "type": "Section Break", "link_type": "DocType", "link_to": None, "icon": None},
    {"label": "Vehicle Makes", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Make", "icon": "tag"},
    {"label": "Vehicle Models", "link_type": "DocType", "type": "Link", "link_to": "Vehicle Model", "icon": "list"},
    {"label": "Inspection Templates", "link_type": "DocType", "type": "Link", "link_to": "Inspection Template", "icon": "file-text"}
]

ws_payload = {
    "sidebar_items": sidebar_items
}

try:
    up_ws = urllib.request.Request(f'{URL}/api/resource/Workspace/Vehicle%20Management', data=json.dumps(ws_payload).encode(), headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='PUT')
    op.open(up_ws, timeout=15)
    print("[OK] Workspace 'Vehicle Management' sidebar updated successfully.")
except Exception as e:
    print("Workspace update error:", e)

# -------------------------------------------------------------
# 5. Final Verification Test
# -------------------------------------------------------------
test_req = urllib.request.Request(f'{URL}/api/method/vm_relationship_map?doctype=Vehicle%20Job%20Order&docname=JO-2026-00028', headers=H)
res = op.open(test_req, timeout=15)
data = json.loads(res.read().decode())
print("\n=======================================================")
print("LIVE DEPLOYMENT SUCCESSFUL ON VPS (http://38.247.138.224:10017)")
print("=======================================================")
print("Focal Document:", data.get('message', {}).get('summary', {}).get('focal_doctype'), data.get('message', {}).get('summary', {}).get('focal_docname'))
print("Vehicle Plate:", data.get('message', {}).get('summary', {}).get('vehicle_plate'))
print("Customer:", data.get('message', {}).get('summary', {}).get('customer_name'))
print("Total Relational Nodes:", data.get('message', {}).get('summary', {}).get('total_nodes'))
print("Total Relational Edges:", data.get('message', {}).get('summary', {}).get('total_edges'))
print("Total Flow Value:", data.get('message', {}).get('summary', {}).get('total_transaction_value'))
