frappe.ui.form.on('BIR Sales Journal', {
    generate_report: function(frm) {
        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Invoice',
                filters: {
                    company: frm.doc.company,
                    posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]],
                    docstatus: 1
                },
                fields: ['name', 'customer_name', 'posting_date', 'net_total', 'grand_total', 'status', 'total_taxes_and_charges', 'tax_id', 'address_display', 'remarks', 'update_stock'],
                limit_page_length: 500,
                order_by: 'posting_date asc, name asc'
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frm.clear_table('sales_entries');
                    frm.clear_table('summary_entries');
                    
                    let invoices = r.message.map(si => si.name);
                    
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
                            
                            let total_taxable = 0;
                            let total_vat = 0;
                            let total_gross = 0;
                            
                            // Map invoice records to the child table
                            r.message.forEach(si => {
                                let row = frm.add_child('sales_entries');
                                row.date = si.posting_date || '';
                                row.payor = si.customer_name;
                                row.tin = si.tax_id || '';
                                
                                // Clean address HTML into single line
                                row.address = (si.address_display || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
                                
                                row.invoice_no = si.name;
                                row.goods_services = si.update_stock ? 'Goods' : 'Services';
                                row.discount_type = 'NONE';
                                row.discount_amount = 0;
                                
                                // Financial Splits
                                let taxes = si.total_taxes_and_charges || 0;
                                if (taxes > 0) {
                                    row.vatable_sales = si.net_total || 0;
                                    row.output_vat = taxes;
                                    row.zero_rated = 0;
                                    row.vat_exempt = 0;
                                    
                                    total_taxable += si.net_total || 0;
                                    total_vat += taxes;
                                } else {
                                    row.vatable_sales = 0;
                                    row.output_vat = 0;
                                    row.zero_rated = 0;
                                    row.vat_exempt = si.net_total || 0;
                                }
                                
                                row.total_sales = si.grand_total || 0;
                                row.w_tax = 0;
                                row.total_receivable = si.grand_total || 0;
                                
                                total_gross += si.grand_total || 0;
                                
                                // Status / Ref / Date
                                row.status_ref_date = `${si.status.toUpperCase()} / INV No. ${si.name}`;
                                
                                // Payment Date lookup
                                let raw_pay_date = payment_dates[si.name];
                                if (raw_pay_date) {
                                    row.payment_date = frappe.datetime.str_to_user(raw_pay_date);
                                } else {
                                    row.payment_date = '-';
                                }
                                
                                row.remarks = si.remarks ? si.remarks.split('\n')[0] : '';
                            });
                            
                            // Add Summary Rows
                            let sum1 = frm.add_child('summary_entries');
                            sum1.summary = 'Documents';
                            sum1.value = r.message.length;
                            
                            let sum2 = frm.add_child('summary_entries');
                            sum2.summary = 'Total Taxable';
                            sum2.value = total_taxable;
                            
                            let sum3 = frm.add_child('summary_entries');
                            sum3.summary = 'Total VAT';
                            sum3.value = total_vat;
                            
                            let sum4 = frm.add_child('summary_entries');
                            sum4.summary = 'Total Gross';
                            sum4.value = total_gross;
                            
                            frm.refresh_field('sales_entries');
                            frm.refresh_field('summary_entries');
                            frappe.show_alert({message: __('Sales journal generated successfully!'), indicator: 'green'});
                        }
                    });
                } else {
                    frappe.msgprint(__('No Sales Invoices found for this period.'));
                }
            }
        });
    }
});
