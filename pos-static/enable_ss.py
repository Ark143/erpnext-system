F = "/workspace/frappe-bench/sites/common_site_config.json"
import json
t = open(F).read()
d = json.loads(t)
d["enable_server_scripts"] = True
open(F,"w").write(json.dumps(d, indent=2))
print("enable_server_scripts set:", d.get("enable_server_scripts"))
