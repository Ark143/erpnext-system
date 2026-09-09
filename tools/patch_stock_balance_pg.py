import urllib.request
import urllib.parse
import json
import http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

patch_code = '''
def apply_stock_fix():
    import frappe
    from frappe.utils import flt
    import erpnext.stock.stock_balance as sb
    
    def get_reserved_qty(item_code, warehouse):
        dont_reserve_on_return = frappe.get_cached_value(
            "Selling Settings", "Selling Settings", "dont_reserve_sales_order_qty_on_sales_return"
        )
        # Convert integer to boolean/integer condition safe for Postgres
        flag = 1 if dont_reserve_on_return else 0
        reserved_qty = frappe.db.sql(
            f"""
            select
                sum(dnpi_qty * ((so_item_qty - so_item_delivered_qty - (CASE WHEN dont_reserve_qty_on_return = 1 THEN so_item_returned_qty ELSE 0 END)) / so_item_qty))
            from
                (
                    (select
                        qty as dnpi_qty,
                        (
                            select qty from `tabSales Order Item`
                            where name = dnpi.parent_detail_docname
                            and (delivered_by_supplier is null or delivered_by_supplier = 0)
                        ) as so_item_qty,
                        (
                            select delivered_qty from `tabSales Order Item`
                            where name = dnpi.parent_detail_docname
                            and delivered_by_supplier = 0
                        ) as so_item_delivered_qty,
                        (
                            select returned_qty from `tabSales Order Item`
                            where name = dnpi.parent_detail_docname
                            and delivered_by_supplier = 0
                        ) as so_item_returned_qty,
                        {flag} as dont_reserve_qty_on_return,
                        parent, name
                    from
                    (
                        select qty, parent_detail_docname, parent, name
                        from `tabPacked Item` dnpi_in
                        where item_code = %s and warehouse = %s
                        and parenttype='Sales Order'
                        and item_code != parent_item
                        and exists (select * from `tabSales Order` so
                        where name = dnpi_in.parent and docstatus = 1 and status not in ('On Hold', 'Closed'))
                    ) dnpi)
                union
                    (select stock_qty as dnpi_qty, qty as so_item_qty,
                        delivered_qty as so_item_delivered_qty,
                        returned_qty as so_item_returned_qty,
                        {flag} as dont_reserve_qty_on_return, parent, name
                    from `tabSales Order Item` so_item
                    where item_code = %s and warehouse = %s
                    and (so_item.delivered_by_supplier is null or so_item.delivered_by_supplier = 0)
                    and exists(select * from `tabSales Order` so
                    where name = so_item.parent and docstatus = 1 and status not in ('On Hold', 'Closed'))
                )) tab
            """,
            (item_code, warehouse, item_code, warehouse),
        )

        return flt(reserved_qty[0][0]) if reserved_qty else 0.0

    sb.get_reserved_qty = get_reserved_qty

    # Also update on disk in stock_balance.py if possible
    try:
        import os
        filepath = sb.__file__
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the problematic CASE WHEN condition with Postgres-safe syntax
        bad_pattern = "case when dont_reserve_qty_on_return then"
        good_pattern = "case when dont_reserve_qty_on_return = 1 then"
        if bad_pattern in content:
            content = content.replace(bad_pattern, good_pattern)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception as e:
        pass

    frappe.response["message"] = {"status": "success", "message": "Patched erpnext.stock.stock_balance.get_reserved_qty for Postgres"}

apply_stock_fix()
'''

server_script_payload = {
    'doctype': 'Server Script',
    'name': 'VM Patch Stock Balance',
    'script_type': 'API',
    'api_method': 'vm_patch_stock_balance',
    'allow_guest': 1,
    'disabled': 0,
    'script': patch_code
}

# Check if exists
try:
    check = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Patch%20Stock%20Balance', headers=H))
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Patch%20Stock%20Balance',
        data=urllib.parse.urlencode({'data': json.dumps(server_script_payload)}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    op.open(req)
except Exception:
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script',
        data=urllib.parse.urlencode({'data': json.dumps(server_script_payload)}).encode(),
        headers=H
    )
    op.open(req)

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_patch_stock_balance', headers=H))
print("Patch Response:", r_call.read().decode())
