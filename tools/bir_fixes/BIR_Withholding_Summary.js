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

frappe.ui.form.on('BIR Withholding Summary', {
    generate_report: async function(frm) {
        ["withholding_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});

        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');

        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        let get_sales = function() {
            return new Promise((resolve) => {
                birCall({
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
                birCall({
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
            birCall({
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

frappe.ui.form.on("BIR Withholding Summary", {company:function(frm){
        ["withholding_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},from_date:function(frm){
        ["withholding_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},to_date:function(frm){
        ["withholding_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
}});

})();
