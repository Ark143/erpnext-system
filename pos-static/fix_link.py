import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()

# Also fix the broken window.open in the Web Page main_section_html
d = frappe.get_doc("Web Page", "vehicle-pos-terminal")
v = d.main_section_html or ""
old = 'window.open("/desk#Form/POS Invoice/"+r.pos_invoice,"_blank")'
new = 'window.open("/desk#Form/Vehicle POS Invoice/"+r.name,"_blank")'
if old in v:
    v = v.replace(old, new, 1)
    frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", v)
    frappe.db.commit()
    print("fixed window.open link:", new in v)
elif new in v:
    print("already fixed")
else:
    print("OLD LINK NOT FOUND in page; current snippet:")
    i = v.find("window.open")
    print(v[i-20:i+120] if i >= 0 else "no window.open at all")
