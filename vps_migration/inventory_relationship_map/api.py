"""Read-only inventory graph; also compiled into a Frappe API Server Script.

Keep build_map compatible with RestrictedPython: no imports inside the function,
no SQL, no get_all, and every document lookup passes a permission-aware get_list.
"""
import frappe


def build_map(params):
    if frappe.session.user == "Guest":
        frappe.throw("Please sign in to view inventory relationships.")
    item_code = params.get("item_code")
    company = params.get("company")
    warehouse = params.get("warehouse")
    from_date = params.get("from_date")
    to_date = params.get("to_date")
    limit = min(300, max(1, int(params.get("limit") or 120)))
    if from_date:
        from_date = str(frappe.utils.getdate(from_date))
    if to_date:
        to_date = str(frappe.utils.getdate(to_date))
    if from_date and to_date and from_date > to_date:
        frappe.throw("From date must be on or before To date.")

    allowed_types = ["Stock Entry", "Stock Reconciliation", "Purchase Receipt",
                     "Delivery Note", "Sales Invoice", "Purchase Invoice", "POS Invoice"]
    root_type = params.get("doctype")
    root_name = params.get("docname")
    source_items = []
    if root_type or root_name:
        if root_type not in allowed_types or not root_name:
            frappe.throw("Choose a supported inventory document and its name.")
        found = frappe.get_list(root_type, filters={"name": root_name}, fields=["name"], limit_page_length=1)
        if not found:
            frappe.throw("Source document is unavailable or you do not have permission to read it.")
        source_doc = frappe.get_doc(root_type, root_name)
        for row in source_doc.get("items") or []:
            code = row.get("item_code")
            if code and code not in source_items:
                source_items.append(code)
        if not company:
            company = source_doc.get("company")
        if not item_code and source_items:
            item_code = source_items[0]
        if not item_code:
            return {"item": None, "source_items": [], "movements": [], "balances": [],
                    "documents": [], "references": [], "truncated": False,
                    "empty_reason": "This source document has no item rows to map."}

    wh_filters = {}
    if company:
        wh_filters["company"] = company
    if warehouse:
        wh_filters["name"] = warehouse
    warehouses = frappe.get_list("Warehouse", filters=wh_filters,
        fields=["name", "company"], order_by="name asc", limit_page_length=501)
    if len(warehouses) > 500:
        frappe.throw("More than 500 warehouses match. Choose a company or warehouse.")
    wh_names = [w.get("name") for w in warehouses]
    company_by_wh = {}
    for w in warehouses:
        company_by_wh[w.get("name")] = w.get("company")
    if warehouse and not wh_names:
        frappe.throw("Warehouse is unavailable for the selected company or your permissions.")
    filters = {"is_cancelled": 0, "warehouse": ["in", wh_names]}
    if company:
        filters["company"] = company
    if not item_code:
        recent = frappe.get_list("Stock Ledger Entry", filters=filters,
            fields=["item_code"], order_by="posting_date desc, posting_time desc, creation desc", limit_page_length=1)
        if recent:
            item_code = recent[0].get("item_code")
    if not item_code:
        return {"item": None, "source_items": source_items, "movements": [], "balances": [],
                "documents": [], "references": [], "truncated": False}
    items = frappe.get_list("Item", filters={"name": item_code},
        fields=["name", "item_name", "stock_uom", "is_stock_item"], limit_page_length=1)
    if not items:
        frappe.throw("Item is unavailable or you do not have permission to read it.")
    filters["item_code"] = item_code
    if from_date and to_date:
        filters["posting_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["posting_date"] = [">=", from_date]
    elif to_date:
        filters["posting_date"] = ["<=", to_date]
    rows = frappe.get_list("Stock Ledger Entry", filters=filters,
        fields=["name", "item_code", "warehouse", "company", "posting_date", "posting_time",
                "voucher_type", "voucher_no", "actual_qty", "qty_after_transaction", "stock_uom",
                "batch_no", "serial_no", "serial_and_batch_bundle"],
        order_by="posting_date desc, posting_time desc, creation desc, name desc", limit_page_length=limit + 1)
    truncated = len(rows) > limit
    rows = rows[:limit]
    # Bin is a current snapshot, independent of the selected ledger dates.
    balances = frappe.get_list("Bin", filters={"item_code": item_code, "warehouse": ["in", wh_names]},
        fields=["name", "warehouse", "actual_qty", "reserved_qty", "ordered_qty", "projected_qty"],
        order_by="warehouse asc", limit_page_length=501)
    if len(balances) > 500:
        frappe.throw("Too many balances. Choose a warehouse.")
    for balance in balances:
        balance["company"] = company_by_wh.get(balance.get("warehouse"))
    documents = []
    references = []
    seen = []
    readable = []
    for row in rows:
        dt = row.get("voucher_type")
        name = row.get("voucher_no")
        key = dt + "::" + name
        if key in seen:
            continue
        seen.append(key)
        if dt not in allowed_types:
            continue
        permitted = frappe.get_list(dt, filters={"name": name}, fields=["name"], limit_page_length=1)
        if not permitted:
            continue
        doc = frappe.get_doc(dt, name)
        readable.append(key)
        documents.append({"id": key, "doctype": dt, "name": name,
            "status": "Cancelled" if doc.get("docstatus") == 2 else (doc.get("status") or "Submitted"),
            "purpose": doc.get("purpose"), "date": str(doc.get("posting_date") or ""),
            "company": doc.get("company"), "party": doc.get("supplier") or doc.get("customer")})
        link_fields = {"purchase_order": "Purchase Order", "purchase_receipt": "Purchase Receipt",
                       "sales_order": "Sales Order", "delivery_note": "Delivery Note",
                       "material_request": "Material Request"}
        for child in doc.get("items") or []:
            if child.get("item_code") != item_code:
                continue
            for field in link_fields:
                linked_name = child.get(field)
                linked_type = link_fields[field]
                if linked_name:
                    allowed = frappe.get_list(linked_type, filters={"name": linked_name}, fields=["name"], limit_page_length=1)
                    edge = {"from": linked_type + "::" + linked_name, "to": key,
                            "doctype": linked_type, "name": linked_name}
                    if allowed and edge not in references:
                        references.append(edge)
        return_against = doc.get("return_against")
        if return_against:
            allowed = frappe.get_list(dt, filters={"name": return_against}, fields=["name"], limit_page_length=1)
            if allowed:
                references.append({"from": dt + "::" + return_against, "to": key,
                                   "doctype": dt, "name": return_against, "label": "Return against"})
    # Ledger rows themselves are permission-filtered. Voucher links are shown only
    # when the source document is also readable.
    for row in rows:
        row["can_open_voucher"] = row.get("voucher_type") + "::" + row.get("voucher_no") in readable
    return {"item": items[0], "source_items": source_items, "company": company,
            "movements": rows, "balances": balances, "documents": documents,
            "references": references, "truncated": truncated, "limit": limit,
            "from_date": from_date, "to_date": to_date}


@frappe.whitelist()
def get_inventory_relationship_map(**kwargs):
    return build_map(kwargs)
