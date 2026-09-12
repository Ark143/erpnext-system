import requests
import json
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

portal_server_script_body = """
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

SERVICE_PACKAGES = [
    {
        "id": "pms-oil",
        "name": "PMS & Synthetic Oil Change Package",
        "category": "PMS / Change Oil",
        "price_range": "PHP 2,500 - PHP 5,800",
        "est_time": "45 - 60 mins",
        "icon": "fa-oil-can",
        "description": "Full synthetic motor oil, OEM oil filter replacement, 35-point safety inspection, engine bay cleaning, and fluid top-ups."
    },
    {
        "id": "tire-mount-balance",
        "name": "Tire Mounting, Balancing & Nitrogen",
        "category": "Tires & Wheels",
        "price_range": "PHP 800 - PHP 1,600",
        "est_time": "30 - 45 mins",
        "icon": "fa-circle-notch",
        "description": "Computerized dynamic balancing, precision weight calibration, tubeless valve stem inspection, and pure nitrogen inflation."
    },
    {
        "id": "laser-alignment",
        "name": "3D High-Definition Laser Alignment",
        "category": "Wheel Alignment & Balancing",
        "price_range": "PHP 1,200 - PHP 2,200",
        "est_time": "40 - 60 mins",
        "icon": "fa-crosshairs",
        "description": "Digital camber, caster, toe calibration with live steering angle sensor reset for smooth handling and even tire wear."
    },
    {
        "id": "brake-overhaul",
        "name": "Brake System Service & Rotor Resurfacing",
        "category": "Brake System Service",
        "price_range": "PHP 1,800 - PHP 4,500",
        "est_time": "60 - 90 mins",
        "icon": "fa-stop-circle",
        "description": "Brake pad replacement, caliper pin lubrication, rotor disc resurfacing/machining, and DOT4 brake fluid flush."
    },
    {
        "id": "underchassis-check",
        "name": "Underchassis & Suspension Refresh",
        "category": "Underchassis & Suspension",
        "price_range": "PHP 2,500 - PHP 8,500",
        "est_time": "1 - 3 hours",
        "icon": "fa-cogs",
        "description": "Tie rod, ball joint, stabilizer link, control arm bushing, and shock absorber inspection and precision replacement."
    },
    {
        "id": "ac-cleaning",
        "name": "Car Aircon Treatment & Freon Recharge",
        "category": "Car Aircon Service",
        "price_range": "PHP 1,500 - PHP 4,800",
        "est_time": "60 - 90 mins",
        "icon": "fa-snowflake",
        "description": "Evaporator antibacterial foam cleaning, cabin filter replacement, R134a/R1234yf leak testing, and vacuum charging."
    },
    {
        "id": "engine-diagnostics",
        "name": "Computerized Engine Scan & Tune-Up",
        "category": "Engine Diagnostics & Tune-up",
        "price_range": "PHP 1,500 - PHP 4,000",
        "est_time": "45 - 90 mins",
        "icon": "fa-laptop-code",
        "description": "OBD2 live sensor diagnostics, spark plug inspection/replacement, throttle body cleaning, and fuel system optimization."
    },
    {
        "id": "detailing-wash",
        "name": "Premium Auto Spa & Interior Sanitize",
        "category": "Car Wash & Detailing",
        "price_range": "PHP 800 - PHP 3,500",
        "est_time": "60 - 120 mins",
        "icon": "fa-shower",
        "description": "pH-neutral foam wash, tire dressing, interior deep vacuum, upholstery steam sanitation, and ozone odor elimination."
    }
]

def handle_get_branches():
    companies = frappe.get_all("Company", filters={"is_group": 0}, fields=["name", "company_name", "abbr"], order_by="name asc")
    branches = []
    for c in companies:
        name = c.name
        if name == "My Company":
            continue
        meta = BRANCH_METADATA.get(name, {
            "title": name,
            "address": "Pampanga, Philippines",
            "phone": "(045) 892-0000",
            "email": "service@ultramrf.ph",
            "hours": "Mon - Sat: 8:00 AM - 5:30 PM",
            "bays": 8,
            "badge": "Authorized Service Center",
            "services": ["PMS / Change Oil", "Tires & Wheels", "Wheel Alignment", "Brakes"]
        })
        branches.append({
            "name": name,
            "company_name": c.company_name or name,
            "abbr": c.abbr or "",
            "title": meta.get("title"),
            "address": meta.get("address"),
            "phone": meta.get("phone"),
            "email": meta.get("email"),
            "hours": meta.get("hours"),
            "bays": meta.get("bays"),
            "badge": meta.get("badge"),
            "services": meta.get("services", [])
        })
    return {
        "branches": branches,
        "default_branch": "Ultra MRF Dau Main" if any(b["name"] == "Ultra MRF Dau Main" for b in branches) else (branches[0]["name"] if branches else "")
    }

def handle_get_reference_data():
    makes = frappe.get_all("Vehicle Make", fields=["name", "make_name"], order_by="name asc")
    if not makes:
        makes = [{"name": m, "make_name": m} for m in [
            "TOYOTA", "MITSUBISHI", "HONDA", "NISSAN", "FORD", "HYUNDAI", 
            "ISUZU", "MAZDA", "SUZUKI", "KIA", "CHEVROLET", "MG", "GEELY", "SUBARU", "BMW", "MERCEDES-BENZ"
        ]]
        
    models = frappe.get_all("Vehicle Model", fields=["name", "make", "model_name", "category"], order_by="make asc, model_name asc", limit_page_length=500)
    
    slots = [
        {"id": "slot-1", "time": "08:00 AM - 10:00 AM", "period": "Morning", "label": "Morning (8:00 AM - 10:00 AM)"},
        {"id": "slot-2", "time": "10:00 AM - 12:00 PM", "period": "Morning", "label": "Morning (10:00 AM - 12:00 PM)"},
        {"id": "slot-3", "time": "01:00 PM - 03:00 PM", "period": "Afternoon", "label": "Afternoon (1:00 PM - 3:00 PM)"},
        {"id": "slot-4", "time": "03:00 PM - 05:00 PM", "period": "Afternoon", "label": "Afternoon (3:00 PM - 5:00 PM)"}
    ]
    
    return {
        "makes": [m.get("make_name") or m.get("name") for m in makes],
        "models": models,
        "service_packages": SERVICE_PACKAGES,
        "time_slots": slots
    }

def handle_lookup_profile(identifier):
    if not identifier:
        return {"found": False, "message": "Identifier required"}
        
    ident = str(identifier).strip().upper()
    cust_name = None
    target_vehicle_name = None
    
    # 1. Search Customer table
    cust_match = frappe.get_all("Customer", filters={"name": ["like", f"%{ident}%"]}, fields=["name", "customer_name", "mobile_no", "email_id", "customer_group", "territory"], limit=1)
    if not cust_match:
        cust_match = frappe.get_all("Customer", filters={"customer_name": ["like", f"%{ident}%"]}, fields=["name", "customer_name", "mobile_no", "email_id", "customer_group", "territory"], limit=1)
    if not cust_match:
        cust_match = frappe.get_all("Customer", filters={"mobile_no": ["like", f"%{ident}%"]}, fields=["name", "customer_name", "mobile_no", "email_id", "customer_group", "territory"], limit=1)

    if cust_match:
        cust_name = cust_match[0].name
    else:
        # Check Customer Vehicle
        veh_match = frappe.get_all("Customer Vehicle", filters={"plate_no": ["like", f"%{ident}%"]}, fields=["name", "customer", "customer_name", "plate_no"], limit=1)
        if veh_match:
            cust_name = veh_match[0].customer
            target_vehicle_name = veh_match[0].name

    if not cust_name:
        jo_match = frappe.get_all("Vehicle Job Order", filters={"plate_no": ["like", f"%{ident}%"]}, fields=["customer", "customer_name", "vehicle", "plate_no"], limit=1)
        if jo_match:
            cust_name = jo_match[0].customer
            target_vehicle_name = jo_match[0].vehicle

    if not cust_name:
        return {
            "found": False,
            "message": f"No records found matching '{identifier}'. You can book as a new customer."
        }

    cust_doc = frappe.db.get_value("Customer", cust_name, ["name", "customer_name", "mobile_no", "email_id", "customer_group", "territory"], as_dict=True) or {"name": cust_name, "customer_name": cust_name, "mobile_no": "", "email_id": ""}
        
    vehicles = frappe.get_all("Customer Vehicle", filters={"customer": cust_name}, fields=["name", "plate_no", "make", "model", "year_model", "color", "current_mileage", "last_service_date"], order_by="creation desc")
    
    vehicle_names = [v.name for v in vehicles]
    if target_vehicle_name and target_vehicle_name not in vehicle_names:
        tv = frappe.db.get_value("Customer Vehicle", target_vehicle_name, ["name", "plate_no", "make", "model", "year_model", "color", "current_mileage", "last_service_date"], as_dict=True)
        if tv:
            vehicles.append(tv)
            vehicle_names.append(tv.name)
            
    # Estimates
    estimates = frappe.get_all("Vehicle Estimate", filters={"customer": cust_name, "docstatus": ["!=", 2]}, fields=["name", "company", "vehicle", "plate_no", "customer_name", "estimate_date", "status", "total_labor", "total_parts", "discount_amount", "grand_total", "valid_till"], order_by="estimate_date desc", limit=30)
    for e in estimates:
        e["services"] = frappe.get_all("Job Order Service Item", filters={"parent": e.name, "parenttype": "Vehicle Estimate"}, fields=["service_item", "description", "hours", "rate", "total_amount"])
        e["parts"] = frappe.get_all("Job Order Part Item", filters={"parent": e.name, "parenttype": "Vehicle Estimate"}, fields=["item_code", "item_name", "qty", "uom", "rate", "amount"])

    # Job Orders
    job_orders = frappe.get_all("Vehicle Job Order", filters={"customer": cust_name, "docstatus": ["!=", 2]}, fields=["name", "company", "vehicle", "plate_no", "customer_name", "job_order_date", "status", "payment_status", "total_labor", "total_parts", "discount_amount", "grand_total", "paid_amount", "time_out as completion_date", "service_advisor"], order_by="job_order_date desc", limit=50)
    for j in job_orders:
        j["services"] = frappe.get_all("Job Order Service Item", filters={"parent": j.name, "parenttype": "Vehicle Job Order"}, fields=["service_item", "description", "hours", "rate", "total_amount"])
        j["parts"] = frappe.get_all("Job Order Part Item", filters={"parent": j.name, "parenttype": "Vehicle Job Order"}, fields=["item_code", "item_name", "qty", "uom", "rate", "amount"])

    # Invoices
    invoices = frappe.get_all("Sales Invoice", filters={"customer": cust_name, "docstatus": ["!=", 2]}, fields=["name", "company", "posting_date", "due_date", "grand_total", "rounded_total", "paid_amount", "outstanding_amount", "status", "custom_vehicle_job_order as job_order"], order_by="posting_date desc", limit=50)

    # Appointments
    appointments = []
    try:
        appointments = frappe.get_all("Vehicle Appointment", filters={"customer": cust_name}, fields=["name", "branch", "appointment_date", "appointment_time", "status", "service_type", "plate_no", "make", "model", "notes", "job_order", "estimate", "creation"], order_by="appointment_date desc", limit=30)
    except Exception:
        appointments = []

    # Reminders
    reminders = []
    if vehicle_names:
        try:
            reminders = frappe.get_all("Vehicle Service Reminder", filters={"vehicle": ["in", vehicle_names]}, fields=["name", "vehicle", "reminder_type", "reminder_date", "due_km", "status", "description"], order_by="reminder_date asc", limit=20)
        except Exception:
            reminders = []

    total_spent = sum(float(j.get("grand_total") or 0.0) for j in job_orders)
    total_visits = len(job_orders)
    loyalty_tier = "VIP Platinum" if total_spent > 50000 or total_visits >= 10 else ("Gold Member" if total_spent > 20000 or total_visits >= 5 else "Silver Member")

    return {
        "found": True,
        "customer": {
            "name": cust_doc.get("name") or cust_name,
            "customer_name": cust_doc.get("customer_name") or cust_name,
            "mobile_no": cust_doc.get("mobile_no") or "",
            "email_id": cust_doc.get("email_id") or "",
            "customer_group": cust_doc.get("customer_group") or "Individual",
            "territory": cust_doc.get("territory") or "All Territories",
            "loyalty_tier": loyalty_tier,
            "total_spent": total_spent,
            "total_visits": total_visits
        },
        "vehicles": vehicles,
        "estimates": estimates,
        "job_orders": job_orders,
        "invoices": invoices,
        "appointments": appointments,
        "reminders": reminders
    }

def handle_book_appointment(raw_data):
    if isinstance(raw_data, str):
        try:
            raw_data = frappe.parse_json(raw_data)
        except Exception:
            raw_data = {}
            
    branch = raw_data.get("branch") or "Ultra MRF Dau Main"
    apt_date = raw_data.get("appointment_date")
    apt_time = raw_data.get("appointment_time") or "08:00 AM - 10:00 AM"
    service_type = raw_data.get("service_type") or "PMS / Change Oil"
    
    cust_name = str(raw_data.get("customer_name") or "").strip().upper()
    phone = str(raw_data.get("customer_phone") or "").strip()
    email = str(raw_data.get("customer_email") or "").strip()
    
    plate_no = str(raw_data.get("plate_no") or "").strip().upper()
    make = str(raw_data.get("make") or "").strip().upper()
    model_input = str(raw_data.get("model") or "").strip().upper()
    year = str(raw_data.get("year") or "").strip()
    color = str(raw_data.get("color") or "").strip().upper()
    notes = str(raw_data.get("notes") or "").strip()

    if not cust_name or not phone or not plate_no or not apt_date:
        return {"success": False, "error": "Missing required fields (Customer Name, Phone, Plate No, Date)"}

    # Ensure Make exists
    if make and not frappe.db.exists("Vehicle Make", make):
        try:
            frappe.get_doc({"doctype": "Vehicle Make", "name": make, "make_name": make}).insert(ignore_permissions=True)
        except Exception:
            pass

    # Ensure Model exists
    model_docname = None
    if make and model_input:
        target_model_name = f"{make}-{model_input}" if not model_input.startswith(make) else model_input
        if frappe.db.exists("Vehicle Model", target_model_name):
            model_docname = target_model_name
        elif frappe.db.exists("Vehicle Model", model_input):
            model_docname = model_input
        else:
            clean_m_name = model_input.replace(f"{make}-", "")
            try:
                vm = frappe.get_doc({
                    "doctype": "Vehicle Model",
                    "make": make,
                    "model_name": clean_m_name,
                    "category": "Sedan"
                })
                vm.insert(ignore_permissions=True)
                model_docname = vm.name
            except Exception:
                model_docname = None

    # Resolve Customer
    customer_docname = None
    existing_cust = frappe.get_all("Customer", filters={"customer_name": cust_name}, pluck="name", limit=1)
    if not existing_cust and phone:
        existing_cust = frappe.get_all("Customer", filters={"mobile_no": phone}, pluck="name", limit=1)
        
    if existing_cust:
        customer_docname = existing_cust[0]
        if phone:
            frappe.db.set_value("Customer", customer_docname, "mobile_no", phone, update_modified=False)
        if email:
            frappe.db.set_value("Customer", customer_docname, "email_id", email, update_modified=False)
    else:
        try:
            new_c = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cust_name,
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "All Territories",
                "mobile_no": phone,
                "email_id": email
            })
            new_c.insert(ignore_permissions=True)
            customer_docname = new_c.name
        except Exception:
            customer_docname = cust_name

    # Resolve Vehicle
    vehicle_docname = None
    existing_veh = frappe.get_all("Customer Vehicle", filters={"plate_no": plate_no}, pluck="name", limit=1)
    if existing_veh:
        vehicle_docname = existing_veh[0]
        if make or model_docname:
            frappe.db.set_value("Customer Vehicle", vehicle_docname, {
                "customer": customer_docname or "Cash Customer",
                "make": make,
                "model": model_docname or model_input,
                "year_model": year,
                "color": color
            }, update_modified=False)
    else:
        try:
            new_v = frappe.get_doc({
                "doctype": "Customer Vehicle",
                "plate_no": plate_no,
                "customer": customer_docname or "Cash Customer",
                "make": make,
                "model": model_docname or model_input,
                "year_model": year,
                "color": color
            })
            new_v.insert(ignore_permissions=True)
            vehicle_docname = new_v.name
        except Exception:
            vehicle_docname = None

    apt_doc = frappe.get_doc({
        "doctype": "Vehicle Appointment",
        "naming_series": "APT-.YYYY.-.#####",
        "branch": branch,
        "appointment_date": apt_date,
        "appointment_time": apt_time,
        "status": "Confirmed",
        "customer": customer_docname,
        "customer_name": cust_name,
        "customer_phone": phone,
        "customer_email": email,
        "vehicle": vehicle_docname,
        "plate_no": plate_no,
        "make": make,
        "model": model_docname,
        "year": year,
        "color": color,
        "service_type": service_type,
        "notes": notes
    })
    apt_doc.insert(ignore_permissions=True)

    branch_info = BRANCH_METADATA.get(branch, {})

    return {
        "success": True,
        "appointment_id": apt_doc.name,
        "branch": branch,
        "branch_title": branch_info.get("title", branch),
        "branch_address": branch_info.get("address", ""),
        "branch_phone": branch_info.get("phone", ""),
        "appointment_date": apt_date,
        "appointment_time": apt_time,
        "service_type": service_type,
        "customer_name": cust_name,
        "plate_no": plate_no,
        "vehicle_display": f"{make} {model_input} ({plate_no})" if make or model_input else plate_no,
        "message": f"Appointment {apt_doc.name} successfully booked for {cust_name} at {branch} on {apt_date} ({apt_time})."
    }

# Main Server Script Dispatcher
form_dict = frappe.form_dict or {}
req_path = (frappe.local.request.path or '') if frappe.local.request else ''

if 'get_portal_branches' in req_path or form_dict.get('cmd') == 'vehicle_management.api.portal.get_portal_branches':
    frappe.response['message'] = handle_get_branches()
elif 'get_vehicle_reference_data' in req_path or form_dict.get('cmd') == 'vehicle_management.api.portal.get_vehicle_reference_data':
    frappe.response['message'] = handle_get_reference_data()
elif 'lookup_customer_profile' in req_path or form_dict.get('cmd') == 'vehicle_management.api.portal.lookup_customer_profile':
    ident = form_dict.get('identifier')
    frappe.response['message'] = handle_lookup_profile(ident)
elif 'book_appointment' in req_path or form_dict.get('cmd') == 'vehicle_management.api.portal.book_appointment':
    raw_data = form_dict.get('data') or form_dict
    frappe.response['message'] = handle_book_appointment(raw_data)
else:
    frappe.response['message'] = handle_get_branches()
"""

apis_to_register = [
    ("VM Portal Get Branches", "vehicle_management.api.portal.get_portal_branches", portal_server_script_body),
    ("VM Portal Get Vehicle Reference Data", "vehicle_management.api.portal.get_vehicle_reference_data", portal_server_script_body),
    ("VM Portal Lookup Customer Profile", "vehicle_management.api.portal.lookup_customer_profile", portal_server_script_body),
    ("VM Portal Book Appointment", "vehicle_management.api.portal.book_appointment", portal_server_script_body),
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
        print(f"[OK] Updated Server Script API: {name} -> {api_method}")
    else:
        s.post(f'{URL}/api/resource/Server%20Script', json=payload)
        print(f"[OK] Created Server Script API: {name} -> {api_method}")

print("\nAll Backend Portal Server Scripts successfully updated with corrected fieldnames and Territory!")
