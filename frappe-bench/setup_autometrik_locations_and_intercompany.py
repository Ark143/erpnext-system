import frappe
from frappe.utils import now

LOCATIONS = [
    {
        "id": 213,
        "name": "Ultra MRF Dau Main",
        "abbr": "UMDM",
        "short_name": "UMD Main",
        "address": "Km. 87 MacArthur Highway, Dau Mabalacat, Pampanga, 2010 Philippines",
        "telephone": "09706667095",
        "email": "ultramrfdaumain.sales@gmail.com",
        "is_warehouse": False
    },
    {
        "id": 214,
        "name": "Ultra MRF Dau Annex",
        "abbr": "UMDA",
        "short_name": "UMD Annex",
        "address": "Dau Annex, Mabalacat, Pampanga",
        "telephone": "+639933152918",
        "email": "",
        "is_warehouse": False
    },
    {
        "id": 215,
        "name": "Ultra MRF Warehouse Dau",
        "abbr": "UMDW",
        "short_name": "UMD Warehouse",
        "address": "Warehouse Dau, Mabalacat, Pampanga",
        "telephone": "+639933152918",
        "email": "",
        "is_warehouse": True
    },
    {
        "id": 169,
        "name": "Ultra MRF San Fernando",
        "abbr": "UMSF",
        "short_name": "Ultra MRF SF",
        "address": "San Fernando, Pampanga",
        "telephone": "09564179525",
        "email": "mrfultra7@gmail.com",
        "is_warehouse": False
    },
    {
        "id": 186,
        "name": "San Fernando Warehouse",
        "abbr": "SFWH",
        "short_name": "SF-WH",
        "address": "San Fernando Pampanga",
        "telephone": "09177777777",
        "email": "",
        "is_warehouse": True
    },
    {
        "id": 191,
        "name": "Ultra MRF Telebastagan",
        "abbr": "UMTEL",
        "short_name": "UMF TEL",
        "address": "Telebastagan, City of San Fernando, Pampanga",
        "telephone": "12345678",
        "email": "",
        "is_warehouse": False
    },
    {
        "id": 296,
        "name": "Ultra MRF Telebastagan 2",
        "abbr": "UMTEL2",
        "short_name": "Ultra MRF Tel 2",
        "address": "Telebastagan 2, City of San Fernando, Pampanga",
        "telephone": "11",
        "email": "",
        "is_warehouse": False
    },
    {
        "id": 187,
        "name": "Ultra MRF Mexico Warehouse",
        "abbr": "MEXWH",
        "short_name": "MEXWH",
        "address": "Mexico Pampanga",
        "telephone": "0917-7777772",
        "email": "",
        "is_warehouse": True
    },
    {
        "id": 279,
        "name": "Automan Car Care Center",
        "abbr": "AUTOMAN",
        "short_name": "AUTOMAN",
        "address": "Friendship Hwy, Angeles City, Pampanga",
        "telephone": "09933152918",
        "email": "mrfts2007@gmail.com",
        "is_warehouse": False
    },
    {
        "id": 170,
        "name": "Wheel Core",
        "abbr": "WCORE",
        "short_name": "Wheel Core",
        "address": "Pampanga",
        "telephone": "0920553708",
        "email": "federick.dumas@yahoo.com",
        "is_warehouse": False
    },
    {
        "id": 285,
        "name": "The Wheelhub",
        "abbr": "WHUB",
        "short_name": "WHEELHUB OPC",
        "address": "600 Shaw Blvd, Brgy Kapitolyo Pasig City",
        "telephone": "111",
        "email": "wheelhubopc@gmail.com",
        "is_warehouse": False
    }
]

def setup_intercompany_and_locations():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    parent_company_name = "ULTRA MRF"
    if not frappe.db.exists("Company", parent_company_name):
        p_comp = frappe.new_doc("Company")
        p_comp.company_name = parent_company_name
        p_comp.abbr = "UM"
        p_comp.is_group = 1
        p_comp.default_currency = "PHP"
        p_comp.country = "Philippines"
        p_comp.insert(ignore_permissions=True)
        print(f"Created Parent Group Company: {parent_company_name}")
    else:
        # Ensure parent company is group and PHP
        frappe.db.set_value("Company", parent_company_name, {
            "is_group": 1,
            "default_currency": "PHP",
            "country": "Philippines"
        })

    # ========================================================
    # 1. Populate Branch records
    # ========================================================
    print("--- 1. Populating Branch records ---")
    for loc in LOCATIONS:
        b_name = loc["name"]
        if not frappe.db.exists("Branch", b_name):
            b_doc = frappe.new_doc("Branch")
            b_doc.branch = b_name
            b_doc.insert(ignore_permissions=True)
            print(f"Created Branch: {b_name}")

    frappe.db.commit()

    # ========================================================
    # 2. Setup Accounting Dimension 'Branch'
    # ========================================================
    print("--- 2. Setting up Accounting Dimension 'Branch' ---")
    if not frappe.db.exists("Accounting Dimension", "Branch"):
        dim = frappe.new_doc("Accounting Dimension")
        dim.document_type = "Branch"
        dim.label = "Branch"
        dim.disabled = 0
        dim.insert(ignore_permissions=True)
        print("Created Accounting Dimension: Branch")
    frappe.db.commit()

    # ========================================================
    # 3. Create Branch Companies (Intercompany hierarchy)
    # ========================================================
    print("--- 3. Creating Intercompany Branch Companies ---")
    for loc in LOCATIONS:
        c_name = loc["name"]
        abbr = loc["abbr"]
        if not frappe.db.exists("Company", c_name):
            try:
                comp = frappe.new_doc("Company")
                comp.company_name = c_name
                comp.abbr = abbr
                comp.parent_company = parent_company_name
                comp.is_group = 0
                comp.default_currency = "PHP"
                comp.country = "Philippines"
                comp.create_chart_of_accounts_based_on = "Standard Template"
                comp.chart_of_accounts = "Standard"
                comp.insert(ignore_permissions=True)
                print(f"Created Branch Company: {c_name} ({abbr})")
            except Exception as e:
                print(f"Error creating company {c_name}: {e}")
        else:
            print(f"Company {c_name} already exists.")

    frappe.db.commit()

    # ========================================================
    # 4. Create Locations in Location DocType (Asset / Physical Location)
    # ========================================================
    print("--- 4. Creating Physical Location master records ---")
    for loc in LOCATIONS:
        l_name = loc["name"]
        if not frappe.db.exists("Location", l_name):
            try:
                loc_doc = frappe.new_doc("Location")
                loc_doc.location_name = l_name
                loc_doc.is_group = 0
                loc_doc.insert(ignore_permissions=True)
                print(f"Created Location: {l_name}")
            except Exception as e:
                print(f"Error creating Location {l_name}: {e}")

    frappe.db.commit()

    # ========================================================
    # 5. Create Cost Centers for each Location under Parent & Companies
    # ========================================================
    print("--- 5. Setting up Cost Centers ---")
    parent_cc = f"{parent_company_name} - UM"
    for loc in LOCATIONS:
        loc_name = loc["name"]
        abbr = loc["abbr"]
        
        # CC under Parent Company
        cc_name = f"{loc_name} - UM"
        if not frappe.db.exists("Cost Center", cc_name):
            try:
                cc = frappe.new_doc("Cost Center")
                cc.cost_center_name = loc_name
                cc.company = parent_company_name
                cc.parent_cost_center = parent_cc
                cc.is_group = 0
                cc.insert(ignore_permissions=True)
                print(f"Created Cost Center under {parent_company_name}: {cc_name}")
            except Exception as e:
                print(f"Error creating Cost Center {cc_name}: {e}")

    frappe.db.commit()

    # ========================================================
    # 6. Create Warehouses for each Location
    # ========================================================
    print("--- 6. Setting up Warehouses ---")
    parent_wh = f"All Warehouses - UM"
    for loc in LOCATIONS:
        loc_name = loc["name"]
        wh_name = f"{loc_name} - UM"
        if not frappe.db.exists("Warehouse", wh_name):
            try:
                wh = frappe.new_doc("Warehouse")
                wh.warehouse_name = loc_name
                wh.company = parent_company_name
                wh.parent_warehouse = parent_wh
                wh.is_group = 0
                wh.insert(ignore_permissions=True)
                print(f"Created Warehouse under {parent_company_name}: {wh_name}")
            except Exception as e:
                print(f"Error creating Warehouse {wh_name}: {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("=== Locations, Intercompany Branches, Warehouses, Cost Centers & Accounting Dimension Setup Complete! ===")

if __name__ == "__main__":
    setup_intercompany_and_locations()
