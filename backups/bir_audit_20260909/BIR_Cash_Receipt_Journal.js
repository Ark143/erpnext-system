frappe.ui.form.on('BIR Cash Receipt Journal', {
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
                    frm.clear_table('journal_entries');
                    frm.clear_table('account_summary');
                    
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
                            
                            let sum_vatable = 0;
                            let sum_vat = 0;
                            let sum_zero = 0;
                            let sum_exempt = 0;
                            let sum_total = 0;
                            let sum_wtax = 0;
                            let sum_net_cash = 0;
                            
                            // Map invoice records to the child table
                            r.message.forEach(si => {
                                let row = frm.add_child('journal_entries');
                                row.date = si.posting_date || '';
                                row.payor = si.customer_name;
                                row.tin = si.tax_id || '';
                                
                                // Clean address HTML into single line
                                row.address = (si.address_display || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
                                
                                row.invoice_no = si.name;
                                row.rendered = si.update_stock ? 'Goods' : 'Services';
                                row.discount_type = 'NONE';
                                row.discount_amount = 0;
                                
                                // Financial Splits
                                let taxes = si.total_taxes_and_charges || 0;
                                if (taxes > 0) {
                                    row.vatable = si.net_total || 0;
                                    row.output_vat = taxes;
                                    row.zero_rated = 0;
                                    row.vat_exempt = 0;
                                    
                                    sum_vatable += si.net_total || 0;
                                    sum_vat += taxes;
                                } else {
                                    row.vatable = 0;
                                    row.output_vat = 0;
                                    row.zero_rated = 0;
                                    row.vat_exempt = si.net_total || 0;
                                    
                                    sum_exempt += si.net_total || 0;
                                }
                                
                                row.total = si.grand_total || 0;
                                row.w_tax = 0;
                                row.net_cash = si.grand_total || 0;
                                row.note = '';
                                row.status = si.status.toUpperCase();
                                
                                sum_total += si.grand_total || 0;
                                sum_net_cash += si.grand_total || 0;
                                
                                // Payment Date lookup
                                let raw_pay_date = payment_dates[si.name];
                                if (raw_pay_date) {
                                    row.payment_date = frappe.datetime.str_to_user(raw_pay_date);
                                } else {
                                    row.payment_date = '-';
                                }
                            });
                            
                            // Add Account Summary Rows
                            let sum1 = frm.add_child('account_summary');
                            sum1.account_title = 'Accounts Receivable';
                            sum1.debit = sum_total;
                            sum1.credit = 0;
                            
                            let sum2 = frm.add_child('account_summary');
                            sum2.account_title = 'Creditable Withholding Tax';
                            sum2.debit = sum_wtax;
                            sum2.credit = 0;
                            
                            let sum3 = frm.add_child('account_summary');
                            sum3.account_title = 'Sales';
                            sum3.debit = 0;
                            sum3.credit = sum_vatable + sum_zero + sum_exempt;
                            
                            let sum4 = frm.add_child('account_summary');
                            sum4.account_title = 'Output VAT Payable';
                            sum4.debit = 0;
                            sum4.credit = sum_vat;
                            
                            let sum_tot = frm.add_child('account_summary');
                            sum_tot.account_title = 'Total';
                            sum_tot.debit = sum1.debit + sum2.debit;
                            sum_tot.credit = sum3.credit + sum4.credit;
                            
                            frm.refresh_field('journal_entries');
                            frm.refresh_field('account_summary');
                            frappe.show_alert({message: __('Cash Receipt journal generated successfully!'), indicator: 'green'});
                        }
                    });
                } else {
                    frappe.msgprint(__('No Sales Invoices found for this period.'));
                }
            }
        });
    }
});
