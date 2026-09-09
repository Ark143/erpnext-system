"""Reconcile generated in-memory reports with live sources and render live formats.

Run audit_bir_generators.mjs first. This script never saves a business document.
"""
import json
import os
from collections import defaultdict
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'backups/bir_fix_candidate_20260909'
BASE=os.environ.get('ERPNEXT_URL','http://38.247.138.224:10017')
s=requests.Session()
s.post(BASE+'/api/method/login',data={'usr':os.environ.get('ERPNEXT_USER','Administrator'),'pwd':os.environ['ERPNEXT_PASSWORD']},timeout=30).raise_for_status()
def read(dt,filters,fields):
    rows=[]
    while True:
        r=s.get(BASE+'/api/method/frappe.client.get_list',params={'doctype':dt,'filters':json.dumps(filters),'fields':json.dumps(fields),'limit_start':len(rows),'limit_page_length':500,'order_by':'name asc'},timeout=60)
        r.raise_for_status();page=r.json()['message'];rows+=page
        if len(page)<500:return rows
def doc(dt):return json.loads((OUT/(dt.replace(' ','_')+'_generated.json')).read_text())
result={'checks':[],'prints':[]}
def check(name,passed):
    assert passed,name
    result['checks'].append(name);print('PASS:',name)
reports=json.loads((OUT/'generator_results.json').read_text())
check('All nine live generators return no runtime or child-field errors',len(reports)==9 and all(not r['errors'] and not r['unknown_fields'] for r in reports))
check('Empty periods clear transactional rows',all(not n for r in reports for k,n in r['empty_period_row_counts'].items() if k not in ['summary_entries','vat_entries','total_entries']))
scope={'company':'ULTRA MRF','is_cancelled':0,'posting_date':['between',['2026-01-01','2026-09-09']]}
gl=read('GL Entry',scope,['account','voucher_type','voucher_no','debit','credit'])
accounts=read('Account',{'company':'ULTRA MRF'},['name','account_type','account_number','account_name'])
cash={r['name'] for r in accounts if r['account_type'] in ['Cash','Bank']}
amounts=defaultdict(float)
for r in gl:
    if r['account'] in cash:amounts[r['voucher_no']]+=float(r['debit'] or 0)-float(r['credit'] or 0)
for dt,sign,field in [('BIR Cash Receipt Journal',1,'net_cash'),('BIR Cash Disbursement Journal',-1,'net_paid')]:
    expected={k:sign*v for k,v in amounts.items() if sign*v>0.000001}
    actual={r['invoice_no']:r[field] for r in doc(dt)['journal_entries']}
    check(dt+' voucher amounts match independently summed cash/bank GL',expected.keys()==actual.keys() and all(abs(actual[k]-v)<0.005 for k,v in expected.items()))
    result[dt]={'vouchers':len(actual),'total':round(sum(actual.values()),2)}
invoices={}
for dt in ['Sales Invoice','Purchase Invoice']:
    invoices.update({r['name']:r for r in read(dt,{'company':'ULTRA MRF','docstatus':1},['name','status','outstanding_amount','grand_total'])})
unpaid={k for k,v in invoices.items() if v['grand_total']>0 and abs(v['outstanding_amount']-v['grand_total'])<0.005}
for dt,table in [('BIR Sales Journal','sales_entries'),('BIR Purchases Book','purchase_entries')]:
    d=doc(dt)
    if table not in d:table=next(k for k,v in d.items() if isinstance(v,list) and v and 'invoice_no' in v[0])
    check(dt+' unpaid invoices have no invented payment date',all(r.get('payment_date') in [None,'','-'] for r in d[table] if r.get('invoice_no') in unpaid))
journal=doc('BIR General Journal')['journal_entries']
check('General Journal invoice statuses match source records',all(r['status']==invoices[r['voucher_no']]['status'].upper() for r in journal if r.get('status') and r.get('voucher_no') in invoices))
for field in ['debit','credit']:
    check('General Ledger '+field+' reconciles to GL',abs(sum(float(r[field] or 0) for r in gl)-sum(float(r.get(field) or 0) for r in doc('BIR General Ledger')['gl_entries'] if not r.get('is_total_row')))<0.005)
opening_file=ROOT/'backups/bir_fix_candidate_opening_20260909/BIR_General_Ledger_generated.json'
if opening_file.exists():
    opening_doc=json.loads(opening_file.read_text())
    prior=read('GL Entry',{'company':'ULTRA MRF','is_cancelled':0,'posting_date':['<',opening_doc['from_date']]},['account','debit','credit'])
    expected=defaultdict(float)
    for r in prior:expected[r['account']]+=float(r['debit'] or 0)-float(r['credit'] or 0)
    expected={k:v for k,v in expected.items() if abs(v)>0.000001}
    actual={r['account']:r['balance'] for r in opening_doc['gl_entries'] if r.get('description')=='Opening balance'}
    check('September ledger opening balances reconcile to prior posted GL',expected.keys()==actual.keys() and all(abs(actual[k]-v)<0.005 for k,v in expected.items()))
    result['opening_accounts']=len(actual)
formats=json.loads((ROOT/'tools/bir_fixes/print_formats.json').read_text())
for pf in formats:
    dt=pf['doc_type'];d=doc(dt)
    r=s.post(BASE+'/api/method/frappe.www.printview.get_html_and_style',data={'doc':json.dumps(d),'print_format':pf['name'],'doctype':dt},timeout=60)
    r.raise_for_status();body=r.json()['message'];html=body['html'];css=body.get('style','')
    (OUT/(dt.replace(' ','_')+'_generated.html')).write_text('<html><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+html+'</body></html>',encoding='utf-8')
    check(dt+' live HTML print renders',len(html)>100)
    result['prints'].append({'doctype':dt,'html_bytes':len(html),'status':r.status_code})
    if 'Cash' in dt:check(dt+' print labels unclassified amounts', 'unclassified' in html and '—' in html)
    if dt=='BIR Form 2307':check('Form 2307 uses restored background','/files/bir_2307_restored_20260909.png' in html)
r=s.get(BASE+'/files/bir_2307_restored_20260909.png',timeout=30)
check('Form 2307 background is accessible and matches source',r.status_code==200 and r.content==(ROOT/'tools/bir_fixes/assets/bir_2307_page1.png').read_bytes())
r=s.get(BASE+'/api/method/frappe.utils.print_format.download_pdf',params={'doctype':'BIR Form 2307','name':doc('BIR Form 2307')['name'],'format':'BIR Form 2307 Print Format'},timeout=60)
result['pdf']={'status':r.status_code,'valid_pdf':r.content.startswith(b'%PDF'),'error':r.json().get('exception') if not r.content.startswith(b'%PDF') else None}
(OUT/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PDF status:',result['pdf'])
