import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

pages = [
    'executive', 'executive-dashboard', 'executive-automan-car-care-center',
    'executive-san-fernando-warehouse', 'executive-the-wheelhub', 'executive-ultra-mrf',
    'executive-ultra-mrf-dau-annex', 'executive-ultra-mrf-dau-main',
    'executive-ultra-mrf-mexico-warehouse', 'executive-ultra-mrf-san-fernando',
    'executive-ultra-mrf-telebastagan', 'executive-ultra-mrf-telebastagan-2',
    'executive-ultra-mrf-warehouse-dau', 'executive-wheel-core'
]

old_block = """function renderApprovals(cards){
  const el=document.getElementById('approvalCards');
  if(!cards || !cards.length){ el.innerHTML='<div class="panel p-pad empty">Nothing pending.</div>'; return; }
  const totalPending = cards.reduce((s,c)=>s+(Number(c.count)||0),0);
  setBadge('badgeApprovals', totalPending);
  el.innerHTML = cards.map(c=>{
    const zero = (Number(c.count)||0)===0;
    const oldCls = c.oldest_days>14?'crit':c.oldest_days>7?'warn':'';
    const ic = APP_ICONS[c.doctype] || '<circle cx="12" cy="12" r="9"/>';
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
      '<div class="va" data-dt="'+c.doctype+'" onclick="openList(this.dataset.dt)">View all '+c.doctype+'s</div></div>';
  }).join('');
}
function openList(dt){ const p='/desk#'+encodeURIComponent((dt||'').toLowerCase().replace(/\\s+/g,'-'));
  try{ window.open(p,'_blank'); }catch(e){} }"""

new_block = """function renderApprovals(cards){
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
          return '<div class="app-txn-row" onclick="openDoc(\\'' + c.doctype + '\\',\\'' + it.name + '\\')" title="View transaction ' + it.name + ' in ERPNext Desk" style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;margin-bottom:4px;border-radius:6px;background:rgba(255,255,255,0.04);cursor:pointer;font-size:11.5px;transition:all .15s;" onmouseover="this.style.background=\\'rgba(255,255,255,0.1)\\'" onmouseout="this.style.background=\\'rgba(255,255,255,0.04)\\'">' +
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

updated = 0
for p in pages:
    r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/Web%20Page/{p}', headers=H))
    doc = json.loads(r.read().decode())['data']
    html = doc.get('main_section_html') or ''
    
    # Normalize \r\n to \n for consistent matching
    html_norm = html.replace('\r\n', '\n')
    old_norm = old_block.replace('\r\n', '\n')
    
    if old_norm in html_norm:
        html_new = html_norm.replace(old_norm, new_block)
        req = urllib.request.Request(
            f'http://38.247.138.224:10017/api/resource/Web%20Page/{p}',
            data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html_new})}).encode(),
            headers=H
        )
        req.get_method = lambda: 'PUT'
        op.open(req)
        updated += 1
        print(f"  [OK] Updated Web Page: {p}")
    else:
        # Fallback: substring replacement from function renderApprovals to end of openList
        start_idx = html_norm.find('function renderApprovals(')
        end_str = "try{ window.open(p,'_blank'); }catch(e){} }"
        end_idx = html_norm.find(end_str, start_idx)
        if start_idx != -1 and end_idx != -1:
            full_end = end_idx + len(end_str)
            html_new = html_norm[:start_idx] + new_block + html_norm[full_end:]
            req = urllib.request.Request(
                f'http://38.247.138.224:10017/api/resource/Web%20Page/{p}',
                data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html_new})}).encode(),
                headers=H
            )
            req.get_method = lambda: 'PUT'
            op.open(req)
            updated += 1
            print(f"  [OK-Fallback] Updated Web Page: {p}")
        else:
            print(f"  [FAIL] Could not locate renderApprovals in {p}")

print(f"\nSuccessfully updated {updated}/{len(pages)} Web Pages!")
