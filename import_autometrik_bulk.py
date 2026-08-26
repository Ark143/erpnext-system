import os
import csv
import frappe
from frappe.utils import now, flt

def clean(s):
    return (s or "").strip()

def run_import():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    base_dir = "C:/Users/josem/Downloads"
    now_ts = now()

    # ==========================================
    # 1. IMPORT MANUFACTURERS
    # ==========================================
    print("--- 1. Importing Manufacturers ---")
    mfg_path = os.path.join(base_dir, "Manufacturers_08152026105232.csv")
    if os.path.exists(mfg_path):
        with open(mfg_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                name = clean(row.get("Name"))
                if name and not frappe.db.exists("Manufacturer", name):
                    frappe.db.sql("""
                        INSERT INTO "tabManufacturer" (name, creation, modified, modified_by, owner, short_name, full_name, notes)
                        VALUES (%s, %s, %s, 'Administrator', 'Administrator', %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (name, now_ts, now_ts, name, name, clean(row.get("Description"))))
                    count += 1
            frappe.db.commit()
            print(f"Imported {count} new Manufacturers.")

    # ==========================================
    # 2. IMPORT CAR MAKES & MODELS
    # ==========================================
    print("--- 2. Importing Car Makes & Models ---")
    makes_path = os.path.join(base_dir, "CarMakes_08152026104956.csv")
    if os.path.exists(makes_path):
        with open(makes_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                make = clean(row.get("Name"))
                if make and not frappe.db.exists("Vehicle Make", make):
                    frappe.db.sql("""
                        INSERT INTO "tabVehicle Make" (name, creation, modified, modified_by, owner, make_name)
                        VALUES (%s, %s, %s, 'Administrator', 'Administrator', %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (make, now_ts, now_ts, make))
                    count += 1
            frappe.db.commit()
            print(f"Imported {count} new Vehicle Makes.")

    models_path = os.path.join(base_dir, "CarModels_08152026105023.csv")
    if os.path.exists(models_path):
        with open(models_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                make = clean(row.get("CarMake"))
                model = clean(row.get("Name"))
                if not make or not model:
                    continue
                # Ensure make exists
                if not frappe.db.exists("Vehicle Make", make):
                    frappe.db.sql("""
                        INSERT INTO "tabVehicle Make" (name, creation, modified, modified_by, owner, make_name)
                        VALUES (%s, %s, %s, 'Administrator', 'Administrator', %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (make, now_ts, now_ts, make))

                model_key = f"{make}-{model}"
                if not frappe.db.exists("Vehicle Model", model_key):
                    frappe.db.sql("""
                        INSERT INTO "tabVehicle Model" (name, creation, modified, modified_by, owner, make, model_name, category)
                        VALUES (%s, %s, %s, 'Administrator', 'Administrator', %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (model_key, now_ts, now_ts, make, model, clean(row.get("Category")) or "Sedan"))
                    count += 1
            frappe.db.commit()
            print(f"Imported {count} new Vehicle Models.")

    # ==========================================
    # 3. IMPORT PRODUCT GROUPS / CATEGORIES
    # ==========================================
    print("--- 3. Importing Item Groups ---")
    pg_path = os.path.join(base_dir, "ProductGroups_08152026105045.csv")
    if os.path.exists(pg_path):
        with open(pg_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                grp = clean(row.get("Name"))
                if grp and not frappe.db.exists("Item Group", grp):
                    doc = frappe.new_doc("Item Group")
                    doc.item_group_name = grp
                    doc.parent_item_group = "All Item Groups"
                    doc.is_group = 0
                    doc.insert(ignore_permissions=True)
        frappe.db.commit()

    # ==========================================
    # 4. IMPORT SUPPLIERS
    # ==========================================
    print("--- 4. Importing Suppliers ---")
    supp_path = os.path.join(base_dir, "Suppliers_08152026104808.csv")
    if os.path.exists(supp_path):
        with open(supp_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                name = clean(row.get("Name"))
                if name and not frappe.db.exists("Supplier", name):
                    frappe.db.sql("""
                        INSERT INTO "tabSupplier" (name, creation, modified, modified_by, owner, supplier_name, supplier_group, supplier_type, tax_id, is_transporter, disabled, language)
                        VALUES (%s, %s, %s, 'Administrator', 'Administrator', %s, 'All Supplier Groups', 'Company', %s, 0, 0, 'en')
                        ON CONFLICT (name) DO NOTHING
                    """, (name, now_ts, now_ts, name, clean(row.get("Tin"))))
                    count += 1
            frappe.db.commit()
            print(f"Imported {count} new Suppliers.")

    # ==========================================
    # 5. IMPORT ACTIVE PRODUCTS (ITEMS)
    # ==========================================
    print("--- 5. Importing Products into Items ---")
    prod_path = os.path.join(base_dir, "Products_08242026025546.csv")
    if os.path.exists(prod_path):
        with open(prod_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                item_name = clean(row.get("Name"))
                part_no = clean(row.get("PartNo"))
                item_code = part_no if part_no else item_name

                if not item_code:
                    continue

                cost = flt(row.get("PurchaseCost"))
                sell = flt(row.get("SellPrice"))
                margin = ((sell - cost) / sell * 100.0) if sell > 0 else 0.0
                markup = ((sell - cost) / cost * 100.0) if cost > 0 else 0.0
                uom = clean(row.get("Unit")) or "Nos"
                if not frappe.db.exists("UOM", uom):
                    uom = "Nos"

                cat = clean(row.get("Category"))
                grp = clean(row.get("ProductGroup")) or "Products"
                if not frappe.db.exists("Item Group", grp):
                    grp = "Products"

                if not frappe.db.exists("Item", item_code):
                    frappe.db.sql("""
                        INSERT INTO "tabItem" (
                            name, creation, modified, modified_by, owner,
                            item_code, item_name, item_group, stock_uom, description,
                            disabled, is_stock_item, is_sales_item, is_purchase_item,
                            custom_print_display_name, custom_part_no, custom_manufacturer_no,
                            custom_product_category, custom_rack, custom_shelf, custom_bin_location,
                            custom_purchase_cost, custom_pricing_rule, custom_markup_rate,
                            custom_sell_price, custom_margin_percent, end_of_life
                        ) VALUES (
                            %s, %s, %s, 'Administrator', 'Administrator',
                            %s, %s, %s, %s, %s,
                            0, 1, 1, 1,
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, '2099-12-31'
                        ) ON CONFLICT (name) DO NOTHING
                    """, (
                        item_code, now_ts, now_ts,
                        item_code, item_name, grp, uom, clean(row.get("Description")),
                        clean(row.get("PrintDisplayName")), part_no, clean(row.get("ManufacturerNo")),
                        cat, clean(row.get("StorageRack")), clean(row.get("StorageShelf")), clean(row.get("StorageBin")),
                        cost, 'MARK-UP 50%', markup,
                        sell, margin
                    ))

                    # Insert UOM child record
                    uom_row_id = frappe.generate_hash(length=10)
                    frappe.db.sql("""
                        INSERT INTO "tabUOM Conversion Detail" (name, creation, modified, modified_by, owner, uom, conversion_factor, parent, parentfield, parenttype)
                        VALUES (%s, %s, %s, 'Administrator', 'Administrator', %s, 1.0, %s, 'uoms', 'Item')
                        ON CONFLICT DO NOTHING
                    """, (uom_row_id, now_ts, now_ts, uom, item_code))

                    count += 1
                    if count % 1000 == 0:
                        frappe.db.commit()
                        print(f"  Processed {count} items...")

            frappe.db.commit()
            print(f"Imported {count} new Products/Items.")

    # ==========================================
    # 6. IMPORT CUSTOMERS
    # ==========================================
    print("--- 6. Importing Customers ---")
    cust_path = os.path.join(base_dir, "Customers_08242026025548.csv")
    if os.path.exists(cust_path):
        with open(cust_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                c_type = clean(row.get("Type")) or "Individual"
                first_name = clean(row.get("FirstName"))
                last_name = clean(row.get("LastName"))
                company = clean(row.get("Company"))

                if c_type.lower() == "company" or c_type.lower() == "corporate":
                    cust_name = company if company else f"{first_name} {last_name}".strip()
                    cust_type = "Company"
                else:
                    cust_name = f"{first_name} {last_name}".strip()
                    cust_type = "Individual"

                if not cust_name:
                    continue

                if not frappe.db.exists("Customer", cust_name):
                    frappe.db.sql("""
                        INSERT INTO "tabCustomer" (
                            name, creation, modified, modified_by, owner,
                            customer_name, customer_type, customer_group, territory,
                            custom_first_name, custom_last_name, custom_contact_person,
                            custom_mobile_no, custom_telephone_no, custom_office_no,
                            custom_email_address, custom_address_text, custom_notes,
                            custom_labor_discount_rate, custom_product_discount_rate,
                            disabled, language
                        ) VALUES (
                            %s, %s, %s, 'Administrator', 'Administrator',
                            %s, %s, 'All Customer Groups', 'All Territories',
                            %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s,
                            0.0, 0.0,
                            0, 'en'
                        ) ON CONFLICT (name) DO NOTHING
                    """, (
                        cust_name, now_ts, now_ts,
                        cust_name, cust_type,
                        first_name, last_name, clean(row.get("ContactPerson")),
                        clean(row.get("MobileNo")), clean(row.get("TelephoneNo")), clean(row.get("OfficeNo")),
                        clean(row.get("EmailAddress")), clean(row.get("Address")), clean(row.get("Notes"))
                    ))
                    count += 1
                    if count % 5000 == 0:
                        frappe.db.commit()
                        print(f"  Processed {count} customers...")

            frappe.db.commit()
            print(f"Imported {count} new Customers.")

    # ==========================================
    # 7. IMPORT VEHICLES
    # ==========================================
    print("--- 7. Importing Customer Vehicles ---")
    veh_path = os.path.join(base_dir, "Vehicles_08242026025519.csv")
    if os.path.exists(veh_path):
        with open(veh_path, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                plate = clean(row.get("PlateNo"))
                if not plate:
                    continue

                make = clean(row.get("CarMake"))
                model = clean(row.get("CarModel"))
                model_key = f"{make}-{model}" if make and model else ""
                cust = clean(row.get("Customer"))
                year = 0
                year_str = clean(row.get("YearModel"))
                if year_str and year_str.isdigit():
                    year = int(year_str)

                if not frappe.db.exists("Customer Vehicle", plate):
                    frappe.db.sql("""
                        INSERT INTO "tabCustomer Vehicle" (
                            name, creation, modified, modified_by, owner,
                            plate_no, customer, customer_name,
                            make, model, year_model, vin, engine_no, color,
                            status, mileage_unit, registration_type
                        ) VALUES (
                            %s, %s, %s, 'Administrator', 'Administrator',
                            %s, %s, %s,
                            %s, %s, %s, %s, %s, %s,
                            'Active', 'km', %s
                        ) ON CONFLICT (name) DO NOTHING
                    """, (
                        plate, now_ts, now_ts,
                        plate, cust, cust,
                        make, model_key, year, clean(row.get("Vin")), clean(row.get("EngineNo")), clean(row.get("Color")),
                        clean(row.get("RegistrationType")) or "Private"
                    ))
                    count += 1
                    if count % 5000 == 0:
                        frappe.db.commit()
                        print(f"  Processed {count} vehicles...")

            frappe.db.commit()
            print(f"Imported {count} new Customer Vehicles.")

    frappe.clear_cache()
    print("=== All Autometrik Data Successfully Imported to ERPNext! ===")

if __name__ == "__main__":
    run_import()
