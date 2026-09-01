import json, csv, os, sys
EXPORT = "C:/Users/josem/erpnext-system/pos-static/export"
CSV = "C:/Users/josem/erpnext-system/pos-static/csv"
os.makedirs(CSV, exist_ok=True)

SKIP = {"creation","modified","modified_by","owner","idx","docstatus","amended_from",
        "_comments","_assign","_user_tags","_liked_by","parent","parentfield","parenttype",
        "_last_updated","__version","lft","rgt","_user","_liked_by"}

def gen(dt):
    fname = dt.replace(" ", "_") + ".json"
    fp = os.path.join(EXPORT, fname)
    if not os.path.exists(fp):
        print("NO EXPORT", dt); return
    rows = json.load(open(fp, encoding="utf-8"))
    # collect all keys
    keys = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in SKIP and k not in seen and not k.startswith("__"):
                seen.add(k); keys.append(k)
    out = os.path.join(CSV, dt.replace(" ", "_") + ".csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = {k: ("" if r.get(k) is None else r.get(k)) for k in keys}
            w.writerow(row)
    print(f"{dt}: {len(rows)} rows -> {out} ({len(keys)} cols)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for dt in sys.argv[1:]: gen(dt)
    else:
        for dt in ["Item Group","Customer Group","Supplier Group","Price List","Vehicle Make",
                   "Vehicle Model","Warehouse","Account","Cost Center","POS Profile","Mode of Payment",
                   "Bin","Cashier Profile","Inspection Template","Item Part Cross Reference",
                   "Item Vehicle Compatibility","Bin Location","Vehicle Service Reminder",
                   "Supplier","Item","Customer","Customer Vehicle","Company"]:
            gen(dt)
