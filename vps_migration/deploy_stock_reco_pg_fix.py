"""
deploy_stock_reco_pg_fix.py  (v3 — no f-strings)
Deploys a Server Script that overrides the broken get_items endpoint
in Stock Reconciliation with a PostgreSQL-safe GROUP BY query.
"""
import urllib.request
import urllib.parse
import http.cookiejar
import json

BASE = "http://38.247.138.224:10017"
jar  = http.cookiejar.CookieJar()
op   = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H    = {"Content-Type": "application/json", "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"}

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req  = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print("  HTTP %d: %s" % (e.code, body[:400]))
        return {}

# Login
login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
op.open(urllib.request.Request(
    BASE + "/api/method/login",
    data=b"usr=Administrator&pwd=admin", headers=login_h
), timeout=30)
print("Login OK")

# ─── Server Script — no imports, no tuple unpacking, no f-strings ──────
SCRIPT = r'''
def do_stock_reco_get_items():
    raw_ignore = frappe.form_dict.get("ignore_empty_stock") or 0
    try:
        ignore_empty_stock = int(raw_ignore)
    except Exception:
        ignore_empty_stock = 0

    warehouse    = frappe.form_dict.get("warehouse")
    posting_date = frappe.form_dict.get("posting_date")
    posting_time = frappe.form_dict.get("posting_time")
    company      = frappe.form_dict.get("company")

    if not (warehouse and company):
        frappe.response["message"] = []
        return

    wh_bounds = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
    if not wh_bounds:
        frappe.response["message"] = []
        return
    lft = wh_bounds[0]
    rgt = wh_bounds[1]

    # Query 1: items already in Bin (no GROUP BY needed)
    q1 = (
        "select i.name as item_code, i.item_name, bin.warehouse as warehouse,"
        " i.has_serial_no, i.has_batch_no"
        " from `tabBin` bin, `tabItem` i"
        " where i.name = bin.item_code"
        " and IFNULL(i.disabled, 0) = 0"
        " and i.is_stock_item = 1"
        " and i.has_variants = 0"
        " and exists("
        "   select name from `tabWarehouse`"
        "   where lft >= " + str(lft) +
        "   and rgt <= " + str(rgt) +
        "   and name = bin.warehouse and is_group = 0"
        " )"
    )
    items = frappe.db.sql(q1, as_dict=1)

    # Query 2: items with default_warehouse — PG-safe GROUP BY
    q2 = (
        "select i.name as item_code, i.item_name, id.default_warehouse as warehouse,"
        " i.has_serial_no, i.has_batch_no"
        " from `tabItem` i, `tabItem Default` id"
        " where i.name = id.parent"
        " and exists("
        "   select name from `tabWarehouse`"
        "   where lft >= %s and rgt <= %s"
        "   and name = id.default_warehouse and is_group = 0"
        " )"
        " and i.is_stock_item = 1"
        " and i.has_variants = 0"
        " and IFNULL(i.disabled, 0) = 0"
        " and id.company = %s"
        " group by i.name, i.item_name, id.default_warehouse, i.has_serial_no, i.has_batch_no"
    )
    items += frappe.db.sql(q2, (lft, rgt, company), as_dict=1)

    # Remove duplicates
    iw_keys = set()
    deduped = []
    for item in items:
        key = str(item.get("item_code")) + ":::" + str(item.get("warehouse"))
        if key not in iw_keys:
            iw_keys.add(key)
            deduped.append(item)

    # Build result rows with qty + valuation_rate
    result = []
    for row in deduped:
        bin_data = frappe.db.get_value(
            "Bin",
            {"item_code": row.get("item_code"), "warehouse": row.get("warehouse")},
            ["actual_qty", "valuation_rate"],
            as_dict=1
        ) or {}
        try:
            qty = float(bin_data.get("actual_qty") or 0.0)
        except Exception:
            qty = 0.0
        try:
            val = float(bin_data.get("valuation_rate") or 0.0)
        except Exception:
            val = 0.0

        if ignore_empty_stock and not qty:
            continue
        result.append({
            "item_code":               row.get("item_code"),
            "item_name":               row.get("item_name"),
            "warehouse":               row.get("warehouse"),
            "has_serial_no":           row.get("has_serial_no"),
            "has_batch_no":            row.get("has_batch_no"),
            "qty":                     qty,
            "valuation_rate":          val,
            "current_qty":             qty,
            "current_valuation_rate":  val,
            "current_amount":          qty * val,
            "amount":                  qty * val,
        })

    frappe.response["message"] = result

do_stock_reco_get_items()
'''

SCRIPT_NAME       = "VMS StockReco PG Fix v3"
SCRIPT_API_METHOD = "erpnext.stock.doctype.stock_reconciliation.stock_reconciliation.get_items"

print("\nDeploying Server Script: %r" % SCRIPT_NAME)
print("  API method: %r" % SCRIPT_API_METHOD)

# Remove any old version
for old_name in ["VMS StockReco PG Fix", "VMS StockReco PG Fix v2", "VMS StockReco PG Fix v3"]:
    try:
        call("/api/resource/Server%20Script/%s" % urllib.parse.quote(old_name), "DELETE")
        print("  Removed old: %r" % old_name)
    except Exception:
        pass

# Update or Create
payload = {
    "script":      SCRIPT,
    "script_type": "API",
    "api_method":  SCRIPT_API_METHOD,
    "allow_guest": 0,
    "disabled":    0,
}

# Try PUT first (update)
target_url = "/api/resource/Server%20Script/" + urllib.parse.quote(SCRIPT_NAME)
result = call(target_url, "PUT", payload)
if not (result.get("data") or result.get("message")):
    # Try POST if not exists
    payload["doctype"] = "Server Script"
    payload["name"] = SCRIPT_NAME
    result = call("/api/resource/Server%20Script", "POST", payload)

if result.get("data") or result.get("message"):
    print("  [OK] Server Script saved successfully!")
else:
    print("  [FAIL] %s" % json.dumps(result)[:400])
    raise SystemExit(1)

# Verify
print("\nVerifying — calling get_items on VPS…")
verify = call(
    "/api/method/erpnext.stock.doctype.stock_reconciliation.stock_reconciliation.get_items",
    "POST",
    {
        "warehouse":          "Automan Car Care Center - UM",
        "posting_date":       "2026-09-10",
        "posting_time":       "10:12:30",
        "company":            "ULTRA MRF",
        "ignore_empty_stock": 1,
    },
)
exc = verify.get("exc_type", "")
msg = verify.get("message")
if exc == "GroupingError":
    print("  [FAIL] GroupingError still occurs!")
elif exc:
    print("  [WARN] Different error (%s): %s" % (exc, verify.get("exception","")[:200]))
elif isinstance(msg, list):
    print("  [OK] get_items returned %d item(s) — GroupingError FIXED!" % len(msg))
else:
    print("  [OK] No GroupingError. Response keys: %s" % list(verify.keys()))
