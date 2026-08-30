F = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/hooks.py"
t = open(F).read()
if "app_icon" not in t:
    t = t.replace(
        'app_name = "vehicle_management"\napp_title = "Vehicle Management"',
        'app_name = "vehicle_management"\napp_title = "Vehicle Management"\napp_icon = "fa fa-car"',
        1)
    open(F,"w").write(t)
    print("app_icon added")
else:
    print("app_icon already present")
# show result
for line in t.splitlines()[:4]:
    print(line)
