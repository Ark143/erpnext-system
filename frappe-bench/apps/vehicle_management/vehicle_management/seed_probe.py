import frappe, json

def main():
    out = []
    # inventory dimension fieldname
    try:
        dim = frappe.get_doc("Inventory Dimension", "Bin Location")
        out.append(f"INVDIM: name={dim.name} fieldname={dim.fieldname} type={dim.type} reference_document={dim.reference_document}")
    except Exception as e:
        out.append(f"INVDIM ERR {e}")

    # child doctypes field lists
    for dt in ["Job Order Service Item","Job Order Part Item","Vehicle Inspection Item"]:
        try:
            meta = frappe.get_meta(dt)
            flds = [(f.fieldname, f.fieldtype, (f.options or "")[:30]) for f in meta.fields if f.fieldtype not in ("Section Break","Column Break","HTML")]
            out.append(f"CHILD {dt}: {flds}")
        except Exception as e:
            out.append(f"CHILD {dt} ERR {e}")

    # sample existing vehicle_estimate to mirror
    try:
        est = frappe.get_all("Vehicle Estimate", limit=1)
        if est:
            d = frappe.get_doc("Vehicle Estimate", est[0].name)
            out.append(f"SAMPLE EST name={d.name} company={d.company} customer={d.customer} vehicle={d.vehicle} service_advisor={d.service_advisor} status={d.status}")
            out.append(f"  services rows={len(d.services)} parts rows={len(d.parts)} grand_total={d.grand_total}")
            if d.services:
                s=d.services[0]
                out.append(f"  service[0] fields: {[(k, getattr(s,k)) for k in ['item_code','description','qty','rate','amount'] if hasattr(s,k)]}")
            if d.parts:
                p=d.parts[0]
                out.append(f"  part[0] fields: {[(k, getattr(p,k)) for k in ['item_code','description','qty','rate','amount'] if hasattr(p,k)]}")
    except Exception as e:
        out.append(f"SAMPLE EST ERR {e}")

    # sample stock entry item fields + dimension usage
    try:
        se = frappe.get_all("Stock Entry", limit=1)
        if se:
            d = frappe.get_doc("Stock Entry", se[0].name)
            out.append(f"SAMPLE SE name={d.name} type={d.stock_entry_type} company={d.company} branch={getattr(d,'branch',None)}")
            if d.items:
                it=d.items[0]
                keys=[k for k in ['item_code','qty','t_warehouse','s_warehouse','cost_center','bin_location','basic_rate'] if hasattr(it,k)]
                out.append(f"  SE item[0]: {[(k, getattr(it,k)) for k in keys]}")
    except Exception as e:
        out.append(f"SAMPLE SE ERR {e}")

    # sample purchase receipt item fields
    try:
        pr = frappe.get_all("Purchase Receipt", limit=1)
        if pr:
            d = frappe.get_doc("Purchase Receipt", pr[0].name)
            out.append(f"SAMPLE PR name={d.name} company={d.company} supplier={d.supplier} branch={getattr(d,'branch',None)}")
            if d.items:
                it=d.items[0]
                keys=[k for k in ['item_code','qty','warehouse','cost_center','bin_location','rate','base_rate'] if hasattr(it,k)]
                out.append(f"  PR item[0]: {[(k, getattr(it,k)) for k in keys]}")
    except Exception as e:
        out.append(f"SAMPLE PR ERR {e}")

    print("\n".join(out))
