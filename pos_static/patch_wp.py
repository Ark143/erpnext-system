import frappe, re
frappe.init("site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
d = frappe.get_doc("Web Page", {"route": "pos-terminal"})
html = d.main_section_html or ""
orig = html

css_edits = [
    ('vpos-app{display:grid;grid-template-columns:68px 1fr 380px;grid-template-areas:"rail main ticket";height:100vh;height:100dvh;overflow:hidden}',
     'vpos-app{display:grid;grid-template-columns:68px 1fr 1fr;grid-template-areas:"rail main ticket";height:100vh;height:100dvh;overflow:hidden}'),
    ('.vpos-ticket{grid-area:ticket;background:var(--card);border-left:1px solid var(--line);display:flex;flex-direction:column;padding:16px;gap:12px;height:100%;overflow-y:auto;z-index:10;box-shadow:-4px 0 16px rgba(0,0,0,.02)}',
     '.vpos-ticket{grid-area:ticket;background:var(--card);border-left:1px solid var(--line);display:flex;flex-direction:column;min-width:0;padding:16px;gap:12px;height:100%;overflow-y:auto;z-index:10;box-shadow:-4px 0 16px rgba(0,0,0,.02)}'),
    ('.vpos-card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:14px;display:flex;flex-direction:column;gap:6px;cursor:pointer;transition:transform .15s,border-color .15s,box-shadow .15s;position:relative;height:100%;box-shadow:0 2px 6px rgba(0,0,0,.02)}',
     '.vpos-card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:14px;display:flex;flex-direction:column;gap:6px;cursor:pointer;transition:transform .15s,border-color .15s,box-shadow .15s;position:relative;min-width:0;height:100%;box-shadow:0 2px 6px rgba(0,0,0,.02)}'),
]
css_edits.append(('@media (min-width:769px) and (max-width:1024px){.vpos-app{grid-template-columns:60px 1fr 340px}',
                   '@media (min-width:769px) and (max-width:1024px){.vpos-app{grid-template-columns:60px 1fr 1fr}'))
css_edits.append(('.vpos-ticket{width:340px;padding:12px}',
                   '.vpos-ticket{width:auto;padding:12px}'))

for old, new in css_edits:
    if old in html:
        html = html.replace(old, new)
        print("CSS patched:", old[:45])
    else:
        print("CSS NOT FOUND:", old[:45])

js_anchor = 'this.cat(box,"","All Categories",true);(meta.categories||[]).forEach(g=>this.cat(box,g,g,false))}'
js_block = (js_anchor +
  'const compSel=document.querySelector(".vpos-company");'
  'if(meta&&compSel){const companies=meta.companies||[];'
  'compSel.innerHTML="";'
  'companies.forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=c;compSel.appendChild(o)});'
  'if(!this.company&&companies.length)this.company=companies[0];'
  'compSel.value=this.company||""}this.totals();')
if js_anchor in html:
    html = html.replace(js_anchor, js_block)
    print("JS patched: company select population")
else:
    print("JS ANCHOR NOT FOUND")

build_old = 'const comp=r.querySelector(".vpos-company");comp.value=this.company||"";'
build_new = 'const comp=r.querySelector(".vpos-company");comp.disabled=false;comp.value=this.company||"";comp.onchange=()=>{this.company=comp.value||null;this.totals()};'
if build_old in html:
    html = html.replace(build_old, build_new)
    print("JS patched: company select enable+onchange")
else:
    print("BUILD ANCHOR NOT FOUND")

d.main_section_html = html
d.save()
frappe.clear_cache("site1.local")
print("SAVED. orig len", len(orig), "new len", len(html))
print("has 50/50:", "68px 1fr 1fr" in html)
print("has old layout:", "74px 1fr 400px" in html)
print("has company population:", "companies.forEach" in html)
