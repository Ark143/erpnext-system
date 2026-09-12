"""Marked live portal acceptance test; no invoices or payments are created.

Test credential/state file stays in the ignored private backup directory. Test
appointments are cancelled and the test account disabled by cleanup_portal_test.py.
"""
from pathlib import Path
import datetime
import json
import secrets
import requests

base='http://38.247.138.224:10017'
prefix='vehicle_management.secure_portal.'
session=requests.Session()
def call(method,data=None,verb='POST'):
    r=session.request(verb,base+'/api/method/'+method,data=data,timeout=30)
    if r.status_code!=200:
        print('FAIL',method,r.status_code,r.text[:600]);r.raise_for_status()
    msg=r.json().get('message',{})
    if isinstance(msg,dict) and msg.get('csrf_token'): session.headers['X-Frappe-CSRF-Token']=msg['csrf_token']
    return msg
refs=call(prefix+'get_vehicle_reference_data',verb='GET')
call(prefix+'get_customer_data',verb='GET')
model=next(m for m in refs['models'] if m['make']=='TOYOTA')
marker=secrets.token_hex(3).upper()
data=dict(customer_name='PORTAL QA '+marker,customer_phone='09990000000',
    customer_email='portal-qa-'+marker.lower()+'@example.invalid',password=secrets.token_urlsafe(24),
    plate_no='QA'+marker,make=model['make'],model=model['name'],year='2025',color='WHITE',fuel_type='Gasoline')
state=Path('backups/appointment_resume_20260913/live_test_state.json')
state.write_text(json.dumps(data))
assert call(prefix+'register_customer_profile',data)['registered']
print('PASS live registration')
call('login',dict(usr=data['customer_email'],pwd=data['password']))
session.headers.pop('X-Frappe-CSRF-Token',None)
profile=call(prefix+'get_customer_data',verb='GET');assert profile['success']
data['customer_docname']=profile['customer']['docname'];state.write_text(json.dumps(data))
print('PASS native login and session refresh')
assert len(call(prefix+'add_customer_vehicle',dict(data,plate_no='QB'+marker))['vehicles'])==2
print('PASS second vehicle')
booking=dict(plate_no=data['plate_no'],branches=json.dumps([refs['branches'][0]['key'],refs['branches'][1]['key']]),
    appointment_date=str(datetime.date.today()+datetime.timedelta(days=7)),appointment_time=refs['time_slots'][0],
    service_type=refs['services'][0]['name'],notes='PORTAL QA — acceptance test; cancel after verification')
apt=call(prefix+'book_appointment',booking);assert apt['status']=='Requested'
data['appointment_id']=apt['appointment_id'];state.write_text(json.dumps(data))
profile=call(prefix+'get_customer_data',verb='GET')
assert len(profile['appointments'])==1 and not profile['invoices']
print('PASS live booking and scoped history',apt['appointment_id'])
for doctype in ['Sales Invoice','POS Invoice','Customer Vehicle','Vehicle Appointment']:
    r=session.get(base+'/api/resource/'+doctype,timeout=20)
    assert r.status_code==403,(doctype,r.status_code)
    print('PASS unrestricted resource access denied',doctype)
call('logout')
session.headers.pop('X-Frappe-CSRF-Token',None)
assert not call(prefix+'get_customer_data',verb='GET')['authenticated']
print('PASS logout invalidates private access')
