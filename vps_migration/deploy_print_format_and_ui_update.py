"""
deploy_print_format_and_ui_update.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Deploys updated Client Script with 'Same Count (System = Actual)' button
2. Deploys professional Jinja Print Format 'Inventory Count Sheet Standard'
3. Verifies both on VPS
"""

import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    try:
        with op.open(req, timeout=60) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code} on {method} {path}: {body[:300]}")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
        ),
        timeout=30,
    )
    print("[OK] Logged into VPS as " + usr)

def deploy_client_script():
    print("\n[1] Deploying updated Client Script...")
    with open(r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\vehicle_management\doctype\inventory_count_sheet\inventory_count_sheet.js", "r", encoding="utf-8") as f:
        js_code = f.read()

    script_name = "VMS Inventory Count Sheet UI"
    quoted = urllib.parse.quote(script_name)
    existing = call(f"/api/resource/Client%20Script/{quoted}", "GET")
    
    payload = {
        "dt": "Inventory Count Sheet",
        "script_type": "Form",
        "script": js_code,
        "enabled": 1,
    }
    
    if existing.get("data"):
        doc = existing["data"]
        doc.update(payload)
        res = call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
    else:
        payload["doctype"] = "Client Script"
        payload["name"] = script_name
        res = call("/api/resource/Client%20Script", "POST", payload)
        
    print("  [OK] Client Script updated with 'Same Count (System = Actual)' button.")

PRINT_HTML = r"""
<div class="print-format-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; padding: 10px;">
  <style>
    @media print {
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .page-break { page-break-after: always; }
    }
    .meta-box { border: 1px solid #cbd5e1; border-collapse: collapse; width: 100%; font-size: 11px; margin-top: 10px; }
    .meta-box td { padding: 5px 8px; border: 1px solid #cbd5e1; }
    .meta-lbl { background: #f8fafc; font-weight: 600; width: 16%; }
    .meta-val { width: 34%; }
    .kpi-tile { flex: 1; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px; text-align: center; background: #fafafa; }
    .tbl-items { width: 100%; border-collapse: collapse; font-size: 10.5px; margin-top: 12px; }
    .tbl-items th { background: #1e293b; color: #fff; padding: 6px 4px; border: 1px solid #334155; }
    .tbl-items td { padding: 5px 4px; border: 1px solid #cbd5e1; }
    .sign-box { border: 1px solid #cbd5e1; background: #fafafa; padding: 8px; vertical-align: top; width: 25%; font-size: 10px; }
  </style>

  <!-- Header -->
  <table style="width: 100%; border-bottom: 2px solid #1e293b; padding-bottom: 8px; margin-bottom: 8px;">
    <tr>
      <td style="vertical-align: middle;">
        <h2 style="margin: 0; font-size: 18px; font-weight: 800; color: #0f172a; letter-spacing: -0.01em;">{{ doc.company }}</h2>
        <div style="font-size: 13px; font-weight: 700; color: #2563eb; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.05em;">
          INVENTORY COUNT SHEET / PHYSICAL CYCLE COUNT
        </div>
      </td>
      <td style="text-align: right; vertical-align: middle;">
        <div style="font-size: 16px; font-weight: 800; font-family: monospace; color: #0f172a;">{{ doc.name }}</div>
        <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Count Date: <strong>{{ doc.count_date }}</strong></div>
        <div style="font-size: 11px; color: #64748b;">Status: <span style="font-weight: 700; color: #2563eb;">{{ doc.status }}</span></div>
      </td>
    </tr>
  </table>

  <!-- Meta Table -->
  <table class="meta-box">
    <tr>
      <td class="meta-lbl">Warehouse / Branch:</td>
      <td class="meta-val"><strong>{{ doc.warehouse or "All Warehouses" }}</strong></td>
      <td class="meta-lbl">Count Type:</td>
      <td class="meta-val"><strong>{{ doc.count_type or "Full Physical Count" }}</strong></td>
    </tr>
    <tr>
      <td class="meta-lbl">Bin / Location:</td>
      <td class="meta-val">{{ doc.bin_filter or "All Locations" }}</td>
      <td class="meta-lbl">Remarks / Notes:</td>
      <td class="meta-val">{{ doc.remarks or "—" }}</td>
    </tr>
  </table>

  <!-- KPI Tiles -->
  <div style="display: flex; gap: 8px; margin-top: 10px; margin-bottom: 10px;">
    <div class="kpi-tile" style="border-top: 3px solid #6366f1;">
      <div style="font-size: 9px; color: #64748b; text-transform: uppercase;">Total Lines</div>
      <div style="font-size: 15px; font-weight: 700; color: #6366f1; font-family: monospace;">{{ doc.total_lines or (doc.items|length) }}</div>
    </div>
    <div class="kpi-tile" style="border-top: 3px solid #22c55e;">
      <div style="font-size: 9px; color: #64748b; text-transform: uppercase;">Counted</div>
      <div style="font-size: 15px; font-weight: 700; color: #22c55e; font-family: monospace;">{{ doc.counted_lines or 0 }}</div>
    </div>
    <div class="kpi-tile" style="border-top: 3px solid #3b82f6;">
      <div style="font-size: 9px; color: #64748b; text-transform: uppercase;">Matched</div>
      <div style="font-size: 15px; font-weight: 700; color: #3b82f6; font-family: monospace;">{{ doc.matched_lines or 0 }}</div>
    </div>
    <div class="kpi-tile" style="border-top: 3px solid #ef4444;">
      <div style="font-size: 9px; color: #64748b; text-transform: uppercase;">Variances</div>
      <div style="font-size: 15px; font-weight: 700; color: #ef4444; font-family: monospace;">{{ doc.variance_lines or 0 }}</div>
    </div>
    <div class="kpi-tile" style="border-top: 3px solid #8b5cf6;">
      <div style="font-size: 9px; color: #64748b; text-transform: uppercase;">Accuracy</div>
      <div style="font-size: 15px; font-weight: 700; color: #8b5cf6; font-family: monospace;">{{ doc.count_accuracy or 0 }}%</div>
    </div>
  </div>

  <!-- Items Table -->
  <table class="tbl-items">
    <thead>
      <tr>
        <th style="width: 22px; text-align: center;">#</th>
        <th style="width: 95px; text-align: left;">Warehouse</th>
        <th style="width: 105px; text-align: left;">Bin / Location</th>
        <th style="width: 120px; text-align: left;">Item Code</th>
        <th style="text-align: left;">Item Description</th>
        <th style="width: 35px; text-align: center;">UOM</th>
        <th style="width: 50px; text-align: right;">System</th>
        <th style="width: 60px; text-align: right;">Physical</th>
        <th style="width: 50px; text-align: right;">Variance</th>
        <th style="width: 50px; text-align: center;">Status</th>
      </tr>
    </thead>
    <tbody>
      {% for item in doc.items %}
      <tr style="{% if loop.index % 2 == 0 %}background: #f8fafc;{% endif %}">
        <td style="text-align: center;">{{ loop.index }}</td>
        <td>{{ item.warehouse or doc.warehouse or "—" }}</td>
        <td style="font-family: monospace; font-size: 9.5px; font-weight: 600; color: #1d4ed8;">{{ item.bin_location or "—" }}</td>
        <td style="font-family: monospace; font-weight: 600;">{{ item.item_code }}</td>
        <td>{{ item.item_name }}</td>
        <td style="text-align: center;">{{ item.uom or "PCS" }}</td>
        <td style="text-align: right; font-family: monospace;">
          {{ "%.2f"|format(item.system_qty|float) if item.system_qty is not none else "0.00" }}
        </td>
        <td style="text-align: right; font-family: monospace; font-weight: 700;">
          {% if item.physical_qty is not none and item.physical_qty != "" %}
            {{ "%.2f"|format(item.physical_qty|float) }}
          {% else %}
            <span style="color: #cbd5e1;">_______</span>
          {% endif %}
        </td>
        <td style="text-align: right; font-family: monospace; {% if (item.variance_qty|float) < 0 %}color: #dc2626; font-weight: 700;{% elif (item.variance_qty|float) > 0 %}color: #2563eb; font-weight: 700;{% endif %}">
          {% if item.physical_qty is not none and item.physical_qty != "" %}
            {{ "%+.2f"|format(item.variance_qty|float) if item.variance_qty != 0 else "0.00" }}
          {% else %}
            —
          {% endif %}
        </td>
        <td style="text-align: center; font-weight: 600;">
          {% if item.count_status == 'Matched' %}
            <span style="color: #16a34a;">Matched</span>
          {% elif item.count_status == 'Over' %}
            <span style="color: #2563eb;">Over</span>
          {% elif item.count_status == 'Short' %}
            <span style="color: #dc2626;">Short</span>
          {% elif item.count_status == 'New Item' %}
            <span style="color: #9333ea;">New</span>
          {% else %}
            <span style="color: #ea580c;">Pending</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <!-- Signatures -->
  <div style="margin-top: 24px; page-break-inside: avoid;">
    <div style="font-size: 11px; font-weight: 700; color: #0f172a; margin-bottom: 6px; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 3px; text-transform: uppercase;">
      Sign-Off & Audit Authorization
    </div>
    <table style="width: 100%; border-collapse: collapse; margin-top: 8px;">
      <tr>
        <td class="sign-box">
          <div style="color: #64748b; font-weight: 600; text-transform: uppercase;">Counted By (Stock Clerk)</div>
          <div style="margin-top: 32px; border-top: 1px solid #0f172a; text-align: center; font-size: 11px; font-weight: 700; padding-top: 3px;">
            {{ doc.counter_name or "Signature over Printed Name" }}
          </div>
          <div style="font-size: 9px; color: #94a3b8; text-align: center; margin-top: 2px;">Date: ______________</div>
        </td>
        <td style="width: 8px;"></td>
        <td class="sign-box">
          <div style="color: #64748b; font-weight: 600; text-transform: uppercase;">Verified By (Warehouse Head)</div>
          <div style="margin-top: 32px; border-top: 1px solid #0f172a; text-align: center; font-size: 11px; font-weight: 700; padding-top: 3px;">
            {{ doc.verifier_name or "Signature over Printed Name" }}
          </div>
          <div style="font-size: 9px; color: #94a3b8; text-align: center; margin-top: 2px;">Date: ______________</div>
        </td>
        <td style="width: 8px;"></td>
        <td class="sign-box">
          <div style="color: #64748b; font-weight: 600; text-transform: uppercase;">Approved By (Branch Manager)</div>
          <div style="margin-top: 32px; border-top: 1px solid #0f172a; text-align: center; font-size: 11px; font-weight: 700; padding-top: 3px;">
            {{ doc.approver_name or "Signature over Printed Name" }}
          </div>
          <div style="font-size: 9px; color: #94a3b8; text-align: center; margin-top: 2px;">Date: ______________</div>
        </td>
        <td style="width: 8px;"></td>
        <td class="sign-box">
          <div style="color: #64748b; font-weight: 600; text-transform: uppercase;">Audited By (Internal Audit)</div>
          <div style="margin-top: 32px; border-top: 1px solid #0f172a; text-align: center; font-size: 11px; font-weight: 700; padding-top: 3px;">
            {{ doc.auditor_name or "Signature over Printed Name" }}
          </div>
          <div style="font-size: 9px; color: #94a3b8; text-align: center; margin-top: 2px;">Date: ______________</div>
        </td>
      </tr>
    </table>
  </div>
</div>
"""

def deploy_print_format():
    print("\n[2] Deploying Print Format 'Inventory Count Sheet Standard'...")
    fmt_name = "Inventory Count Sheet Standard"
    quoted = urllib.parse.quote(fmt_name)
    existing = call(f"/api/resource/Print%20Format/{quoted}", "GET")
    
    payload = {
        "doc_type": "Inventory Count Sheet",
        "module": "Vehicle Management",
        "standard": "No",
        "custom_format": 1,
        "print_format_type": "Jinja",
        "html": PRINT_HTML,
        "disabled": 0,
        "default_print_language": "en",
    }
    
    if existing.get("data"):
        doc = existing["data"]
        doc.update(payload)
        res = call("/api/method/frappe.client.save", "POST", {"doc": json.dumps(doc)})
        print("  [OK] Existing Print Format updated.")
    else:
        payload["doctype"] = "Print Format"
        payload["name"] = fmt_name
        res = call("/api/resource/Print%20Format", "POST", payload)
        print("  [OK] New Print Format created.")

def verify():
    print("\n[3] Verifying Print Format on VPS...")
    fmt_name = "Inventory Count Sheet Standard"
    r = call(f"/api/resource/Print%20Format/{urllib.parse.quote(fmt_name)}", "GET")
    if r.get("data"):
        print(f"  [OK] Print Format '{fmt_name}' is active on VPS for doc_type: {r['data']['doc_type']}.")
    else:
        print(f"  [FAIL] Print Format not found: {r}")

if __name__ == "__main__":
    login()
    deploy_client_script()
    deploy_print_format()
    verify()
    print("\n[DONE] All updates successfully deployed and verified!")
