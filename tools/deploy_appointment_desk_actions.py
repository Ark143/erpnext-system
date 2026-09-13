import requests
import json
import urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
r_login = s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})
print(f"[LOGIN] {r_login.status_code}")

client_script_code = '''
frappe.ui.form.on('Vehicle Appointment', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Status banner and indicators
            if (frm.doc.status === 'Confirmed') {
                frm.page.set_indicator(__('Confirmed Appointment'), 'green');
            } else if (frm.doc.status === 'In Progress') {
                frm.page.set_indicator(__('In Progress'), 'blue');
            } else if (frm.doc.status === 'Completed') {
                frm.page.set_indicator(__('Completed'), 'darkgrey');
            }

            // Group: "Create / Convert" Actions
            frm.add_custom_button(__('Vehicle Estimate'), function() {
                convertAppointment(frm, 'Vehicle Estimate');
            }, __('Create'));

            frm.add_custom_button(__('Vehicle Inspection'), function() {
                convertAppointment(frm, 'Vehicle Inspection');
            }, __('Create'));

            frm.add_custom_button(__('Vehicle Job Order'), function() {
                convertAppointment(frm, 'Vehicle Job Order');
            }, __('Create'));

            // Quick Jump buttons if already created
            if (frm.doc.job_order) {
                frm.add_custom_button(__('View Job Order (' + frm.doc.job_order + ')'), function() {
                    frappe.set_route('Form', 'Vehicle Job Order', frm.doc.job_order);
                }, __('Linked Docs'));
            }

            if (frm.doc.estimate) {
                frm.add_custom_button(__('View Estimate (' + frm.doc.estimate + ')'), function() {
                    frappe.set_route('Form', 'Vehicle Estimate', frm.doc.estimate);
                }, __('Linked Docs'));
            }
        }
    }
});

function convertAppointment(frm, targetDocType) {
    frappe.confirm(
        __('Create <b>' + targetDocType + '</b> for customer <b>' + (frm.doc.customer_name || frm.doc.customer) + '</b> (' + frm.doc.plate_no + ') at <b>' + (frm.doc.branch || 'Branch') + '</b>?'),
        function() {
            frappe.show_alert({
                message: __('Generating ' + targetDocType + '...'),
                indicator: 'blue'
            }, 3);

            frappe.call({
                method: 'vehicle_management.api.portal.convert_appointment_to_doc',
                args: {
                    appointment_id: frm.doc.name,
                    target_doctype: targetDocType
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: __(r.message.message || (targetDocType + ' created successfully!')),
                            indicator: 'green'
                        }, 5);
                        frm.reload_doc();
                        if (r.message.url) {
                            frappe.set_route('Form', targetDocType, r.message.doc_name);
                        }
                    } else {
                        frappe.msgprint({
                            title: __('Action Error'),
                            message: __(r.message ? r.message.error : 'Failed to create document.'),
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}
'''

script_name = "Vehicle Appointment Actions"
payload = {
    'doctype': 'Client Script',
    'name': script_name,
    'dt': 'Vehicle Appointment',
    'view': 'Form',
    'enabled': 1,
    'script': client_script_code
}

chk = s.get(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(script_name)}')
if chk.status_code == 200:
    res = s.put(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(script_name)}', json={'script': client_script_code, 'enabled': 1})
    print(f"[OK] Updated Client Script: {script_name} -> {res.status_code}")
else:
    res = s.post(f'{URL}/api/resource/Client%20Script', json=payload)
    print(f"[OK] Created Client Script: {script_name} -> {res.status_code}")

print("Vehicle Appointment Desk Actions successfully deployed.")
