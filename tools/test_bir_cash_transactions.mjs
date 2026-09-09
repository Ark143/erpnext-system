// Isolated transaction scenarios; never connects to or writes production.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const company='Test Company';
const accounts=['Cash','Bank','Receivable','Payable','Sales'].map(name=>({name,account_type:['Cash','Bank'].includes(name)?name:''}));
const entries=[];
function voucher(name, debitAccount, creditAccount, amount, cancelled=0) {
 for(const [account,debit,credit] of [[debitAccount,amount,0],[creditAccount,0,amount]])
  entries.push({name:name+account,company,is_cancelled:cancelled,posting_date:'2026-09-01',voucher_type:'Journal Entry',voucher_no:name,account,debit,credit});
}
voucher('UNPAID','Receivable','Sales',1000);
voucher('PARTIAL','Cash','Receivable',250);
voucher('FULL','Bank','Receivable',1000);
voucher('SUPPLIER','Payable','Bank',400);
voucher('REFUND','Receivable','Cash',75);
voucher('TRANSFER','Bank','Cash',200);
voucher('CANCELLED','Cash','Receivable',999,1);
// Cross the 500-row fetch boundary, checking that no receipt is lost.
for(let i=0;i<260;i++)voucher('PAGED'+i,'Cash','Receivable',1);
for(const [dt,expected,total] of [
 ['BIR Cash Receipt Journal',262,1510],['BIR Cash Disbursement Journal',2,475]
]) {
 let handlers={},fail=false;
 const doc={doctype:dt,company,from_date:'2026-09-01',to_date:'2026-09-09'};
 const frm={doc,clear_table:k=>doc[k]=[],refresh_field(){},add_child:k=>{const r={};doc[k].push(r);return r;}};
 const frappe={ui:{form:{on:(name,h)=>Object.assign(handlers,h)}},throw:m=>{throw Error(m);},msgprint(){},call:options=>{
  if(fail){options.error(Error('source unavailable'));return;}
  const a=options.args;
  assert.equal(options.method,'frappe.client.get_list');
  let rows=a.doctype==='Account'?accounts:entries.filter(e=>e.company===a.filters.company&&e.is_cancelled===a.filters.is_cancelled&&e.posting_date>=a.filters.posting_date[1][0]&&e.posting_date<=a.filters.posting_date[1][1]);
  options.callback({message:rows.slice(a.limit_start,a.limit_start+a.limit_page_length)});
 }};
 vm.runInNewContext(fs.readFileSync('tools/bir_fixes/'+dt.replaceAll(' ','_')+'.js','utf8'),{frappe,__:s=>s});
 await handlers.generate_report(frm);
 assert.equal(doc.journal_entries.length,expected);
 assert.equal(doc.journal_entries.reduce((s,r)=>s+r.total,0),total);
 assert(!doc.journal_entries.some(r=>['UNPAID','CANCELLED','TRANSFER'].includes(r.invoice_no)));
 assert(doc.journal_entries.every(r=>r.vatable===null));
 const summary=doc.account_summary.at(-1);assert.equal(summary.debit,summary.credit);
 doc.from_date='1900-01-01';doc.to_date='1900-01-02';await handlers.generate_report(frm);
 assert.equal(doc.journal_entries.length,0);assert.equal(doc.account_summary.length,0);
 doc.journal_entries.push({stale:true});fail=true;
 await assert.rejects(handlers.generate_report(frm),/source unavailable/);
 assert.equal(doc.journal_entries.length,0);
 console.log(dt+': partial/full payment, refund, unpaid, cancellation, transfer, pagination, empty period and failure clearing PASS');
}
