import psycopg2
conn = psycopg2.connect(dbname="site1_local", user="postgres")
cur = conn.cursor()
cur.execute("""SELECT main_section FROM "tabWeb Page" WHERE route='executive-ultra-mrf'""")
s = cur.fetchone()[0]
print("len", len(s))
i = s.find("<script>")
print("script_at", i)
print(s[i:i+800])
for kw in ["make_control", "set_route", "frappe.ready", "frappe.call", "frappe.ui", "DOMContentLoaded"]:
    print(kw, "->", s.count(kw))
