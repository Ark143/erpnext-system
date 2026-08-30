import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
fname = "ultra_mrf_logo.png"
url = "/files/" + fname
# avoid duplicate
if frappe.db.exists("File", {"file_url": url}):
    print("File record already exists:", frappe.db.get_value("File", {"file_url": url}, "name"))
else:
    doc = frappe.get_doc({
        "doctype": "File",
        "file_name": fname,
        "file_url": url,
        "is_private": 0,
        "is_public": 1,
        "attached_to_doctype": None,
        "attached_to_name": None,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Created File record:", doc.name, "->", doc.file_url)
# verify physical file present
import os
phys = "/workspace/frappe-bench/sites/site1.local/public/files/" + fname
print("physical file exists:", os.path.exists(phys), "size:", os.path.getsize(phys) if os.path.exists(phys) else 0)
