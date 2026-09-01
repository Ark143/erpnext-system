#!/usr/bin/env python3
import frappe, base64
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

logo_path = "/workspace/frappe-bench/sites/site1.local/public/files/ultra_mrf_logo.png"
logo_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
DATA = "data:image/png;base64," + logo_b64

# The broken insertion (from my earlier bad patch) — find and fix it.
# Current broken form (single-quote JS string that my repr() shattered):
#   '<image x="8" y="4" width="24" height="24" href='data:image/png;base64,....' preserveAspectRatio="xMidYMid meet"/>'+
# Fix: replace the whole bad segment with a correct single JS string using double-quoted attribute.
import re
# locate the bad segment
start = html.find("<image x=\"8\" y=\"4\" width=\"24\" height=\"24\" href=")
if start == -1:
    print("image tag not found")
else:
    # find the end: preserveAspectRatio meet"/>
    end_marker = 'preserveAspectRatio="xMidYMid meet"/>'
    end = html.find(end_marker, start)
    print("bad segment start", start, "end", end)
    # replace from start to end+len(end_marker) with correct string
    good = '<image x="8" y="4" width="24" height="24" href="' + DATA + '" preserveAspectRatio="xMidYMid meet"/>'
    html = html[:start] + good + html[end+len(end_marker):]
    print("replaced. new segment head:", repr(html[start:start+80]))

frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
frappe.db.commit()
print("committed. len", len(html))
