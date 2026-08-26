import frappe

def main():
    out = []
    def cnt(dt):
        try:
            return frappe.db.count(dt)
        except Exception as e:
            return f"ERR:{e}"
    def names(dt, limit=12):
        try:
            return frappe.get_all(dt, fields=["name"], limit=limit)
        except Exception as e:
            return f"ERR:{e}"

    for dt in ["Company","Branch","Cost Center","Sales Person","Customer","Customer Vehicle",
               "Warehouse","Item","Inspection Template","User","Vehicle Make","Vehicle Model",
               "Bin Location","Vehicle Estimate","Vehicle Job Order","Vehicle Inspection",
               "Inventory Dimension","Stock Entry","Purchase Receipt","Sales Invoice","Payment Entry"]:
        c = cnt(dt)
        out.append(f"{dt}: {c}")
    out.append("---- sample names ----")
    for dt in ["Company","Branch","Cost Center","Sales Person","Inspection Template","Bin Location","Vehicle Make"]:
        out.append(f"{dt} sample: {[r['name'] for r in names(dt)]}")
    # customers & vehicles sample
    out.append("Customer sample: " + str([r['name'] for r in names('Customer', 8)]))
    out.append("Customer Vehicle sample: " + str([r['name'] for r in names('Customer Vehicle', 8)]))
    out.append("Item sample: " + str([r['name'] for r in names('Item', 8)]))
    out.append("Warehouse sample: " + str([r['name'] for r in names('Warehouse', 8)]))
    out.append("Inventory Dimension sample: " + str([r['name'] for r in names('Inventory Dimension', 8)]))
    print("\n".join(out))
