import requests

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

# 1. Purchase Invoice
url_pi = f"{BASE}/printview?doctype=Purchase%20Invoice&name=ACC-PINV-2026-00188&format=BIR%202307%20-%20Purchase%20Invoice&no_letterhead=1&_lang=en"
res_pi = s.get(url_pi)
print(f"PI Printview Status: {res_pi.status_code}, Length: {len(res_pi.text)}, Contains BIR 2307: {'bir-2307-container' in res_pi.text}")

# 2. Sales Invoice
url_si = f"{BASE}/printview?doctype=Sales%20Invoice&name=ACC-SINV-2026-00451&format=BIR%202307%20-%20Sales%20Invoice&no_letterhead=1&_lang=en"
res_si = s.get(url_si)
print(f"SI Printview Status: {res_si.status_code}, Length: {len(res_si.text)}, Contains BIR 2307: {'bir-2307-container' in res_si.text}")

# 3. Test PDF download endpoint for both
pdf_pi = s.get(f"{BASE}/api/method/frappe.utils.print_format.download_pdf?doctype=Purchase%20Invoice&name=ACC-PINV-2026-00188&format=BIR%202307%20-%20Purchase%20Invoice&no_letterhead=1")
print(f"PI PDF Download Status: {pdf_pi.status_code}, Length: {len(pdf_pi.content)}, PDF header: {pdf_pi.content.startswith(b'%PDF')}")

pdf_si = s.get(f"{BASE}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name=ACC-SINV-2026-00451&format=BIR%202307%20-%20Sales%20Invoice&no_letterhead=1")
print(f"SI PDF Download Status: {pdf_si.status_code}, Length: {len(pdf_si.content)}, PDF header: {pdf_si.content.startswith(b'%PDF')}")

