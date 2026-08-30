import urllib.request, urllib.parse, json, http.cookiejar
URL="http://localhost"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H={"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}

def raw(method, args=None, data=None):
    if data is not None:
        req=urllib.request.Request(URL+"/api/method/"+method, data=urllib.parse.urlencode(data).encode(), headers=H)
    else:
        p=urllib.parse.urlencode({"args":json.dumps(args or {})})
        req=urllib.request.Request(URL+"/api/method/"+method+"?"+p, headers=H)
    return op.open(req, timeout=40).read()

# login
lr = op.open(urllib.request.Request(URL+"/api/method/login",
        data=urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode(), headers=H), timeout=30).read()
print("LOGIN:", json.loads(lr).get("message", lr.decode()[:120]))

def apicall(method, args=None, data=None):
    try:
        r = op.open(urllib.request.Request(
            URL+"/api/method/"+method + ("?"+urllib.parse.urlencode({"args":json.dumps(args or {})}) if args is not None else ""),
            data=(urllib.parse.urlencode(data).encode() if data is not None else None),
            headers=H), timeout=40)
        j=json.loads(r.read()); return r.status, j
    except urllib.error.HTTPError as e:
        try: bd=json.loads(e.read())
        except: bd={}
        return e.code, bd
    except Exception as e:
        return "ERR", {"exc_type":type(e).__name__}

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
    st,j=apicall("frappe.desk.search.search_link", args)
    if st==200:
        msg="ok:"+str(len(j.get("message",[])))
        exc=""
    else:
        msg=j.get("exc_type","?"); exc=j.get("exc",j.get("exception",""))[-300:]
    results.append((f"search {dt}"+(f" [{query.split('.')[-1]}]" if query else ""), st, msg, exc))

for dt in ["Sales Invoice","Delivery Note","Stock Entry","Payment Entry","Journal Entry","Material Request","Lead","Quotation","Asset"]:
    st,j=apicall("frappe.desk.reportview.get", {"doctype":dt,"fields":'["name"]',"limit_page_length":5})
    if st==200:
        msg="ok:"+str(len(j.get("message",[]))); exc=""
    else:
        msg=j.get("exc_type","?"); exc=j.get("exc",j.get("exception",""))[-300:]
    results.append((f"list {dt}", st, msg, exc))

print(f"\n{'TEST':52} {'HTTP':5} RESULT")
print("-"*90)
for name,st,msg,exc in results:
    flag = "" if (st==200) else "  <-- FAIL"
    print(f"{name:52} {str(st):5} {msg}{flag}")
    if exc: print("     ", exc.replace("\n"," ")[:200])
