#!/usr/bin/env python3
"""Frontend patch for the served POS SPA (Web Page vehicle-pos-terminal):
- renderHistory: real-time fetch + timestamp + per-tx "Print Receipt"
- renderProfile: revamp to show ONLY the Cashier ID card; shift open/close + full details collapsed
- add printReceipt / openCashier / closeCashier / loadShift methods + CSS
"""
import frappe, subprocess, os

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
orig = len(html)

# ---------- 1. renderHistory -> real-time + timestamp + print receipt ----------
i = html.find("renderHistory(){")
j = html.find("renderProfile(main){")
assert i != -1 and j != -1 and j > i, f"markers {i} {j}"

NEW_HISTORY = """renderHistory(){
    const view=document.getElementById("vpos-view-history");
    if(!view)return;
    view.innerHTML='<div class="vpos-empty">Loading transactions…</div>';
    api("vehicle_management.vehicle_management.pos_api.get_history").then(h=>{
      this.history=h||[];
      if(!this.history.length){view.innerHTML='<div class="vpos-empty">No transactions yet.</div>';return;}
      view.innerHTML=this.history.map(t=>`<div class="vpos-hist"><div class="vpos-hist-top"><b>${t.name}</b><span>${t.timestamp||t.posting_date||""}</span></div><div class="vpos-hist-sub">${t.customer_name||""} ${t.vehicle?"· "+t.vehicle:""}</div><div class="vpos-hist-foot"><span>${peso(t.total_amount)}</span><span>${t.payment_method||""}</span></div><div class="vpos-hist-actions"><button class="vpos-hist-receipt" data-name="${t.name}">🖨 Print Receipt</button></div></div>`).join("");
      view.querySelectorAll(".vpos-hist-receipt").forEach(b=>b.onclick=()=>this.printReceipt(b.getAttribute("data-name")));
    });
  },
  printReceipt(name){
    api("vehicle_management.vehicle_management.pos_api.get_receipt",{name:name}).then(r=>{
      if(!r)return;
      const items=(r.items||[]).map(x=>`<tr><td>${esc(x.item_name||x.item_code)}</td><td class="r">${flt(x.qty)}</td><td class="r">${peso(x.rate)}</td><td class="r">${peso(x.amount)}</td></tr>`).join("");
      const w=window.open("","_blank","width=400,height=640");
      if(!w){alert("Pop-up blocked. Allow pop-ups to print receipts.");return;}
      w.document.write(`<!DOCTYPE html><html><head><title>Receipt ${esc(r.name)}</title><style>body{font-family:'Courier New',monospace;font-size:13px;max-width:340px;margin:0 auto;padding:16px}.c{text-align:center}.r{text-align:right}h1{font-size:18px;margin:4px 0}.ln{border-top:1px dashed #000;margin:8px 0}table{width:100%;border-collapse:collapse}th,td{padding:4px 2px;border-bottom:1px dotted #ccc;font-size:12px;text-align:left}</style></head><body><div class="c"><h1>ULTRA MRF</h1><div>Vehicle POS Receipt</div></div><div class="ln"></div><div><b>${esc(r.name)}</b></div><div>${esc(r.timestamp||"")}</div><div>Cashier: ${esc(r.cashier||"")}</div><div>Customer: ${esc(r.customer_name||r.customer||"")}</div><div>Vehicle: ${esc(r.vehicle||"")} ${esc(r.plate_no||"")}</div><div>Payment: ${esc(r.payment_method||"")}</div><div class="ln"></div><table><tr><th>Item</th><th class="r">Qty</th><th class="r">Rate</th><th class="r">Amount</th></tr>${items}</table><div class="ln"></div><div style="display:flex;justify-content:space-between"><span>Total</span><b>${peso(r.total_amount)}</b></div><div style="display:flex;justify-content:space-between"><span>Paid</span><b>${peso(r.paid_amount)}</b></div><div style="display:flex;justify-content:space-between"><span>Change</span><b>${peso(r.balance_amount)}</b></div><div class="ln"></div><div class="c">Thank you!</div><div class="c" style="margin-top:12px"><button onclick="window.print()" style="padding:8px 20px;font-size:14px">Print</button></div></body></html>`);
      w.document.close();
    });
  },
  loadShift(){
    api("vehicle_management.vehicle_management.pos_api.get_cashier_shift").then(s=>{
      this.shift=s||{open:false};
      const el=document.getElementById("vpos-shift");
      if(el)el.innerHTML=s&&s.open?`<span class="vpos-shift-open">● Open shift — ${esc(s.name||"")}</span>`:`<span class="vpos-shift-closed">○ No open shift</span>`;
      const ob=document.getElementById("vpos-shift-open"); if(ob)ob.style.display=(s&&s.open)?"none":"inline-block";
      const cb=document.getElementById("vpos-shift-close"); if(cb)cb.style.display=(s&&s.open)?"inline-block":"none";
    });
  },
  openCashier(){
    const ob=document.getElementById("vpos-shift-open"); if(ob){ob.disabled=true;ob.textContent="Opening…";}
    api("vehicle_management.vehicle_management.pos_api.open_cashier",{company:this.company||""}).then(r=>{this.loadShift();if(ob){ob.disabled=false;ob.textContent="🔓 Open Cashier";}});
  },
  closeCashier(){
    const cb=document.getElementById("vpos-shift-close"); if(cb){cb.disabled=true;cb.textContent="Closing…";}
    api("vehicle_management.vehicle_management.pos_api.close_cashier").then(r=>{this.loadShift();this.renderHistory();if(cb){cb.disabled=false;cb.textContent="🔒 Close Cashier";}});
  },
"""

html = html[:i] + NEW_HISTORY + html[j:]

# ---------- 2. renderProfile -> only ID card + shift + collapsed details ----------
k = html.find("renderProfile(main){")
l = html.find("downloadCard(){")
assert k != -1 and l != -1 and l > k, f"profile markers {k} {l}"

NEW_PROFILE = """renderProfile(main){
    const view=document.getElementById("vpos-view-profile");
    if(!view)return;
    const qrData=(this.email||this.cashier||"")+"|"+(window.__vposPwd||"");
    let svg="";
    try{
      const qr=window.qrcode(0,"M");qr.addData(qrData);qr.make();
      svg=qr.createSvgTag({cellSize:6,margin:8,scalable:true});
    }catch(e){svg="<div style='color:#b91c1c'>QR unavailable</div>";}
    view.innerHTML=`<div class="vpos-prof">
      <div class="vpos-shift-bar" id="vpos-shift">Loading shift…</div>
      <div class="vpos-shift-actions">
        <button class="vpos-li-qr" id="vpos-shift-open" style="flex:1;margin:0">🔓 Open Cashier</button>
        <button class="vpos-li-qr" id="vpos-shift-close" style="flex:1;margin:0;display:none">🔒 Close Cashier</button>
      </div>
      <div class="vpos-idcard" id="vpos-idcard">
        <div class="vpos-id-head">
          <div class="vpos-id-logo"><img src="/files/ultra_mrf_logo.png" alt="company logo"></div>
          <div class="vpos-id-co">${this.company||""}</div>
          <div class="vpos-id-title">CASHIER ID</div>
        </div>
        <div class="vpos-id-body">
          <div class="vpos-id-info">
            <div class="vpos-id-name">${this.empName||this.employee||"—"}</div>
            <div class="vpos-id-line"><span>Emp #</span><b>${this.empNo||"—"}</b></div>
            <div class="vpos-id-line"><span>Designation</span><b>${this.designation||"—"}</b></div>
            <div class="vpos-id-line"><span>Branch</span><b>${this.branch||"—"}</b></div>
            <div class="vpos-id-line"><span>Email</span><b>${this.email||this.cashier||""}</b></div>
          </div>
          <div class="vpos-id-qr">${svg}</div>
        </div>
      </div>
      <div style="display:flex;gap:8px;margin-top:12px">
        <button class="vpos-prof-print" onclick="window.print()" style="flex:1">🖨 Print ID</button>
        <button class="vpos-li-qr" id="vpos-prof-dl" style="flex:1;margin:0">⬇ Download ID</button>
      </div>
      <details class="vpos-details">
        <summary>Full Cashier Details</summary>
        <div class="vpos-prof-row"><span>Employee #</span><b>${this.empNo||"—"}</b></div>
        <div class="vpos-prof-row"><span>Employee</span><b>${this.empName||this.employee||"—"}</b></div>
        <div class="vpos-prof-row"><span>Designation</span><b>${this.designation||"—"}</b></div>
        <div class="vpos-prof-row"><span>Company</span><b>${this.company||""}</b></div>
        <div class="vpos-prof-row"><span>Branch</span><b>${this.branch||"—"}</b></div>
        <div class="vpos-prof-row"><span>Department</span><b>${this.department||"—"}</b></div>
        <div class="vpos-prof-row"><span>Reports To</span><b>${this.reportsTo||"—"}</b></div>
        <div class="vpos-prof-row"><span>Email</span><b>${this.email||this.cashier||""}</b></div>
        <div class="vpos-prof-code" id="vpos-prof-code">${qrData}</div>
        <button class="vpos-li-qr" id="vpos-prof-copy" style="margin-top:8px">📋 Copy badge code</button>
      </details>
    </div>`;
    const dl=document.getElementById("vpos-prof-dl"); if(dl)dl.onclick=()=>POS.downloadCard();
    const cp=document.getElementById("vpos-prof-copy"); if(cp)cp.onclick=()=>{if(navigator.clipboard)navigator.clipboard.writeText(qrData);cp.textContent="Copied!";setTimeout(()=>cp.textContent="📋 Copy badge code",1200);};
    const ob=document.getElementById("vpos-shift-open"); if(ob)ob.onclick=()=>this.openCashier();
    const cb=document.getElementById("vpos-shift-close"); if(cb)cb.onclick=()=>this.closeCashier();
    this.loadShift();
  },
"""

html = html[:k] + NEW_PROFILE + html[l:]

# ---------- 3. CSS ----------
CSS = """.vpos-shift-bar{padding:10px 14px;border-radius:12px;font-weight:700;font-size:13px;margin-bottom:8px}.vpos-shift-open{color:#0fa76d;background:#dcfce7;padding:8px 12px;border-radius:10px;display:inline-block}.vpos-shift-closed{color:#b45309;background:#fef3c7;padding:8px 12px;border-radius:10px;display:inline-block}.vpos-shift-actions{display:flex;gap:8px;margin-bottom:12px}.vpos-details{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-top:12px}.vpos-details summary{font-weight:700;cursor:pointer;color:#0f766e}.vpos-hist-actions{margin-top:8px}.vpos-hist-receipt{border:1px solid #bfe3dd;background:#eef7f3;color:#0f766e;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;font-size:12px}"""
anchor = "@media print{"
m = html.find(anchor)
assert m != -1, "css anchor not found"
html = html[:m] + CSS + html[m:]

print("orig", orig, "-> new", len(html))

# ---------- validate JS before committing ----------
open("/tmp/new_terminal.html", "w", encoding="utf-8").write(html)
node = subprocess.run(
    ["node", "-e",
     "const fs=require('fs');const h=fs.readFileSync('/tmp/new_terminal.html','utf8');"
     "const s=[...h.matchAll(/<script[^>]*>([\\s\\S]*?)<\\/script>/g)].map(m=>m[1]);"
     "let bad=0;s.forEach((b,i)=>{try{new Function(b)}catch(e){console.log('block',i,'ERR',e.message.slice(0,120));bad++}});"
     "console.log('blocks',s.length,'bad',bad);process.exit(bad?1:0)"],
    capture_output=True, text=True,
)
print("NODE:", node.stdout.strip(), node.stderr.strip())
if node.returncode != 0:
    print("!! JS INVALID — NOT committing")
    raise SystemExit(2)

frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
frappe.db.commit()
print("COMMITTED. readback len", len(frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")))
