"""Deploy the inventory map using authenticated Frappe REST APIs.

Set ERPNEXT_URL, ERPNEXT_USER and ERPNEXT_PASSWORD. No SSH or restart required.
Only the feature's own Server Script, Web Page, Client Scripts and Stock
workspace shortcut are changed. Before-images are saved for rollback.
"""
import argparse
import ast
from datetime import datetime
import json
import os
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "inventory_relationship_map"
SCRIPT_NAME = "Inventory Relationship Map API"
PAGE_NAME = "inventory-relationship-map"
FORM_TYPES = ["Item", "Warehouse", "Stock Entry", "Stock Reconciliation", "Purchase Receipt",
              "Delivery Note", "Purchase Invoice", "Sales Invoice", "POS Invoice"]


def server_script():
    source = (ASSETS / "api.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build_map")
    return ast.get_source_segment(source, function) + '\n\nfrappe.response["message"] = build_map(frappe.form_dict)\n'


def client_script(doctype):
    return """frappe.ui.form.on(%s, {
    refresh(frm) {
        if (frm.is_new()) return;
        frm.add_custom_button(__('Inventory Relationship Map'), () => {
            const params = new URLSearchParams();
            if (frm.doctype === 'Item') params.set('item_code', frm.doc.name);
            else if (frm.doctype === 'Warehouse') params.set('warehouse', frm.doc.name);
            else { params.set('doctype', frm.doctype); params.set('docname', frm.doc.name); }
            if (frm.doc.company) params.set('company', frm.doc.company);
            window.open('/inventory-relationship-map?' + params.toString(), '_blank', 'noopener');
        }, __('View'));
    }
});""" % json.dumps(doctype)


class Deployment:
    def __init__(self):
        self.base = os.environ.get("ERPNEXT_URL", "http://38.247.138.224:10017").rstrip("/")
        self.session = requests.Session()
        self.session.post(self.base + "/api/method/login", data={
            "usr": os.environ.get("ERPNEXT_USER", "Administrator"),
            "pwd": os.environ["ERPNEXT_PASSWORD"]}, timeout=30).raise_for_status()
        self.backup = ROOT / "backups" / ("inventory_map_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.before = []

    def get(self, dt, name):
        response = self.session.get(self.base + "/api/resource/" + quote(dt, safe="") + "/" + quote(name, safe=""), timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()["data"]

    def upsert(self, dt, name, fields):
        old = self.get(dt, name)
        self.backup.mkdir(parents=True, exist_ok=True)
        self.before.append({"doctype": dt, "name": name, "document": old,
                            "updated_fields": list(fields)})
        (self.backup / "before.json").write_text(json.dumps(self.before, indent=2), encoding="utf-8")
        endpoint = self.base + "/api/resource/" + quote(dt, safe="")
        if old:
            response = self.session.put(endpoint + "/" + quote(name, safe=""), json=fields, timeout=45)
        else:
            response = self.session.post(endpoint, json={"doctype": dt, "name": name, **fields}, timeout=45)
        if not response.ok:
            print(response.text[:2500])
        response.raise_for_status()
        saved = self.get(dt, name)
        for field, value in fields.items():
            if isinstance(value, (str, int)):
                assert saved.get(field) == value, (dt, name, field)
        print("Verified:", dt, name, flush=True)

    def deploy(self):
        self.upsert("Server Script", SCRIPT_NAME, {"script_type": "API", "api_method": "inventory_relationship_map",
            "allow_guest": 0, "disabled": 0, "script": server_script()})
        # Run the read-only API before publishing any navigation or UI.
        response = self.session.get(self.base + "/api/method/inventory_relationship_map", timeout=60)
        if not response.ok:
            print(response.text[:4000])
        response.raise_for_status()
        result = response.json()["message"]
        assert "movements" in result and "balances" in result
        print("API smoke test:", len(result["movements"]), "ledger entries", flush=True)
        self.upsert("Web Page", PAGE_NAME, {"title": "Inventory Relationship Map", "route": PAGE_NAME,
            "published": 1, "content_type": "HTML", "full_width": 1, "show_title": 0,
            "main_section_html": (ASSETS / "page.html").read_text(encoding="utf-8"),
            "css": (ASSETS / "page.css").read_text(encoding="utf-8"),
            "javascript": (ASSETS / "page.js").read_text(encoding="utf-8"),
            "context_script": "context.no_cache = 1\n"})
        for dt in FORM_TYPES:
            self.upsert("Client Script", "Inventory Relationship Map - " + dt,
                {"dt": dt, "view": "Form", "enabled": 1, "script": client_script(dt)})
        stock = self.get("Workspace", "Stock")
        shortcuts = stock.get("shortcuts") or []
        shortcuts = [s for s in shortcuts if s.get("label") != "Inventory Relationship Map"]
        shortcuts.append({"type": "URL", "label": "Inventory Relationship Map", "url": "/" + PAGE_NAME, "color": "Green"})
        content = json.loads(stock.get("content") or "[]")
        if not any(b.get("data", {}).get("shortcut_name") == "Inventory Relationship Map" for b in content):
            content.insert(0, {"id": "inventory-map-shortcut", "type": "shortcut",
                "data": {"shortcut_name": "Inventory Relationship Map", "col": 3}})
        self.upsert("Workspace", "Stock", {"shortcuts": shortcuts, "content": json.dumps(content)})
        (self.backup / "verification.json").write_text(json.dumps({"url": self.base + "/" + PAGE_NAME,
            "item": result.get("item"), "ledger_entries": len(result["movements"]),
            "deployed_records": len(self.before)}, indent=2), encoding="utf-8")
        print("Backup:", self.backup)
        print("Live:", self.base + "/" + PAGE_NAME)

    def rollback(self, path):
        records = json.loads(Path(path).read_text(encoding="utf-8"))
        for record in reversed(records):
            dt, name, old = record["doctype"], record["name"], record["document"]
            endpoint = self.base + "/api/resource/" + quote(dt, safe="") + "/" + quote(name, safe="")
            if old:
                response = self.session.put(endpoint, json={k: old.get(k) for k in record["updated_fields"]}, timeout=45)
            else:
                response = self.session.delete(endpoint, timeout=45)
            if response.status_code != 404:
                response.raise_for_status()
            print("Restored:", dt, name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollback", help="Path to a deployment's before.json")
    args = parser.parse_args()
    deployment = Deployment()
    if args.rollback:
        deployment.rollback(args.rollback)
    else:
        deployment.deploy()
