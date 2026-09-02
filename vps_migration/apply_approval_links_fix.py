import urllib.request, urllib.parse, json, http.cookiejar, re

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

# ==========================================
# 1. Update Server Script Executive Dashboard API
# ==========================================
print("1. Updating Server Script 'Executive Dashboard API'...")
r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script/Executive%20Dashboard%20API', headers=H))
doc = json.loads(r.read().decode())['data']
script = doc['script']

old_approvals_target = """def get_approvals():
    cards = []
    doctypes = [
        ("Purchase Order", "grand_total", "transaction_date"),
        ("Purchase Invoice", "grand_total", "posting_date"),
        ("Payment Entry", "paid_amount", "posting_date"),
        ("Journal Entry", "total_debit", "posting_date"),
        ("Expense Claim", "total_claimed_amount", "posting_date"),
        ("Stock Reconciliation", "0", "posting_date"),
    ]
    for dt, amt_col, date_col in doctypes:
        try:
            drafts = frappe.db.sql(f\"\"\"
                SELECT COUNT(name) as cnt, COALESCE(SUM({amt_col}), 0) as tot, COALESCE(MAX({amt_col}), 0) as high,
                       MIN({date_col}) as oldest
                FROM "tab{dt}"
                WHERE company = %s AND docstatus = 0
            \"\"\", (company,), as_dict=True)[0]
            
            oldest_days = 0
            cards.append({
                "doctype": dt,
                "count": cint(drafts['cnt']),
                "oldest_days": oldest_days,
                "avg_wait_days": 0,
                "highest": flt(drafts['high']),
                "total": flt(drafts['tot'])
            })
        except Exception:
            cards.append({
                "doctype": dt,
                "count": 0,
                "oldest_days": 0,
                "avg_wait_days": 0,
                "highest": 0.0,
                "total": 0.0
            })
    return cards"""

new_approvals_body = """def get_approvals():
    cards = []
    doctypes = [
        ("Purchase Order", "grand_total", "transaction_date"),
        ("Purchase Invoice", "grand_total", "posting_date"),
        ("Payment Entry", "paid_amount", "posting_date"),
        ("Journal Entry", "total_debit", "posting_date"),
        ("Expense Claim", "total_claimed_amount", "posting_date"),
        ("Stock Reconciliation", "0", "posting_date"),
    ]
    for dt, amt_col, date_col in doctypes:
        try:
            drafts = frappe.db.sql(f\"\"\"
                SELECT COUNT(name) as cnt, COALESCE(SUM({amt_col}), 0) as tot, COALESCE(MAX({amt_col}), 0) as high,
                       MIN({date_col}) as oldest
                FROM "tab{dt}"
                WHERE company = %s AND docstatus = 0
            \"\"\", (company,), as_dict=True)[0]
            
            oldest_days = 0
            if drafts.get('oldest'):
                try:
                    d_val = frappe.utils.getdate(drafts['oldest'])
                    oldest_days = max(0, (frappe.utils.getdate(frappe.utils.nowdate()) - d_val).days)
                except Exception:
                    oldest_days = 0

            # Top pending documents
            items = []
            try:
                party_col = "supplier" if dt in ["Purchase Order", "Purchase Invoice"] else ("party" if dt == "Payment Entry" else "owner")
                has_party = frappe.db.has_column(dt, party_col)
                party_field = party_col if has_party else "owner"
                raw_items = frappe.db.sql(f\"\"\"
                    SELECT name, {amt_col} as amount, {date_col} as date, {party_field} as party
                    FROM "tab{dt}"
                    WHERE company = %s AND docstatus = 0
                    ORDER BY {date_col} DESC, creation DESC
                    LIMIT 5
                \"\"\", (company,), as_dict=True)
                for ri in raw_items:
                    items.append({
                        "name": ri["name"],
                        "amount": float(ri.get("amount") or 0.0),
                        "date": str(ri.get("date") or "")[:10],
                        "party": str(ri.get("party") or "")
                    })
            except Exception:
                items = []

            cards.append({
                "doctype": dt,
                "count": cint(drafts['cnt']),
                "oldest_days": oldest_days,
                "avg_wait_days": 0,
                "highest": flt(drafts['high']),
                "total": flt(drafts['tot']),
                "items": items
            })
        except Exception:
            cards.append({
                "doctype": dt,
                "count": 0,
                "oldest_days": 0,
                "avg_wait_days": 0,
                "highest": 0.0,
                "total": 0.0,
                "items": []
            })
    return cards"""

if old_approvals_target in script:
    script = script.replace(old_approvals_target, new_approvals_body)
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script/Executive%20Dashboard%20API',
        data=urllib.parse.urlencode({'data': json.dumps({'script': script})}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    op.open(req)
    print("Updated Server Script Executive Dashboard API successfully!")
else:
    print("Warning: old_approvals_target not found in Executive Dashboard API. Trying regex...")
    pattern = r'def get_approvals\(\):.*?(?=def get_operations)'
    script = re.sub(pattern, new_approvals_body + "\n\n", script, flags=re.DOTALL)
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script/Executive%20Dashboard%20API',
        data=urllib.parse.urlencode({'data': json.dumps({'script': script})}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    op.open(req)
    print("Updated Server Script Executive Dashboard API via regex successfully!")

# ==========================================
# 2. Update all 14 Web Pages
# ==========================================
print("\n2. Updating all 14 Web Pages...")
pages = [
    'executive', 'executive-dashboard', 'executive-automan-car-care-center',
    'executive-san-fernando-warehouse', 'executive-the-wheelhub', 'executive-ultra-mrf',
    'executive-ultra-mrf-dau-annex', 'executive-ultra-mrf-dau-main',
    'executive-ultra-mrf-mexico-warehouse', 'executive-ultra-mrf-san-fernando',
    'executive-ultra-mrf-telebastagan', 'executive-ultra-mrf-telebastagan-2',
    'executive-ultra-mrf-warehouse-dau', 'executive-wheel-core'
]

old_render_approvals_pattern = r'function renderApprovals\(cards\)\{.*?function openList\(dt\)\{[^\}]*\}\s*\}'

new_render_approvals_code = """function renderApprovals(cards){
  const el=document.getElementById('approvalCards');
  if(!cards || !cards.length){ el.innerHTML='<div class="panel p-pad empty">Nothing pending.</div>'; return; }
  const totalPending = cards.reduce((s,c)=>s+(Number(c.count)||0),0);
  setBadge('badgeApprovals', totalPending);
  el.innerHTML = cards.map(c=>{
    const zero = (Number(c.count)||0)===0;
    const oldCls = c.oldest_days>14?'crit':c.oldest_days>7?'warn':'';
    const ic = APP_ICONS[c.doctype] || '<circle cx="12" cy="12" r="9"/>';
    let txnsHtml = '';
    if(c.items && c.items.length){
      txnsHtml = '<div class="app-txns" style="margin-top:12px;padding-top:10px;border-top:1px dashed var(--line,#2a2a2a);">' +
        '<div style="font-size:10px;font-weight:700;color:var(--muted,#888);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;">Pending Transactions:</div>' +
        c.items.map(it => {
          const sub = it.party ? (' · ' + it.party) : '';
          return '<div class="app-txn-row" onclick="openDoc(\\'' + c.doctype + '\\',\\'' + it.name + '\\')" title="View ' + it.name + ' in ERPNext Desk" style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;margin-bottom:4px;border-radius:6px;background:rgba(255,255,255,0.04);cursor:pointer;font-size:11.5px;transition:all .15s;" onmouseover="this.style.background=\\'rgba(255,255,255,0.1)\\'" onmouseout="this.style.background=\\'rgba(255,255,255,0.04)\\'">' +
            '<div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:65%;">' +
              '<span style="font-weight:700;color:var(--accent,#38bdf8);text-decoration:underline;">' + it.name + '</span>' +
              '<span style="font-size:10.5px;color:var(--muted,#888);margin-left:4px;">' + sub + '</span>' +
            '</div>' +
            '<span style="font-weight:700;color:var(--text,#fff);">' + pesoC(it.amount) + '</span>' +
          '</div>';
        }).join('') +
      '</div>';
    }
    return '<div class="appcard'+(zero?' zero':'')+'"><div class="ah">'+
      '<div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9">'+ic+'</svg></div>'+
      '<div class="t">'+c.doctype+'<span>'+pesoC(c.total)+' total value</span></div></div>'+
      '<div class="cnt">'+int(c.count)+'<small>pending</small></div>'+
      '<div class="meta">'+
        '<div class="m"><div class="k">Oldest waiting</div><div class="v '+oldCls+'">'+(c.oldest_days||0)+'d</div></div>'+
        '<div class="m"><div class="k">Avg wait</div><div class="v">'+(c.avg_wait_days||0)+'d</div></div>'+
        '<div class="m"><div class="k">Highest value</div><div class="v">'+pesoC(c.highest)+'</div></div>'+
        '<div class="m"><div class="k">Total value</div><div class="v">'+pesoC(c.total)+'</div></div>'+
      '</div>'+
      txnsHtml+
      '<div class="va" data-dt="'+c.doctype+'" onclick="openList(this.dataset.dt)">View all '+c.doctype+'s in Desk &rarr;</div></div>';
  }).join('');
}
function openDoc(dt, name){
  const slug = (dt||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  const p = '/desk/' + encodeURIComponent(slug) + '/' + encodeURIComponent(name);
  try{ window.open(p,'_blank'); }catch(e){}
}
function openList(dt){
  const slug = (dt||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  const co = (typeof CURRENT_COMPANY !== 'undefined' && CURRENT_COMPANY) ? CURRENT_COMPANY : (typeof COMPANY !== 'undefined' ? COMPANY : '');
  let p = '/desk/' + encodeURIComponent(slug);
  if(co){
    p += '?company=' + encodeURIComponent(co);
  }
  try{ window.open(p,'_blank'); }catch(e){}
}"""

updated_count = 0
for p in pages:
    r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Web%20Page/{p}', headers=H))
    doc = json.loads(r.read().decode())['data']
    html = doc.get('main_section_html') or ''
    
    if re.search(old_render_approvals_pattern, html, flags=re.DOTALL):
        html_new = re.sub(old_render_approvals_pattern, new_render_approvals_code, html, flags=re.DOTALL)
        req = urllib.request.Request(
            f'http://38.247.138.224:10017/api/resource/Web%20Page/{p}',
            data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html_new})}).encode(),
            headers=H
        )
        req.get_method = lambda: 'PUT'
        op.open(req)
        updated_count += 1
        print(f"  [OK] Updated Web Page: {p}")
    else:
        print(f"  [WARN] Pattern not matched in Web Page: {p}")

print(f"\nCompleted updating {updated_count}/{len(pages)} Web Pages!")
