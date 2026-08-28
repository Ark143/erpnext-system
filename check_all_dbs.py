import psycopg2

conn = psycopg2.connect(host='127.0.0.1', port=55433, user='postgres', password='admin', dbname='testdb')
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name ILIKE '%company%' LIMIT 10;")
print("Company tables in testdb:", cur.fetchall())

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name ILIKE '%vehicle%' LIMIT 10;")
print("Vehicle tables in testdb:", cur.fetchall())

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name ILIKE '%order%' LIMIT 10;")
print("Order tables in testdb:", cur.fetchall())
