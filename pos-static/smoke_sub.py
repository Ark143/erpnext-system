import subprocess, json

REPORTS = [
    ("Sales Order Trends", {"period":"Monthly","based_on":"Item","company":"ULTRA MRF"}),
    ("Purchase Order Trends", {"period":"Monthly","based_on":"Item","company":"ULTRA MRF","period_based_on":"posting_date"}),
    ("Delivery Note Trends", {"period":"Yearly","based_on":"Customer","company":"ULTRA MRF"}),
    ("Purchase Receipt Trends", {"period":"Monthly","based_on":"Supplier","company":"ULTRA MRF","period_based_on":"posting_date"}),
    ("Sales Analytics", {"doc_type":"Sales Invoice","tree_type":"Customer","based_on":"Item","company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","range":"age","value_quantity":"Value"}),
    ("Sales Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Purchase Register", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Cash Flow", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","periodicity":"Monthly"}),
    ("Gross Profit", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","group_by":"Invoice"}),
    ("Accounts Receivable", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31","report_date":"2026-12-31"}),
    ("Stock Ledger", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Profit and Loss Statement", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
    ("Balance Sheet", {"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}),
]

subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","cp",
                "/mnt/c/Users/josem/erpnext-system/pos-static/rpt_one.py","erp-frappe:/tmp/rpt_one.py"],
               check=True, capture_output=True, text=True)

ok=0; fail=0
for name, fl in REPORTS:
    p = subprocess.run(
        ["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",
         '/workspace/frappe-bench/env/bin/python /tmp/rpt_one.py ' + json.dumps(name) + ' ' + json.dumps(json.dumps(fl))],
        capture_output=True, text=True, timeout=120)
    out = (p.stdout.strip().splitlines() or [p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""])[-1]
    status = "OK" if out.startswith("OK") else "FAIL"
    if status=="OK": ok+=1
    else: fail+=1
    print(f"{status:4} {name}: {out}")
print(f"\nFINAL SUMMARY ok={ok} fail={fail}")
