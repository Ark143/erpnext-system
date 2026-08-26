"""
Script to:
1. Update all Price Lists to use PHP currency
2. Create Item Price records for all items using their standard_rate
3. Set default selling/buying price list to Philippine Peso

Run from frappe-bench/sites:
    ..\env\Scripts\python.exe ..\seed_price_list_php.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))

import frappe

frappe.init("site1.local")
frappe.connect()


# ─────────────────────────────────────────────────────────
# 1. Ensure "Philippine Peso" Price Lists exist and use PHP
# ─────────────────────────────────────────────────────────

PRICE_LISTS = [
    {"name": "Standard Selling", "currency": "PHP", "selling": 1, "buying": 0, "enabled": 1},
    {"name": "Standard Buying",  "currency": "PHP", "selling": 0, "buying": 1, "enabled": 1},
    {"name": "Selling",          "currency": "PHP", "selling": 1, "buying": 0, "enabled": 1},
]

print("\n=== Updating Price Lists to PHP ===")
for pl_data in PRICE_LISTS:
    name = pl_data["name"]
    if frappe.db.exists("Price List", name):
        doc = frappe.get_doc("Price List", name)
        doc.currency = "PHP"
        doc.selling = pl_data["selling"]
        doc.buying = pl_data["buying"]
        doc.enabled = 1
        doc.save(ignore_permissions=True)
        print(f"  UPDATED: {name} -> PHP")
    else:
        doc = frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": name,
            "currency": "PHP",
            "selling": pl_data["selling"],
            "buying": pl_data["buying"],
            "enabled": 1,
        })
        doc.insert(ignore_permissions=True)
        print(f"  CREATED: {name} -> PHP")

frappe.db.commit()


# ─────────────────────────────────────────────────────────
# 2. Update Selling Settings default price list
# ─────────────────────────────────────────────────────────

print("\n=== Updating Selling & Buying Settings defaults ===")
try:
    selling_settings = frappe.get_single("Selling Settings")
    selling_settings.selling_price_list = "Standard Selling"
    selling_settings.save(ignore_permissions=True)
    print("  Selling Settings -> Standard Selling (PHP)")
except Exception as e:
    print(f"  WARNING Selling Settings: {e}")

try:
    buying_settings = frappe.get_single("Buying Settings")
    buying_settings.buying_price_list = "Standard Buying"
    buying_settings.save(ignore_permissions=True)
    print("  Buying Settings -> Standard Buying (PHP)")
except Exception as e:
    print(f"  WARNING Buying Settings: {e}")

frappe.db.commit()


# ─────────────────────────────────────────────────────────
# 3. Create/update Item Prices for all Items with standard_rate > 0
# ─────────────────────────────────────────────────────────

print("\n=== Seeding Item Prices (PHP) ===")

# Fetch all items that have a standard_rate
items = frappe.db.sql("""
    SELECT name, item_code, item_name, standard_rate, is_stock_item
    FROM `tabItem`
    WHERE disabled = 0
      AND (standard_rate IS NOT NULL AND standard_rate > 0)
""", as_dict=True)

print(f"  Items with standard_rate > 0: {len(items)}")

price_list = "Standard Selling"
created = 0
updated = 0
skipped = 0

for item in items:
    rate = float(item.standard_rate or 0)
    if rate <= 0:
        skipped += 1
        continue

    # Check if item price already exists for this item + price list
    existing = frappe.db.get_value(
        "Item Price",
        {"item_code": item.item_code, "price_list": price_list},
        "name"
    )

    if existing:
        # Update existing price
        frappe.db.set_value("Item Price", existing, {
            "price_list_rate": rate,
            "currency": "PHP",
        })
        updated += 1
    else:
        # Create new price entry
        try:
            ip = frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item.item_code,
                "price_list": price_list,
                "price_list_rate": rate,
                "currency": "PHP",
                "selling": 1,
            })
            ip.insert(ignore_permissions=True)
            created += 1
        except Exception as e:
            skipped += 1
            if skipped <= 5:
                print(f"  ERROR {item.item_code}: {str(e)[:100]}")

    # Commit every 500 records
    if (created + updated) % 500 == 0 and (created + updated) > 0:
        frappe.db.commit()
        print(f"  Progress: {created} created, {updated} updated so far...")

frappe.db.commit()
print(f"\n  Item Prices: {created} created, {updated} updated, {skipped} skipped")


# ─────────────────────────────────────────────────────────
# 4. Also update any existing Item Prices with wrong currency
# ─────────────────────────────────────────────────────────

print("\n=== Fixing existing Item Price currencies to PHP ===")
wrong_currency = frappe.db.sql("""
    SELECT name FROM `tabItem Price`
    WHERE currency != 'PHP'
""", as_dict=True)

if wrong_currency:
    names = [r.name for r in wrong_currency]
    frappe.db.sql("""
        UPDATE `tabItem Price`
        SET currency = 'PHP'
        WHERE currency != 'PHP'
    """)
    frappe.db.commit()
    print(f"  Fixed {len(names)} Item Price records to PHP")
else:
    print("  All Item Price records already use PHP")


print("\n=== Summary ===")
total_ip = frappe.db.count("Item Price")
php_ip   = frappe.db.sql("SELECT COUNT(*) FROM `tabItem Price` WHERE currency='PHP'")[0][0]
print(f"  Total Item Prices : {total_ip}")
print(f"  PHP Item Prices   : {php_ip}")
print("\nDone!")
