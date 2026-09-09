import requests
import json

BASE_URL = 'http://38.247.138.224:10017'
session = requests.Session()
session.post(f'{BASE_URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Let's test calling SQL via a simple Server Script that returns error details if any
script_content = """
def run_fix():
    errs = []
    
    # 1. Function 1
    try:
        frappe.db.sql('''
            CREATE OR REPLACE FUNCTION public.int_to_bool(integer) 
            RETURNS boolean AS $$ 
                SELECT ($1 IS NOT NULL AND $1 != 0); 
            $$ LANGUAGE sql STRICT IMMUTABLE;
        ''')
        frappe.db.commit()
    except Exception as e:
        errs.append("fn1: " + str(e))
        
    # 2. Cast 1
    try:
        frappe.db.sql('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_cast 
                    WHERE castsource = 'integer'::regtype 
                      AND casttarget = 'boolean'::regtype
                ) THEN
                    CREATE CAST (integer AS boolean) WITH FUNCTION public.int_to_bool(integer) AS IMPLICIT;
                END IF;
            END $$;
        ''')
        frappe.db.commit()
    except Exception as e:
        errs.append("cast1: " + str(e))

    # 3. Function 2 (smallint)
    try:
        frappe.db.sql('''
            CREATE OR REPLACE FUNCTION public.int2_to_bool(smallint) 
            RETURNS boolean AS $$ 
                SELECT ($1 IS NOT NULL AND $1 != 0); 
            $$ LANGUAGE sql STRICT IMMUTABLE;
        ''')
        frappe.db.commit()
    except Exception as e:
        errs.append("fn2: " + str(e))

    # 4. Cast 2
    try:
        frappe.db.sql('''
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_cast 
                    WHERE castsource = 'smallint'::regtype 
                      AND casttarget = 'boolean'::regtype
                ) THEN
                    CREATE CAST (smallint AS boolean) WITH FUNCTION public.int2_to_bool(smallint) AS IMPLICIT;
                END IF;
            END $$;
        ''')
        frappe.db.commit()
    except Exception as e:
        errs.append("cast2: " + str(e))

    # Test query:
    try:
        t = frappe.db.sql("SELECT CASE WHEN 0 THEN 'TRUE' ELSE 'FALSE' END AS t0, CASE WHEN 1 THEN 'TRUE' ELSE 'FALSE' END AS t1", as_dict=True)
        frappe.response["message"] = {"status": "success", "errs": errs, "test": t}
    except Exception as e:
        frappe.response["message"] = {"status": "error", "errs": errs, "test_err": str(e)}

run_fix()
"""

# Update Server Script
r = session.put(
    f"{BASE_URL}/api/resource/Server%20Script/VM%20PG%20Implicit%20Cast",
    json={
        'doctype': 'Server Script',
        'name': 'VM PG Implicit Cast',
        'script_type': 'API',
        'api_method': 'vm_pg_implicit_cast',
        'allow_guest': 1,
        'disabled': 0,
        'script': script_content
    }
)
print("Updated Server Script status:", r.status_code)

res = session.get(f"{BASE_URL}/api/method/vm_pg_implicit_cast")
print("API Result:", res.status_code, res.text)
