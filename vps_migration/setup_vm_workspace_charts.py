import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def save_doc(doctype, name, doc_data):
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}', headers=H))
        print(f"Updating {doctype} '{name}'...")
        req = urllib.request.Request(
            f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}',
            data=urllib.parse.urlencode({'data': json.dumps(doc_data)}).encode(),
            headers=H
        )
        req.get_method = lambda: 'PUT'
        op.open(req)
        print(f"Updated {doctype} '{name}'.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Creating {doctype} '{name}'...")
            payload = dict(doc_data)
            payload['name'] = name
            payload['doctype'] = doctype
            req = urllib.request.Request(
                f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}',
                data=urllib.parse.urlencode({'data': json.dumps(payload)}).encode(),
                headers=H
            )
            op.open(req)
            print(f"Created {doctype} '{name}'.")
        else:
            print(f"Error {e.code}: {e.read().decode()}")
            raise

# 1. Number Card: Total Registered Vehicles
save_doc("Number Card", "Total Registered Vehicles", {
    "label": "Total Registered Vehicles",
    "type": "Document Type",
    "function": "Count",
    "document_type": "Customer Vehicle",
    "is_public": 1,
    "color": "#16a34a",
    "module": "Vehicle Management",
    "show_percentage_stats": 1,
    "stats_time_interval": "Daily"
})

# 2. Number Card: Vehicle POS Invoices
save_doc("Number Card", "Vehicle POS Invoices Count", {
    "label": "Vehicle POS Invoices Count",
    "type": "Document Type",
    "function": "Count",
    "document_type": "Vehicle POS Invoice",
    "is_public": 1,
    "color": "#9333ea",
    "module": "Vehicle Management",
    "show_percentage_stats": 1,
    "stats_time_interval": "Daily"
})

# 3. Dashboard Chart: Vehicle POS Sales by Company
save_doc("Dashboard Chart", "Vehicle POS Sales by Company", {
    "chart_name": "Vehicle POS Sales by Company",
    "chart_type": "Group By",
    "document_type": "Vehicle POS Invoice",
    "group_by_type": "Sum",
    "group_by_based_on": "company",
    "aggregate_function_based_on": "total_amount",
    "type": "Bar",
    "is_public": 1,
    "currency": "PHP",
    "module": "Vehicle Management",
    "timespan": "Last Year",
    "time_interval": "Monthly",
    "filters_json": "[]"
})

# 4. Dashboard Chart: Customer Vehicles by Make
save_doc("Dashboard Chart", "Customer Vehicles by Make", {
    "chart_name": "Customer Vehicles by Make",
    "chart_type": "Group By",
    "document_type": "Customer Vehicle",
    "group_by_type": "Count",
    "group_by_based_on": "make",
    "aggregate_function_based_on": "name",
    "number_of_groups": 7,
    "type": "Donut",
    "is_public": 1,
    "module": "Vehicle Management",
    "filters_json": "[]"
})

# 5. Dashboard Chart: Vehicle Job Orders by Status
save_doc("Dashboard Chart", "Vehicle Job Orders by Status", {
    "chart_name": "Vehicle Job Orders by Status",
    "chart_type": "Group By",
    "document_type": "Vehicle Job Order",
    "group_by_type": "Count",
    "group_by_based_on": "status",
    "aggregate_function_based_on": "name",
    "type": "Percentage",
    "is_public": 1,
    "module": "Vehicle Management",
    "filters_json": "[]"
})

print("Successfully ensured all Number Cards and Dashboard Charts for Vehicle Management!")
