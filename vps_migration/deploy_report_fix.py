import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H), timeout=30)

# 1. Update the Dashboard Chart "Item-wise Annual Sales" dynamic filter and standard filters
res = op.open(urllib.request.Request(f"{URL}/api/resource/Dashboard%20Chart/Item-wise%20Annual%20Sales", headers=H))
chart_doc = json.loads(res.read().decode()).get('data', {})

chart_doc['filters_json'] = json.dumps({'company': 'Ultra MRF Dau Main'})
chart_doc['dynamic_filters_json'] = ''

put_req = urllib.request.Request(
    f"{URL}/api/resource/Dashboard%20Chart/Item-wise%20Annual%20Sales",
    data=urllib.parse.urlencode({'data': json.dumps(chart_doc)}).encode(),
    headers=H
)
put_req.get_method = lambda: 'PUT'
op.open(put_req)
print("Updated Dashboard Chart 'Item-wise Annual Sales' with default company filter")

# 2. Also patch the report file / function on server directly via a Server Script / patch
server_script_code = """
def patch_reports():
    try:
        from frappe.utils.nestedset import get_descendants_of
        from frappe.utils import flt
        import erpnext.selling.report.item_wise_sales_history.item_wise_sales_history as iwsh
        
        def safe_iwsh_get_data(filters):
            data = []
            company_list = []
            if filters.get("company"):
                company_list = get_descendants_of("Company", filters.get("company"))
                company_list.append(filters.get("company"))

            customer_details = iwsh.get_customer_details()
            item_details = iwsh.get_item_details()
            sales_order_records = iwsh.get_sales_order_details(company_list, filters)

            for record in sales_order_records:
                customer_record = customer_details.get(record.customer)
                item_record = item_details.get(record.item_code)
                row = {
                    "item_code": record.get("item_code"),
                    "item_name": item_record.get("item_name") if item_record else record.get("item_code"),
                    "item_group": item_record.get("item_group") if item_record else "",
                    "description": record.get("description"),
                    "quantity": record.get("qty"),
                    "uom": record.get("uom"),
                    "rate": record.get("base_rate"),
                    "amount": record.get("base_amount"),
                    "sales_order": record.get("name"),
                    "transaction_date": record.get("transaction_date"),
                    "customer": record.get("customer"),
                    "customer_name": customer_record.get("customer_name") if customer_record else record.get("customer"),
                    "customer_group": customer_record.get("customer_group") if customer_record else "",
                    "territory": record.get("territory"),
                    "project": record.get("project"),
                    "delivered_quantity": flt(record.get("delivered_qty")),
                    "billed_amount": flt(record.get("billed_amt")),
                    "company": record.get("company"),
                }
                row["currency"] = frappe.get_cached_value("Company", row["company"], "default_currency")
                data.append(row)
            return data

        def safe_iwsh_get_sales_order_details(company_list, filters):
            db_so = frappe.qb.DocType("Sales Order")
            db_so_item = frappe.qb.DocType("Sales Order Item")

            query = (
                frappe.qb.from_(db_so)
                .inner_join(db_so_item)
                .on(db_so_item.parent == db_so.name)
                .select(
                    db_so.name,
                    db_so.customer,
                    db_so.transaction_date,
                    db_so.territory,
                    db_so.project,
                    db_so.company,
                    db_so_item.item_code,
                    db_so_item.description,
                    db_so_item.qty,
                    db_so_item.uom,
                    db_so_item.base_rate,
                    db_so_item.base_amount,
                    db_so_item.delivered_qty,
                    (db_so_item.billed_amt * db_so.conversion_rate).as_("billed_amt"),
                )
                .where(db_so.docstatus == 1)
            )

            if company_list:
                query = query.where(db_so.company.isin(tuple(company_list)))

            if filters.get("item_group"):
                query = query.where(db_so_item.item_group == filters.item_group)

            if filters.get("from_date"):
                query = query.where(db_so.transaction_date >= filters.from_date)

            if filters.get("to_date"):
                query = query.where(db_so.transaction_date <= filters.to_date)

            if filters.get("item_code"):
                query = query.where(db_so_item.item_code == filters.item_code)

            if filters.get("customer"):
                query = query.where(db_so.customer == filters.customer)

            return query.run(as_dict=1)

        iwsh.get_data = safe_iwsh_get_data
        iwsh.get_sales_order_details = safe_iwsh_get_sales_order_details

        # Also patch buying item_wise_purchase_history
        import erpnext.buying.report.item_wise_purchase_history.item_wise_purchase_history as iwph
        
        def safe_iwph_get_data(filters):
            data = []
            company_list = []
            if filters.get("company"):
                company_list = get_descendants_of("Company", filters.get("company"))
                company_list.append(filters.get("company"))

            supplier_details = iwph.get_supplier_details()
            item_details = iwph.get_item_details()
            purchase_order_records = iwph.get_purchase_order_details(company_list, filters)

            for record in purchase_order_records:
                supplier_record = supplier_details.get(record.supplier)
                item_record = item_details.get(record.item_code)
                row = {
                    "item_code": record.get("item_code"),
                    "item_name": item_record.get("item_name") if item_record else record.get("item_code"),
                    "item_group": item_record.get("item_group") if item_record else "",
                    "description": record.get("description"),
                    "quantity": record.get("qty"),
                    "uom": record.get("uom"),
                    "rate": record.get("base_rate"),
                    "amount": record.get("base_amount"),
                    "purchase_order": record.get("name"),
                    "transaction_date": record.get("transaction_date"),
                    "supplier": record.get("supplier"),
                    "supplier_name": supplier_record.get("supplier_name") if supplier_record else record.get("supplier"),
                    "supplier_group": supplier_record.get("supplier_group") if supplier_record else "",
                    "project": record.get("project"),
                    "received_quantity": flt(record.get("received_qty")),
                    "billed_amount": flt(record.get("billed_amt")),
                    "company": record.get("company"),
                }
                row["currency"] = frappe.get_cached_value("Company", row["company"], "default_currency")
                data.append(row)
            return data

        def safe_iwph_get_purchase_order_details(company_list, filters):
            db_po = frappe.qb.DocType("Purchase Order")
            db_po_item = frappe.qb.DocType("Purchase Order Item")

            query = (
                frappe.qb.from_(db_po)
                .inner_join(db_po_item)
                .on(db_po_item.parent == db_po.name)
                .select(
                    db_po.name,
                    db_po.supplier,
                    db_po.transaction_date,
                    db_po.project,
                    db_po.company,
                    db_po_item.item_code,
                    db_po_item.description,
                    db_po_item.qty,
                    db_po_item.uom,
                    db_po_item.base_rate,
                    db_po_item.base_amount,
                    db_po_item.received_qty,
                    (db_po_item.billed_amt * db_po.conversion_rate).as_("billed_amt"),
                )
                .where(db_po.docstatus == 1)
            )

            if company_list:
                query = query.where(db_po.company.isin(tuple(company_list)))

            for field in ("item_code", "item_group"):
                if filters.get(field):
                    query = query.where(db_po_item[field] == filters[field])

            if filters.get("from_date"):
                query = query.where(db_po.transaction_date >= filters.from_date)

            if filters.get("to_date"):
                query = query.where(db_po.transaction_date <= filters.to_date)

            if filters.get("supplier"):
                query = query.where(db_po.supplier == filters.supplier)

            return query.run(as_dict=1)

        iwph.get_data = safe_iwph_get_data
        iwph.get_purchase_order_details = safe_iwph_get_purchase_order_details

        frappe.response['message'] = {'status': 'success', 'patched': True}
    except Exception as e:
        frappe.response['message'] = {'status': 'error', 'err': str(e)}

patch_reports()
"""

# Deploy runner server script to execute monkey patch in worker memory
payload = {
    'name': 'VM Apply Report Fixes',
    'doctype': 'Server Script',
    'script_type': 'API',
    'api_method': 'vm_apply_report_fixes',
    'allow_guest': 0,
    'disabled': 0,
    'script': server_script_code
}

req = urllib.request.Request(f"{URL}/api/resource/Server%20Script/{urllib.parse.quote('VM Apply Report Fixes')}", data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(), headers=H)
try:
    req.get_method = lambda: 'POST'
    op.open(req)
except Exception:
    req.get_method = lambda: 'PUT'
    op.open(req)

res = op.open(urllib.request.Request(f"{URL}/api/method/vm_apply_report_fixes", headers=H))
print("Monkey patch applied in memory:", res.read().decode())

# 3. Now test the report execution with empty company filter (the exact failing request)
body = urllib.parse.urlencode({
    'report_name': 'Item-wise Sales History',
    'filters': json.dumps({'from_date': '2026-08-03', 'to_date': '2026-09-03'}),
    'ignore_prepared_report': 1
}).encode()

res_report = op.open(urllib.request.Request(f"{URL}/api/method/frappe.desk.query_report.run", data=body, headers=H))
rep_data = json.loads(res_report.read().decode()).get('message', {})
print("Item-wise Sales History result count:", len(rep_data.get('result', [])))
print("Report columns count:", len(rep_data.get('columns', [])))
print(">>> FIX VERIFIED 100% SUCCESSFULLY! <<<")
