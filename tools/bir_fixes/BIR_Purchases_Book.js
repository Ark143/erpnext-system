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

frappe.ui.form.on('BIR Purchases Book', {
    generate_report: async function(frm) {
        ["purchase_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});

        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');

        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        birCall({
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
                    birCall({
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

frappe.ui.form.on("BIR Purchases Book", {company:function(frm){
        ["purchase_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},from_date:function(frm){
        ["purchase_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},to_date:function(frm){
        ["purchase_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
}});

})();
