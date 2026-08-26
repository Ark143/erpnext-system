import frappe

def seed_data():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    # 1. Seed Makes
    makes = ["Toyota", "Honda", "Mitsubishi", "Ford", "Nissan", "Hyundai", "Isuzu", "Mazda", "Kia", "Suzuki", "Subaru", "BMW", "Mercedes-Benz"]
    for m in makes:
        if not frappe.db.exists("Vehicle Make", m):
            doc = frappe.new_doc("Vehicle Make")
            doc.make_name = m
            doc.insert(ignore_permissions=True)
            print(f"Created Make: {m}")

    # 2. Seed Models
    models = [
        ("Toyota", "Vios", "Sedan"),
        ("Toyota", "Fortuner", "SUV"),
        ("Toyota", "Hilux", "Pickup"),
        ("Toyota", "Innova", "Van"),
        ("Toyota", "Corolla Cross", "SUV"),
        ("Honda", "Civic", "Sedan"),
        ("Honda", "City", "Sedan"),
        ("Honda", "CR-V", "SUV"),
        ("Honda", "HR-V", "SUV"),
        ("Mitsubishi", "Montero Sport", "SUV"),
        ("Mitsubishi", "Strada / Triton", "Pickup"),
        ("Mitsubishi", "Xpander", "Van"),
        ("Mitsubishi", "Mirage G4", "Sedan"),
        ("Ford", "Ranger", "Pickup"),
        ("Ford", "Everest", "SUV"),
        ("Ford", "Territory", "SUV"),
        ("Nissan", "Navara", "Pickup"),
        ("Nissan", "Terra", "SUV"),
        ("Nissan", "Almera", "Sedan"),
        ("Isuzu", "D-Max", "Pickup"),
        ("Isuzu", "mu-X", "SUV")
    ]
    for make, model, cat in models:
        model_key = f"{make}-{model}"
        if not frappe.db.exists("Vehicle Model", model_key):
            doc = frappe.new_doc("Vehicle Model")
            doc.make = make
            doc.model_name = model
            doc.category = cat
            doc.insert(ignore_permissions=True)
            print(f"Created Model: {model_key}")

    # 3. Seed Inspection Templates
    templates = [
        {
            "name": "INSPECTION REPORT",
            "description": "Comprehensive Multi-Point Vehicle Health Inspection",
            "items": [
                {"category": "ENGINE COMPARTMENT", "item_name": "Engine Oil Level & Condition", "standard_description": "Check dip stick level, color, and viscosity."},
                {"category": "ENGINE COMPARTMENT", "item_name": "Engine Coolant Level", "standard_description": "Inspect radiator reserve tank level and cap seal."},
                {"category": "ENGINE COMPARTMENT", "item_name": "Brake Fluid Level", "standard_description": "Check master cylinder reservoir level and moisture content."},
                {"category": "ENGINE COMPARTMENT", "item_name": "Drive Belts (Serpentine / Timing)", "standard_description": "Inspect for cracks, fraying, and tension."},
                {"category": "ELECTRICAL & BATTERY", "item_name": "Battery Voltage & Terminals", "standard_description": "Test cold cranking amps and inspect for corrosion."},
                {"category": "ELECTRICAL & BATTERY", "item_name": "Headlights, Signal & Brake Lights", "standard_description": "Verify high/low beams, indicators, and hazard lights."},
                {"category": "BRAKES & SUSPENSION", "item_name": "Front Brake Pads & Rotors", "standard_description": "Measure pad thickness (>3mm) and check rotor surface."},
                {"category": "BRAKES & SUSPENSION", "item_name": "Rear Brake Pads / Shoes", "standard_description": "Check pad/shoe wear and drum/disc condition."},
                {"category": "BRAKES & SUSPENSION", "item_name": "Shock Absorbers & Struts", "standard_description": "Inspect for oil leaks and bushing damage."},
                {"category": "UNDERCARRIAGE & TIRES", "item_name": "Tire Tread Depth & Pressure", "standard_description": "Inspect all 4 tires + spare tire PSI and tread depth (>2mm)."},
                {"category": "UNDERCARRIAGE & TIRES", "item_name": "Exhaust System & Underbody", "standard_description": "Inspect for leaks, rust, and loose heat shields."}
            ]
        },
        {
            "name": "25 POINT CHECK-UP",
            "description": "Standard Quick 25-Point Safety and Maintenance Check",
            "items": [
                {"category": "FLUIDS", "item_name": "Motor Oil", "standard_description": "Level and condition check."},
                {"category": "FLUIDS", "item_name": "Transmission Fluid", "standard_description": "Level and clarity check."},
                {"category": "FLUIDS", "item_name": "Windshield Washer Fluid", "standard_description": "Top-up and spray nozzle test."},
                {"category": "SAFETY", "item_name": "Wiper Blades", "standard_description": "Check rubber tear and streak test."},
                {"category": "SAFETY", "item_name": "Horn Operation", "standard_description": "Audible check."},
                {"category": "BRAKES", "item_name": "Handbrake / Parking Brake", "standard_description": "Check engagement clicks and hold test."}
            ]
        },
        {
            "name": "PERIODIC MAINTENANCE SERVICE (PMS - HEAVY)",
            "description": "Heavy Maintenance (40k, 80k, 100k km intervals)",
            "items": [
                {"category": "MAJOR SERVICE", "item_name": "Spark Plugs / Glow Plugs", "standard_description": "Inspect gap and electrode wear."},
                {"category": "MAJOR SERVICE", "item_name": "Fuel Filter Replacement", "standard_description": "Inspect fuel flow and filter status."},
                {"category": "MAJOR SERVICE", "item_name": "Cabin & Air Filter", "standard_description": "Check dust accumulation and airflow."},
                {"category": "MAJOR SERVICE", "item_name": "Differential / Transfer Case Fluid", "standard_description": "Inspect fluid level and metal shavings on drain plug."},
                {"category": "MAJOR SERVICE", "item_name": "Wheel Alignment & Balancing", "standard_description": "Check camber/toe alignment and wheel weights."}
            ]
        }
    ]

    for t in templates:
        if not frappe.db.exists("Inspection Template", t["name"]):
            doc = frappe.new_doc("Inspection Template")
            doc.template_name = t["name"]
            doc.description = t["description"]
            for item in t["items"]:
                doc.append("items", item)
            doc.insert(ignore_permissions=True)
            print(f"Created Template: {t['name']}")

    # 4. Create sample customer if not exists
    cust_name = "Juan Dela Cruz"
    if not frappe.db.exists("Customer", {"customer_name": cust_name}):
        cust = frappe.new_doc("Customer")
        cust.customer_name = cust_name
        cust.customer_type = "Individual"
        cust.customer_group = "Individual"
        cust.territory = "All Territories"
        cust.mobile_no = "+63 917 123 4567"
        cust.email_id = "juan.delacruz@example.ph"
        cust.insert(ignore_permissions=True)
        print(f"Created Customer: {cust_name}")
    else:
        cust = frappe.get_doc("Customer", {"customer_name": cust_name})

    # 5. Create sample vehicle
    plate = "NAA 1234"
    if not frappe.db.exists("Customer Vehicle", plate):
        veh = frappe.new_doc("Customer Vehicle")
        veh.plate_no = plate
        veh.customer = cust.name
        veh.make = "Toyota"
        veh.model = "Toyota-Fortuner"
        veh.year_model = 2023
        veh.color = "Pearl White"
        veh.vin = "MHFJ1234567890123"
        veh.engine_no = "1GD-FTV-987654"
        veh.transmission = "Automatic"
        veh.cylinders = 4
        veh.fuel_type = "Diesel"
        veh.current_mileage = 15420.0
        veh.mileage_unit = "km"
        veh.registration_type = "Private"
        veh.insurance_company = "Standard Insurance"
        veh.insurance_expiry_date = "2027-05-15"
        veh.notes = "Preferred synthetic oil 5W-30. Keyless entry."
        veh.insert(ignore_permissions=True)
        print(f"Created Customer Vehicle: {plate}")
    else:
        veh = frappe.get_doc("Customer Vehicle", plate)

    # 6. Create sample Job Order
    if not frappe.db.exists("Vehicle Job Order", {"vehicle": veh.name}):
        jo = frappe.new_doc("Vehicle Job Order")
        jo.vehicle = veh.name
        jo.job_order_date = frappe.utils.nowdate()
        jo.status = "In Progress"
        jo.mileage = 15420.0
        jo.customer_complaint = "Routine 15,000 km PMS checkup and slight squeaking sound on front left brake."
        jo.append("services", {
            "description": "15k km Periodic Maintenance Service Labor",
            "mechanic": "Lead Mechanic (Mark)",
            "hours": 2.5,
            "rate": 800.0,
            "discount_amount": 100.0,
            "next_service_date": "2027-02-24"
        })
        jo.append("services", {
            "description": "Front Brake Cleaning & Caliper Inspection",
            "mechanic": "Junior Mechanic (Leo)",
            "hours": 1.0,
            "rate": 500.0,
            "discount_amount": 0.0
        })
        jo.append("parts", {
            "item_name": "Fully Synthetic Engine Oil 5W-30 (1L)",
            "part_no": "08880-83389",
            "qty": 7.0,
            "rate": 650.0,
            "discount_amount": 150.0
        })
        jo.append("parts", {
            "item_name": "Genuine Oil Filter Element",
            "part_no": "04152-YZZA1",
            "qty": 1.0,
            "rate": 480.0,
            "discount_amount": 0.0
        })
        jo.calculate_totals()
        jo.insert(ignore_permissions=True)
        print(f"Created Job Order: {jo.name} for {plate}")

    frappe.db.commit()
    print("Seed data completed successfully!")

if __name__ == "__main__":
    seed_data()
