import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def login(usr="Administrator", pwd="admin"):
    login_h = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    with op.open(
        urllib.request.Request(
            BASE + "/api/method/login",
            data=f"usr={usr}&pwd={pwd}".encode(),
            headers=login_h,
            method="POST",
        ),
        timeout=30,
    ) as r:
        pass

def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=H, method=method)
    with op.open(req, timeout=60) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw.strip() else {}

login()

# Let's inspect column data type
script_check = """
try:
    frappe.db.sql('''
        CREATE OR REPLACE FUNCTION pg_catalog.smallint(boolean)
        RETURNS smallint AS $$
            SELECT CASE WHEN $1 THEN 1::smallint ELSE 0::smallint END;
        $$ LANGUAGE SQL IMMUTABLE STRICT;
    ''')
    frappe.db.sql('''
        CREATE CAST (boolean AS smallint)
        WITH FUNCTION pg_catalog.smallint(boolean)
        AS IMPLICIT;
    ''')
    frappe.db.commit()
    frappe.response["message"] = "Cast created successfully"
except Exception as e:
    frappe.response["message"] = str(e)
"""
call(f"/api/resource/Server%20Script/{urllib.parse.quote('VM Test Partial Payment Flow')}", "PUT", {"script": script_check, "disabled": 0})
print("Cast result:", call("/api/method/vm_test_partial_payment_flow", "POST", {}))


