"""Read-only checks against the deployed API and independent REST ledger reads.

Run with ERPNEXT_PASSWORD set. No stock documents or user accounts are created.
"""
import json
import os
import unittest

import requests


class LiveInventoryMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = os.environ.get("ERPNEXT_URL", "http://38.247.138.224:10017").rstrip("/")
        cls.s = requests.Session()
        cls.s.post(cls.base + "/api/method/login", data={
            "usr": os.environ.get("ERPNEXT_USER", "Administrator"),
            "pwd": os.environ["ERPNEXT_PASSWORD"]}, timeout=30).raise_for_status()
        entries = cls.resource("Stock Ledger Entry", ["item_code", "warehouse", "company", "voucher_type", "voucher_no"], {"is_cancelled": 0})
        cls.seed = next((e for e in entries if e["voucher_type"] == "Purchase Receipt"), entries[0])

    @classmethod
    def resource(cls, dt, fields, filters):
        response = cls.s.get(cls.base + "/api/resource/" + dt,
            params={"fields": json.dumps(fields), "filters": json.dumps(filters), "limit_page_length": 1000}, timeout=45)
        response.raise_for_status()
        return response.json()["data"]

    def call(self, **params):
        response = self.s.get(self.base + "/api/method/inventory_relationship_map", params=params, timeout=60)
        self.assertEqual(response.status_code, 200, response.text[:1800])
        result = response.json()["message"]
        self.assertNotIn("error", result)
        return result

    def test_ledger_matches_authoritative_rows(self):
        data = self.call(item_code=self.seed["item_code"], limit=300)
        raw = self.resource("Stock Ledger Entry", ["name", "actual_qty"], {"item_code": self.seed["item_code"], "is_cancelled": 0})
        self.assertFalse(data["truncated"])
        self.assertEqual({r["name"] for r in raw}, {r["name"] for r in data["movements"]})
        self.assertAlmostEqual(sum(r["actual_qty"] for r in raw), sum(r["actual_qty"] for r in data["movements"]))
        self.assertTrue(data["documents"])

    def test_company_and_warehouse_isolation(self):
        seed = self.seed
        data = self.call(item_code=seed["item_code"], company=seed["company"], warehouse=seed["warehouse"])
        self.assertTrue(data["movements"])
        self.assertTrue(all(r["company"] == seed["company"] and r["warehouse"] == seed["warehouse"] for r in data["movements"]))
        self.assertTrue(all(b["warehouse"] == seed["warehouse"] for b in data["balances"]))
        bins = self.resource("Bin", ["name", "actual_qty"], {"item_code": seed["item_code"], "warehouse": seed["warehouse"]})
        self.assertEqual(sum(b["actual_qty"] for b in bins), sum(b["actual_qty"] for b in data["balances"]))

    def test_empty_period_preserves_current_balances(self):
        full = self.call(item_code=self.seed["item_code"])
        empty = self.call(item_code=self.seed["item_code"], from_date="1900-01-01", to_date="1900-01-02")
        self.assertEqual(empty["movements"], [])
        self.assertEqual(empty["balances"], full["balances"])

    def test_limit_and_date_validation(self):
        data = self.call(item_code=self.seed["item_code"], limit=1)
        self.assertEqual(len(data["movements"]), 1)
        self.assertTrue(data["truncated"])
        response = self.s.get(self.base + "/api/method/inventory_relationship_map", params={
            "item_code": self.seed["item_code"], "from_date": "2026-09-08", "to_date": "2026-01-01"}, timeout=30)
        self.assertGreaterEqual(response.status_code, 400)

    def test_document_launch_context(self):
        data = self.call(doctype=self.seed["voucher_type"], docname=self.seed["voucher_no"])
        self.assertIn(data["item"]["name"], data["source_items"])
        self.assertEqual(data["company"], self.seed["company"])
        self.assertTrue(data["references"], "Seed receipt must exercise real upstream order links")

    def test_unknown_item_and_unsupported_root_rejected(self):
        for params in [{"item_code": "__inventory_map_missing_item__"}, {"doctype": "User", "docname": "Administrator"}]:
            response = self.s.get(self.base + "/api/method/inventory_relationship_map", params=params, timeout=30)
            self.assertGreaterEqual(response.status_code, 400)

    def test_guest_cannot_read_stock(self):
        response = requests.get(self.base + "/api/method/inventory_relationship_map", timeout=30)
        self.assertIn(response.status_code, (401, 403))
        self.assertNotIn('"movements":', response.text)

    def test_ui_and_shortcut_installed(self):
        response = self.s.get(self.base + "/inventory-relationship-map", timeout=30)
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="inventory-map-app"', response.text)
        response = self.s.get(self.base + "/api/resource/Workspace/Stock", timeout=30)
        response.raise_for_status()
        shortcuts = response.json()["data"]["shortcuts"]
        self.assertEqual(len([s for s in shortcuts if s["label"] == "Inventory Relationship Map"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
