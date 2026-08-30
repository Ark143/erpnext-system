import frappe
frappe.init('site1.local', sites_path='/workspace/frappe-bench/sites')
frappe.connect()

items = ["185/70 R14 YOKOHAMA ES32","WHEEL ALIGNMENT (TOE-IN, TOE-OUT)","PMS LABOR (LIGHT)","STRL-CAR PROTECT KIT (CAR CLEAN SET)"]
print("=== ITEMS referenced by generator ===")
for it in items:
    print("  ITEM", repr(it), "->", frappe.db.exists("Item", it))

comps = frappe.get_all("Company", fields=["name","abbr"])
print("=== COMPANIES:", len(comps))
for c in comps:
    abbr = c["abbr"]
    wh = frappe.db.exists("Warehouse", "Stores - " + abbr)
    bins = frappe.db.count("Bin Location", {"warehouse": "Stores - " + abbr})
    sales = frappe.db.exists("Account", "Sales - " + abbr)
    cash = frappe.db.exists("Account", "Cash - " + abbr)
    debt = frappe.db.exists("Account", "Debtors - " + abbr)
    cred = frappe.db.exists("Account", "Creditors - " + abbr)
    cogs = frappe.db.exists("Account", "Cost of Goods Sold - " + abbr)
    print(f"  {c['name']} ({abbr}) wh={wh} bins={bins} sales={sales} cash={cash} debt={debt} cred={cred} cogs={cogs}")

print("=== EXISTING TRANSACTION COUNTS (baseline) ===")
for dt in ["Vehicle Estimate","Vehicle Job Order","Vehicle Inspection","Sales Invoice","Purchase Order","Purchase Receipt","Purchase Invoice","Payment Entry","Stock Entry","Sales Person","Customer Vehicle"]:
    try:
        print("  ", dt, "=", frappe.db.count(dt))
    except Exception as e:
        print("  ", dt, "ERR", e)
