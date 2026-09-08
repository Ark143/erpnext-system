import os
import shutil
import glob
import json

# Ensure target directories exist
target_dirs = [
    "frappe-bench/apps/erpnext/erpnext/accounts/doctype",
    "docs/bir_module"
]

for d in target_dirs:
    os.makedirs(d, exist_ok=True)

# Copy all DocTypes into vehicle_management or accounts doctypes
doctype_files = glob.glob("tools/bir_export/doctypes/*.json")
for df in doctype_files:
    dt_basename = os.path.splitext(os.path.basename(df))[0]
    folder_name = dt_basename.lower()
    dest_dir = os.path.join("frappe-bench/apps/erpnext/erpnext/accounts/doctype", folder_name)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(df, os.path.join(dest_dir, f"{folder_name}.json"))
    print(f"Synced DocType schema -> {dest_dir}/{folder_name}.json")

print("\nAll BIR DocTypes synced into local repo frappe-bench/apps/erpnext!")
