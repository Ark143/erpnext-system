"""
Bulk-create Item Price records for all items using custom_sell_price (from Autometrik).
Also updates standard_rate for items where it's 0 but custom_sell_price exists.

Run from frappe-bench/sites:
    ..\env\Scripts\python.exe ..\seed_item_prices_from_sell_price.py
"""
import frappe

frappe.init("site1.local")
frappe.connect()

PRICE_LIST = "Standard Selling"
CURRENCY   = "PHP"

print("=== Bulk Item Price Creation from custom_sell_price ===\n")

# Fetch all enabled items with a sell price
items = frappe.db.sql(
    """
    SELECT item_code, item_name, standard_rate, custom_sell_price
    FROM tabItem
    WHERE disabled = 0
      AND custom_sell_price IS NOT NULL
      AND custom_sell_price > 0
    ORDER BY item_code
    """,
    as_dict=True,
)

print(f"Items with custom_sell_price > 0: {len(items)}")

created = 0
updated = 0
rate_updated = 0
skipped = 0
batch_size = 500

for i, item in enumerate(items):
    rate = float(item.custom_sell_price or 0)
    if rate <= 0:
        skipped += 1
        continue

    # Also update standard_rate on the item if it's 0
    if not item.standard_rate or float(item.standard_rate) == 0:
        frappe.db.set_value("Item", item.item_code, "standard_rate", rate)
        rate_updated += 1

    # Create or update Item Price
    existing = frappe.db.get_value(
        "Item Price",
        {"item_code": item.item_code, "price_list": PRICE_LIST},
        "name",
    )

    if existing:
        frappe.db.set_value("Item Price", existing, {
            "price_list_rate": rate,
            "currency": CURRENCY,
        })
        updated += 1
    else:
        try:
            ip = frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item.item_code,
                "price_list": PRICE_LIST,
                "price_list_rate": rate,
                "currency": CURRENCY,
                "selling": 1,
            })
            ip.insert(ignore_permissions=True)
            created += 1
        except Exception as e:
            skipped += 1
            if skipped <= 5:
                print(f"  ERROR {item.item_code}: {str(e)[:100]}")

    # Commit every batch_size records
    if (i + 1) % batch_size == 0:
        frappe.db.commit()
        print(f"  Progress: {i+1}/{len(items)} processed ({created} created, {updated} updated)...")

frappe.db.commit()

print(f"\n=== Summary ===")
print(f"  Item Prices created  : {created}")
print(f"  Item Prices updated  : {updated}")
print(f"  Standard rate synced : {rate_updated}")
print(f"  Skipped              : {skipped}")

total_ip = frappe.db.count("Item Price")
php_ip = frappe.db.sql("SELECT COUNT(*) FROM tabItem t1 WHERE 1=0")[0][0] if False else frappe.db.sql(
    "SELECT COUNT(*) FROM \"tabItem Price\" WHERE currency='PHP'"
)[0][0]
print(f"\n  Total Item Prices    : {total_ip}")
print(f"  PHP Item Prices      : {php_ip}")
print("\nDone!")
