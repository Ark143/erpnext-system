import os, sys

bench_dir = os.path.abspath(os.path.dirname(__file__))
sites_dir = os.path.join(bench_dir, "sites")
assets_dir = os.path.join(sites_dir, "assets")

os.makedirs(assets_dir, exist_ok=True)
for sub in ["js", "css"]:
    os.makedirs(os.path.join(assets_dir, sub), exist_ok=True)

apps = [
    ("frappe", "apps/frappe/frappe/public"),
    ("erpnext", "apps/erpnext/erpnext/public"),
    ("vehicle_management", "apps/vehicle_management/vehicle_management/public"),
]

for app_name, rel_target in apps:
    link_path = os.path.join(assets_dir, app_name)
    # relative target from assets_dir is ../../rel_target
    target = os.path.join("..", "..", rel_target)
    
    if os.path.islink(link_path) or os.path.exists(link_path):
        try:
            os.remove(link_path)
        except Exception:
            try:
                os.unlink(link_path)
            except Exception:
                pass
    
    try:
        os.symlink(target, link_path)
        print(f"Linked {link_path} -> {target}")
    except Exception as e:
        print(f"Error linking {app_name}: {e}")

print("\n--- Current assets directory contents ---")
for item in sorted(os.listdir(assets_dir)):
    p = os.path.join(assets_dir, item)
    is_link = os.path.islink(p)
    target = os.readlink(p) if is_link else ""
    exists = os.path.exists(p)
    print(f"  {item:20s} | is_link: {str(is_link):5s} | exists: {str(exists):5s} | target: {target}")
