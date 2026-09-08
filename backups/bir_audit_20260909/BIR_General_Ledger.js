frappe.ui.form.on('BIR General Ledger', {
    generate_report: function(frm) {
        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'GL Entry',
                filters: {
                    company: frm.doc.company,
                    posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]]
                },
                fields: ['posting_date', 'account', 'voucher_type', 'voucher_no', 'debit', 'credit', 'remarks', 'party'],
                limit_page_length: 5000,
                order_by: 'account asc, posting_date asc, name asc'
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frm.clear_table('gl_entries');
                    
                    // Group entries by account
                    let grouped = {};
                    r.message.forEach(entry => {
                        if (!grouped[entry.account]) {
                            grouped[entry.account] = [];
                        }
                        grouped[entry.account].push(entry);
                    });
                    
                    // Process each account group
                    Object.keys(grouped).sort().forEach(account => {
                        let entries = grouped[account];
                        let running_balance = 0;
                        let total_debit = 0;
                        let total_credit = 0;
                        
                        entries.forEach(entry => {
                            let row = frm.add_child('gl_entries');
                            row.account = account;
                            row.date = entry.posting_date || '';
                            
                            // Format description: VoucherType VoucherNo (Party - Remarks)
                            let party_info = entry.party ? `${entry.party} ` : '';
                            let rem = entry.remarks ? `(${entry.remarks.split('\n')[0]})` : '';
                            row.description = `${entry.voucher_type} ${entry.voucher_no} ${party_info}${rem}`;
                            
                            row.debit = entry.debit || 0;
                            row.credit = entry.credit || 0;
                            
                            running_balance += (entry.debit || 0) - (entry.credit || 0);
                            row.balance = running_balance;
                            row.indent = 1;
                            row.is_total_row = 0;
                            
                            total_debit += (entry.debit || 0);
                            total_credit += (entry.credit || 0);
                        });
                        
                        // Add TOTAL row for the group
                        let total_row = frm.add_child('gl_entries');
                        total_row.account = account;
                        total_row.date = '';
                        total_row.description = ''; // Leave blank for TOTAL label block in print formatting
                        total_row.debit = total_debit;
                        total_row.credit = total_credit;
                        total_row.balance = running_balance;
                        total_row.indent = 2;
                        total_row.is_total_row = 1;
                    });
                    
                    frm.refresh_field('gl_entries');
                    frappe.show_alert({message: __('Ledger generated successfully!'), indicator: 'green'});
                } else {
                    frappe.msgprint(__('No GL Entries found for this period.'));
                }
            }
        });
    }
});
