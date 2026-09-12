frappe.ui.form.on('Vehicle Appointment', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            if (frm.doc.status !== 'Completed' && frm.doc.status !== 'Cancelled') {
                if (!frm.doc.job_order) {
                    frm.add_custom_button(__('Create Job Order'), function() {
                        frappe.model.open_mapped_doc({
                            method: 'vehicle_management.api.portal.create_job_order_from_appointment',
                            frm: frm
                        });
                    }, __('Actions'));
                }
                if (!frm.doc.estimate) {
                    frm.add_custom_button(__('Create Estimate'), function() {
                        frappe.model.open_mapped_doc({
                            method: 'vehicle_management.api.portal.create_estimate_from_appointment',
                            frm: frm
                        });
                    }, __('Actions'));
                }
            }
        }
    }
});
