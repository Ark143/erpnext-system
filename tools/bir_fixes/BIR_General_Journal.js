(() => {

const birRead = (method,args) => new Promise((resolve,reject)=>frappe.call({method,args,callback:r=>resolve(r.message),error:reject}));
async function birList(args) {
 let all=[];
 for(let start=0;;start+=500){const page=await birRead('frappe.client.get_list',{order_by:'name asc',...args,limit_start:start,limit_page_length:500});
 all=all.concat(page||[]);if(!page||page.length<500)return all;if(start>=99500)throw Error('Narrow the report date range.');}
}
function birCall(options) {
 const run=async()=>{
  let result;
  if(options.args.doctype==='Payment Ledger Entry') {
   const wanted=new Set(options.args.filters.against_voucher_no[1]);result=[];
   const payments=await birList({doctype:'Payment Entry',filters:{company:options.args.filters.company,docstatus:1},fields:['name','posting_date'],order_by:'posting_date asc, name asc'});
   for(const payment of payments){const doc=await birRead('frappe.client.get',{doctype:'Payment Entry',name:payment.name});
    for(const ref of doc.references||[])if(wanted.has(ref.reference_name)&&Number(ref.allocated_amount)>0)
     result.push({against_voucher_no:ref.reference_name,posting_date:payment.posting_date});}
  } else result=options.method==='frappe.client.get_list'?await birList(options.args):await birRead(options.method,options.args);
  options.callback?.({message:result});return {message:result};
 };
 return run().catch(error=>{frappe.msgprint('Report generation failed. Do not use incomplete results: '+(error.message||'Check source access.'));throw error;});
}

frappe.ui.form.on('BIR General Journal', {
    generate_report: async function(frm) {
        ["journal_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});

        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');

        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        birCall({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'GL Entry',
                filters: {
                    company: frm.doc.company,
                    is_cancelled: 0,
                    posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]]
                },
                fields: ['posting_date', 'account', 'voucher_type', 'voucher_no', 'debit', 'credit', 'remarks', 'party'],
                limit_page_length: 5000,
                order_by: 'posting_date asc, voucher_no asc, debit desc'
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    frm.clear_table('journal_entries');
                    
                    // Group entries by voucher_no
                    let transactions = [];
                    let last_voucher = null;
                    let current_tx = null;
                    
                    r.message.forEach(entry => {
                        if (entry.voucher_no !== last_voucher) {
                            if (current_tx) {
                                transactions.push(current_tx);
                            }
                            current_tx = {
                                voucher_no: entry.voucher_no,
                                voucher_type: entry.voucher_type,
                                date: entry.posting_date,
                                remarks: entry.remarks || '',
                                postings: []
                            };
                            last_voucher = entry.voucher_no;
                        }
                        current_tx.postings.push(entry);
                    });
                    if (current_tx) {
                        transactions.push(current_tx);
                    }
                    
                    // Collect all invoices for status fetching
                    let purchase_invoices = transactions.filter(t => t.voucher_type === 'Purchase Invoice').map(t => t.voucher_no);
                    let sales_invoices = transactions.filter(t => t.voucher_type === 'Sales Invoice').map(t => t.voucher_no);
                    
                    let invoice_statuses = {};
                    
                    let get_pi_status = function() {
                        return new Promise((resolve) => {
                            if (purchase_invoices.length === 0) return resolve();
                            birCall({
                                method: 'frappe.client.get_list',
                                args: {
                                    doctype: 'Purchase Invoice',
                                    filters: { name: ['in', purchase_invoices] },
                                    fields: ['name', 'status']
                                },
                                callback: function(res) {
                                    if (res.message) {
                                        res.message.forEach(d => {
                                            invoice_statuses[d.name] = d.status.toUpperCase();
                                        });
                                    }
                                    resolve();
                                }
                            });
                        });
                    };
                    
                    let get_si_status = function() {
                        return new Promise((resolve) => {
                            if (sales_invoices.length === 0) return resolve();
                            birCall({
                                method: 'frappe.client.get_list',
                                args: {
                                    doctype: 'Sales Invoice',
                                    filters: { name: ['in', sales_invoices] },
                                    fields: ['name', 'status']
                                },
                                callback: function(res) {
                                    if (res.message) {
                                        res.message.forEach(d => {
                                            invoice_statuses[d.name] = d.status.toUpperCase();
                                        });
                                    }
                                    resolve();
                                }
                            });
                        });
                    };
                    
                    Promise.all([get_pi_status(), get_si_status(), birList({doctype:'Account',filters:{company:frm.doc.company},fields:['name','account_name','account_number']})]).then(results => {
                        const birAccounts=Object.fromEntries(results[2].map(a=>[a.name,a]));
                        // Render transactions into the child table
                        transactions.forEach(tx => {
                            let tx_status = invoice_statuses[tx.voucher_no] || 'POSTED';
                            
                            tx.postings.forEach((post, index) => {
                                let row = frm.add_child('journal_entries');
                                row.voucher_no = tx.voucher_no;
                                row.voucher_type = tx.voucher_type;
                                
                                // Only the first row of the block gets Date and Status
                                row.date = (index === 0) ? tx.date : '';
                                row.status = (index === 0) ? tx_status : '';
                                
                                // Format Account Code and Name
                                let parts = post.account.split(' - ');
                                row.code = (birAccounts[post.account]||{}).account_number || '';
                                row.account_title = (birAccounts[post.account]||{}).account_name || post.account;
                                
                                row.debit = post.debit || 0;
                                row.credit = post.credit || 0;
                                
                                // Indent credit rows
                                row.indent = (post.credit > 0) ? 2 : 1;
                                row.is_explanation_row = 0;
                            });
                            
                            // Add explanation row at the end of the transaction
                            let expl_row = frm.add_child('journal_entries');
                            expl_row.voucher_no = tx.voucher_no;
                            expl_row.voucher_type = tx.voucher_type;
                            expl_row.date = '';
                            expl_row.status = '';
                            expl_row.code = '';
                            expl_row.account_title = '';
                            expl_row.debit = 0;
                            expl_row.credit = 0;
                            
                            // Format explanation (standardize remarks)
                            let short_remarks = tx.remarks.split('\n')[0];
                            expl_row.explanation = short_remarks || `Record transaction (${tx.voucher_type})`;
                            expl_row.is_explanation_row = 1;
                            expl_row.indent = 0;
                        });
                        
                        frm.refresh_field('journal_entries');
                        frappe.show_alert({message: __('Journal generated successfully!'), indicator: 'green'});
                    });
                } else {
                    frappe.msgprint(__('No GL Entries found for this period.'));
                }
            }
        });
    }
});

frappe.ui.form.on("BIR General Journal", {company:function(frm){
        ["journal_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},from_date:function(frm){
        ["journal_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},to_date:function(frm){
        ["journal_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
}});

})();
