import urllib.request, urllib.parse, json, http.cookiejar, time, sys
URL="http://127.0.0.1:8000"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H={"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
op.timeout=20

def apicall(method, args=None, data=None):
    try:
        req=urllib.request.Request(
            URL+"/api/method/"+method + ("?"+urllib.parse.urlencode({"args":json.dumps(args or {})}) if args is not None else ""),
            data=(urllib.parse.urlencode(data).encode() if data is not None else None), headers=H)
        r=op.open(req, timeout=20); j=json.loads(r.read()); return r.status, j
    except urllib.error.HTTPError as e:
        try: bd=json.loads(e.read())
        except: bd={}
        return e.code, bd
    except Exception as e:
        return "ERR", {"exc_type":type(e).__name__,"msg":str(e)[:80]}

lr=op.open(urllib.request.Request(URL+"/api/method/login",
    data=urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode(), headers=H), timeout=20).read()
print("LOGIN:", json.loads(lr).get("message","?")[:60], flush=True)

results=[]
search_tests = [
    ("Customer","Sales Order Customer","erpnext.controllers.queries.customer_query",{}),
    ("Supplier","Purchase Order Supplier","erpnext.controllers.queries.supplier_query",{}),
    ("Item","Sales Order Item","erpnext.controllers.queries.item_query",{"is_sales_item":1,"has_variants":0}),
    ("Item","Purchase Order Item","erpnext.controllers.queries.item_query",{"is_purchase_item":1,"has_variants":0}),
    ("Warehouse","Stock Entry Warehouse",None,{}),
    ("Account","GL Entry Account","erpnext.controllers.queries.ledger_account_query",{}),
    ("BOM",None,None,{}),
    ("Sales Order",None,None,{}),
    ("Purchase Order",None,None,{}),
    ("Employee",None,None,{}),
    ("Customer Group",None,None,{}),
]
for dt, ref, query, filt in search_tests:
    args={"txt":"","doctype":dt,"page_length":"10","link_fieldname":dt.lower().replace(" ","_")}
    if ref: args["reference_doctype"]=ref
    if query: args["query"]=query
    if filt: args["filters"]=json.dumps(filt)
    t0=time.time(); st,j=apicall("frappe.desk.search.search_link", args)
    if st==200: msg="ok:"+str(len(j.get("message",[]))); exc=""
    else: msg=j.get("exc_type","?"); exc=j.get("exc",j.get("exception",""))[-240:]
    results.append(("search "+dt+(" ["+query.split('.')[-1]+"]" if query else ""), st, round(time.time()-t0,1), msg, exc))

print(f"\n{'TEST':54} {'HTTP':5} {'s':5} RESULT", flush=True)
print("-"*95, flush=True)
for name,st,sec,msg,exc in results:
    flag = "" if st==200 else "  <-- FAIL"
    print(f"{name:54} {str(st):5} {sec:<5} {msg}{flag}", flush=True)
    if exc: print("      ", exc.replace("\n"," ")[:180], flush=True)
