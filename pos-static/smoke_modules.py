import urllib.request, urllib.parse, json, http.cookiejar, traceback
URL="http://localhost"
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H={"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
def apicall(method, args=None, data=None):
    try:
        if data is not None:
            req=urllib.request.Request(URL+"/api/method/"+method, data=urllib.parse.urlencode(data).encode(), headers=H)
        else:
            p=urllib.parse.urlencode({"args":json.dumps(args or {})})
            req=urllib.request.Request(URL+"/api/method/"+method+"?"+p, headers=H)
        r=op.open(req, timeout=40)
        j=json.loads(r.read())
        return r.status, j
    except urllib.error.HTTPError as e:
        try: bd=json.loads(e.read())
        except: bd={}
        return e.code, bd
    except Exception as e:
        return "ERR", {"exc_type":type(e).__name__,"msg":str(e)[:120]}

# login as admin
op.open(urllib.request.Request(URL+"/api/method/login", data=urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode(), headers=H), timeout=30)

results=[]
# 1) Link searches using erpnext custom query functions (the MySQL-syntax ones)
search_tests = [
    ("Customer", "Sales Order Customer", "erpnext.controllers.queries.customer_query", {}),
    ("Supplier", "Purchase Order Supplier", "erpnext.controllers.queries.supplier_query", {}),
    ("Item", "Sales Order Item", "erpnext.controllers.queries.item_query", {"is_sales_item":1,"has_variants":0}),
    ("Item", "Purchase Order Item", "erpnext.controllers.queries.item_query", {"is_purchase_item":1,"has_variants":0}),
    ("Warehouse", "Stock Entry Warehouse", None, {}),
    ("Account", "GL Entry Account", "erpnext.controllers.queries.ledger_account_query", {}),
    ("BOM", "BOM Item", None, {}),
    ("Sales Order", None, None, {}),
    ("Purchase Order", None, None, {}),
    ("Employee", None, None, {}),
    ("Customer Group", None, None, {}),
]
for dt, ref, query, filt in search_tests:
    args={"txt":"","doctype":dt,"page_length":"10","link_fieldname":dt.lower().replace(" ","_")}
    if ref: args["reference_doctype"]=ref
    if query: args["query"]=query
    if filt: args["filters"]=json.dumps(filt)
    st,j=apicall("frappe.desk.search.search_link", args)
    msg=j.get("exc_type") or ("ok:"+str(len(j.get("message",[]))))
    results.append((f"search {dt}"+(f" [{query.split('.')[-1]}]" if query else ""), st, msg))

# 2) Module key reports / get_list
for dt in ["Sales Invoice","Purchase Invoice","Delivery Note","Purchase Receipt","Stock Entry","Payment Entry","Journal Entry","Material Request","Lead","Opportunity","Quotation","Purchase Request","Asset"]:
    st,j=apicall("frappe.desk.reportview.get", {"doctype":dt,"fields":'["name"]',"limit_page_length":5,"order_by":"modified desc"})
    msg=j.get("exc_type") or ("ok:"+str(len(j.get("message",[]))))
    results.append((f"list {dt}", st, msg))

print(f"{'TEST':55} {'HTTP':5} RESULT")
print("-"*100)
for name,st,msg in results:
    flag = "" if (st==200 or (isinstance(st,int) and st<400)) else "  <-- FAIL"
    print(f"{name:55} {str(st):5} {msg}{flag}")
