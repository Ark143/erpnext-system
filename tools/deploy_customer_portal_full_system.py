import requests
import json
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
r_login = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print(f"[LOGIN] {r_login.status_code}")

server_script_code = '''
BRANCH_METADATA = {
    "Ultra MRF Dau Main": {
        "title": "ULTRA MRF Dau Main Branch",
        "address": "MacArthur Highway, Dau, Mabalacat City, Pampanga",
        "phone": "(045) 892-1234 / 0917-555-0101",
        "email": "dau.main@ultramrf.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM | Sun: 8:00 AM - 12:00 PM",
        "bays": 12,
        "badge": "Main Service Hub & Tire Center",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes", "Underchassis", "Car Aircon", "Engine Diagnostics"]
    },
    "Ultra MRF Dau Annex": {
        "title": "ULTRA MRF Dau Annex Branch",
        "address": "Dau Access Road, Mabalacat City, Pampanga",
        "phone": "(045) 892-5678 / 0917-555-0102",
        "email": "dau.annex@ultramrf.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
        "bays": 8,
        "badge": "Quick Service & Tire Express",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes", "Car Wash & Detailing"]
    },
    "Ultra MRF San Fernando": {
        "title": "ULTRA MRF San Fernando Branch",
        "address": "Jose Abad Santos Ave (OG Road), San Fernando, Pampanga",
        "phone": "(045) 961-4321 / 0917-555-0201",
        "email": "sanfernando@ultramrf.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
        "bays": 10,
        "badge": "Full Service Auto Center & Alignment Hub",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes", "Underchassis", "Car Aircon", "Engine Diagnostics"]
    },
    "Ultra MRF Telebastagan": {
        "title": "ULTRA MRF Telebastagan Branch",
        "address": "MacArthur Highway, Telebastagan, City of San Fernando, Pampanga",
        "phone": "(045) 436-7890 / 0917-555-0301",
        "email": "telebastagan@ultramrf.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
        "bays": 8,
        "badge": "Suspension & Performance Tire Specialist",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes", "Underchassis", "Engine Diagnostics"]
    },
    "Ultra MRF Telebastagan 2": {
        "title": "ULTRA MRF Telebastagan 2 Express",
        "address": "Commercial Complex, Telebastagan, Pampanga",
        "phone": "(045) 436-7892 / 0917-555-0302",
        "email": "telebastagan2@ultramrf.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
        "bays": 6,
        "badge": "Fast PMS & Wheel Balancing Bay",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes"]
    },
    "Automan Car Care Center": {
        "title": "Automan Car Care Center",
        "address": "Lazatin Blvd, Dolores, City of San Fernando, Pampanga",
        "phone": "(045) 963-8888 / 0917-555-0401",
        "email": "service@automan.ph",
        "hours": "Mon - Sat: 7:30 AM - 6:00 PM | Sun: 8:00 AM - 3:00 PM",
        "bays": 14,
        "badge": "Premier Fleet & Advanced Diagnostics Hub",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes", "Underchassis", "Car Aircon", "Engine Diagnostics", "Battery & Electrical", "Car Wash & Detailing"]
    },
    "Wheel Core": {
        "title": "Wheel Core Custom & Tire Depot",
        "address": "Sindalan Commercial Corridor, San Fernando, Pampanga",
        "phone": "(045) 961-9999 / 0917-555-0501",
        "email": "sales@wheelcore.ph",
        "hours": "Mon - Sat: 8:30 AM - 5:30 PM",
        "bays": 6,
        "badge": "Mags, Custom Wheels & Stance Specialist",
        "services": ["Tires & Wheels", "Wheel Alignment", "Brakes", "Underchassis"]
    },
    "The Wheelhub": {
        "title": "The Wheelhub Auto Concept",
        "address": "Clark Perimeter Road, Angeles City, Pampanga",
        "phone": "(045) 625-1111 / 0917-555-0601",
        "email": "info@wheelhub.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
        "bays": 6,
        "badge": "Wheel Alignment & Tire Care Center",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes"]
    },
    "ULTRA MRF": {
        "title": "ULTRA MRF Central Operations",
        "address": "Pampanga Main Commercial Hub",
        "phone": "(045) 892-0000 / 0917-555-0000",
        "email": "customercare@ultramrf.ph",
        "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
        "bays": 10,
        "badge": "Headquarters & VIP Customer Concierge",
        "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes", "Underchassis", "Car Aircon", "Engine Diagnostics", "General Mechanical Repair"]
    }
}

SERVICE_TYPES = [
    {"name": "PMS / Change Oil", "icon": "fa-oil-can", "duration": "45-60 min", "desc": "Synthetic / Semi-synth oil replacement, OEM oil filter, 30-pt safety inspection"},
    {"name": "Tires & Wheels", "icon": "fa-compact-disc", "duration": "30-45 min", "desc": "Tire mounting, computerized wheel balancing, nitrogen inflation & tire rotation"},
    {"name": "Wheel Alignment", "icon": "fa-arrows-to-dot", "duration": "45-60 min", "desc": "Precision 3D laser wheel alignment (camber, caster, toe calibration)"},
    {"name": "Brakes", "icon": "fa-circle-stop", "duration": "60-90 min", "desc": "Brake pad & rotor replacement, caliper cleaning, rotor resurfacing, brake fluid flush"},
    {"name": "Underchassis", "icon": "fa-gears", "duration": "60-120 min", "desc": "Shock absorbers, tie rods, ball joints, bushings, rack & pinion inspection"},
    {"name": "Car Aircon", "icon": "fa-snowflake", "duration": "60-90 min", "desc": "Evaporator cleaning, Freon recharge, cabin filter replacement & leak testing"},
    {"name": "Engine Diagnostics", "icon": "fa-microchip", "duration": "30-60 min", "desc": "OBD-II computer scan, spark plug check, throttle body cleaning & sensor health"},
    {"name": "Battery & Electrical", "icon": "fa-car-battery", "duration": "30-45 min", "desc": "Battery load testing, alternator charging system check, starter health"},
    {"name": "Car Wash & Detailing", "icon": "fa-shower", "duration": "60-180 min", "desc": "Engine bay wash, interior deep detailing, paint protection & wax"}
]

TIME_SLOTS = [
    "08:00 AM - 10:00 AM",
    "10:00 AM - 12:00 PM",
    "01:00 PM - 03:00 PM",
    "03:00 PM - 05:00 PM"
]

def ensure_vehicle_model(make, model):
    if not make and not model:
        return None
    make = str(make or "").strip().upper()
    model = str(model or "").strip().upper()

    if make and not frappe.db.exists("Vehicle Make", make):
        try:
            frappe.get_doc({"doctype": "Vehicle Make", "name": make, "make_name": make}).insert(ignore_permissions=True)
        except Exception:
            pass

    if make and model:
        combined = make + "-" + model
        if frappe.db.exists("Vehicle Model", combined):
            return combined
        if frappe.db.exists("Vehicle Model", model):
            return model
        found = frappe.db.get_value("Vehicle Model", {"model_name": model, "make": make}, "name")
        if found:
            return found
        try:
            vm = frappe.get_doc({
                "doctype": "Vehicle Model",
                "name": combined,
                "make": make,
                "model_name": model
            })
            vm.insert(ignore_permissions=True)
            return vm.name
        except Exception:
            return combined
    elif model:
        if frappe.db.exists("Vehicle Model", model):
            return model
        try:
            vm = frappe.get_doc({
                "doctype": "Vehicle Model",
                "name": model,
                "model_name": model
            })
            vm.insert(ignore_permissions=True)
            return vm.name
        except Exception:
            return model
    return None

def normalize_time_slot(slot):
    s = str(slot or "").strip()
    if not s:
        return TIME_SLOTS[0]
    if s in TIME_SLOTS:
        return s
    for ts in TIME_SLOTS:
        if s.lower() in ts.lower() or ts.lower() in s.lower():
            return ts
    return TIME_SLOTS[0]

# ── 1. BRANCHES & REFERENCE DATA ──
def handle_get_branches():
    branches_list = []
    for k, v in BRANCH_METADATA.items():
        item = {
            "key": k,
            "title": v.get("title", k),
            "address": v.get("address", ""),
            "phone": v.get("phone", ""),
            "email": v.get("email", ""),
            "hours": v.get("hours", ""),
            "bays": v.get("bays", 6),
            "badge": v.get("badge", ""),
            "services": v.get("services", [])
        }
        branches_list.append(item)
    return {
        "success": True,
        "branches": branches_list,
        "services": SERVICE_TYPES,
        "time_slots": TIME_SLOTS
    }

def handle_get_reference_data():
    makes = []
    if frappe.db.exists("DocType", "Vehicle Make"):
        makes = frappe.db.get_all("Vehicle Make", fields=["name", "make_name"], order_by="name asc", limit_page_length=100)
    
    models = []
    if frappe.db.exists("DocType", "Vehicle Model"):
        models = frappe.db.get_all("Vehicle Model", fields=["name", "model_name", "make"], order_by="model_name asc", limit_page_length=200)
    
    branches_list = handle_get_branches().get("branches", [])
    return {
        "success": True,
        "makes": makes,
        "models": models,
        "services": SERVICE_TYPES,
        "time_slots": TIME_SLOTS,
        "branches": branches_list
    }

# ── 2. CUSTOMER AUTHENTICATION & LOGIN ──
def handle_customer_login(identifier):
    ident = str(identifier or "").strip()
    if not ident:
        return {"success": False, "error": "Please enter your Customer Name, Mobile Phone, Email, or Plate Number."}
    
    cust_docname = None
    if frappe.db.exists("Customer", ident):
        cust_docname = ident
    elif frappe.db.exists("Customer", ident.upper()):
        cust_docname = ident.upper()
    else:
        found = frappe.db.get_value("Customer", {"custom_mobile_no": ident}, "name")
        if not found:
            found = frappe.db.get_value("Customer", {"mobile_no": ident}, "name")
        if not found:
            found = frappe.db.get_value("Customer", {"custom_email_address": ident}, "name")
        if not found:
            found = frappe.db.get_value("Customer", {"email_id": ident}, "name")
        if not found:
            found = frappe.db.get_value("Customer", {"customer_name": ["like", "%" + ident + "%"]}, "name")
        if found:
            cust_docname = found

    if not cust_docname:
        plate_upper = ident.upper().replace(" ", "").replace("-", "")
        cv_match = frappe.db.get_value("Customer Vehicle", {"name": plate_upper}, ["customer", "customer_name", "contact_no", "email"], as_dict=True)
        if not cv_match:
            cv_match = frappe.db.get_value("Customer Vehicle", {"plate_no": ident.upper()}, ["customer", "customer_name", "contact_no", "email"], as_dict=True)
        if not cv_match:
            cv_match = frappe.db.get_value("Customer Vehicle", {"contact_no": ident}, ["customer", "customer_name", "contact_no", "email"], as_dict=True)
        
        if cv_match and cv_match.get("customer") and frappe.db.exists("Customer", cv_match.get("customer")):
            cust_docname = cv_match.get("customer")
        elif cv_match:
            return build_customer_portal_payload(
                customer_name=cv_match.get("customer_name") or ident,
                customer_docname=cv_match.get("customer"),
                phone=cv_match.get("contact_no") or ident,
                email=cv_match.get("email") or "",
                address=""
            )

    if not cust_docname:
        return {"success": False, "not_found": True, "error": f"No existing customer profile found for '{ident}'. Please click 'Create Customer Profile' to register."}

    cust_vals = frappe.db.get_value("Customer", cust_docname, ["customer_name", "custom_mobile_no", "mobile_no", "custom_email_address", "email_id", "custom_address_text"], as_dict=True) or {}

    return build_customer_portal_payload(
        customer_name=cust_vals.get("customer_name") or cust_docname,
        customer_docname=cust_docname,
        phone=cust_vals.get("custom_mobile_no") or cust_vals.get("mobile_no") or "",
        email=cust_vals.get("custom_email_address") or cust_vals.get("email_id") or "",
        address=cust_vals.get("custom_address_text") or ""
    )

# ── 3. CREATE / REGISTER CUSTOMER PROFILE & LINK CUSTOMER VEHICLE ──
def handle_register_customer_profile(data):
    form = frappe.form_dict or {}
    cust_name = str(data.get("customer_name") or form.get("customer_name") or "").strip().upper()
    phone = str(data.get("customer_phone") or data.get("phone") or form.get("customer_phone") or form.get("phone") or "").strip()
    email = str(data.get("customer_email") or data.get("email") or form.get("customer_email") or form.get("email") or "").strip()
    address = str(data.get("customer_address") or data.get("address") or form.get("customer_address") or form.get("address") or "").strip()
    
    plate_no = str(data.get("plate_no") or form.get("plate_no") or "").strip().upper()
    make = str(data.get("make") or form.get("make") or "").strip().upper()
    model = str(data.get("model") or form.get("model") or "").strip().upper()
    year = str(data.get("year") or form.get("year") or "").strip()
    color = str(data.get("color") or form.get("color") or "").strip().upper()
    fuel_type = str(data.get("fuel_type") or form.get("fuel_type") or "Gasoline").strip()
    transmission = str(data.get("transmission") or form.get("transmission") or "Automatic").strip()
    vin = str(data.get("vin") or form.get("vin") or "-").strip()
    engine_no = str(data.get("engine_no") or form.get("engine_no") or "").strip()
    current_mileage = float(data.get("current_mileage") or form.get("current_mileage") or 0.0)

    if not cust_name:
        return {"success": False, "error": "Customer Full Name is required."}
    if not phone:
        return {"success": False, "error": "Contact Mobile Phone number is required."}

    # Step A: Customer Master - Create if not exists
    customer_docname = None
    if frappe.db.exists("Customer", cust_name):
        customer_docname = cust_name
        if phone:
            frappe.db.set_value("Customer", customer_docname, "custom_mobile_no", phone)
        if email:
            frappe.db.set_value("Customer", customer_docname, "custom_email_address", email)
    else:
        found_c = frappe.db.get_value("Customer", {"custom_mobile_no": phone}, "name")
        if found_c:
            customer_docname = found_c
        else:
            try:
                new_cust = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": cust_name,
                    "customer_type": "Individual",
                    "customer_group": "Individual",
                    "territory": "All Territories",
                    "custom_mobile_no": phone,
                    "custom_email_address": email,
                    "custom_address_text": address
                })
                new_cust.insert(ignore_permissions=True)
                customer_docname = new_cust.name
            except Exception as ex:
                customer_docname = cust_name

    # Step B: Ensure Model Doc
    model_docname = ensure_vehicle_model(make, model)

    # Step C: Customer Vehicle - Link or Create
    if plate_no:
        clean_name = plate_no.replace(" ", "").replace("-", "")
        existing_cv = None
        if frappe.db.exists("Customer Vehicle", clean_name):
            existing_cv = clean_name
        elif frappe.db.exists("Customer Vehicle", plate_no):
            existing_cv = plate_no
        else:
            found_cv = frappe.db.get_value("Customer Vehicle", {"plate_no": plate_no}, "name")
            if found_cv:
                existing_cv = found_cv

        if existing_cv:
            frappe.db.set_value("Customer Vehicle", existing_cv, {
                "customer": customer_docname,
                "customer_name": cust_name,
                "contact_no": phone,
                "email": email,
                "make": make or frappe.db.get_value("Customer Vehicle", existing_cv, "make"),
                "model": model_docname or frappe.db.get_value("Customer Vehicle", existing_cv, "model"),
                "color": color or frappe.db.get_value("Customer Vehicle", existing_cv, "color"),
                "status": "Active"
            })
        else:
            try:
                cv_doc = frappe.get_doc({
                    "doctype": "Customer Vehicle",
                    "name": clean_name,
                    "plate_no": plate_no,
                    "customer": customer_docname,
                    "customer_name": cust_name,
                    "contact_no": phone,
                    "email": email,
                    "company": "ULTRA MRF",
                    "status": "Active",
                    "make": make,
                    "model": model_docname or model,
                    "year_model": int(year) if year and str(year).isdigit() else 0,
                    "color": color,
                    "vin": vin or "-",
                    "engine_no": engine_no or "",
                    "fuel_type": fuel_type,
                    "transmission": transmission,
                    "current_mileage": current_mileage
                })
                cv_doc.insert(ignore_permissions=True)
            except Exception:
                pass

    frappe.db.commit()

    return build_customer_portal_payload(
        customer_name=cust_name,
        customer_docname=customer_docname,
        phone=phone,
        email=email,
        address=address,
        just_registered=True
    )

# ── 4. ADD NEW VEHICLE TO LOGGED-IN CUSTOMER ──
def handle_add_customer_vehicle(data):
    form = frappe.form_dict or {}
    cust_name = str(data.get("customer_name") or form.get("customer_name") or "").strip().upper()
    phone = str(data.get("customer_phone") or form.get("customer_phone") or "").strip()
    email = str(data.get("customer_email") or form.get("customer_email") or "").strip()
    customer_docname = data.get("customer_docname") or form.get("customer_docname") or cust_name
    
    plate_no = str(data.get("plate_no") or form.get("plate_no") or "").strip().upper()
    make = str(data.get("make") or form.get("make") or "").strip().upper()
    model = str(data.get("model") or form.get("model") or "").strip().upper()
    year = str(data.get("year") or form.get("year") or "").strip()
    color = str(data.get("color") or form.get("color") or "").strip().upper()
    fuel_type = str(data.get("fuel_type") or form.get("fuel_type") or "Gasoline").strip()
    transmission = str(data.get("transmission") or form.get("transmission") or "Automatic").strip()
    vin = str(data.get("vin") or form.get("vin") or "-").strip()
    engine_no = str(data.get("engine_no") or form.get("engine_no") or "").strip()
    current_mileage = float(data.get("current_mileage") or form.get("current_mileage") or 0.0)

    if not plate_no:
        return {"success": False, "error": "Vehicle Plate Number is required."}

    model_docname = ensure_vehicle_model(make, model)
    clean_name = plate_no.replace(" ", "").replace("-", "")

    if frappe.db.exists("Customer Vehicle", clean_name):
        frappe.db.set_value("Customer Vehicle", clean_name, {
            "customer": customer_docname,
            "customer_name": cust_name,
            "contact_no": phone,
            "email": email,
            "make": make,
            "model": model_docname or model,
            "year_model": int(year) if year and str(year).isdigit() else 0,
            "color": color,
            "vin": vin or "-",
            "status": "Active"
        })
    elif frappe.db.exists("Customer Vehicle", plate_no):
        frappe.db.set_value("Customer Vehicle", plate_no, {
            "customer": customer_docname,
            "customer_name": cust_name,
            "contact_no": phone,
            "email": email,
            "make": make,
            "model": model_docname or model,
            "year_model": int(year) if year and str(year).isdigit() else 0,
            "color": color,
            "vin": vin or "-",
            "status": "Active"
        })
    else:
        cv_doc = frappe.get_doc({
            "doctype": "Customer Vehicle",
            "name": clean_name,
            "plate_no": plate_no,
            "customer": customer_docname,
            "customer_name": cust_name,
            "contact_no": phone,
            "email": email,
            "company": "ULTRA MRF",
            "status": "Active",
            "make": make,
            "model": model_docname or model,
            "year_model": int(year) if year and str(year).isdigit() else 0,
            "color": color,
            "vin": vin or "-",
            "engine_no": engine_no or "",
            "fuel_type": fuel_type,
            "transmission": transmission,
            "current_mileage": current_mileage
        })
        cv_doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return build_customer_portal_payload(
        customer_name=cust_name,
        customer_docname=customer_docname,
        phone=phone,
        email=email
    )

# ── 5. BOOK APPOINTMENT WITH MULTI-BRANCH SELECTION ──
def handle_book_appointment(data):
    form = frappe.form_dict or {}
    raw_branches = data.get("branches") or form.get("branches")
    branches = []
    if raw_branches:
        if isinstance(raw_branches, str):
            try:
                parsed_b = frappe.parse_json(raw_branches)
                if isinstance(parsed_b, list):
                    branches = [str(x).strip() for x in parsed_b if str(x).strip()]
                elif isinstance(parsed_b, str):
                    branches = [parsed_b.strip()]
            except Exception:
                branches = [raw_branches.strip()]
        elif isinstance(raw_branches, list):
            branches = [str(x).strip() for x in raw_branches if str(x).strip()]

    single_b = data.get("branch") or form.get("branch")
    if not branches and single_b and isinstance(single_b, str):
        branches = [single_b.strip()]

    if not branches:
        branches = ["Ultra MRF Dau Main"]

    # Ensure primary branch is valid Company string
    primary_branch = branches[0]
    if not frappe.db.exists("Company", primary_branch):
        found_comp = frappe.db.get_value("Company", {"company_name": primary_branch}, "name")
        if found_comp:
            primary_branch = found_comp
        else:
            primary_branch = "ULTRA MRF"

    multi_branch_str = ", ".join(branches)

    apt_date = data.get("appointment_date") or form.get("appointment_date")
    raw_time = data.get("appointment_time") or form.get("appointment_time")
    apt_time = normalize_time_slot(raw_time)
    service_type = data.get("service_type") or form.get("service_type") or "PMS / Change Oil"
    
    cust_name = str(data.get("customer_name") or form.get("customer_name") or "").strip().upper()
    phone = str(data.get("customer_phone") or data.get("phone") or form.get("customer_phone") or form.get("phone") or "").strip()
    email = str(data.get("customer_email") or data.get("email") or form.get("customer_email") or form.get("email") or "").strip()
    
    plate_no = str(data.get("plate_no") or form.get("plate_no") or "").strip().upper()
    make = str(data.get("make") or form.get("make") or "").strip().upper()
    model_input = str(data.get("model") or form.get("model") or "").strip().upper()
    year = str(data.get("year") or form.get("year") or "").strip()
    color = str(data.get("color") or form.get("color") or "").strip().upper()
    user_notes = str(data.get("notes") or form.get("notes") or "").strip()

    if not cust_name or not phone or not plate_no or not apt_date:
        return {"success": False, "error": "Customer Name, Mobile Phone, Vehicle Plate No, and Date are required."}

    # Customer Master
    customer_docname = None
    if frappe.db.exists("Customer", cust_name):
        customer_docname = cust_name
    else:
        found_c = frappe.db.get_value("Customer", {"custom_mobile_no": phone}, "name")
        if not found_c:
            found_c = frappe.db.get_value("Customer", {"mobile_no": phone}, "name")
        if found_c:
            customer_docname = found_c
        else:
            try:
                new_c = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": cust_name,
                    "customer_type": "Individual",
                    "customer_group": "Individual",
                    "territory": "All Territories",
                    "custom_mobile_no": phone,
                    "custom_email_address": email,
                    "custom_address_text": ""
                })
                new_c.insert(ignore_permissions=True)
                customer_docname = new_c.name
            except Exception as ex:
                customer_docname = cust_name

    model_docname = ensure_vehicle_model(make, model_input)
    clean_plate = plate_no.replace(" ", "").replace("-", "")

    # Customer Vehicle
    vehicle_docname = None
    if frappe.db.exists("Customer Vehicle", clean_plate):
        vehicle_docname = clean_plate
    elif frappe.db.exists("Customer Vehicle", plate_no):
        vehicle_docname = plate_no
    else:
        found_cv = frappe.db.get_value("Customer Vehicle", {"plate_no": plate_no}, "name")
        if found_cv:
            vehicle_docname = found_cv
        else:
            try:
                cv = frappe.get_doc({
                    "doctype": "Customer Vehicle",
                    "name": clean_plate,
                    "plate_no": plate_no,
                    "customer": customer_docname,
                    "customer_name": cust_name,
                    "contact_no": phone,
                    "email": email,
                    "company": "ULTRA MRF",
                    "status": "Active",
                    "make": make,
                    "model": model_docname or model_input,
                    "year_model": int(year) if year and str(year).isdigit() else 0,
                    "color": color
                })
                cv.insert(ignore_permissions=True)
                vehicle_docname = cv.name
            except Exception:
                vehicle_docname = clean_plate

    notes_parts = []
    if len(branches) > 1:
        notes_parts.append(f"Preferred Branch Options: {multi_branch_str}")
    if user_notes:
        notes_parts.append(f"Customer Notes: {user_notes}")
    combined_notes = " | ".join(notes_parts)

    apt_doc = frappe.get_doc({
        "doctype": "Vehicle Appointment",
        "branch": primary_branch,
        "appointment_date": apt_date,
        "appointment_time": apt_time,
        "status": "Confirmed",
        "customer": customer_docname,
        "customer_name": cust_name,
        "customer_phone": phone,
        "customer_email": email,
        "vehicle": vehicle_docname or clean_plate,
        "plate_no": plate_no,
        "make": make,
        "model": model_docname or model_input,
        "year": str(year) if year else "",
        "color": color,
        "service_type": service_type,
        "notes": combined_notes
    })
    apt_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    branch_info = BRANCH_METADATA.get(primary_branch, {})

    return {
        "success": True,
        "appointment_id": apt_doc.name,
        "branch": primary_branch,
        "selected_branches": branches,
        "branch_title": branch_info.get("title", primary_branch),
        "branch_address": branch_info.get("address", ""),
        "branch_phone": branch_info.get("phone", ""),
        "appointment_date": apt_date,
        "appointment_time": apt_time,
        "service_type": service_type,
        "customer_name": cust_name,
        "plate_no": plate_no,
        "vehicle_display": f"{make} {model_input} ({plate_no})" if make or model_input else plate_no,
        "message": f"Appointment {apt_doc.name} successfully scheduled at {primary_branch} for {cust_name} on {apt_date} ({apt_time})."
    }

# ── 6. BUILD ISOLATED CUSTOMER PAYLOAD (Invoices, Vehicles, Appointments) ──
def build_customer_portal_payload(customer_name, customer_docname=None, phone="", email="", address="", just_registered=False):
    cust_name = str(customer_name or "").strip().upper()
    customer_docname = customer_docname or cust_name

    # 1. Fetch strictly customer vehicles
    vehicles = []
    vehicle_records = frappe.db.get_all(
        "Customer Vehicle",
        filters={"customer": ["in", [customer_docname, cust_name]]},
        fields=["name", "plate_no", "make", "model", "year_model", "color", "vin", "engine_no", "fuel_type", "transmission", "current_mileage", "status", "total_spent", "total_visits", "unpaid_balance", "last_service_date"]
    )
    if not vehicle_records and phone:
        vehicle_records = frappe.db.get_all(
            "Customer Vehicle",
            filters={"contact_no": phone},
            fields=["name", "plate_no", "make", "model", "year_model", "color", "vin", "engine_no", "fuel_type", "transmission", "current_mileage", "status", "total_spent", "total_visits", "unpaid_balance", "last_service_date"]
        )

    plates_list = []
    for v in vehicle_records:
        p = v.get("plate_no") or v.get("name")
        plates_list.append(p)
        clean_p = p.replace(" ", "").replace("-", "")
        if clean_p not in plates_list:
            plates_list.append(clean_p)
        vehicles.append({
            "name": v.get("name"),
            "plate_no": p,
            "make": v.get("make") or "",
            "model": v.get("model") or "",
            "year": v.get("year_model") or "",
            "color": v.get("color") or "",
            "vin": v.get("vin") or "-",
            "engine_no": v.get("engine_no") or "",
            "fuel_type": v.get("fuel_type") or "Gasoline",
            "transmission": v.get("transmission") or "Automatic",
            "mileage": v.get("current_mileage") or 0.0,
            "status": v.get("status") or "Active",
            "total_spent": float(v.get("total_spent") or 0.0),
            "total_visits": int(v.get("total_visits") or 0),
            "unpaid_balance": float(v.get("unpaid_balance") or 0.0),
            "last_service_date": str(v.get("last_service_date") or "")
        })

    # 2. Fetch Strictly ISOLATED Invoices for this customer only
    invoices = []
    si_records = frappe.db.get_all(
        "Sales Invoice",
        filters={"customer": ["in", [customer_docname, cust_name]]},
        fields=["name", "customer", "customer_name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "company", "currency"],
        order_by="posting_date desc",
        limit_page_length=50
    )
    
    pos_records = []
    if frappe.db.exists("DocType", "POS Invoice"):
        try:
            pos_records = frappe.db.get_all(
                "POS Invoice",
                filters={"customer": ["in", [customer_docname, cust_name]]},
                fields=["name", "customer", "customer_name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "company", "currency"],
                order_by="posting_date desc",
                limit_page_length=50
            )
        except Exception:
            pos_records = []

    all_raw_invoices = si_records + pos_records
    total_spent_calc = 0.0
    total_outstanding_calc = 0.0

    for inv in all_raw_invoices:
        inv_name = inv.get("name")
        gt = float(inv.get("grand_total") or 0.0)
        outst = float(inv.get("outstanding_amount") or 0.0)
        total_spent_calc += gt
        total_outstanding_calc += outst

        items = []
        try:
            is_si = inv in si_records
            doctype_name = "Sales Invoice Item" if is_si else "POS Invoice Item"
            items = frappe.db.get_all(
                doctype_name,
                filters={"parent": inv_name},
                fields=["item_code", "item_name", "qty", "rate", "amount", "description"]
            )
        except Exception:
            items = []

        invoices.append({
            "invoice_number": inv_name,
            "date": str(inv.get("posting_date") or ""),
            "due_date": str(inv.get("due_date") or ""),
            "company": inv.get("company") or "ULTRA MRF",
            "grand_total": gt,
            "outstanding_amount": outst,
            "status": inv.get("status") or ("Paid" if outst == 0 else "Unpaid"),
            "items": items
        })

    # 3. Fetch Strictly ISOLATED Appointments
    appointments = []
    apt_records = []
    if plates_list:
        apt_records = frappe.db.get_all(
            "Vehicle Appointment",
            filters={"plate_no": ["in", plates_list]},
            fields=["name", "branch", "appointment_date", "appointment_time", "status", "service_type", "plate_no", "make", "model", "notes", "creation"],
            order_by="appointment_date desc",
            limit_page_length=50
        )
    if not apt_records:
        apt_records = frappe.db.get_all(
            "Vehicle Appointment",
            filters={"customer": ["in", [customer_docname, cust_name]]},
            fields=["name", "branch", "appointment_date", "appointment_time", "status", "service_type", "plate_no", "make", "model", "notes", "creation"],
            order_by="appointment_date desc",
            limit_page_length=50
        )

    for a in apt_records:
        appointments.append({
            "appointment_id": a.get("name"),
            "branch": a.get("branch"),
            "appointment_date": str(a.get("appointment_date") or ""),
            "appointment_time": a.get("appointment_time") or "",
            "service_type": a.get("service_type") or "PMS / Change Oil",
            "status": a.get("status") or "Confirmed",
            "plate_no": a.get("plate_no") or "",
            "vehicle": f"{a.get('make','')} {a.get('model','')}".strip(),
            "notes": a.get("notes") or ""
        })

    loyalty_points = int(total_spent_calc // 100)
    loyalty_tier = "Standard"
    if total_spent_calc >= 100000:
        loyalty_tier = "Diamond VIP"
    elif total_spent_calc >= 50000:
        loyalty_tier = "Platinum"
    elif total_spent_calc >= 20000:
        loyalty_tier = "Gold"
    elif total_spent_calc >= 5000:
        loyalty_tier = "Silver"

    return {
        "success": True,
        "just_registered": just_registered,
        "customer": {
            "name": cust_name,
            "docname": customer_docname,
            "phone": phone,
            "email": email,
            "address": address,
            "loyalty_tier": loyalty_tier,
            "loyalty_points": loyalty_points,
            "total_spent": total_spent_calc,
            "unpaid_balance": total_outstanding_calc,
            "total_invoices": len(invoices),
            "total_vehicles": len(vehicles),
            "total_appointments": len(appointments)
        },
        "vehicles": vehicles,
        "invoices": invoices,
        "appointments": appointments,
        "branches": handle_get_branches().get("branches", []),
        "services": SERVICE_TYPES,
        "time_slots": TIME_SLOTS
    }

# ── DISPATCH ──
req_path = (frappe.local.request.path or "") if frappe.local.request else ""
form = frappe.form_dict or {}
cmd = form.get("cmd") or ""

if "get_portal_branches" in req_path or cmd == "vehicle_management.api.portal.get_portal_branches":
    frappe.response["message"] = handle_get_branches()
elif "get_vehicle_reference_data" in req_path or cmd == "vehicle_management.api.portal.get_vehicle_reference_data":
    frappe.response["message"] = handle_get_reference_data()
elif "customer_login" in req_path or cmd == "vehicle_management.api.portal.customer_login":
    ident = form.get("identifier")
    if not ident and isinstance(form.get("data"), dict):
        ident = form.get("data", {}).get("identifier")
    frappe.response["message"] = handle_customer_login(ident)
elif "register_customer_profile" in req_path or cmd == "vehicle_management.api.portal.register_customer_profile":
    pdata = form.get("data") if isinstance(form.get("data"), dict) else form
    frappe.response["message"] = handle_register_customer_profile(pdata)
elif "add_customer_vehicle" in req_path or cmd == "vehicle_management.api.portal.add_customer_vehicle":
    pdata = form.get("data") if isinstance(form.get("data"), dict) else form
    frappe.response["message"] = handle_add_customer_vehicle(pdata)
elif "lookup_customer_profile" in req_path or cmd == "vehicle_management.api.portal.lookup_customer_profile" or "get_customer_data" in req_path or cmd == "vehicle_management.api.portal.get_customer_data":
    ident = form.get("identifier")
    if not ident and isinstance(form.get("data"), dict):
        ident = form.get("data", {}).get("identifier")
    frappe.response["message"] = handle_customer_login(ident)
elif "book_appointment" in req_path or cmd == "vehicle_management.api.portal.book_appointment":
    pdata = form.get("data") if isinstance(form.get("data"), dict) else form
    frappe.response["message"] = handle_book_appointment(pdata)
else:
    frappe.response["message"] = handle_get_branches()
'''

apis_to_register = [
    ("VM Portal Get Branches", "vehicle_management.api.portal.get_portal_branches", server_script_code),
    ("VM Portal Get Vehicle Reference Data", "vehicle_management.api.portal.get_vehicle_reference_data", server_script_code),
    ("VM Portal Customer Login", "vehicle_management.api.portal.customer_login", server_script_code),
    ("VM Portal Register Customer Profile", "vehicle_management.api.portal.register_customer_profile", server_script_code),
    ("VM Portal Add Customer Vehicle", "vehicle_management.api.portal.add_customer_vehicle", server_script_code),
    ("VM Portal Lookup Customer Profile", "vehicle_management.api.portal.lookup_customer_profile", server_script_code),
    ("VM Portal Get Customer Data", "vehicle_management.api.portal.get_customer_data", server_script_code),
    ("VM Portal Book Appointment", "vehicle_management.api.portal.book_appointment", server_script_code),
]

for name, api_method, sc in apis_to_register:
    payload = {
        'doctype': 'Server Script',
        'name': name,
        'script_type': 'API',
        'api_method': api_method,
        'allow_guest': 1,
        'disabled': 0,
        'script': sc
    }
    chk = s.get(f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}')
    if chk.status_code == 200:
        s.put(f'{URL}/api/resource/Server%20Script/{urllib.parse.quote(name)}', json={'script': sc, 'disabled': 0, 'allow_guest': 1})
        print(f"[OK] Updated API: {name}")
    else:
        s.post(f'{URL}/api/resource/Server%20Script', json=payload)
        print(f"[OK] Created API: {name}")

print("\nServer scripts fully deployed.")
