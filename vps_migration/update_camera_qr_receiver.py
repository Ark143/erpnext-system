import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

client_script_code = """
frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        vm_ensure_jsqr();
        vm_setup_receiver_verification(frm);
    },
    stock_entry_type: function(frm) {
        vm_setup_receiver_verification(frm);
    }
});

function vm_ensure_jsqr() {
    if (!window.jsQR) {
        let s = document.createElement('script');
        s.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js';
        document.head.appendChild(s);
    }
}

function vm_setup_receiver_verification(frm) {
    if (frm.doc.stock_entry_type !== 'Material Issue') {
        return;
    }

    if (frm.doc.docstatus === 0) {
        frm.add_custom_button(__('📷 Verify Receiver QR & Photo'), function() {
            vm_open_receiver_dialog(frm);
        }, __('Safety Check')).addClass('btn-primary-action btn-success');
    }

    let isVerified = Boolean(frm.doc.custom_receiver_user);
    let html = `
    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:12px;padding:16px;margin:8px 0;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="font-weight:700;font-size:14px;color:#0f172a;display:flex;align-items:center;gap:6px;">
                    <span>🛡️</span> Receiver Verification & Handover Safety Check
                </div>
                <div style="font-size:12px;color:#64748b;margin-top:2px;">
                    Scan the recipient's employee QR badge using device camera or scanner gun, and capture a handover turnover photo.
                </div>
            </div>
            ${frm.doc.docstatus === 0 ? `
            <button type="button" class="btn btn-sm btn-primary" id="btn-vm-verify-rec" style="font-weight:700;padding:6px 14px;border-radius:8px;background:#16c784;border-color:#16c784;color:#04201a;">
                📷 ${isVerified ? 'Re-Verify / Change Receiver' : 'Scan Receiver QR & Photo'}
            </button>` : ''}
        </div>
        ${isVerified ? `
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

    let field = frm.get_field('custom_receiver_btn_html');
    if (field && field.$wrapper) {
        field.$wrapper.html(html);
        field.$wrapper.find('#btn-vm-verify-rec').on('click', function() {
            vm_open_receiver_dialog(frm);
        });
    }
}

function vm_open_receiver_dialog(frm) {
    let verifiedData = null;
    let photoDataUrl = null;
    let cameraStream = null;

    let d = new frappe.ui.Dialog({
        title: __('Receiver Safety Check & Handover Verification'),
        size: 'large',
        fields: [
            {
                fieldname: 'sec_badge',
                fieldtype: 'Section Break',
                label: __('Step 1: Scan Receiver QR Badge (Camera / Scanner)')
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
                    message: __('Please scan or verify the receiver\\'s QR badge first.'),
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

            stopLiveCamera();

            frm.set_value('custom_receiver_user', verifiedData.user_id);
            frm.set_value('custom_receiver_employee', verifiedData.employee_id || '');
            frm.set_value('custom_receiver_name', verifiedData.employee_name || verifiedData.user_name || verifiedData.user_id);
            frm.set_value('custom_receiver_verified_at', frappe.datetime.now_datetime());
            frm.set_value('custom_receiver_verified_by_qr', 1);

            if (photoDataUrl) {
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
                        frappe.show_alert({ message: __('Receiver verified and photo attached successfully!'), indicator: 'green' });
                    }
                });
            } else {
                d.hide();
                frm.save();
                frappe.show_alert({ message: __('Receiver verified successfully!'), indicator: 'green' });
            }
        }
    });

    d.on_hide = function() {
        stopLiveCamera();
    };

    function stopLiveCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach(t => t.stop());
            cameraStream = null;
        }
        $('#vm-dlg-camera-box').hide();
    }

    let badgeHtml = `
    <div style="background:#f1f5f9;border-radius:10px;padding:14px;">
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
            <button type="button" class="btn btn-primary" id="vm-dlg-open-cam-btn" style="font-weight:700;background:#16c784;border-color:#16c784;color:#04201a;">
                📷 Scan with Live Camera
            </button>
            <label class="btn btn-default" style="cursor:pointer;margin-bottom:0;background:#fff;display:flex;align-items:center;gap:4px;">
                <span>📁</span> Snap / Upload QR Photo
                <input type="file" id="vm-dlg-qr-file" accept="image/*" capture="environment" style="display:none;">
            </label>
            <input type="text" id="vm-dlg-badge-input" class="form-control" placeholder="Or enter badge code / User ID..." style="flex:1;min-width:180px;font-size:13px;background:#fff;">
            <button type="button" class="btn btn-default" id="vm-dlg-badge-btn" style="font-weight:700;">Verify</button>
        </div>

        <div id="vm-dlg-camera-box" style="display:none;position:relative;margin-top:12px;border-radius:12px;overflow:hidden;background:#000;max-width:440px;margin-left:auto;margin-right:auto;">
            <video id="vm-dlg-video" playsinline style="width:100%;display:block;border-radius:12px;"></video>
            <div style="position:absolute;inset:15%;border:2px dashed #16c784;border-radius:10px;pointer-events:none;box-shadow:0 0 0 9999px rgba(0,0,0,0.4);"></div>
            <button type="button" id="vm-dlg-stop-cam-btn" style="position:absolute;bottom:8px;left:50%;transform:translateX(-50%);background:rgba(239,68,68,0.9);color:#fff;border:none;padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700;">✕ Stop Camera</button>
        </div>

        <div id="vm-dlg-badge-status" style="margin-top:8px;font-size:12px;color:#64748b;">Click 'Scan with Live Camera' or snap a photo of the recipient's QR badge.</div>
        <div id="vm-dlg-receiver-card" style="display:none;margin-top:12px;background:#fff;border:1.5px solid #16c784;border-radius:8px;padding:12px;"></div>
    </div>`;
    d.get_field('badge_html').$wrapper.html(badgeHtml);

    let photoHtml = `
    <div style="background:#f1f5f9;border-radius:10px;padding:14px;">
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
            <label class="btn btn-default" style="cursor:pointer;margin-bottom:0;display:flex;align-items:center;gap:6px;background:#fff;">
                <span>📷</span> Take Handover Photo / Upload
                <input type="file" id="vm-dlg-photo-file" accept="image/*" capture="environment" style="display:none;">
            </label>
            <span id="vm-dlg-photo-status" style="font-size:12px;color:#64748b;">Take turnover photo of recipient holding the issued items.</span>
        </div>
        <div id="vm-dlg-photo-preview" style="margin-top:10px;display:none;">
            <img id="vm-dlg-photo-img" style="max-width:240px;max-height:180px;border-radius:8px;border:1px solid #cbd5e1;object-fit:cover;">
        </div>
    </div>`;
    d.get_field('photo_html').$wrapper.html(photoHtml);

    function doVerifyBadge(code) {
        code = (code || '').trim();
        if (!code) return;
        $('#vm-dlg-badge-status').html('<span style="color:#0284c7;">Verifying receiver in ERPNext...</span>');
        frappe.call({
            method: 'vm_verify_receiver_badge',
            args: { qr_data: code },
            callback: function(r) {
                let res = r.message;
                if (res && res.ok) {
                    verifiedData = res;
                    stopLiveCamera();
                    $('#vm-dlg-badge-input').val(res.user_id);
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

    // Live Camera QR Scanner
    function startLiveCameraScan() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            $('#vm-dlg-qr-file').click();
            return;
        }

        $('#vm-dlg-camera-box').show();
        $('#vm-dlg-badge-status').html('<span style="color:#0284c7;">Point camera at recipient\\'s QR badge...</span>');
        const v = document.getElementById('vm-dlg-video');

        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(stream => {
            cameraStream = stream;
            v.srcObject = stream;
            v.play();

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            let isScanning = true;

            const scanLoop = async () => {
                if (!cameraStream || !isScanning) return;
                if (v.readyState === 4 && v.videoWidth > 0) {
                    canvas.width = v.videoWidth;
                    canvas.height = v.videoHeight;
                    ctx.drawImage(v, 0, 0, canvas.width, canvas.height);

                    let qrCode = null;
                    if ('BarcodeDetector' in window) {
                        try {
                            const detector = new BarcodeDetector({ formats: ['qr_code'] });
                            const barcodes = await detector.detect(canvas);
                            if (barcodes && barcodes.length > 0) qrCode = barcodes[0].rawValue;
                        } catch(e){}
                    }
                    if (!qrCode && window.jsQR) {
                        try {
                            const d = ctx.getImageData(0, 0, canvas.width, canvas.height);
                            const res = window.jsQR(d.data, d.width, d.height, { inversionAttempts: 'attemptBoth' });
                            if (res && res.data) qrCode = res.data;
                        } catch(e){}
                    }

                    if (qrCode) {
                        isScanning = false;
                        doVerifyBadge(qrCode);
                        return;
                    }
                }
                requestAnimationFrame(scanLoop);
            };
            requestAnimationFrame(scanLoop);
        }).catch(err => {
            $('#vm-dlg-camera-box').hide();
            $('#vm-dlg-qr-file').click();
        });
    }

    d.$wrapper.find('#vm-dlg-open-cam-btn').on('click', startLiveCameraScan);
    d.$wrapper.find('#vm-dlg-stop-cam-btn').on('click', stopLiveCamera);

    // QR Image Upload / Photo Decode
    d.$wrapper.find('#vm-dlg-qr-file').on('change', function(e) {
        let file = e.target.files[0];
        if (!file) return;
        $('#vm-dlg-badge-status').html('<span style="color:#0284c7;">Scanning QR code from image...</span>');
        let reader = new FileReader();
        reader.onload = async function() {
            let img = new Image();
            img.onload = async function() {
                let qrFound = null;
                if ('BarcodeDetector' in window) {
                    try {
                        let bmp = await createImageBitmap(file);
                        let detector = new BarcodeDetector({ formats: ['qr_code'] });
                        let barcodes = await detector.detect(bmp);
                        if (barcodes && barcodes.length > 0) qrFound = barcodes[0].rawValue;
                    } catch(e){}
                }
                if (!qrFound && window.jsQR) {
                    let canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    let ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    let d = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    let res = window.jsQR(d.data, d.width, d.height, { inversionAttempts: 'attemptBoth' });
                    if (res && res.data) qrFound = res.data;
                }
                if (qrFound) {
                    doVerifyBadge(qrFound);
                } else {
                    $('#vm-dlg-badge-status').html('<span style="color:#dc2626;">No QR found in photo. Please try again or type User ID.</span>');
                }
            };
            img.src = reader.result;
        };
        reader.readAsDataURL(file);
    });

    d.$wrapper.find('#vm-dlg-badge-btn').on('click', function() {
        doVerifyBadge($('#vm-dlg-badge-input').val());
    });
    d.$wrapper.find('#vm-dlg-badge-input').on('keydown', function(e) {
        if (e.key === 'Enter') {
            doVerifyBadge($(this).val());
        }
    });

    // Step 2 Handover Photo
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
}
"""

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Client%20Script/VM%20Stock%20Entry%20Receiver%20Safety%20Check',
    data=urllib.parse.urlencode({'data': json.dumps({'script': client_script_code})}).encode(),
    headers=H
)
req.get_method = lambda: 'PUT'
op.open(req)
print("Updated Client Script with Live Camera QR Scanner & Photo Capture successfully!")
