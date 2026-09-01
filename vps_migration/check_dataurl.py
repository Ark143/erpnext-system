#!/usr/bin/env python3
import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")
i = html.find("href=")
# find the data url insertion
i2 = html.find("data:image/png;base64,")
print("data url at", i2)
if i2 >= 0:
    print(repr(html[i2-120:i2+120]))
    print("...")
    # check the end of the data url and following chars
    # find the closing of the href value
    end = html.find('"', i2)
    print("closing quote found at", end, repr(html[i2+9000:i2+9200]))
