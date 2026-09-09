import urllib.request
import urllib.parse
import json
import http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

sql_script = '''
def run_pg_cast():
    # 1. Check if integer to boolean cast can be created
    queries = [
        """
        CREATE OR REPLACE FUNCTION pg_catalog.int_to_bool(integer) 
        RETURNS boolean AS $$ 
            SELECT $1 != 0; 
        $$ LANGUAGE sql STRICT IMMUTABLE;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_cast 
                WHERE castsource = 'integer'::regtype 
                  AND casttarget = 'boolean'::regtype 
                  AND castcontext = 'i'
            ) THEN
                CREATE CAST (integer AS boolean) WITH FUNCTION pg_catalog.int_to_bool(integer) AS IMPLICIT;
            END IF;
        END $$;
        """,
        """
        CREATE OR REPLACE FUNCTION pg_catalog.int2_to_bool(smallint) 
        RETURNS boolean AS $$ 
            SELECT $1 != 0; 
        $$ LANGUAGE sql STRICT IMMUTABLE;
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_cast 
                WHERE castsource = 'smallint'::regtype 
                  AND casttarget = 'boolean'::regtype 
                  AND castcontext = 'i'
            ) THEN
                CREATE CAST (smallint AS boolean) WITH FUNCTION pg_catalog.int2_to_bool(smallint) AS IMPLICIT;
            END IF;
        END $$;
        """
    ]
    
    results = []
    for q in queries:
        try:
            frappe.db.sql(q)
            frappe.db.commit()
            results.append("OK")
        except Exception as e:
            results.append("Err: " + str(e))
            
    # Test query that failed earlier:
    test_res = frappe.db.sql("SELECT CASE WHEN 0 THEN 'TRUE' ELSE 'FALSE' END AS t1, CASE WHEN 1 THEN 'TRUE' ELSE 'FALSE' END AS t2", as_dict=True)
    frappe.response["message"] = {"status": "success", "results": results, "test_query": test_res}

run_pg_cast()
'''

server_script_payload = {
    'doctype': 'Server Script',
    'name': 'VM PG Implicit Cast',
    'script_type': 'API',
    'api_method': 'vm_pg_implicit_cast',
    'allow_guest': 1,
    'disabled': 0,
    'script': sql_script
}

try:
    check = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Server%20Script/VM%20PG%20Implicit%20Cast', headers=H))
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20PG%20Implicit%20Cast',
        data=urllib.parse.urlencode({'data': json.dumps(server_script_payload)}).encode(),
        headers=H
    )
    req.get_method = lambda: 'PUT'
    op.open(req)
except Exception:
    req = urllib.request.Request(
        'http://38.247.138.224:10017/api/resource/Server%20Script',
        data=urllib.parse.urlencode({'data': json.dumps(server_script_payload)}).encode(),
        headers=H
    )
    op.open(req)

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_pg_implicit_cast', headers=H))
print("Cast setup response:", r_call.read().decode())
