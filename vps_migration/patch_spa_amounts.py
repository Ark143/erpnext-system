#!/usr/bin/env python3
"""Frontend: prompt cashier for opening/closing amount via dialog; show opening amount."""
import frappe, subprocess

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# ---- loadShift: show opening amount in the shift bar ----
old_load = '''loadShift(){
    api("vehicle_management.vehicle_management.pos_api.get_cashier_shift").then(s=>{
      this.shift=s||{open:false};
      const el=document.getElementById("vpos-shift");
      if(el)el.innerHTML=s&&s.open?`<span class="vpos-shift-open">● Open shift — ${esc(s.name||"")}</span>`:`<span class="vpos-shift-closed">○ No open shift</span>`;
      const ob=document.getElementById("vpos-shift-open"); if(ob)ob.style.display=(s&&s.open)?"none":"inline-block";
      const cb=document.getElementById("vpos-shift-close"); if(cb)cb.style.display=(s&&s.open)?"inline-block":"none";
    });
  },'''
new_load = '''loadShift(){
    api("vehicle_management.vehicle_management.pos_api.get_cashier_shift").then(s=>{
      this.shift=s||{open:false};
      const el=document.getElementById("vpos-shift");
      if(el)el.innerHTML=s&&s.open?`<span class="vpos-shift-open">● Open shift — ${esc(s.name||"")} · Opening ${peso(s.opening_amount||0)}</span>`:`<span class="vpos-shift-closed">○ No open shift</span>`;
      const ob=document.getElementById("vpos-shift-open"); if(ob)ob.style.display=(s&&s.open)?"none":"inline-block";
      const cb=document.getElementById("vpos-shift-close"); if(cb)cb.style.display=(s&&s.open)?"inline-block":"none";
    });
  },'''
assert old_load in html, "loadShift not found"
html = html.replace(old_load, new_load, 1)

# ---- openCashier: prompt for opening amount ----
old_open = '''openCashier(){
    const ob=document.getElementById("vpos-shift-open"); if(ob){ob.disabled=true;ob.textContent="Opening…";}
    api("vehicle_management.vehicle_management.pos_api.open_cashier",{company:this.company||""}).then(r=>{this.loadShift();if(ob){ob.disabled=false;ob.textContent="🔓 Open Cashier";}});
  },'''
new_open = '''openCashier(){
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
assert old_open in html, "openCashier not found"
html = html.replace(old_open, new_open, 1)

# ---- closeCashier: prompt for closing amount ----
old_close = '''closeCashier(){
    const cb=document.getElementById("vpos-shift-close"); if(cb){cb.disabled=true;cb.textContent="Closing…";}
    api("vehicle_management.vehicle_management.pos_api.close_cashier").then(r=>{this.loadShift();this.renderHistory();if(cb){cb.disabled=false;cb.textContent="🔒 Close Cashier";}});
  },'''
new_close = '''closeCashier(){
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
assert old_close in html, "closeCashier not found"
html = html.replace(old_close, new_close, 1)

print("orig", 384019, "-> new", len(html))

# validate JS before commit
open("/tmp/new_terminal2.html", "w", encoding="utf-8").write(html)
node = subprocess.run(
    ["node", "-e",
     "const fs=require('fs');const h=fs.readFileSync('/tmp/new_terminal2.html','utf8');"
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
