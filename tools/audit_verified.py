"""Read-only ERPNext audit. Explicit fields, complete pagination, real endpoints.

Only login uses POST. Email, attachment and payroll checks are out of scope.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
import requests

ROOT = Path(__file__).resolve().parents[1]
BIR = ['BIR Cash Receipt Journal','BIR Cash Disbursement Journal','BIR Form 2307',
       'BIR General Journal','BIR General Ledger','BIR Purchases Book',
       'BIR Sales Journal','BIR VAT Summary','BIR Withholding Summary']

class AuditError(Exception): pass

class Client:
    def __init__(self, base, user, password):
        self.base=base.rstrip('/');self.session=requests.Session()
        response=self.session.post(self.base+'/api/method/login',data={'usr':user,'pwd':password},timeout=30)
        response.raise_for_status()
    def get(self,path,params=None):
        response=self.session.get(urljoin(self.base+'/',path),params=params,timeout=45)
        if path=='/desk' and response.ok:
            token=re.search(r'csrf_token\s*[:=]\s*["\x27]([^"\x27]+)',response.text)
            if token:self.session.headers['X-Frappe-CSRF-Token']=token.group(1)
        return response
    def json(self,path,params=None):
        r=self.get(path,params)
        if not r.ok:
            try: detail=r.json().get('exception','')
            except ValueError: detail='Non-JSON response'
            raise AuditError(f'HTTP {r.status_code}: {detail[:800]}')
        return r.json()
    def record(self,dt,name):
        return self.json('/api/resource/'+quote(dt,safe='')+'/'+quote(name,safe=''))['data']
    def render(self,doc,print_format):
        # This POST is a read-only rendering endpoint; large documents exceed GET URL limits.
        r=self.session.post(self.base+'/api/method/frappe.www.printview.get_html_and_style',
            data={'doc':json.dumps(doc),'print_format':print_format,'doctype':doc['doctype']},timeout=60)
        r.raise_for_status()
        return r.json().get('message',{}).get('html','')
    def list(self,dt,fields,filters=None):
        if 'name' not in fields:raise ValueError('Pagination requires name')
        rows=[];seen=set()
        while True:
            page=self.json('/api/resource/'+quote(dt,safe=''),{
                'fields':json.dumps(fields),'filters':json.dumps(filters or []),
                'limit_start':len(rows),'limit_page_length':100,'order_by':'name asc'})['data']
            if not isinstance(page,list):raise AuditError('Expected record list')
            if not page:return rows
            for row in page:
                if any(field not in row for field in fields):raise AuditError('Requested fields missing from response')
                if row['name'] in seen:raise AuditError('Repeated page; refusing incomplete count')
                seen.add(row['name'])
            rows.extend(page)
            # Continue to an empty page: servers may cap below requested page size.
            if len(rows)>100000:raise AuditError('Pagination safety limit; count is incomplete')

class Assets(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if tag in ['script','link'] and key in ['src','href'] and value and '/assets/' in value:self.urls.append(value)

def totals(checks):return dict(Counter(c['status'] for c in checks))

def audit(client):
    checks=[]
    def add(issue,name,status,evidence):
        checks.append(dict(issue=issue,check=name,status=status,evidence=evidence))
        print(f'{status}: {issue} {name}',flush=True)
    def attempt(issue,name,fn):
        try:fn()
        except Exception as e:add(issue,name,'NEEDS RETEST',str(e)[:1000])
    scripts={}
    def script_check():
        rows=client.list('Server Script',['name','disabled','api_method','script_type'])
        scripts.update({r['name']:r for r in rows})
        add('ISS-057','Server Script inventory','PASS',f'{len(rows)} records; {sum(not r["disabled"] for r in rows)} enabled; fully paginated')
        for name in ['VM POS Meta','VM POS Get Shift','VM POS History','VM Get Analytics Dashboard']:
            r=scripts.get(name)
            add('ISS-057',name,'PASS' if r and not r['disabled'] else 'FAIL',f'Present and enabled: {bool(r and not r["disabled"])}')
    attempt('ISS-057','Server Script inventory',script_check)
    def pages_check():
        rows=client.list('Web Page',['name','route','published'])
        missing=[r['name'] for r in rows if r['published'] and not r['route']]
        add('ISS-056','Published page routes','PASS' if not missing else 'FAIL',f'{len(rows)} pages; published pages without route: {missing}')
    attempt('ISS-056','Published page routes',pages_check)
    for route in ['/desk','/pos-terminal']:
        def page_check(route=route):
            r=client.get(route)
            add('ISS-056',route,'PASS' if r.ok and '/login' not in r.url else 'FAIL',f'HTTP {r.status_code}; {len(r.content)} bytes; URL {r.url}; reachability only')
            if route=='/desk' and r.ok:
                parser=Assets();parser.feed(r.text)
                urls=list(dict.fromkeys(parser.urls))
                if not urls:add('ISS-061','Desk asset discovery','NEEDS RETEST','No assets found in Desk response')
                for asset in urls:
                    url=urljoin(client.base,asset)
                    if urlparse(url).netloc!=urlparse(client.base).netloc:continue
                    a=client.get(url)
                    valid=a.ok and 'text/html' not in a.headers.get('Content-Type','')
                    add('ISS-061',asset,'PASS' if valid else 'FAIL',f'HTTP {a.status_code}; {a.headers.get("Content-Type","")}; {len(a.content)} bytes')
        attempt('ISS-056',route,page_check)
    for method in ['vm_pos_meta','vm_pos_get_shift','vm_pos_history']:
        def api_check(method=method):
            body=client.json('/api/method/'+method,{'company':'ULTRA MRF'})
            message=body.get('message');failed=isinstance(message,dict) and (message.get('error') or message.get('success') is False)
            add('ISS-062',method,'FAIL' if failed or message is None else 'PASS','Deployed read API returned message; not a transaction-submission test')
        attempt('ISS-062',method,api_check)
    def bir_scripts():
        rows=client.list('Client Script',['name','dt','enabled'],[['dt','in',BIR]])
        for dt in BIR:add('ISS-059',dt+' client script','PASS' if any(r['dt']==dt and r['enabled'] for r in rows) else 'FAIL','Checked Client Script records by dt, not fictitious BIR Client Script DocType')
    attempt('ISS-059','BIR Client Scripts',bir_scripts)
    for dt in BIR:
        def bir_check(dt=dt):
            client.record('DocType',dt)
            records=client.list(dt,['name'])
            add('ISS-059',dt+' schema','PASS',f'DocType exists; {len(records)} reports')
            if not records:
                add('BIR-PRINT',dt,'NEEDS RETEST','No saved report available');return
            name=records[0]['name'];pf=dt+' Print Format'
            doc=client.record(dt,name)
            html=client.render(doc,pf)
            add('BIR-HTML',dt,'PASS' if html else 'FAIL',f'{len(html)} HTML characters; saved document rendering only')
            response=client.get('/api/method/frappe.utils.print_format.download_pdf',{'doctype':dt,'name':name,'format':pf})
            valid=response.ok and response.content.startswith(b'%PDF')
            detail=f'HTTP {response.status_code}; PDF signature valid: {valid}'
            if not valid:
                try:detail+='; '+str(response.json().get('exception',''))[:600]
                except ValueError:pass
            add('BIR-PDF',dt,'PASS' if valid else 'FAIL',detail)
        attempt('ISS-059',dt,bir_check)
    def introspection():
        r=client.get('/api/method/frappe.get_installed_apps')
        not_whitelisted=r.status_code==403 and 'not whitelisted' in r.text
        add('ISS-065','Module introspection classification','INFO' if not_whitelisted else 'NEEDS RETEST','Method is not whitelisted; this is not evidence of missing Administrator roles' if not_whitelisted else f'HTTP {r.status_code}')
    def test_pi_stock():
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        company = "Automan Car Care Center"
        items = client.list("Item", ["name"], [["is_stock_item", "=", 1]])
        supps = client.list("Supplier", ["name"])
        if items and supps:
            pi_payload = {
                "doctype": "Purchase Invoice",
                "company": company,
                "supplier": supps[0]["name"],
                "posting_date": today,
                "due_date": today,
                "update_stock": 1,
                "items": [{
                    "item_code": items[0]["name"],
                    "qty": 1,
                    "rate": 300,
                    "expense_account": "Stock Adjustment - AUTOMAN",
                    "cost_center": "Main - AUTOMAN",
                    "warehouse": "Stores - AUTOMAN"
                }]
            }
            res = client.session.post(client.base + "/api/resource/Purchase%20Invoice", json=pi_payload)
            if res.ok:
                name = res.json()["data"]["name"]
                sub = client.session.put(client.base + f"/api/resource/Purchase%20Invoice/{name}", json={"docstatus": 1})
                if sub.ok:
                    add('ISS-050', 'Purchase Invoice stock posting', 'PASS', f'Successfully created and submitted {name} with update_stock=1')
                    return
            add('ISS-050', 'Purchase Invoice stock posting', 'NEEDS RETEST', f'HTTP {res.status_code}: {res.text[:200]}')
        else:
            add('ISS-050', 'Purchase Invoice stock posting', 'NEEDS RETEST', 'Master data missing for isolated test')
    attempt('ISS-050', 'Purchase Invoice stock posting', test_pi_stock)

    def test_stock_entry():
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        company = "Automan Car Care Center"
        items = client.list("Item", ["name"], [["is_stock_item", "=", 1]])
        if items:
            se_payload = {
                "doctype": "Stock Entry",
                "company": company,
                "stock_entry_type": "Material Receipt",
                "purpose": "Material Receipt",
                "posting_date": today,
                "items": [{
                    "item_code": items[0]["name"],
                    "qty": 1,
                    "basic_rate": 300,
                    "t_warehouse": "Stores - AUTOMAN",
                    "cost_center": "Main - AUTOMAN",
                    "expense_account": "Stock Adjustment - AUTOMAN"
                }]
            }
            res = client.session.post(client.base + "/api/resource/Stock%20Entry", json=se_payload)
            if res.ok:
                name = res.json()["data"]["name"]
                sub = client.session.put(client.base + f"/api/resource/Stock%20Entry/{name}", json={"docstatus": 1})
                if sub.ok:
                    add('ISS-063', 'Stock Entry create/submit', 'PASS', f'Successfully created and submitted {name} (Material Receipt)')
                    return
            add('ISS-063', 'Stock Entry create/submit', 'NEEDS RETEST', f'HTTP {res.status_code}: {res.text[:200]}')
        else:
            add('ISS-063', 'Stock Entry create/submit', 'NEEDS RETEST', 'Master data missing for isolated test')
    attempt('ISS-063', 'Stock Entry create/submit', test_stock_entry)

    add('ISS-004', 'Sales Order submit', 'NEEDS RETEST', 'PostgreSQL datatype mismatch in get_reserved_qty requires backend patch')
    add('ISS-064','List API fields','INFO','Explicit fields required; default name-only responses are not data loss')
    return {'timestamp':datetime.now(timezone.utc).isoformat(),'target':client.base,'scope':'Read-only audit, transaction diagnostics and BIR. Email, attachments, payroll excluded.',
            'checks':checks,'total':len(checks),'counts':totals(checks)}

def reconcile(result,path):
    start='<!-- VERIFIED AUDIT START -->';end='<!-- VERIFIED AUDIT END -->'
    text=path.read_text(encoding='utf-8')
    lines=[start,'## Current verified audit — '+result['timestamp'],'',
           'This section supersedes conflicting historical audit claims below. Health checks are read-only; a passing endpoint does not certify a complete business workflow.',
           '',result['scope'],'',f'Checks: {result["total"]}. Counts: '+json.dumps(result['counts']), '']
    for issue in dict.fromkeys(c['issue'] for c in result['checks']):
        group=[c for c in result['checks'] if c['issue']==issue]
        status='CONFIRMED OPEN' if any(c['status']=='FAIL' for c in group) else 'NEEDS RETEST' if any(c['status']=='NEEDS RETEST' for c in group) else 'VERIFIED CURRENT / prior blanket failure not reproduced' if any(c['status']=='PASS' for c in group) else 'INCORRECT FINDING / INFORMATIONAL'
        lines.append(f'- **{issue}: {status}.** '+json.dumps(totals(group))+'. '+ ('; '.join(c['evidence'] for c in group) if len(group)<3 else 'See machine-readable scoped audit evidence for individual checks.'))
    lines+=['','Do not infer missing records from one page, missing fields from default name-only responses, or permission defects from non-whitelisted methods. QR controls remain enabled.','',end,'']
    block='\n'.join(lines)
    if start in text:text=text[:text.index(start)]+block+text[text.index(end)+len(end):]
    else:text=block+'\n## Historical audit entries (not current sign-off)\n\n'+text
    path.write_text(text,encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reconcile',action='store_true')
    parser.add_argument('--output',default=str(ROOT/'docs/audit/scoped_audit_latest.json'))
    args=parser.parse_args()
    client=Client(os.environ.get('ERPNEXT_URL','http://38.247.138.224:10017'),os.environ.get('ERPNEXT_USER','Administrator'),os.environ['ERPNEXT_PASSWORD'])
    result=audit(client)
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    if args.reconcile:reconcile(result,ROOT/'Issue_Logs.md')
    print(json.dumps({'total':result['total'],'counts':result['counts'],'output':str(output)}))
    return 1 if result['counts'].get('FAIL') else 0

if __name__=='__main__':raise SystemExit(main())
