import requests, json, urllib.parse

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

# Standardized generic form uppercase script generator
def make_uppercase_script(doctype_name):
    return f"""// Auto-Uppercase Engine for {doctype_name}
frappe.ui.form.on('{doctype_name}', {{
    setup: function(frm) {{
        // Inject global real-time uppercase styling and event listeners
        if (!window.__auto_caps_initialized) {{
            window.__auto_caps_initialized = true;
            var style = document.createElement('style');
            style.innerHTML = 'input[type="text"]:not([type="email"]):not([type="password"]):not([data-fieldtype="Code"]):not([data-fieldtype="JSON"]), textarea {{ text-transform: uppercase; }}';
            document.head.appendChild(style);
        }}
    }},
    
    validate: function(frm) {{
        if (!frm.doc || !frm.meta) return;
        
        var EXCLUDED_FIELDS = [
            'email', 'user_email', 'email_id', 'contact_email', 'password', 
            'api_key', 'api_secret', 'token', 'route', 'url', 'image', 'file',
            'script', 'css', 'json', 'py', 'js', 'html', 'code'
        ];
        
        function auto_caps_doc(doc, meta) {{
            if (!doc || !meta || !meta.fields) return;
            meta.fields.forEach(function(df) {{
                if (['Data', 'Small Text', 'Text', 'Long Text'].indexOf(df.fieldtype) !== -1) {{
                    var fn = df.fieldname;
                    if (EXCLUDED_FIELDS.indexOf(fn) !== -1) return;
                    if (df.options === 'Email' || df.options === 'Password' || df.options === 'URL') return;
                    
                    var val = doc[fn];
                    if (typeof val === 'string' && val.trim()) {{
                        if (val.indexOf('http://') === 0 || val.indexOf('https://') === 0 || val.indexOf('@') !== -1) return;
                        doc[fn] = val.toUpperCase().trim();
                    }}
                }} else if (['Table'].indexOf(df.fieldtype) !== -1 && Array.isArray(doc[df.fieldname])) {{
                    var child_meta = frappe.get_meta(df.options);
                    if (child_meta) {{
                        doc[df.fieldname].forEach(function(child_row) {{
                            auto_caps_doc(child_row, child_meta);
                        }});
                    }}
                }}
            }});
        }}
        
        auto_caps_doc(frm.doc, frm.meta);
        frm.refresh_fields();
    }}
}});
"""

# Custom script for Vehicle Model
vehicle_model_script = """// Vehicle Model Deduplication & Uppercase Engine
frappe.ui.form.on('Vehicle Model', {
    setup: function(frm) {
        if (!window.__auto_caps_initialized) {
            window.__auto_caps_initialized = true;
            var style = document.createElement('style');
            style.innerHTML = 'input[type="text"]:not([type="email"]):not([type="password"]):not([data-fieldtype="Code"]):not([data-fieldtype="JSON"]), textarea { text-transform: uppercase; }';
            document.head.appendChild(style);
        }
        
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
        
        frm.doc.make = frm.doc.make.toUpperCase().trim();
        frm.doc.model_name = frm.doc.model_name.toUpperCase().trim();
        
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
                            message: __('Vehicle Model <b>' + frm.doc.model_name + '</b> already exists for Make <b>' + frm.doc.make + '</b> (Record: <code>' + r.message[0].name + '</code>). Duplicate vehicle models are strictly not allowed.')
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

# Target DocTypes for comprehensive system coverage
TARGET_DOCTYPES = [
    'Item',
    'Customer',
    'Supplier',
    'Customer Vehicle',
    'Vehicle Make',
    'Vehicle Job Order',
    'Vehicle Estimate',
    'Vehicle Inspection',
    'Vehicle POS Invoice',
    'Sales Invoice',
    'Purchase Invoice',
    'Quotation',
    'Sales Order',
    'Delivery Note',
    'Purchase Order',
    'Stock Entry',
    'Payment Entry',
    'Address',
    'Contact',
    'Lead',
    'Brand',
    'Item Group',
    'Customer Group',
    'Supplier Group',
    'Territory',
    'Warehouse',
    'Department',
    'Designation'
]

# Deploy Vehicle Model
cs_vm_name = 'VM Vehicle Model Deduplication'
chk = s.get(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(cs_vm_name)}')
if chk.status_code == 200:
    s.put(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(cs_vm_name)}', json={'script': vehicle_model_script, 'enabled': 1, 'dt': 'Vehicle Model'})
else:
    s.post(f'{URL}/api/resource/Client%20Script', json={'doctype': 'Client Script', 'name': cs_vm_name, 'dt': 'Vehicle Model', 'view': 'Form', 'enabled': 1, 'script': vehicle_model_script})
print(f"[OK] Deployed Vehicle Model Deduplication & Uppercase script")

# Deploy to all target DocTypes
for dt in TARGET_DOCTYPES:
    cs_name = f'VM Auto Uppercase - {dt}'
    script_content = make_uppercase_script(dt)
    
    chk = s.get(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(cs_name)}')
    if chk.status_code == 200:
        s.put(f'{URL}/api/resource/Client%20Script/{urllib.parse.quote(cs_name)}', json={'script': script_content, 'enabled': 1, 'dt': dt})
    else:
        s.post(f'{URL}/api/resource/Client%20Script', json={'doctype': 'Client Script', 'name': cs_name, 'dt': dt, 'view': 'Form', 'enabled': 1, 'script': script_content})
    print(f"[OK] Deployed Auto Uppercase to {dt}")

print("\nAll 29 DocTypes successfully configured with Auto-Capitalization and Validation!")
