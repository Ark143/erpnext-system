// Read-only execution of the live client generators against live Frappe reads.
// The form is in memory, never saved. Only get/get_list calls are allowed.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const dir = path.resolve(process.argv[2] || 'backups/bir_audit_20260909');
const base = process.env.ERPNEXT_URL || 'http://38.247.138.224:10017';
const login = await fetch(base+'/api/method/login',{method:'POST',body:new URLSearchParams({usr:process.env.ERPNEXT_USER || 'Administrator',pwd:process.env.ERPNEXT_PASSWORD})});
if(!login.ok)throw new Error('Login failed');
const cookie=login.headers.getSetCookie().map(s=>s.split(';')[0]).join('; ');
async function read(method,args){
 if(!['frappe.client.get','frappe.client.get_list'].includes(method))throw new Error('Non-read method blocked: '+method);
 const params=Object.fromEntries(Object.entries(args).map(([k,v])=>[k,typeof v==='object'?JSON.stringify(v):v]));
 const r=await fetch(base+'/api/method/'+method+'?'+new URLSearchParams(params),{headers:{Cookie:cookie}});
 const body=await r.json(); if(!r.ok)throw new Error(args.doctype+' HTTP '+r.status+' '+(body.exception || body._server_messages));return body.message;
}
const scripts=JSON.parse(fs.readFileSync(path.join(dir,'Client_Script.json')));
const results=[];
for(const script of scripts){
 const dt=script.dt,slug=dt.replaceAll(' ','_'),meta=JSON.parse(fs.readFileSync(path.join(dir,slug+'_meta.json')));
 const doc=JSON.parse(fs.readFileSync(path.join(dir,slug+'_record.json')));
 doc.company='ULTRA MRF';doc.from_date=dt==='BIR Form 2307'?'2026-07-01':'2026-01-01';doc.to_date='2026-09-09';
 if(dt==='BIR Form 2307'){
  const inv=await read('frappe.client.get_list',{doctype:'Sales Invoice',filters:{company:doc.company,docstatus:1},fields:['customer'],limit_page_length:1});
  doc.party_type='Customer';doc.party=inv[0]?.customer;
 }
 const tables=new Map(meta.fields.filter(f=>f.fieldtype==='Table').map(f=>[f.fieldname,f.options]));
 for(const key of tables.keys())doc[key]=[];
 const result={doctype:dt,company:doc.company,from_date:doc.from_date,to_date:doc.to_date,errors:[],messages:[],calls:[]};
 const pending=new Set();let handler;
 const frm={doc,clear_table(name){if(!tables.has(name))throw new Error('Unknown table '+name);doc[name]=[];},
 add_child(name){if(!tables.has(name))throw new Error('Unknown table '+name);const row={doctype:tables.get(name),parent:doc.name,parenttype:dt,parentfield:name,idx:doc[name].length+1};doc[name].push(row);return row;},
 refresh_field(){},set_value(name,value){doc[name]=value;return Promise.resolve();}};
 const frappe={ui:{form:{on(name,h){handler={...handler,...h};}}},datetime:{str_to_obj:s=>new Date(s),str_to_user:s=>s},
 throw(message){throw new Error(message);},show_alert:m=>result.messages.push(m),msgprint:m=>result.messages.push(m),
 call(options){const entry={method:options.method,args:options.args};result.calls.push(entry);
  const promise=read(options.method,options.args).then(message=>{entry.rows=Array.isArray(message)?message.length:1;options.callback?.({message});}).catch(e=>{result.errors.push(e.message);});
  pending.add(promise);promise.finally(()=>pending.delete(promise));return promise;
 }};
 const onUnhandled=e=>result.errors.push('Async: '+e.message);
 process.on('unhandledRejection',onUnhandled);
 try{
  vm.runInNewContext(script.script,{frappe,__:s=>s,console,Date,Promise},{timeout:3000});
  await handler.generate_report(frm);
  for(let i=0;i<50;i++){await Promise.all([...pending]);await new Promise(r=>setTimeout(r,20));if(!pending.size)break;}
 }catch(e){result.errors.push(e.message);}
 process.off('unhandledRejection',onUnhandled);
 result.row_counts=Object.fromEntries([...tables.keys()].map(k=>[k,doc[k].length]));
 result.unknown_fields={};
 for(const [field,childtype]of tables){if(!doc[field].length)continue;const child=await read('frappe.client.get',{doctype:'DocType',name:childtype});const valid=new Set(['doctype','parent','parenttype','parentfield','idx',...child.fields.map(f=>f.fieldname)]);const bad=[...new Set(doc[field].flatMap(r=>Object.keys(r).filter(k=>!valid.has(k))))];if(bad.length)result.unknown_fields[field]=bad;}
 fs.writeFileSync(path.join(dir,slug+'_generated.json'),JSON.stringify(doc,null,2));
 // A report must clear previous rows when the next period has no source data.
 doc.from_date='1900-01-01';doc.to_date='1900-01-02';
 try{
  await handler.generate_report(frm);
  for(let i=0;i<50;i++){await Promise.all([...pending]);await new Promise(r=>setTimeout(r,20));if(!pending.size)break;}
  result.empty_period_row_counts=Object.fromEntries([...tables.keys()].map(k=>[k,doc[k].length]));
 }catch(e){result.errors.push('Empty-period check: '+e.message);}
 results.push(result);console.log(JSON.stringify({doctype:dt,errors:result.errors,rows:result.row_counts,unknown:result.unknown_fields,messages:result.messages}));
}
fs.writeFileSync(path.join(dir,'generator_results.json'),JSON.stringify(results,null,2));
