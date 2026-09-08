frappe.ui.form.on('BIR Cash Disbursement Journal', {
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
                fields: ['name', 'supplier_name', 'posting_date', 'bill_no', 'net_total', 'grand_total', 'outstanding_amount', 'status', 'total_taxes_and_charges', 'taxes_and_charges_deducted', 'tax_id'],
                limit_page_length: 500
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frm.clear_table('journal_entries');
                    frm.clear_table('account_summary');
                    
                    let total_vatable = 0;
                    let total_input_vat = 0;
                    let total_exempt = 0;
                    let total_zero = 0;
                    let total_grand = 0;
                    let total_ewt = 0;
                    let total_net_paid = 0;
                    
                    r.message.forEach(pi => {
                        let row = frm.add_child('journal_entries');
                        row.date = pi.posting_date || '';
                        row.payee = pi.supplier_name;
                        row.tin = pi.tax_id || '';
                        row.invoice_no = pi.bill_no || pi.name;
                        row.discount_type = 'NONE';
                        row.discount_amount = 0;
                        row.status = pi.status.toUpperCase();
                        
                        let taxes = pi.total_taxes_and_charges || 0;
                        let ewt = pi.taxes_and_charges_deducted || 0;
                        let grand = pi.grand_total || 0;
                        let net_paid = grand - ewt;
                        
                        row.total = grand;
                        row.ewt = ewt;
                        row.net_paid = net_paid;
                        
                        if (taxes > 0) {
                            row.nature = 'VATable Expense';
                            row.vatable = pi.net_total;
                            row.input_vat = taxes;
                            row.exempt = 0;
                            row.zero = 0;
                            
                            total_vatable += pi.net_total;
                            total_input_vat += taxes;
                        } else {
                            row.nature = 'Exempt Expense';
                            row.vatable = 0;
                            row.input_vat = 0;
                            row.exempt = pi.net_total;
                            row.zero = 0;
                            
                            total_exempt += pi.net_total;
                        }
                        
                        total_grand += grand;
                        total_ewt += ewt;
                        total_net_paid += net_paid;
                    });
                    
                    // Add Account Summary Rows
                    let sum1 = frm.add_child('account_summary');
                    sum1.account_title = 'Purchases / Expenses';
                    sum1.debit = total_vatable + total_exempt + total_zero;
                    sum1.credit = 0;
                    
                    let sum2 = frm.add_child('account_summary');
                    sum2.account_title = 'Input VAT';
                    sum2.debit = total_input_vat;
                    sum2.credit = 0;
                    
                    let sum3 = frm.add_child('account_summary');
                    sum3.account_title = 'Cash / Bank';
                    sum3.debit = 0;
                    sum3.credit = total_net_paid;
                    
                    let sum4 = frm.add_child('account_summary');
                    sum4.account_title = 'Creditable Withholding Tax';
                    sum4.debit = 0;
                    sum4.credit = total_ewt;
                    
                    let sum_tot = frm.add_child('account_summary');
                    sum_tot.account_title = 'Total';
                    sum_tot.debit = sum1.debit + sum2.debit;
                    sum_tot.credit = sum3.credit + sum4.credit;
                    
                    frm.refresh_field('journal_entries');
                    frm.refresh_field('account_summary');
                    frappe.show_alert({message: __('Report generated successfully!'), indicator: 'green'});
                } else {
                    frappe.msgprint(__('No submitted Purchase Invoices found for this period.'));
                }
            }
        });
    }
});
