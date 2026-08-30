import frappe, json

base="/workspace/frappe-bench/apps/vehicle_management/vehicle_management/www/"
html=open(base+"pos_terminal.html").read()
libs=open(base+"jsqr.min.js").read()+"\n"+open(base+"qrcode.min.js").read()
html=html.replace('<script id="vpos-libs"></script>', '<script id="vpos-libs">'+libs+'</script>')

# --- responsive hardening: prevent select/branch horizontal overflow on phone ---
anchor='.vpos-stock-toggle { flex: 0 0 auto; height: 42px; font-size: 11.5px; padding: 0 10px; }'
add='\n  .vpos-branch { min-width: 0; }\n  .vpos-branch select { min-width: 0; width: 100%; }\n  .vpos-main { overflow-x: hidden; }\n  .vpos-bar { width: 100%; }\n'
assert anchor in html, "anchor missing"
html=html.replace(anchor, anchor+add, 1)

open(base+"pos_terminal.html","w").write(html)
print("source hardened + libs inlined, bytes:", len(html), "| has mobile-cart-bar:", "vpos-mobile-cart-bar" in html, "| has 768 block:", "@media (max-width: 768px)" in html)

# --- deploy to Web Page on served sites ---
sites_path="/workspace/frappe-bench/sites"
deployed=[]
for site in ["erp.localhost","site1.local"]:
    try:
        frappe.init(site=site, sites_path=sites_path)
        frappe.connect(); frappe.set_user("Administrator")
        name=frappe.db.get_value("Web Page", {"name":"vehicle-pos-terminal"}, "name")
        if name:
            frappe.db.set_value("Web Page","vehicle-pos-terminal","main_section_html",html)
            frappe.db.set_value("Web Page","vehicle-pos-terminal","published",1)
            frappe.db.commit()
            deployed.append(site)
            print("deployed to", site)
        else:
            print("Web Page not found in", site)
    except Exception as e:
        print("skip", site, "->", str(e)[:80])
print("DEPLOYED_SITES:", deployed)
