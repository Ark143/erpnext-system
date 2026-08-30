import subprocess, sys, json

APIS = ["vm_pos_meta","vm_pos_history","vm_pos_cashier","vm_pos_items","vm_pos_vehicles",
        "vm_pos_vehicle_customer","vm_pos_stock","executive_dashboard","vm_company_dashboard_api","vm_probe_api"]

RUNNER = r'''
import urllib.request, urllib.parse, http.cookiejar, json, sys
BASE="http://localhost"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.open(urllib.request.Request(BASE+"/api/method/login", data=json.dumps({"usr":"administrator","pwd":"admin"}).encode(), headers={"Content-Type":"application/json"}), timeout=30)
m=sys.argv[1]
try:
    r=op.open(urllib.request.Request(BASE+"/api/method/"+m), timeout=80)
    d=json.loads(r.read().decode()); msg=d.get("message")
    sz=len(msg) if isinstance(msg,(list,dict)) else 0
    print(f"OK   {m}: http={r.status} type={type(msg).__name__} size={sz}")
except urllib.error.HTTPError as e:
    print(f"FAIL {m}: HTTP {e.code} {e.read().decode()[:160]}")
except Exception as e:
    print(f"FAIL {m}: {type(e).__name__}: {str(e)[:120]}")
'''

with open("/tmp/runner_single.py","w") as f: f.write(RUNNER)

for m in APIS:
    p = subprocess.run([sys.executable, "-c", RUNNER, m], capture_output=True, text=True, timeout=100)
    out = p.stdout.strip() or p.stderr.strip()
    print(out.splitlines()[0] if out else f"HANG {m}")
