import urllib.request, urllib.parse, json, http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest','Accept':'application/json'}
data = urllib.parse.urlencode({'cmd':'login','usr':'administrator','pwd':'admin'}).encode()
op.open(urllib.request.Request(URL+'/api/method/login', data=data, headers=H), timeout=30)

def get_doc(doctype, name):
    try:
        res = op.open(urllib.request.Request(f"{URL}/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}", headers=H))
        return json.loads(res.read().decode()).get('data', {})
    except Exception as e:
        return {"error": str(e)}

charts_to_check = [
    "VM Job Orders by Company",
    "Vehicle POS Sales by Company",
    "Customer Vehicles by Make",
    "Vehicle Job Orders by Status",
    "Purchase Order Trends",
    "Top Suppliers",
    "Purchase Receipt Trends",
    "Incoming Bills (Purchase Invoice)",
    "Warehouse wise Stock Value",
    "Stock Value by Item Group",
    "Item Shortage Summary",
    "Delivery Trends",
    "Sales Order Trends",
    "Outgoing Bills (Sales Invoice)",
    "Item-wise Annual Sales",
    "Top Customers",
    "Profit and Loss",
    "Job Card Analysis"
]

for c in charts_to_check:
    doc = get_doc("Dashboard Chart", c)
    if "error" in doc:
        print(f"Chart '{c}': NOT FOUND or ERROR: {doc['error']}")
    else:
        print(f"Chart '{c}': OK (type: {doc.get('chart_type')}, doctype: {doc.get('document_type')})")
