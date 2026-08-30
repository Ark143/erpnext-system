import urllib.request, urllib.parse, json, http.cookiejar, time
URL="http://127.0.0.1:8000"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H={"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
op.timeout=30

def apicall(method, params):
    try:
        p=urllib.parse.urlencode(params)
        r=op.open(urllib.request.Request(URL+"/api/method/"+method+"?"+p, headers=H), timeout=30)
        j=json.loads(r.read()); return r.status, j
    except urllib.error.HTTPError as e:
        try: bd=json.loads(e.read())
        except: bd={}
        return e.code, bd
    except Exception as e:
        return "ERR", {"exc_type":type(e).__name__}

lr=op.open(urllib.request.Request(URL+"/api/method/login",
    data=urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode(), headers=H), timeout=30).read()
print("LOGIN:", json.loads(lr).get("message","?")[:40], flush=True)

# corrected: use REAL query functions found via grep
search_tests = [
    ("Item","Sales Order Item","erpnext.controllers.queries.item_query",{"is_sales_item":1,"has_variants":0}),
    ("Item","Purchase Order Item","erpnext.controllers.queries.item_query",{"is_purchase_item":1,"has_variants":0}),
    ("Warehouse","Stock Entry Warehouse","erpnext.controllers.queries.warehouse_query",{}),
    ("Account","GL Entry Account","erpnext.controllers.queries.get_account_list",{}),
    ("BOM",None,"erpnext.controllers.queries.bom",{}),
    ("Employee",None,"erpnext.controllers.queries.employee_query",{}),
    ("Lead",None,"erpnext.controllers.queries.lead_query",{}),
    ("Customer",None,None,{}),
    ("Supplier",None,None,{}),
]
results=[]
for dt, ref, query, filt in search_tests:
    params={"txt":"","doctype":dt,"page_length":"10","link_fieldname":dt.lower().replace(" ","_")}
    if ref: params["reference_doctype"]=ref
    if query: params["query"]=query
    if filt: params["filters"]=json.dumps(filt)
    t0=time.time(); st,j=apicall("frappe.desk.search.search_link", params)
    if st==200: msg="ok:"+str(len(j.get("message",[]))); exc=""
    else: msg=j.get("exc_type","?"); exc=j.get("exc",j.get("exception",""))[-240:]
    results.append(("search "+dt+(" ["+query.split('.')[-1]+"]" if query else " [default]"), st, round(time.time()-t0,1), msg, exc))

# key reports
for rpt in ["Stock Ledger","General Ledger","Trial Balance","Accounts Receivable","Accounts Payable","Item Valuation","Stock Balance"]:
    params={"report_name":rpt,"doctype":rpt,"filters":json.dumps({})}
    t0=time.time(); st,j=apicall("frappe.desk.query_report.run", params)
    if st==200: msg="ok:"+str(len(j.get("message",{}).get("result",[]) if isinstance(j.get("message"),dict) else [])); exc=""
    else: msg=j.get("exc_type","?"); exc=j.get("exc",j.get("exception",""))[-240:]
    results.append(("report "+rpt, st, round(time.time()-t0,1), msg, exc))

print(f"\n{'TEST':54} {'HTTP':5} {'s':5} RESULT", flush=True)
print("-"*95, flush=True)
fails=0
for name,st,sec,msg,exc in results:
    flag = "" if st==200 else "  <-- FAIL"
    if st!=200: fails+=1
    print(f"{name:54} {str(st):5} {sec:<5} {msg}{flag}", flush=True)
    if exc: print("      ", exc.replace("\n"," ")[:180], flush=True)
print(f"\nTOTAL FAILS: {fails}/{len(results)}", flush=True)
