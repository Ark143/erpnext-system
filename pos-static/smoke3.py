import urllib.request, urllib.parse, json, http.cookiejar, sys, time
URL="http://localhost"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H={"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
op.timeout=15

def apicall(method, args=None, data=None):
    try:
        req=urllib.request.Request(
            URL+"/api/method/"+method + ("?"+urllib.parse.urlencode({"args":json.dumps(args or {})}) if args is not None else ""),
            data=(urllib.parse.urlencode(data).encode() if data is not None else None), headers=H)
        r=op.open(req, timeout=15); j=json.loads(r.read()); return r.status, j
    except urllib.error.HTTPError as e:
        try: bd=json.loads(e.read())
        except: bd={}
        return e.code, bd
    except Exception as e:
        return "ERR", {"exc_type":type(e).__name__,"msg":str(e)[:80]}

# login
try:
    lr=op.open(urllib.request.Request(URL+"/api/method/login",
        data=urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode(), headers=H), timeout=15).read()
    print("LOGIN:", json.loads(lr).get("message","?")[:80], flush=True)
except Exception as e:
    print("LOGIN FAILED:", e, flush=True)

results=[]
search_tests = [
    ("Customer","Sales Order Customer","erpnext.controllers.queries.customer_query",{}),
    ("Supplier","Purchase Order Supplier","erpnext.controllers.queries.supplier_query",{}),
    ("Item","Sales Order Item","erpnext.controllers.queries.item_query",{"is_sales_item":1,"has_variants":0}),
    ("Warehouse","Stock Entry Warehouse",None,{}),
    ("Account","GL Entry Account","erpnext.controllers.queries.ledger_account_query",{}),
    ("BOM",None,None,{}),
    ("Sales Order",None,None,{}),
    ("Employee",None,None,{}),
]
for dt, ref, query, filt in search_tests:
    args={"txt":"","doctype":dt,"page_length":"10","link_fieldname":dt.lower().replace(" ","_")}
    if ref: args["reference_doctype"]=ref
    if query: args["query"]=query
    if filt: args["filters"]=json.dumps(filt)
    t0=time.time(); st,j=apicall("frappe.desk.search.search_link", args)
    if st==200: msg="ok:"+str(len(j.get("message",[]))); exc=""
    else: msg=j.get("exc_type","?"); exc=j.get("exc",j.get("exception",""))[-260:]
    results.append((f"search {dt}"+(f" [{query.split('.')[-1]}]" if query else ""), st, round(time.time()-t0,1), msg, exc))

print(f"\n{'TEST':52} {'HTTP':5} {'s':4} RESULT", flush=True)
print("-"*90, flush=True)
for name,st,sec,msg,exc in results:
    flag = "" if st==200 else "  <-- FAIL"
    print(f"{name:52} {str(st):5} {sec:<4} {msg}{flag}", flush=True)
    if exc: print("     ", exc.replace("\n"," ")[:200], flush=True)
