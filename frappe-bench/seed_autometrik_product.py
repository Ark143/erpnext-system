import frappe

def seed_product():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    item_code = "DB 2429GCT"
    if not frappe.db.exists("Item", item_code):
        doc = frappe.new_doc("Item")
        doc.item_code = item_code
        doc.item_name = "BRAKE PADS, BENDIX DB 2429GCT RR DM-DAS-OS"
        doc.item_group = "Products"
        doc.stock_uom = "Nos"
        doc.description = "Bendix General CT (GCT) Rear Brake Pads for Honda Civic 2016-2021"
        
        # Autometrik custom fields
        doc.custom_print_display_name = "Bendix GCT Rear Brake Pads"
        doc.custom_part_no = "DB 2429GCT"
        doc.custom_manufacturer_no = "43022-TBA-A01"
        doc.custom_product_category = "Brake System"
        doc.custom_color = "Titanium Blue / Black"
        doc.custom_incentive = 50.0
        doc.custom_allow_zero_value = 0

        # Physical Binning / Storage
        doc.custom_rack = "RACK-B"
        doc.custom_shelf = "SHELF-02"
        doc.custom_bin_location = "BIN-14"
        doc.custom_order_multiple = 1.0

        # Autometrik Pricing
        doc.custom_purchase_cost = 1500.0
        doc.custom_pricing_rule = "MARK-UP 50%"
        doc.custom_markup_rate = 50.0
        doc.custom_sell_price = 2250.0
        doc.custom_margin_percent = 33.33

        # Vehicle Compatibility (Fitment)
        doc.append("custom_vehicle_compatibility", {
            "make": "Honda",
            "model": "Honda-Civic",
            "year_from": 2016,
            "year_to": 2021,
            "engine": "1.5L Turbo / 1.8L",
            "transmission": "All",
            "fitment_notes": "Rear Axle (Left & Right)"
        })
        doc.append("custom_vehicle_compatibility", {
            "make": "Honda",
            "model": "Honda-CR-V",
            "year_from": 2017,
            "year_to": 2022,
            "engine": "1.6L i-DTEC / 2.0L / 2.4L",
            "transmission": "Automatic",
            "fitment_notes": "Rear Brake Calipers"
        })

        # Cross Reference Parts
        doc.append("custom_part_cross_references", {
            "brand_or_oem": "Honda Genuine OEM",
            "part_number": "43022-TBA-A01",
            "reference_type": "OEM Genuine",
            "remarks": "Factory OEM rear brake pads"
        })
        doc.append("custom_part_cross_references", {
            "brand_or_oem": "Akebono",
            "part_number": "ACT1878",
            "reference_type": "Aftermarket Equivalent",
            "remarks": "Ultra-Premium Ceramic"
        })

        doc.insert(ignore_permissions=True)
        print(f"Created sample automotive item: {item_code}")
    else:
        print(f"Item {item_code} already exists")

    frappe.db.commit()

if __name__ == "__main__":
    seed_product()
