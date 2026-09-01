#!/usr/bin/env python3
"""Replace the frappe.ui.Dialog prompt (doesn't render in standalone POS SPA) with a
self-contained inline modal for opening/closing amount entry."""
import frappe, subprocess

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# ---- openCashier: inline modal ----
old_open = '''openCashier(){
    const self=this;
    const d=new frappe.ui.Dialog({title:"Open Cashier",fields:[
      {fieldtype:"Currency",fieldname:"opening_amount",label:"Opening Amount",reqd:1,default:0}
    ],primary_action_label:"Open Shift",primary_action(values){
      const amt=flt(values.opening_amount);
      if(amt<0){frappe.msgprint("Opening amount cannot be negative.");return;}
      d.hide();
      const ob=document.getElementById("vpos-shift-open"); if(ob){ob.disabled=true;ob.textContent="Opening…";}
      api("vehicle_management.vehicle_management.pos_api.open_cashier",{company:self.company||"",opening_amount:amt}).then(r=>{self.loadShift();if(ob){ob.disabled=false;ob.textContent="🔓 Open Cashier";}});
    }});
    d.show();
  },'''
new_open = '''openCashier(){
    const self=this;
    this._promptAmount("Open Cashier","Opening Amount","Open Shift",amt=>{
      const ob=document.getElementById("vpos-shift-open"); if(ob){ob.disabled=true;ob.textContent="Opening…";}
      api("vehicle_management.vehicle_management.pos_api.open_cashier",{company:self.company||"",opening_amount:amt}).then(r=>{self.loadShift();if(ob){ob.disabled=false;ob.textContent="🔓 Open Cashier";}});
    });
  },'''
assert old_open in html, "openCashier not found"
html = html.replace(old_open, new_open, 1)

# ---- closeCashier: inline modal ----
old_close = '''closeCashier(){
    const self=this;
    const d=new frappe.ui.Dialog({title:"Close Cashier",fields:[
      {fieldtype:"Currency",fieldname:"closing_amount",label:"Closing Amount (counted cash)",reqd:1,default:0}
    ],primary_action_label:"Close Shift",primary_action(values){
      const amt=flt(values.closing_amount);
      if(amt<0){frappe.msgprint("Closing amount cannot be negative.");return;}
      d.hide();
      const cb=document.getElementById("vpos-shift-close"); if(cb){cb.disabled=true;cb.textContent="Closing…";}
      api("vehicle_management.vehicle_management.pos_api.close_cashier",{closing_amount:amt}).then(r=>{self.loadShift();self.renderHistory();if(cb){cb.disabled=false;cb.textContent="🔒 Close Cashier";}});
    }});
    d.show();
  },'''
new_close = '''closeCashier(){
    const self=this;
    this._promptAmount("Close Cashier","Closing Amount (counted cash)","Close Shift",amt=>{
      const cb=document.getElementById("vpos-shift-close"); if(cb){cb.disabled=true;cb.textContent="Closing…";}
      api("vehicle_management.vehicle_management.pos_api.close_cashier",{closing_amount:amt}).then(r=>{self.loadShift();self.renderHistory();if(cb){cb.disabled=false;cb.textContent="🔒 Close Cashier";}});
    });
  },'''
assert old_close in html, "closeCashier not found"
html = html.replace(old_close, new_close, 1)

# ---- add _promptAmount helper (inline modal) right before openCashier ----
anchor = "openCashier(){"
helper = '''_promptAmount(title,label,btnLabel,cb){
    const self=this;
    const ov=document.createElement("div");
    ov.className="vpos-amt-ov";
    ov.innerHTML=`<div class="vpos-amt-card"><h3>${esc(title)}</h3><label>${esc(label)}</label><input type="number" step="0.01" min="0" id="vpos-amt-inp" inputmode="decimal" placeholder="0.00"><div class="vpos-amt-actions"><button class="vpos-li-qr" id="vpos-amt-cancel">Cancel</button><button class="vpos-li-qr" id="vpos-amt-ok" style="background:#0f766e;color:#fff">${esc(btnLabel)}</button></div></div>`;
    document.body.appendChild(ov);
    const inp=document.getElementById("vpos-amt-inp"); inp.focus();
    const close=()=>ov.remove();
    document.getElementById("vpos-amt-cancel").onclick=close;
    document.getElementById("vpos-amt-ok").onclick=()=>{const a=flt(inp.value); if(a<0){inp.style.borderColor="#b91c1c";return;} close(); cb(a);};
    ov.onclick=e=>{if(e.target===ov)close();};
  },
  openCashier(){'''
assert anchor in html, "anchor not found"
html = html.replace(anchor, helper, 1)

# ---- add CSS for the modal ----
css = '''.vpos-amt-ov{position:fixed;inset:0;background:rgba(4,32,26,.45);display:flex;align-items:center;justify-content:center;z-index:9999}.vpos-amt-card{background:#fff;border-radius:16px;padding:20px;width:min(92vw,360px);box-shadow:0 10px 40px rgba(0,0,0,.2)}.vpos-amt-card h3{margin:0 0 4px;color:#04201a}.vpos-amt-card label{display:block;margin:10px 0 4px;font-size:12px;color:#557}.vpos-amt-card input{width:100%;padding:10px 12px;font-size:18px;border:1px solid #bfe3dd;border-radius:10px;outline:none}.vpos-amt-actions{display:flex;gap:8px;margin-top:14px}.vpos-amt-actions button{flex:1;margin:0}'''
anchor2 = ".vpos-shift-bar{padding:"
assert anchor2 in html, "css anchor not found"
html = html.replace(anchor2, css + anchor2, 1)

print("orig -> new len", len(html))

open("/tmp/new_terminal3.html", "w", encoding="utf-8").write(html)
node = subprocess.run(
    ["node", "-e",
     "const fs=require('fs');const h=fs.readFileSync('/tmp/new_terminal3.html','utf8');"
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
