import requests, json, urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# 1. Global Desk Uppercase Engine & Form Validator Client Script
global_uppercase_client_script = """
frappe.ui.form.on('*', {
    validate: function(frm) {
        if (!frm.doc || !frm.meta) return;
        
        // Excluded DocTypes that should preserve exact case
        var EXCLUDED_DOCTYPES = [
            'DocType', 'DocField', 'Custom Field', 'Property Setter', 'Client Script', 
            'Server Script', 'User', 'Role', 'Workflow', 'Print Format', 'Workspace',
            'Web Page', 'Email Account', 'Email Template', 'System Settings'
        ];
        if (EXCLUDED_DOCTYPES.indexOf(frm.doctype) !== -1) return;
        
        var EXCLUDED_FIELDNAMES = [
            'email', 'user_email', 'email_id', 'contact_email', 'password', 
            'api_key', 'api_secret', 'token', 'route', 'url', 'image', 'file',
            'script', 'css', 'json', 'py', 'js', 'html', 'code'
        ];
        
        function uppercase_fields(doc, meta) {
            if (!doc || !meta || !meta.fields) return;
            meta.fields.forEach(function(df) {
                if (['Data', 'Small Text', 'Text', 'Long Text'].indexOf(df.fieldtype) !== -1) {
                    var fn = df.fieldname;
                    if (EXCLUDED_FIELDNAMES.indexOf(fn) !== -1) return;
                    if (df.options === 'Email' || df.options === 'Password' || df.options === 'URL') return;
                    
                    var val = doc[fn];
                    if (typeof val === 'string' && val.trim()) {
                        // Skip if it is a URL or email address
                        if (val.indexOf('http://') === 0 || val.indexOf('https://') === 0 || val.indexOf('@') !== -1) return;
                        doc[fn] = val.toUpperCase().trim();
                    }
                } else if (['Table'].indexOf(df.fieldtype) !== -1 && Array.isArray(doc[df.fieldname])) {
                    var child_meta = frappe.get_meta(df.options);
                    if (child_meta) {
                        doc[df.fieldname].forEach(function(child_row) {
                            uppercase_fields(child_row, child_meta);
                        });
                    }
                }
            });
        }
        
        uppercase_fields(frm.doc, frm.meta);
        frm.refresh_fields();
    }
});
"""

# 2. Vehicle Model Specific Client Script (Validation, Pre-check duplicate, Auto-Caps)
vehicle_model_client_script = """
frappe.ui.form.on('Vehicle Model', {
    setup: function(frm) {
        // Real-time uppercase on make and model_name fields
        frm.fields_dict['make'] && frm.fields_dict['make'].$input && frm.fields_dict['make'].$input.on('input blur', function() {
            if (frm.doc.make) {
                frm.set_value('make', frm.doc.make.toUpperCase().trim());
            }
        });
        frm.fields_dict['model_name'] && frm.fields_dict['model_name'].$input && frm.fields_dict['model_name'].$input.on('input blur', function() {
            if (frm.doc.model_name) {
                frm.set_value('model_name', frm.doc.model_name.toUpperCase().trim());
            }
        });
    },
    
    validate: function(frm) {
        if (!frm.doc.make || !frm.doc.model_name) {
            frappe.msgprint({
                title: __('Missing Required Fields'),
                indicator: 'red',
                message: __('Both Make and Model Name are required.')
            });
            frappe.validated = false;
            return;
        }
        
        // Ensure clean uppercase
        frm.doc.make = frm.doc.make.toUpperCase().trim();
        frm.doc.model_name = frm.doc.model_name.toUpperCase().trim();
        
        // Synchronous duplicate check via frappe.db.get_list / API
        return new Promise(function(resolve, reject) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Vehicle Model',
                    filters: {
                        make: frm.doc.make,
                        model_name: frm.doc.model_name,
                        name: ['!=', frm.doc.name || '']
                    },
                    fields: ['name', 'make', 'model_name']
                },
                callback: function(r) {
                    if (r && r.message && r.message.length > 0) {
                        frappe.msgprint({
                            title: __('Duplicate Vehicle Model'),
                            indicator: 'red',
                            message: __('Vehicle Model <b>{0}</b> already exists for Make <b>{1}</b> (Record: <code>{2}</code>). Duplicate vehicle models are strictly not allowed.', [frm.doc.model_name, frm.doc.make, r.message[0].name])
                        });
                        frappe.validated = false;
                        reject();
                    } else {
                        resolve();
                    }
                }
            });
        });
    }
});
"""

# 3. Customer Vehicle Specific Client Script
customer_vehicle_client_script = """
frappe.ui.form.on('Customer Vehicle', {
    validate: function(frm) {
        if (frm.doc.plate_no) frm.doc.plate_no = frm.doc.plate_no.toUpperCase().trim();
        if (frm.doc.color) frm.doc.color = frm.doc.color.toUpperCase().trim();
        if (frm.doc.make) frm.doc.make = frm.doc.make.toUpperCase().trim();
        if (frm.doc.chassis_no) frm.doc.chassis_no = frm.doc.chassis_no.toUpperCase().trim();
        if (frm.doc.engine_no) frm.doc.engine_no = frm.doc.engine_no.toUpperCase().trim();
    }
});
"""

# Deploy Client Scripts
scripts = [
    ('VM Global Uppercase Engine', 'Item', global_uppercase_client_script),
    ('VM Vehicle Model Deduplication', 'Vehicle Model', vehicle_model_client_script),
    ('VM Customer Vehicle Uppercase', 'Customer Vehicle', customer_vehicle_client_script)
]

for name, dt, sc in scripts:
    payload = {
        'doctype': 'Client Script',
        'name': name,
        'dt': dt,
        'view': 'Form',
        'enabled': 1,
        'script': sc
    }
    chk = s.get(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(name)}')
    if chk.status_code == 200:
        s.put(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(name)}', json={'script': sc, 'enabled': 1, 'dt': dt})
        print(f"[OK] Updated Client Script: {name}")
    else:
        s.post(f'{URL}/api/resource/Client%20Script', json=payload)
        print(f"[OK] Created Client Script: {name}")

print("\nClient Scripts deployed successfully!")
