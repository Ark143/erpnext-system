import frappe, os
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
# Where does frappe resolve the public folder for this site?
print("sites_path:", frappe.local.sites_path if hasattr(frappe.local, "sites_path") else "?")
site_path = frappe.get_site_path()
print("site_path:", site_path)
pub = os.path.join(site_path, "public")
print("public dir:", pub, "exists:", os.path.isdir(pub))
files_dir = os.path.join(pub, "files")
print("public/files:", files_dir, "exists:", os.path.isdir(files_dir))
logo = os.path.join(files_dir, "ultra_mrf_logo.png")
print("logo exists:", os.path.exists(logo), "size:", os.path.getsize(logo) if os.path.exists(logo) else 0)
# list whats in public
print("public contents:", os.listdir(pub) if os.path.isdir(pub) else "NO PUBLIC DIR")
# shared_data config from common_site_config? Actually frappe serves /files from site public
# Check frappe's static mapping config
import json
csc = frappe.read_file(os.path.join(frappe.local.sites_path, "common_site_config.json"))
print("common_site_config shared_data? keys:", list(json.loads(csc).keys()))
