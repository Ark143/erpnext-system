import subprocess, json
REPORTS = [
    ("Profit and Loss Statement", {"company":"ULTRA MRF","period_start_date":"2026-01-01","period_end_date":"2026-12-31","accumulated_values":0,"presentation_currency":"","filter_based_on":"Date","periodicity":"Monthly","selected_view":"Report"}),
    ("Balance Sheet", {"company":"ULTRA MRF","period_start_date":"2026-01-01","period_end_date":"2026-12-31","accumulated_values":0,"presentation_currency":"","filter_based_on":"Date","periodicity":"Monthly"}),
]
for name, fl in REPORTS:
    p = subprocess.run(["wsl","-d","podman-machine-default","sudo","podman","exec","erp-frappe","bash","-c",
        '/workspace/frappe-bench/env/bin/python /tmp/rpt_one.py ' + json.dumps(name) + ' ' + json.dumps(json.dumps(fl))],
        capture_output=True, text=True, timeout=120)
    out = (p.stdout.strip().splitlines() or [p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""])[-1]
    print(f"{name}: {out}")
