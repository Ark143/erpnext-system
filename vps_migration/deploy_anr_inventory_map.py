"""Deploy warehouse-based inventory traceability to ANR using env credentials."""
import json
from pathlib import Path
import deploy_inventory_relationship_map as base

base.ASSETS = Path(__file__).resolve().parent / "anr_inventory_relationship_map"
base.FORM_TYPES = [dt for dt in base.FORM_TYPES if dt != "Bin Location"]

class ANRDeployment(base.Deployment):
    def upsert(self, dt, name, fields):
        if dt == "Workspace" and name == "Stock":
            for shortcut in fields.get("shortcuts", []):
                if shortcut.get("type") == "Report" and shortcut.get("link_to") == "Global Stock Balance":
                    if not self.get("Report", "Global Stock Balance"):
                        assert self.get("Report", "Stock Balance")
                        shortcut["link_to"] = "Stock Balance"
        return super().upsert(dt, name, fields)

if __name__ == "__main__":
    deployment = ANRDeployment()
    deployment.deploy()
    home = deployment.get("Workspace", "Home")
    label = "Inventory Relationship Map"
    shortcuts = [s for s in home.get("shortcuts", []) if s.get("label") != label]
    shortcuts.append({"type": "URL", "label": label, "url": "/inventory-relationship-map", "color": "Green"})
    content = json.loads(home.get("content") or "[]")
    if not any(b.get("data", {}).get("shortcut_name") == label for b in content):
        content.insert(0, {"id": "inventory-map-shortcut", "type": "shortcut", "data": {"shortcut_name": label, "col": 3}})
    deployment.upsert("Workspace", "Home", {"shortcuts": shortcuts, "content": json.dumps(content)})
