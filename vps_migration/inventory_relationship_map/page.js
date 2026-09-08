(() => {
  'use strict';
  const app = document.getElementById('inventory-map-app');
  if (!app || app.dataset.ready) return;
  app.dataset.ready = '1';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const num = value => Number(value || 0).toLocaleString(undefined, {maximumFractionDigits:3});
  const url = (dt, name) => '/desk/' + dt.toLowerCase().replace(/ /g, '-') + '/' + encodeURIComponent(name);
  const link = (dt, name, label) => `<a href="${esc(url(dt,name))}" target="_blank" rel="noopener">${esc(label || name)}</a>`;
  let requestId = 0, data = null, zoom = 1, lookupId = 0, graphLimit = 36;
  const initial = new URLSearchParams(location.search);
  const source = {};
  if (initial.get('doctype') && initial.get('docname')) {
    source.doctype = initial.get('doctype'); source.docname = initial.get('docname');
  }
  async function api(path, params = {}) {
    const response = await fetch(path + '?' + new URLSearchParams(params), {credentials:'same-origin',headers:{Accept:'application/json'}});
    const body = await response.json().catch(() => ({}));
    if (!response.ok || body.exc || body.exception) {
      let message = 'Unable to load inventory data. Check your access and try again.';
      try { message = JSON.parse(JSON.parse(body._server_messages)[0]).message.replace(/<[^>]*>/g,''); } catch (_) {}
      if (response.status === 403 || response.status === 401) message = 'Please sign in with an account that can read stock records.';
      throw new Error(message);
    }
    return body.message ?? body.data;
  }
  const list = (dt, fields, filters, extra = {}) => api('/api/resource/' + encodeURIComponent(dt), {
    fields:JSON.stringify(fields), filters:JSON.stringify(filters), limit_page_length:100, ...extra
  });
  function notice(message, error = false) { $('im-status').innerHTML = message ? `<div class="im-notice ${error?'im-error':''}">${esc(message)}</div>` : ''; }
  function table(headers, rows) {
    if (!rows.length) return '<div class="im-empty">No records match these filters.</div>';
    return `<div class="im-table-wrap"><table class="im-table"><thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(cells=>`<tr>${cells.map((c,i)=>`<td${headers[i].includes('qty') || headers[i].includes('balance') ? ' class="im-num"':''}>${c}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function render() {
    if (!data.item) { $('im-results').innerHTML = '<div class="im-empty">'+esc(data.empty_reason || 'No inventory movements found. Select an item to explore its relationships.')+'</div>'; return; }
    const rows = data.movements, balances = data.balances, uom = esc(data.item.stock_uom);
    const locationCell = row => {
      if (!row.bin_location) return '<span class="im-muted">Not recorded</span>';
      const location = (data.locations || []).find(l=>l.name===row.bin_location);
      return (location ? link('Bin Location',location.name) : esc(row.bin_location)) +
        (location ? '<br><small>'+esc([location.zone,location.rack,location.shelf,location.bin_no].filter(Boolean).join(' / '))+'</small>' : '');
    };
    const incoming = rows.reduce((n,r)=>n+Math.max(0,Number(r.actual_qty)),0);
    const outgoing = rows.reduce((n,r)=>n+Math.abs(Math.min(0,Number(r.actual_qty))),0);
    const current = balances.reduce((n,r)=>n+Number(r.actual_qty),0);
    const stats = [[num(current),'Current stock',`${balances.length} warehouse balances · ${uom}`],
      [num(incoming),'Inward qty',`Displayed movements · ${uom}`],[num(outgoing),'Outward qty',`Displayed movements · ${uom}`],
      [rows.length,'Ledger entries',data.truncated?'Latest entries only · limit '+data.limit:'All entries matching the filters']];
    $('im-results').innerHTML = `<div class="im-item-title"><div><h2>${esc(data.item.item_name)}</h2><div class="im-muted">${link('Item',data.item.name)} · Stock UOM: ${uom}${data.company?' · '+esc(data.company):''}</div></div><span class="im-badge">${data.item.is_stock_item?'Stock item':'Non-stock item'}</span></div>
      <div class="im-summary">${stats.map(s=>`<div class="im-stat"><small>${s[1]}</small><strong>${s[0]}</strong><span>${s[2]}</span></div>`).join('')}</div>
      <div class="im-muted">Current stock is the warehouse-level Bin balance; date and bin-location filters affect movements only. Location cards show the net of displayed movements, not current bin stock. Transfers contribute to both inward and outward quantities.</div>
      <div class="im-tabs" role="tablist" aria-label="Inventory views">${['Relationship map','Movement ledger','Warehouse balances','Document references'].map((n,i)=>`<button type="button" class="im-button" role="tab" id="im-tab-${i}" aria-controls="im-panel-${i}" aria-selected="${i===0}" data-panel="${i}">${n}</button>`).join('')}</div>
      <section class="im-panel" role="tabpanel" aria-labelledby="im-tab-0" id="im-panel-0"><div class="im-graph-toolbar"><p id="im-graph-caption"></p><div><button class="im-button" type="button" id="im-minus" aria-label="Zoom out">−</button> <button class="im-button" type="button" id="im-reset">100%</button> <button class="im-button" type="button" id="im-plus" aria-label="Zoom in">+</button></div></div><div class="im-graph-viewport"><div id="im-graph" class="im-graph"></div></div><div class="im-legend"><span><i style="background:#077c78"></i>Inward movement</span><span><i style="background:#bd7348"></i>Outward / zero-qty adjustment</span><span><i style="background:#536fc1"></i>Warehouse</span></div></section>
      <section class="im-panel" role="tabpanel" aria-labelledby="im-tab-1" id="im-panel-1" hidden>${table(['Posted','Source document','Company / warehouse','Bin location','Movement qty','Warehouse balance after','Batch / serial'], rows.map(r=>[
        esc(r.posting_date)+'<br><small>'+esc(r.posting_time)+'</small>',
        '<small>'+esc(r.voucher_type)+'</small><br>'+(r.can_open_voucher?link(r.voucher_type,r.voucher_no):'Source document restricted'),
        esc(r.company)+'<br>'+link('Warehouse',r.warehouse),
        locationCell(r),
        `<span class="${r.actual_qty<0?'im-negative':'im-positive'}">${r.actual_qty>0?'+':''}${num(r.actual_qty)}</span> ${uom}`,
        num(r.qty_after_transaction)+' '+uom,
        esc([r.batch_no,r.serial_no,r.serial_and_batch_bundle].filter(Boolean).join(' / ') || '—')]))}</section>
      <section class="im-panel" role="tabpanel" aria-labelledby="im-tab-2" id="im-panel-2" hidden><p class="im-muted">Current warehouse totals across all bin locations, regardless of movement dates or bin-location filter. All quantities use ${uom}.</p>${table(['Warehouse','Company','Actual qty','Reserved qty','Ordered qty','Projected qty'],balances.map(b=>[link('Warehouse',b.warehouse),esc(b.company),num(b.actual_qty),num(b.reserved_qty),num(b.ordered_qty),num(b.projected_qty)]))}</section>
      <section class="im-panel" role="tabpanel" aria-labelledby="im-tab-3" id="im-panel-3" hidden><p class="im-muted">Explicit source links on document item rows for this item. Orders and requests are references; they do not themselves change stock.</p>${data.references.length?data.references.map(r=>`<div class="im-reference">${link(r.doctype,r.name,r.doctype+' · '+r.name)}<span>→ ${esc(r.label || 'Referenced by')} →</span>${link(r.to.split('::')[0],r.to.split('::').slice(1).join('::'))}</div>`).join(''):'<div class="im-empty">No readable upstream document references found for the displayed movements.</div>'}</section>`;
    app.querySelectorAll('[data-panel]').forEach(button=>button.addEventListener('click',()=>{
      app.querySelectorAll('[data-panel]').forEach(b=>b.setAttribute('aria-selected',String(b===button)));
      app.querySelectorAll('.im-panel').forEach(p=>p.hidden=p.id!=='im-panel-'+button.dataset.panel);
    }));
    const countControl = document.createElement('select');
    countControl.className='im-button';countControl.setAttribute('aria-label','Graph entries');
    countControl.innerHTML='<option value="36">Latest 36 entries</option><option value="300">All loaded entries</option>';
    countControl.value=String(graphLimit);
    $('im-minus').parentElement.prepend(countControl);
    countControl.onchange=()=>{graphLimit=Number(countControl.value);drawGraph();};
    zoom=1; drawGraph();
    const setZoom = value => {zoom=Math.min(1.5,Math.max(.5,value));$('im-graph').style.zoom=zoom;$('im-reset').textContent=Math.round(zoom*100)+'%';};
    $('im-plus').onclick=()=>setZoom(zoom+.1);$('im-minus').onclick=()=>setZoom(zoom-.1);$('im-reset').onclick=()=>setZoom(1);
  }
  function drawGraph() {
    const rows=data.movements.slice(0,graphLimit);
    const locationKey = row => JSON.stringify([row.warehouse,row.bin_location || '']);
    const whs=[...new Set(rows.map(locationKey))];
    $('im-graph-caption').textContent=`${rows.length} of ${data.movements.length} loaded ledger entries shown. Open a card to view its record; scroll to explore. The movement ledger contains every loaded entry.`;
    if (!rows.length) { $('im-graph').innerHTML='<div class="im-empty">No stock movements for this item in the selected period.</div>'; return; }
    const ins=rows.filter(r=>r.actual_qty>0), outs=rows.filter(r=>r.actual_qty<=0);
    const height=Math.max(ins.length,outs.length,whs.length)*108+90;
    const whY={};whs.forEach((w,i)=>whY[w]=64+i*(height-90)/Math.max(1,whs.length));
    let cards='',paths='';
    const node=(x,y,cls,href,type,title,detail,qty)=>`<a class="im-node ${cls}" style="left:${x}px;top:${y}px" href="${esc(href)}" target="_blank" rel="noopener" title="${esc(type+' · '+title)}"><small>${esc(type)}</small><strong>${esc(title)}</strong><small>${esc(detail)}</small><span class="im-quantity">${esc(qty)}</span></a>`;
    whs.forEach(w=>{
      const matching=rows.filter(r=>locationKey(r)===w), first=matching[0];
      const location=(data.locations || []).find(l=>l.name===first.bin_location);
      const title=first.bin_location || 'Bin not recorded';
      const details=[first.warehouse,location?.zone,location?.rack,location?.shelf,location?.bin_no].filter(Boolean).join(' / ');
      const href=location?url('Bin Location',location.name):url('Warehouse',first.warehouse);
      cards+=node(365,whY[w],'im-wh',href,'WAREHOUSE / BIN LOCATION',title,details,'Displayed net: '+num(matching.reduce((n,r)=>n+Number(r.actual_qty),0))+' '+data.item.stock_uom);
    });
    [ins,outs].forEach((set,side)=>set.forEach((r,i)=>{
      const y=64+i*108,wy=whY[locationKey(r)]+44,inward=side===0;
      const dt=data.documents.find(d=>d.id===r.voucher_type+'::'+r.voucher_no);
      const href=r.can_open_voucher?url(r.voucher_type,r.voucher_no):url('Stock Ledger Entry',r.name);
      cards+=node(inward?35:695,y,inward?'':'im-out',href,r.voucher_type,r.can_open_voucher?r.voucher_no:'Source document restricted',r.posting_date+(dt?.purpose?' · '+dt.purpose:''),(r.actual_qty>0?'+':'')+num(r.actual_qty)+' '+data.item.stock_uom);
      const x1=inward?305:635,x2=inward?365:695,y1=inward?y+44:wy,y2=inward?wy:y+44;
      paths+=`<path d="M ${x1} ${y1} C ${x1+30} ${y1}, ${x2-30} ${y2}, ${x2} ${y2}" stroke="${inward?'#77b9ad':'#d4aa8a'}" stroke-width="1.6" fill="none" marker-end="url(#im-arrow-${side})"/>`;
    }));
    $('im-graph').style.height=height+'px';$('im-graph').style.width='1000px';
    $('im-graph').innerHTML=`<div class="im-column-label" style="left:35px">INWARD / RECEIPTS</div><div class="im-column-label" style="left:365px">STOCK LOCATIONS</div><div class="im-column-label" style="left:695px">OUTWARD / ADJUSTMENTS</div><svg width="1000" height="${height}" aria-hidden="true"><defs>${['#77b9ad','#d4aa8a'].map((color,i)=>`<marker id="im-arrow-${i}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="${color}"/></marker>`).join('')}</defs>${paths}</svg>${cards}`;
  }
  async function load() {
    const id=++requestId;
    notice('Loading inventory relationships…');$('im-results').innerHTML='';
    const params={...source,item_code:$('im-item').value.trim(),company:$('im-company').value,warehouse:$('im-warehouse').value.trim(),bin_location:$('im-bin').value.trim(),from_date:$('im-from').value,to_date:$('im-to').value};
    if(params.from_date && params.to_date && params.from_date>params.to_date){notice('From date must be on or before To date.',true);return;}
    try {
      const result=await api('/api/method/inventory_relationship_map',params);
      if(id!==requestId)return;
      data=result;if(data.item)$('im-item').value=data.item.name;
      if(data.company)$('im-company').value=data.company;
      if(data.source_items?.length)$('im-items').innerHTML=data.source_items.map(v=>`<option value="${esc(v)}"></option>`).join('');
      notice(data.truncated?`Showing the latest ${data.limit} entries. Narrow the date range or warehouse to see older movements.`:'');
      render();
    }catch(error){if(id===requestId)notice(error.message,true);}
  }
  let timer;
  $('im-item').addEventListener('input',()=>{clearTimeout(timer);const id=++lookupId;timer=setTimeout(async()=>{
    try{const query=$('im-item').value.trim();const items=await list('Item',['name','item_name'],[],{or_filters:JSON.stringify([['name','like','%'+query+'%'],['item_name','like','%'+query+'%']]),limit_page_length:30});
      if(id===lookupId)$('im-items').innerHTML=items.map(i=>`<option value="${esc(i.name)}">${esc(i.item_name)}</option>`).join('');
    }catch(e){notice(e.message,true);}
  },250);});
  async function warehouses(){const filters=$('im-company').value?{company:$('im-company').value}:{};const values=await list('Warehouse',['name'],filters,{limit_page_length:500});$('im-warehouses').innerHTML=values.map(v=>`<option value="${esc(v.name)}"></option>`).join('');}
  let binLookupId=0;
  async function binLocations(){const id=++binLookupId;const filters={};if($('im-company').value)filters.company=$('im-company').value;if($('im-warehouse').value.trim())filters.warehouse=$('im-warehouse').value.trim();if($('im-bin').value.trim())filters.name=['like','%'+$('im-bin').value.trim()+'%'];const values=await list('Bin Location',['name','zone','rack','shelf','bin_no'],filters,{limit_page_length:100});if(id===binLookupId)$('im-bins').innerHTML=values.map(v=>`<option value="${esc(v.name)}">${esc([v.zone,v.rack,v.shelf,v.bin_no].filter(Boolean).join(' / '))}</option>`).join('');}
  $('im-company').addEventListener('change',()=>{$('im-warehouse').value='';$('im-bin').value='';Promise.all([warehouses(),binLocations()]).catch(e=>notice(e.message,true));});
  $('im-warehouse').addEventListener('change',()=>{$('im-bin').value='';binLocations().catch(e=>notice(e.message,true));});
  let binTimer;
  $('im-bin').addEventListener('input',()=>{clearTimeout(binTimer);++binLookupId;binTimer=setTimeout(()=>binLocations().catch(e=>notice(e.message,true)),250);});
  $('im-filters').addEventListener('submit',event=>{event.preventDefault();load();});
  async function init(){
    try{
      await api('/api/method/frappe.auth.get_logged_user');
      const companies=await list('Company',['name'],{});
      $('im-company').innerHTML='<option value="">All permitted companies</option>'+companies.map(c=>`<option value="${esc(c.name)}">${esc(c.name)}</option>`).join('');
      for(const [key,id] of [['item_code','im-item'],['company','im-company'],['warehouse','im-warehouse'],['bin_location','im-bin'],['from_date','im-from'],['to_date','im-to']])if(initial.has(key))$(id).value=initial.get(key);
      await Promise.all([warehouses(),binLocations()]);await load();
    }catch(e){notice(e.message,true);if(e.message.includes('sign in'))$('im-results').innerHTML='<a class="im-button im-primary" href="/login?redirect-to=%2Finventory-relationship-map">Sign in to ERPNext</a>';}
  }
  init();
})();
