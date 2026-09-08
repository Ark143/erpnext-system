frappe.ui.form.on('BIR Purchases Book', {
    generate_report: function(frm) {
        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Purchase Invoice',
                filters: {
                    company: frm.doc.company,
                    posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]],
                    docstatus: 1
                },
                fields: ['name', 'supplier_name', 'posting_date', 'bill_no', 'net_total', 'grand_total', 'status', 'total_taxes_and_charges', 'tax_id', 'address_display', 'remarks'],
                limit_page_length: 500,
                order_by: 'posting_date asc, name asc'
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frm.clear_table('purchase_entries');
                    
                    let invoices = r.message.map(pi => pi.name);
                    
                    // Fetch payment dates in bulk from Payment Ledger
                    frappe.call({
                        method: 'frappe.client.get_list',
                        args: {
                            doctype: 'Payment Ledger Entry',
                            filters: {
                                against_voucher_no: ['in', invoices],
                                company: frm.doc.company,
                                delinked: 0
                            },
                            fields: ['against_voucher_no', 'posting_date'],
                            limit_page_length: 5000
                        },
                        callback: function(ple_res) {
                            let payment_dates = {};
                            if (ple_res.message) {
                                ple_res.message.forEach(ple => {
                                    payment_dates[ple.against_voucher_no] = ple.posting_date;
                                });
                            }
                            
                            // Map invoice records to the child table
                            r.message.forEach(pi => {
                                let row = frm.add_child('purchase_entries');
                                row.date = pi.posting_date || '';
                                row.payee = pi.supplier_name;
                                row.tin = pi.tax_id || '';
                                
                                // Clean supplier address HTML into single line
                                row.address = (pi.address_display || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
                                
                                row.invoice_no = pi.bill_no || pi.name;
                                row.discount_type = 'NONE';
                                row.discount_amount = 0;
                                
                                // Financial Splits
                                let taxes = pi.total_taxes_and_charges || 0;
                                row.vatable = pi.net_total || 0;
                                row.input_vat = taxes;
                                row.total_expense = pi.grand_total || 0;
                                
                                // Status / Ref / Date
                                let bill_ref = pi.bill_no || pi.name;
                                row.status_ref_date = `${pi.status.toUpperCase()} / INV No. ${bill_ref}`;
                                
                                // Payment Date lookup
                                let raw_pay_date = payment_dates[pi.name];
                                if (raw_pay_date) {
                                    row.payment_date = frappe.datetime.str_to_user(raw_pay_date);
                                } else {
                                    row.payment_date = '-';
                                }
                                
                                row.remarks = pi.remarks ? pi.remarks.split('\n')[0] : '';
                            });
                            
                            frm.refresh_field('purchase_entries');
                            frappe.show_alert({message: __('Purchases book generated successfully!'), indicator: 'green'});
                        }
                    });
                } else {
                    frappe.msgprint(__('No Purchase Invoices found for this period.'));
                }
            }
        });
    }
});
