import urllib.request, urllib.parse, json, http.cookiejar, time
URL="http://127.0.0.1:8000"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H={"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
op.timeout=40

def apicall(method, params):
    try:
        p=urllib.parse.urlencode(params)
        r=op.open(urllib.request.Request(URL+"/api/method/"+method+"?"+p, headers=H), timeout=40)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: bd=json.loads(e.read())
        except: bd={}
        return e.code, bd
    except Exception as e:
        return "ERR", {"exc_type":type(e).__name__}

op.open(urllib.request.Request(URL+"/api/method/login",
    data=urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode(), headers=H), timeout=30).read()

def run_report(rpt, extra=None):
    base={"company":"ULTRA MRF","from_date":"2026-01-01","to_date":"2026-12-31"}
    if extra: base.update(extra)
    params={"report_name":rpt,"doctype":rpt,"filters":json.dumps(base)}
    st,j=apicall("frappe.desk.query_report.run", params)
    if st==200:
        m=j.get("message",{})
        res=m.get("result",[]) if isinstance(m,dict) else []
        return st, f"ok rows={len(res)}"
    return st, j.get("exc_type","?")+" | "+j.get("exc",j.get("exception",""))[-220:]

for rpt,extra in [
    ("Stock Ledger",{}),
    ("Trial Balance",{}),
    ("Item Valuation",{}),
    ("Stock Balance",{}),
    ("General Ledger",{"account":"%"}),
    ("Stock Ledger",{"voucher_type":"Stock Entry"}),
]:
    st,msg=run_report(rpt,extra)
    print(f"report {rpt:22} -> {st}  {msg}", flush=True)

# BOM search with txt
for txt in ["", "BOM"]:
    params={"txt":txt,"doctype":"BOM","page_length":"10","link_fieldname":"name","query":"erpnext.controllers.queries.bom"}
    st,j=apicall("frappe.desk.search.search_link", params)
    print(f"search BOM txt='{txt}' -> {st}  {j.get('exc_type','ok:'+str(len(j.get('message',[])))) if st!=200 else 'ok:'+str(len(j.get('message',[])))}", flush=True)
