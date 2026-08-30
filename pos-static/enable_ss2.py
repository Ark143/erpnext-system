F = "/workspace/frappe-bench/sites/common_site_config.json"
import json
d = json.loads(open(F).read())
# wrong key removed, correct key set
d.pop("enable_server_scripts", None)
d["server_script_enabled"] = True
open(F,"w").write(json.dumps(d, indent=2))
print("server_script_enabled:", d.get("server_script_enabled"))
