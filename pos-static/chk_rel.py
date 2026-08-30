import frappe, re, os
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()
# Website Settings logo/favicon
ws=frappe.get_single("Website Settings")
for f in ["app_logo","favicon"]:
    v=getattr(ws,f,None)
    if v: print("WebsiteSettings",f,"->",v, "(relative?)" if not str(v).startswith("/") else "")
# scan navbar + base templates for relative ultra_mrf (no leading /)
hits=[]
for root,_,files in os.walk("/workspace/frappe-bench/apps/frappe/frappe/templates"):
    for fn in files:
        if fn.endswith((".html",".js")):
            t=open(os.path.join(root,fn),encoding="utf-8",errors="ignore").read()
            for m in re.findall(r'(?:src|href)=["\x27](?!/{0,2}|https?://)[^"\x27]*ultra_mrf[^"\x27]*', t):
                hits.append((fn,m))
print("relative ultra_mrf refs in frappe templates:", hits or "NONE")
print("favicon.ico exists:", os.path.exists("/workspace/frappe-bench/sites/site1.local/public/files/favicon.ico"))
