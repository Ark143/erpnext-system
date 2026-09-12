"""Customer portal: native Frappe sessions and explicit Customer portal-user links.

Public identifiers never establish ownership. Writes are atomic request transactions.
"""
import math
import re

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import getdate, nowdate, validate_email_address

BRANCHES = (
    'Ultra MRF Dau Main', 'Ultra MRF Dau Annex', 'Ultra MRF San Fernando',
    'Ultra MRF Telebastagan', 'Ultra MRF Telebastagan 2', 'Automan Car Care Center',
    'Wheel Core', 'The Wheelhub',
)


def _text(data, key, required=False, max_length=140):
    value = str(data.get(key) or '').strip()
    if required and not value:
        frappe.throw(f'{key.replace("_", " ").title()} is required.')
    if len(value) > max_length or any(ord(c) < 32 and c not in '\n\t' for c in value):
        frappe.throw(f'Invalid {key.replace("_", " ")}.')
    return value


def _data(data=None, **kwargs):
    if isinstance(data, str):
        data = frappe.parse_json(data)
    return frappe._dict(data or kwargs)


def _customer():
    user = frappe.session.user
    if user == 'Guest':
        frappe.throw('Please sign in with your email and password.', frappe.AuthenticationError)
    names = frappe.get_all('Portal User', filters={'user': user, 'parenttype': 'Customer',
        'parentfield': 'portal_users'}, pluck='parent', limit_page_length=2)
    if len(names) != 1:
        frappe.throw('Ask your branch to link this account to one Customer profile.', frappe.PermissionError)
    return frappe.get_doc('Customer', names[0])


def _plate(value):
    value = re.sub(r'[\s-]', '', str(value or '').upper())
    if not re.fullmatch(r'[A-Z0-9]{3,20}', value):
        frappe.throw('Enter a valid plate or conduction sticker (3–20 letters or digits).')
    return value


def _lock_plate(plate):
    # Transaction-scoped database lock serializes formatted plate variants and retries.
    # PostgreSQL is the deployed database; MariaDB uses the unique document name.
    if frappe.db.db_type == 'postgres':
        frappe.db.sql('SELECT pg_advisory_xact_lock(hashtext(%s))', ('portal-plate:' + plate,))


def _find_vehicle(plate):
    vehicle = frappe.db.get_value('Customer Vehicle', {'plate_no': plate}, 'name')
    if vehicle:
        return vehicle
    # Legacy plates have spaces/dashes; exact normalization prevents duplicate ownership.
    rows = frappe.db.sql("""SELECT name FROM "tabCustomer Vehicle"
        WHERE upper(replace(replace(plate_no, ' ', ''), '-', ''))=%s LIMIT 1""", (plate,))
    return rows[0][0] if rows else None


def _vehicle(customer, data):
    plate = _plate(_text(data, 'plate_no', required=True))
    _lock_plate(plate)
    existing = _find_vehicle(plate)
    if existing:
        if frappe.db.get_value('Customer Vehicle', existing, 'customer') != customer.name:
            frappe.throw('This vehicle is already registered. Ask your branch to verify ownership.', frappe.PermissionError)
        return frappe.get_doc('Customer Vehicle', existing)
    make = _text(data, 'make', required=True)
    model = _text(data, 'model', required=True)
    if not frappe.db.exists('Vehicle Make', make):
        frappe.throw('Select an available vehicle make.')
    model_name = frappe.db.get_value('Vehicle Model', {'name': model, 'make': make}, 'name')
    if not model_name:
        model_name = frappe.db.get_value('Vehicle Model', {'model_name': model, 'make': make}, 'name')
    if not model_name:
        frappe.throw('Select a model for this make. Ask your branch to add a missing model.')
    year = _text(data, 'year')
    if year and (not year.isdigit() or not 1900 <= int(year) <= getdate(nowdate()).year + 1):
        frappe.throw('Enter a valid vehicle year.')
    try:
        mileage = float(data.get('current_mileage') or 0)
    except (ValueError, TypeError):
        frappe.throw('Mileage must be a non-negative number.')
    if not math.isfinite(mileage) or mileage < 0:
        frappe.throw('Mileage must be a non-negative number.')
    fuel = _text(data, 'fuel_type') or 'Gasoline'
    if fuel not in ('Gasoline', 'Diesel', 'Hybrid', 'Electric'):
        frappe.throw('Select an available fuel type.')
    return frappe.get_doc(dict(doctype='Customer Vehicle', plate_no=plate,
        customer=customer.name, customer_name=customer.customer_name,
        contact_no=customer.get('custom_mobile_no') or '', email=customer.get('custom_email_address') or '',
        make=make, model=model_name, year_model=int(year) if year else 0,
        color=_text(data, 'color'), fuel_type=fuel, current_mileage=mileage, status='Active'
    )).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True, methods=['GET'])
def get_portal_branches():
    branches = []
    for name in BRANCHES:
        company = frappe.db.get_value('Company', {'name': name, 'is_group': 0},
            ['name', 'phone_no', 'email'], as_dict=True)
        if company:
            branches.append(dict(key=name, title=name, phone=company.phone_no or '',
                email=company.email or '', address='', hours='Contact branch to confirm availability',
                badge='Appointment requests', services=[]))
    return dict(success=True, branches=branches)


@frappe.whitelist(allow_guest=True, methods=['GET'])
def get_vehicle_reference_data():
    meta = frappe.get_meta('Vehicle Appointment')
    return dict(success=True,
        makes=frappe.get_all('Vehicle Make', fields=['name', 'make_name'], order_by='name'),
        models=frappe.get_all('Vehicle Model', fields=['name', 'model_name', 'make'], order_by='name'),
        branches=get_portal_branches()['branches'],
        services=[dict(name=s, icon='fa-wrench', duration='', desc=s)
            for s in meta.get_field('service_type').options.splitlines() if s],
        time_slots=meta.get_field('appointment_time').options.splitlines())


@frappe.whitelist(allow_guest=True, methods=['POST'])
@rate_limit(limit=5, seconds=3600)
def register_customer_profile(data=None, **kwargs):
    data = _data(data, **kwargs)
    if frappe.session.user != 'Guest':
        frappe.throw('Sign out before creating another account.')
    name = _text(data, 'customer_name', required=True)
    phone = _text(data, 'customer_phone', required=True)
    email = validate_email_address(_text(data, 'customer_email', required=True).lower(), throw=True)
    password = str(data.get('password') or '')
    if len(password) < 12 or len(password) > 128:
        frappe.throw('Use a password between 12 and 128 characters.')
    plate = _plate(_text(data, 'plate_no', required=True))
    _lock_plate(plate)
    if frappe.db.exists('User', email) or _find_vehicle(plate):
        frappe.throw('An account or vehicle already exists. Sign in or ask your branch to link your profile.')
    # Never claim an existing Customer based on a public name, phone or email.
    for field, value in [('custom_email_address', email), ('custom_mobile_no', phone)]:
        if frappe.get_meta('Customer').has_field(field) and frappe.db.exists('Customer', {field: value}):
            frappe.throw('An existing profile needs branch verification before account linking.')
    user = frappe.get_doc(dict(doctype='User', email=email, first_name=name,
        enabled=1, user_type='Website User', send_welcome_email=0, new_password=password))
    user.flags.no_welcome_mail = True
    user.flags.create_contact_now = True
    user.insert(ignore_permissions=True)
    customer = frappe.get_doc(dict(doctype='Customer', customer_name=name,
        customer_type='Individual', customer_group='Individual', territory='All Territories',
        custom_mobile_no=phone, custom_email_address=email,
        custom_address_text=_text(data, 'customer_address', max_length=1000)))
    customer.append('portal_users', {'user': user.name})
    customer.insert(ignore_permissions=True)
    vehicle = _vehicle(customer, data)
    return dict(success=True, registered=True, vehicle=vehicle.name)


@frappe.whitelist(methods=['POST'])
def add_customer_vehicle(data=None, **kwargs):
    customer = _customer()
    _vehicle(customer, _data(data, **kwargs))
    return get_customer_data()


@frappe.whitelist(methods=['POST'])
def save_customer_vehicle(customer=None, vehicle_data=None, **kwargs):
    # Compatibility alias; supplied Customer never determines authorization.
    return add_customer_vehicle(vehicle_data, **kwargs)


@frappe.whitelist(methods=['POST'])
def book_appointment(data=None, **kwargs):
    customer = _customer()
    data = _data(data, **kwargs)
    plate = _plate(_text(data, 'plate_no', required=True))
    _lock_plate(plate)
    name = _find_vehicle(plate)
    if not name or frappe.db.get_value('Customer Vehicle', name, 'customer') != customer.name:
        frappe.throw('Select a vehicle from your garage.', frappe.PermissionError)
    vehicle = frappe.get_doc('Customer Vehicle', name)
    branches = data.get('branches') or [data.get('branch')]
    if isinstance(branches, str):
        branches = frappe.parse_json(branches)
    available = {b['key'] for b in get_portal_branches()['branches']}
    if not isinstance(branches, list) or not branches or any(b not in available for b in branches):
        frappe.throw('Select an available service branch.')
    branches = list(dict.fromkeys(branches))
    date = getdate(_text(data, 'appointment_date', required=True))
    if date <= getdate(nowdate()) or (date - getdate(nowdate())).days > 365:
        frappe.throw('Choose a date from tomorrow through the next 365 days.')
    slot = _text(data, 'appointment_time', required=True)
    service = _text(data, 'service_type', required=True)
    meta = frappe.get_meta('Vehicle Appointment')
    if slot not in meta.get_field('appointment_time').options.splitlines():
        frappe.throw('Select an available time slot.')
    if service not in meta.get_field('service_type').options.splitlines():
        frappe.throw('Select an available service.')
    if frappe.db.exists('Vehicle Appointment', {'vehicle': name, 'appointment_date': date,
            'appointment_time': slot, 'status': ['not in', ['Cancelled', 'No Show']]}):
        frappe.throw('This vehicle already has an appointment in that time slot.')
    notes = _text(data, 'notes', max_length=1000)
    if len(branches) > 1:
        notes = 'Alternative preferred branches: ' + ', '.join(branches[1:]) + '\n' + notes
    doc = frappe.get_doc(dict(doctype='Vehicle Appointment', branch=branches[0],
        appointment_date=date, appointment_time=slot, status='Requested',
        customer=customer.name, customer_name=customer.customer_name,
        customer_phone=customer.get('custom_mobile_no') or customer.mobile_no,
        customer_email=customer.get('custom_email_address') or customer.email_id,
        vehicle=vehicle.name, plate_no=vehicle.plate_no, make=vehicle.make, model=vehicle.model,
        year=str(vehicle.year_model or ''), color=vehicle.color, service_type=service, notes=notes))
    doc.insert(ignore_permissions=True)
    return dict(success=True, appointment_id=doc.name, status=doc.status,
        branch=doc.branch, selected_branches=branches)


@frappe.whitelist(allow_guest=True, methods=['GET', 'POST'])
def get_customer_data(**kwargs):
    from frappe.sessions import get_csrf_token
    csrf = get_csrf_token()
    if frappe.session.user == 'Guest':
        return dict(success=False, authenticated=False, csrf_token=csrf)
    customer = _customer()
    vehicles = frappe.get_all('Customer Vehicle', filters={'customer': customer.name},
        fields=['name', 'plate_no', 'make', 'model', 'year_model as year', 'color',
            'fuel_type', 'current_mileage as mileage', 'status'])
    invoices = []
    totals = {}
    for dt in ['Sales Invoice', 'POS Invoice']:
        filters = {'customer': customer.name, 'docstatus': 1}
        # Consolidated POS bills are represented by their submitted Sales Invoice.
        if dt == 'POS Invoice' and frappe.get_meta(dt).has_field('consolidated_invoice'):
            filters['consolidated_invoice'] = ['is', 'not set']
        for inv in frappe.get_all(dt, filters=filters, fields=['name', 'posting_date', 'due_date',
                'company', 'grand_total', 'outstanding_amount', 'currency', 'status'], order_by='posting_date desc'):
            items = frappe.get_all(dt + ' Item', filters={'parent': inv.name, 'parenttype': dt},
                fields=['item_code', 'item_name', 'qty', 'rate', 'amount'], order_by='idx')
            invoices.append(dict(invoice_number=inv.name, doctype=dt, date=str(inv.posting_date),
                due_date=str(inv.due_date or ''), company=inv.company, currency=inv.currency,
                grand_total=inv.grand_total, outstanding_amount=inv.outstanding_amount, status=inv.status, items=items))
            total = totals.setdefault(inv.currency, {'spent': 0, 'outstanding': 0})
            total['spent'] += float(inv.grand_total or 0)
            total['outstanding'] += float(inv.outstanding_amount or 0)
    invoices.sort(key=lambda inv: (inv['date'], inv['invoice_number']), reverse=True)
    appointments = frappe.get_all('Vehicle Appointment', filters={'customer': customer.name},
        fields=['name as appointment_id', 'branch', 'appointment_date', 'appointment_time',
            'status', 'service_type', 'plate_no', 'notes'], order_by='appointment_date desc')
    php = totals.get('PHP', {'spent': 0, 'outstanding': 0})
    return dict(success=True, authenticated=True, csrf_token=csrf,
        customer=dict(name=customer.customer_name, docname=customer.name,
            phone=customer.get('custom_mobile_no') or customer.mobile_no or '',
            email=customer.get('custom_email_address') or customer.email_id or '',
            address=customer.get('custom_address_text') or '', total_spent=php['spent'],
            unpaid_balance=php['outstanding'], total_invoices=len(invoices),
            total_vehicles=len(vehicles), total_appointments=len(appointments),
            loyalty_tier='Customer', loyalty_points=0),
        vehicles=vehicles, invoices=invoices, appointments=appointments, totals_by_currency=totals)


@frappe.whitelist(allow_guest=True, methods=['GET', 'POST'])
def customer_login(identifier=None, **kwargs):
    return get_customer_data()


@frappe.whitelist(allow_guest=True, methods=['GET', 'POST'])
def lookup_customer_profile(identifier=None, **kwargs):
    return get_customer_data()
