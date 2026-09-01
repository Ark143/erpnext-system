import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

def create_or_update_doc(doctype, name, doc_data):
    try:
        r = op.open(urllib.request.Request(f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}', headers=H))
        print(f"{doctype} '{name}' exists, updating...")
        req = urllib.request.Request(
            f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}/{urllib.parse.quote(name)}',
            data=urllib.parse.urlencode({'data': json.dumps(doc_data)}).encode(),
            headers=H
        )
        req.get_method = lambda: 'PUT'
        op.open(req)
        print(f"Updated {doctype} '{name}'")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Creating {doctype} '{name}'...")
            doc_data['doctype'] = doctype
            req = urllib.request.Request(
                f'http://38.247.138.224:10017/api/resource/{urllib.parse.quote(doctype)}',
                data=urllib.parse.urlencode({'data': json.dumps(doc_data)}).encode(),
                headers=H
            )
            op.open(req)
            print(f"Created {doctype} '{name}'")
        else:
            raise

# 1. Server Script API: verify_receiver_badge
server_script_api = """
raw = (frappe.form_dict.get('qr_data') or '').strip()
raw = raw.replace('\\r', '').replace('\\n', '').strip()

usr = ''
pwd = ''

if raw.startswith('{') and raw.endswith('}'):
    try:
        import json
        pj = json.loads(raw)
        usr = pj.get('usr') or pj.get('user') or pj.get('username') or pj.get('email') or ''
        pwd = pj.get('pwd') or pj.get('password') or ''
    except Exception:
        pass

if not usr:
    parts = raw.split('|')
    if len(parts) < 2 and '\\t' in raw:
        parts = raw.split('\\t')
    if len(parts) < 2 and ':' in raw:
        parts = raw.split(':')
    usr = (parts[0] or '').strip()
    if len(parts) > 1:
        pwd = parts[1].strip()

if not usr:
    frappe.response['message'] = {'ok': False, 'message': 'No User ID found in scanned QR badge.'}
else:
    user_doc = frappe.db.get_value('User', {'name': usr}, ['name', 'full_name', 'email', 'user_image'], as_dict=True)
    if not user_doc and '@' in usr:
        user_doc = frappe.db.get_value('User', {'email': usr}, ['name', 'full_name', 'email', 'user_image'], as_dict=True)
    if not user_doc:
        # Check if it was an employee number
        emp_match = frappe.db.get_value('Employee', {'name': usr}, ['name', 'employee_name', 'user_id', 'department', 'designation', 'image'], as_dict=True)
        if not emp_match:
            emp_match = frappe.db.get_value('Employee', {'employee_number': usr}, ['name', 'employee_name', 'user_id', 'department', 'designation', 'image'], as_dict=True)
        if emp_match and emp_match.user_id:
            user_doc = frappe.db.get_value('User', {'name': emp_match.user_id}, ['name', 'full_name', 'email', 'user_image'], as_dict=True)
        elif emp_match:
            user_doc = {'name': emp_match.name, 'full_name': emp_match.employee_name, 'email': '', 'user_image': emp_match.image}

    if not user_doc:
        frappe.response['message'] = {'ok': False, 'message': 'User "' + str(usr) + '" does not exist in ERPNext.'}
    else:
        # Find Employee
        emp = frappe.db.get_value('Employee', {'user_id': user_doc.name}, ['name', 'employee_name', 'department', 'designation', 'image', 'company'], as_dict=True)
        if not emp and user_doc.email:
            emp = frappe.db.get_value('Employee', {'prefered_email': user_doc.email}, ['name', 'employee_name', 'department', 'designation', 'image', 'company'], as_dict=True)
        if not emp:
            emp = frappe.db.get_value('Employee', {'company_email': user_doc.email}, ['name', 'employee_name', 'department', 'designation', 'image', 'company'], as_dict=True)

        frappe.response['message'] = {
            'ok': True,
            'user_id': user_doc.name,
            'user_name': user_doc.full_name or user_doc.name,
            'employee_id': emp.name if emp else '',
            'employee_name': (emp.employee_name if emp else user_doc.full_name) or user_doc.name,
            'department': emp.department if emp else '',
            'designation': emp.designation if emp else '',
            'company': emp.company if emp else '',
            'photo': (emp.image if emp and emp.image else user_doc.user_image) or ''
        }
"""

create_or_update_doc("Server Script", "VM Verify Receiver Badge", {
    "script_type": "API",
    "api_method": "vm_verify_receiver_badge",
    "allow_guest": 0,
    "script": server_script_api
})

# 2. Server Script DocType Event: Safety Check on Stock Entry before_submit
server_script_validator = """
if doc.stock_entry_type == 'Material Issue':
    if not doc.custom_receiver_user:
        frappe.throw(
            '<b>SAFETY CHECK REQUIRED</b><br>' +
            'You cannot submit a Material Issue without scanning the receiver\\'s QR code badge.<br>' +
            'Please click <b>Verify Receiver QR & Capture Photo</b> to verify the receiver.',
            title='Receiver Verification Missing'
        )
    if not doc.custom_receiver_photo:
        frappe.throw(
            '<b>SAFETY CHECK REQUIRED</b><br>' +
            'A handover / receiver photo is required before submitting a Material Issue.<br>' +
            'Please take or upload a photo proof of handover.',
            title='Handover Photo Missing'
        )
"""

create_or_update_doc("Server Script", "VM Stock Entry Safety Check", {
    "script_type": "DocType Event",
    "reference_doctype": "Stock Entry",
    "doctype_event": "Before Submit",
    "script": server_script_validator
})

# 3. Client Script for Stock Entry Form
client_script_code = """
frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        vm_setup_receiver_verification(frm);
    },
    stock_entry_type: function(frm) {
        vm_setup_receiver_verification(frm);
    }
});

function vm_setup_receiver_verification(frm) {
    if (frm.doc.stock_entry_type !== 'Material Issue') {
        return;
    }

    // Add prominent action button in form header
    if (frm.doc.docstatus === 0) {
        frm.add_custom_button(__('📷 Verify Receiver QR & Photo'), function() {
            vm_open_receiver_dialog(frm);
        }, __('Safety Check')).addClass('btn-primary-action btn-success');
    }

    // Render interactive verification card inside the custom HTML field
    let html = `
    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:12px;padding:16px;margin:8px 0;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="font-weight:700;font-size:14px;color:#0f172a;display:flex;align-items:center;gap:6px;">
                    <span>🛡️</span> Receiver Verification & Handover Safety Check
                </div>
                <div style="font-size:12px;color:#64748b;margin-top:2px;">
                    Material Issue policy mandates scanning the recipient's employee QR badge and taking a handover turnover photo.
                </div>
            </div>
            ${frm.doc.docstatus === 0 ? `
            <button type="button" class="btn btn-sm btn-primary" id="btn-vm-verify-rec" style="font-weight:700;padding:6px 14px;border-radius:8px;background:#16c784;border-color:#16c784;color:#04201a;">
                📷 ${frm.doc.custom_receiver_user ? 'Re-Verify / Change Receiver' : 'Scan Receiver QR & Photo'}
            </button>` : ''}
        </div>
        ${frm.doc.custom_receiver_user ? `
        <div style="margin-top:14px;display:flex;align-items:center;gap:14px;background:#fff;border:1px solid #cbd5e1;border-radius:10px;padding:12px;">
            ${frm.doc.custom_receiver_photo ? `<img src="${frm.doc.custom_receiver_photo}" style="width:54px;height:54px;border-radius:8px;object-fit:cover;border:1px solid #e2e8f0;">` : '<div style="width:54px;height:54px;border-radius:8px;background:#e2e8f0;display:flex;align-items:center;justify-content:center;font-size:20px;">👤</div>'}
            <div style="flex:1;">
                <div style="font-weight:700;color:#0f172a;font-size:14px;">${frm.doc.custom_receiver_name || frm.doc.custom_receiver_user}</div>
                <div style="font-size:12px;color:#64748b;">User: <b>${frm.doc.custom_receiver_user}</b> · Emp ID: <b>${frm.doc.custom_receiver_employee || '—'}</b></div>
                <div style="font-size:11px;color:#16a34a;margin-top:2px;">✓ Verified via QR Badge at ${frm.doc.custom_receiver_verified_at || ''}</div>
            </div>
            <span class="badge badge-success" style="background:#dcfce7;color:#15803d;padding:6px 10px;border-radius:6px;font-size:11px;">VERIFIED</span>
        </div>` : `
        <div style="margin-top:12px;padding:10px;background:#fff1f2;border:1px dashed #fecdd3;border-radius:8px;color:#be123c;font-size:12px;display:flex;align-items:center;gap:8px;">
            <span>⚠️</span> <b>Pending Verification:</b> Receiver has not scanned their QR badge yet.
        </div>`}
    </div>`;

    frm.get_field('custom_receiver_btn_html').$wrapper.html(html);
    frm.get_field('custom_receiver_btn_html').$wrapper.find('#btn-vm-verify-rec').on('click', function() {
        vm_open_receiver_dialog(frm);
    });
}

function vm_open_receiver_dialog(frm) {
    let verifiedData = null;
    let photoDataUrl = null;

    let d = new frappe.ui.Dialog({
        title: __('Receiver Safety Check & Handover Verification'),
        size: 'large',
        fields: [
            {
                fieldname: 'sec_badge',
                fieldtype: 'Section Break',
                label: __('Step 1: Scan Receiver QR Badge')
            },
            {
                fieldname: 'badge_html',
                fieldtype: 'HTML'
            },
            {
                fieldname: 'sec_photo',
                fieldtype: 'Section Break',
                label: __('Step 2: Handover / Turnover Photo Proof')
            },
            {
                fieldname: 'photo_html',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: __('Save & Apply Verification'),
        primary_action: function() {
            if (!verifiedData) {
                frappe.msgprint({
                    title: __('Receiver Verification Required'),
                    message: __('Please scan or enter the receiver\\'s QR badge first.'),
                    indicator: 'orange'
                });
                return;
            }
            if (!photoDataUrl && !frm.doc.custom_receiver_photo) {
                frappe.msgprint({
                    title: __('Handover Photo Required'),
                    message: __('Please capture or upload a handover photo as proof of receipt.'),
                    indicator: 'orange'
                });
                return;
            }

            frm.set_value('custom_receiver_user', verifiedData.user_id);
            frm.set_value('custom_receiver_employee', verifiedData.employee_id || '');
            frm.set_value('custom_receiver_name', verifiedData.employee_name || verifiedData.user_name || verifiedData.user_id);
            frm.set_value('custom_receiver_verified_at', frappe.datetime.now_datetime());
            frm.set_value('custom_receiver_verified_by_qr', 1);

            if (photoDataUrl) {
                // Upload photo as file attached to Stock Entry
                frappe.call({
                    method: 'upload_file',
                    args: {
                        from_form: 1,
                        doctype: 'Stock Entry',
                        docname: frm.doc.name,
                        filename: 'receiver_proof_' + frappe.datetime.now_datetime().replace(/[^0-9]/g, '') + '.jpg',
                        filedata: photoDataUrl.split(',')[1],
                        is_private: 0
                    },
                    callback: function(r) {
                        if (r.message && r.message.file_url) {
                            frm.set_value('custom_receiver_photo', r.message.file_url);
                        }
                        d.hide();
                        frm.save();
                    }
                });
            } else {
                d.hide();
                frm.save();
            }
        }
    });

    // Render Badge Scanner Section
    let badgeHtml = `
    <div style="background:#f1f5f9;border-radius:10px;padding:14px;">
        <div style="display:flex;gap:8px;">
            <input type="text" id="vm-dlg-badge-input" class="form-control" placeholder="Scan receiver badge QR or type user|pass..." style="flex:1;font-size:14px;background:#fff;" autofocus>
            <button type="button" class="btn btn-primary" id="vm-dlg-badge-btn" style="font-weight:700;background:#0f172a;border-color:#0f172a;color:#fff;">Verify</button>
        </div>
        <div id="vm-dlg-badge-status" style="margin-top:8px;font-size:12px;color:#64748b;">Point 2D barcode scanner gun or paste badge code.</div>
        <div id="vm-dlg-receiver-card" style="display:none;margin-top:12px;background:#fff;border:1.5px solid #16c784;border-radius:8px;padding:12px;"></div>
    </div>`;
    d.get_field('badge_html').$wrapper.html(badgeHtml);

    // Render Photo Capture Section
    let photoHtml = `
    <div style="background:#f1f5f9;border-radius:10px;padding:14px;">
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
            <label class="btn btn-default" style="cursor:pointer;margin-bottom:0;display:flex;align-items:center;gap:6px;background:#fff;">
                <span>📷</span> Take Photo / Upload File
                <input type="file" id="vm-dlg-photo-file" accept="image/*" capture="environment" style="display:none;">
            </label>
            <span id="vm-dlg-photo-status" style="font-size:12px;color:#64748b;">Capture receiver handover photo.</span>
        </div>
        <div id="vm-dlg-photo-preview" style="margin-top:10px;display:none;">
            <img id="vm-dlg-photo-img" style="max-width:240px;max-height:180px;border-radius:8px;border:1px solid #cbd5e1;object-fit:cover;">
        </div>
    </div>`;
    d.get_field('photo_html').$wrapper.html(photoHtml);

    function doVerifyBadge(code) {
        if (!code) return;
        $('#vm-dlg-badge-status').html('<span style="color:#0284c7;">Verifying receiver in ERPNext...</span>');
        frappe.call({
            method: 'vm_verify_receiver_badge',
            args: { qr_data: code },
            callback: function(r) {
                let res = r.message;
                if (res && res.ok) {
                    verifiedData = res;
                    $('#vm-dlg-badge-status').html('<span style="color:#16a34a;font-weight:700;">✓ Receiver identity verified!</span>');
                    $('#vm-dlg-receiver-card').show().html(`
                        <div style="display:flex;align-items:center;gap:12px;">
                            ${res.photo ? `<img src="${res.photo}" style="width:48px;height:48px;border-radius:8px;object-fit:cover;">` : '<div style="width:48px;height:48px;border-radius:8px;background:#e2e8f0;display:flex;align-items:center;justify-content:center;font-size:18px;">👤</div>'}
                            <div>
                                <div style="font-weight:700;font-size:14px;color:#0f172a;">${res.employee_name}</div>
                                <div style="font-size:12px;color:#475569;">User: <b>${res.user_id}</b> · Emp ID: <b>${res.employee_id || '—'}</b></div>
                                <div style="font-size:11px;color:#64748b;">${res.designation ? res.designation + ' · ' : ''}${res.department || ''} ${res.company ? '(' + res.company + ')' : ''}</div>
                            </div>
                        </div>
                    `);
                } else {
                    verifiedData = null;
                    $('#vm-dlg-receiver-card').hide();
                    $('#vm-dlg-badge-status').html('<span style="color:#dc2626;font-weight:700;">✗ ' + ((res && res.message) ? res.message : 'Invalid badge') + '</span>');
                }
            }
        });
    }

    d.$wrapper.find('#vm-dlg-badge-btn').on('click', function() {
        doVerifyBadge($('#vm-dlg-badge-input').val());
    });
    d.$wrapper.find('#vm-dlg-badge-input').on('keydown', function(e) {
        if (e.key === 'Enter') {
            doVerifyBadge($(this).val());
        }
    });

    d.$wrapper.find('#vm-dlg-photo-file').on('change', function(e) {
        let file = e.target.files[0];
        if (!file) return;
        let reader = new FileReader();
        reader.onload = function() {
            photoDataUrl = reader.result;
            $('#vm-dlg-photo-preview').show();
            $('#vm-dlg-photo-img').attr('src', photoDataUrl);
            $('#vm-dlg-photo-status').html('<span style="color:#16a34a;font-weight:700;">✓ Photo captured!</span>');
        };
        reader.readAsDataURL(file);
    });

    d.show();
    setTimeout(() => { $('#vm-dlg-badge-input').focus(); }, 300);
}
"""

create_or_update_doc("Client Script", "VM Stock Entry Receiver Safety Check", {
    "dt": "Stock Entry",
    "view": "Form",
    "enabled": 1,
    "script": client_script_code
})

print("Successfully configured Server Scripts and Client Scripts for Receiver Safety Check!")
