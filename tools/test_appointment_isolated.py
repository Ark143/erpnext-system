"""Runs inside the VPS container against the dedicated, unserved portal test DB.

The deployment harness prepends PORTAL_SOURCE. No production writes or outbound jobs.
"""
import inspect
import json
import os
from pathlib import Path
import secrets
import sys
import textwrap
import types

import frappe

root=Path('/tmp/codex-portal-sites-20260913')
site=root/'codex-portal.local'
(site/'logs').mkdir(parents=True,exist_ok=True)
(root/'logs').mkdir(exist_ok=True)
(root.parent/'logs').mkdir(exist_ok=True)
source=Path('/workspace/frappe-bench/sites')
config=json.loads((source/'site1.local/site_config.json').read_text())
config.update(db_name='codex_portal_20260913',db_user='site1_local',pause_scheduler=1)
(site/'site_config.json').write_text(json.dumps(config));(site/'site_config.json').chmod(0o600)
(root/'common_site_config.json').write_bytes((source/'common_site_config.json').read_bytes())
(root/'common_site_config.json').chmod(0o600)
(root/'apps.txt').write_bytes((source/'apps.txt').read_bytes())
os.chdir(root)
frappe.init(site='codex-portal.local',sites_path=str(root));frappe.connect()
assert frappe.conf.db_name=='codex_portal_20260913'
frappe.set_user('Administrator')

# Match the scoped User hook patch, without modifying the production module on disk.
from frappe.core.doctype.user.user import User
method=textwrap.dedent(inspect.getsource(User.on_update))
method=method.replace('now = frappe.in_test or frappe.flags.in_install',
    'now = frappe.in_test or frappe.flags.in_install or self.flags.create_contact_now')
method=method.replace('self.__new_password','self._User__new_password')
scope=dict(User.on_update.__globals__);exec(method,scope);User.on_update=scope['on_update']
# No jobs or messages leave this isolated test process.
def no_outbound(*args,**kwargs):
    raise AssertionError('Unexpected outbound notification')
frappe.sendmail=no_outbound
frappe.publish_realtime=lambda *args,**kwargs: None

portal=types.ModuleType('vehicle_management.secure_portal')
sys.modules[portal.__name__]=portal
exec(PORTAL_SOURCE,portal.__dict__)
results=[]
def check(name, condition):
    assert condition, name
    results.append(name);print('PASS',name)
def denied(name, fn):
    try: fn()
    except (frappe.ValidationError,frappe.PermissionError,frappe.AuthenticationError):
        results.append(name);print('PASS',name)
    else: raise AssertionError(name)

try:
    frappe.local.request=None
    frappe.local.session_obj=types.SimpleNamespace(update=lambda **kwargs: None)
    frappe.set_user('Guest')
    check('guest cannot retrieve invoices',not portal.get_customer_data()['success'])
    check('public identifier cannot log in',not portal.customer_login(identifier='DANILO OBRA')['success'])
    refs=portal.get_vehicle_reference_data()
    model=next(m for m in refs['models'] if m.make and frappe.db.exists('Vehicle Make',m.make))
    marker=secrets.token_hex(4).upper()
    password=secrets.token_urlsafe(24)
    payload=dict(customer_name='PORTAL TEST '+marker,customer_phone='0999000'+marker,
        customer_email='portal-'+marker.lower()+'@example.invalid',password=password,
        plate_no='T'+marker,make=model.make,model=model.name,year='2025',color='WHITE',fuel_type='Gasoline')
    registered=portal.register_customer_profile(payload)
    check('registration creates customer and first vehicle atomically',registered['success'])
    from frappe.utils.password import check_password
    check('native password hash authenticates',check_password(payload['customer_email'],password)==payload['customer_email'])
    denied('wrong password rejected',lambda: check_password(payload['customer_email'],'wrong'))
    frappe.set_user(payload['customer_email'])
    profile=portal.get_customer_data();customer=profile['customer']['docname']
    check('account sees exactly its own first vehicle',len(profile['vehicles'])==1 and profile['vehicles'][0].plate_no==payload['plate_no'])
    second=dict(payload,plate_no='U'+marker,customer_docname='DANILO OBRA',customer_name='DANILO OBRA')
    updated=portal.add_customer_vehicle(second)
    check('forged customer ignored while adding second vehicle',len(updated['vehicles'])==2 and all(frappe.db.get_value('Customer Vehicle',v.name,'customer')==customer for v in updated['vehicles']))
    other=frappe.get_all('Customer Vehicle',filters={'customer':['!=',customer]},fields=['name','plate_no','customer'],limit=1)[0]
    denied('cannot take another customer vehicle',lambda: portal.add_customer_vehicle(dict(second,plate_no=other.plate_no)))
    from frappe.utils import add_days,nowdate
    booking=dict(plate_no=payload['plate_no'],branches=[refs['branches'][0]['key'],refs['branches'][1]['key']],
        appointment_date=add_days(nowdate(),3),appointment_time=refs['time_slots'][0],service_type=refs['services'][0]['name'],notes='Isolated acceptance test')
    apt=portal.book_appointment(booking)
    check('multi-branch request creates one correctly linked appointment',frappe.db.get_value('Vehicle Appointment',apt['appointment_id'],'customer')==customer and apt['status']=='Requested')
    denied('duplicate slot rejected',lambda: portal.book_appointment(booking))
    denied('past date rejected',lambda: portal.book_appointment(dict(booking,appointment_date='2020-01-01')))
    denied('invalid branch rejected',lambda: portal.book_appointment(dict(booking,branches=['Not a branch'])))
    denied('invalid service rejected',lambda: portal.book_appointment(dict(booking,service_type='Brakes')))
    denied('other customer vehicle cannot be booked',lambda: portal.book_appointment(dict(booking,plate_no=other.plate_no)))
    check('appointment history scoped to signed-in customer',len(portal.get_customer_data()['appointments'])==1)
    check('existing financial records not exposed',portal.get_customer_data()['invoices']==[])
    # Copy an existing invoice into the isolated test customer as a read fixture only.
    # No insert/submit bypass is presented as an accounting transaction test.
    invoice=frappe.db.get_value('Sales Invoice',{'docstatus':1},'name')
    if invoice:
        frappe.db.set_value('Sales Invoice',invoice,'customer',customer,update_modified=False)
        profile=portal.get_customer_data()
        check('invoice history and line items returned for owner',any(i['invoice_number']==invoice and i['items'] for i in profile['invoices']))
        frappe.db.set_value('Sales Invoice',invoice,'docstatus',0,update_modified=False)
        check('draft invoices excluded',not any(i['invoice_number']==invoice for i in portal.get_customer_data()['invoices']))
    frappe.set_user('Guest')
    denied('guest cannot add vehicle',lambda: portal.add_customer_vehicle(second))
    print(json.dumps({'passed':len(results),'checks':results}))
finally:
    frappe.db.rollback()
    frappe.destroy()
