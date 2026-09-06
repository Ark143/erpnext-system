import requests, json

s = requests.Session()
s.post('http://38.247.138.224:10017/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

cust_meta = s.get('http://38.247.138.224:10017/api/method/frappe.desk.form.load.getdoctype?doctype=Customer').json()
fields = cust_meta.get('docs', [{}])[0].get('fields', [])
for f in fields:
    if f.get('fieldtype') == 'Table':
        print(f"Customer Table Field: {f['fieldname']} -> Options: {f['options']}")

supp_meta = s.get('http://38.247.138.224:10017/api/method/frappe.desk.form.load.getdoctype?doctype=Supplier').json()
s_fields = supp_meta.get('docs', [{}])[0].get('fields', [])
for f in s_fields:
    if f.get('fieldtype') == 'Table':
        print(f"Supplier Table Field: {f['fieldname']} -> Options: {f['options']}")
