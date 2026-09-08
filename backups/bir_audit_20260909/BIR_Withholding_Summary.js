frappe.ui.form.on('BIR Withholding Summary', {
    generate_report: function(frm) {
        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        let get_sales = function() {
            return new Promise((resolve) => {
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Sales Invoice',
                        filters: {
                            company: frm.doc.company,
                            posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]],
                            docstatus: 1
                        },
                        fields: ['name', 'posting_date', 'customer', 'customer_name', 'tax_id', 'net_total'],
                        limit_page_length: 5000,
                        order_by: 'posting_date asc, name asc'
                    },
                    callback: function(r) {
                        resolve(r.message || []);
                    }
                });
            });
        };
        
        let get_purchases = function() {
            return new Promise((resolve) => {
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Purchase Invoice',
                        filters: {
                            company: frm.doc.company,
                            posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]],
                            docstatus: 1
                        },
                        fields: ['name', 'posting_date', 'supplier', 'supplier_name', 'tax_id', 'net_total'],
                        limit_page_length: 5000,
                        order_by: 'posting_date asc, name asc'
                    },
                    callback: function(r) {
                        resolve(r.message || []);
                    }
                });
            });
        };
        
        Promise.all([get_sales(), get_purchases()]).then(results => {
            let sales_invs = results[0];
            let purchase_invs = results[1];
            
            let all_names = sales_invs.map(si => si.name).concat(purchase_invs.map(pi => pi.name));
            
            if (all_names.length === 0) {
                frm.clear_table('withholding_entries');
                frm.refresh_field('withholding_entries');
                frappe.msgprint(__('No Sales or Purchase Invoices found for this period.'));
                return;
            }
            
            // 2. Fetch GL Entries for Withholding
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'GL Entry',
                    filters: {
                        voucher_no: ['in', all_names]
                    },
                    fields: ['voucher_no', 'account', 'debit', 'credit'],
                    limit_page_length: 5000
                },
                callback: function(gl_res) {
                    let tax_map = {};
                    if (gl_res.message) {
                        gl_res.message.forEach(gl => {
                            let head = (gl.account || '').toLowerCase();
                            if (head.includes('ewt') || head.includes('withholding') || head.includes('creditable') || head.includes('tds')) {
                                if (!tax_map[gl.voucher_no]) {
                                    tax_map[gl.voucher_no] = [];
                                }
                                tax_map[gl.voucher_no].push(gl);
                            }
                        });
                    }
                    
                    frm.clear_table('withholding_entries');
                    
                    let add_entries = function(invoices, is_ap) {
                        invoices.forEach(inv => {
                            let wt_rows = tax_map[inv.name] || [];
                            
                            if (wt_rows.length > 0) {
                                wt_rows.forEach(wt => {
                                    let row = frm.add_child('withholding_entries');
                                    row.document_type = is_ap ? 'A/P Invoice' : 'A/R Invoice';
                                    row.doc_date = inv.posting_date || '';
                                    row.tax_date = inv.posting_date || '';
                                    row.doc_no = inv.name;
                                    row.bp_code = is_ap ? inv.supplier : inv.customer;
                                    row.bp_name = is_ap ? inv.supplier_name : inv.customer_name;
                                    row.tin = inv.tax_id || '';
                                    
                                    let code_parts = wt.account.split(' - ');
                                    row.wt_code = code_parts[0] || 'EWT';
                                    
                                    let amt = Math.abs((wt.debit || 0) - (wt.credit || 0));
                                    let rate = Math.round((amt / (inv.net_total || 1)) * 100 * 100) / 100;
                                    
                                    row.wt_rate = rate;
                                    row.wt_taxable = inv.net_total || 0;
                                    row.wt_amount = amt;
                                    row.status = 'Posted';
                                });
                            } else if (!frm.doc.only_wtax) {
                                let row = frm.add_child('withholding_entries');
                                row.document_type = is_ap ? 'A/P Invoice' : 'A/R Invoice';
                                row.doc_date = inv.posting_date || '';
                                row.tax_date = inv.posting_date || '';
                                row.doc_no = inv.name;
                                row.bp_code = is_ap ? inv.supplier : inv.customer;
                                row.bp_name = is_ap ? inv.supplier_name : inv.customer_name;
                                row.tin = inv.tax_id || '';
                                row.wt_code = '-';
                                row.wt_rate = 0.00;
                                row.wt_taxable = inv.net_total || 0;
                                row.wt_amount = 0.00;
                                row.status = 'Posted';
                            }
                        });
                    };
                    
                    add_entries(sales_invs, false);
                    add_entries(purchase_invs, true);
                    
                    frm.refresh_field('withholding_entries');
                    frappe.show_alert({message: __('Withholding Summary generated successfully!'), indicator: 'green'});
                }
            });
        });
    }
});
