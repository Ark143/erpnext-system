(() => {

const birRead = (method,args) => new Promise((resolve,reject)=>frappe.call({method,args,callback:r=>resolve(r.message),error:reject}));
async function birList(args) {
 let all=[];
 for(let start=0;;start+=500){const page=await birRead('frappe.client.get_list',{...args,limit_start:start,limit_page_length:500});
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

frappe.ui.form.on('BIR VAT Summary', {
    generate_report: async function(frm) {
        ["vat_entries", "total_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});

        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');

        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        // 1. Fetch Sales Invoices (Output VAT)
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
                        fields: ['name', 'net_total', 'grand_total', 'total_taxes_and_charges'],
                        limit_page_length: 5000
                    },
                    callback: function(r) {
                        let sales_stats = { docs: 0, taxable: 0, vat: 0, gross: 0 };
                        if (r.message) {
                            sales_stats.docs = r.message.length;
                            r.message.forEach(si => {
                                if (si.total_taxes_and_charges > 0) {
                                    sales_stats.taxable += si.net_total || 0;
                                    sales_stats.vat += si.total_taxes_and_charges || 0;
                                    sales_stats.gross += si.grand_total || 0;
                                } else {
                                    // Tax-exempt or zero-rated still contributes to gross but not taxable VAT
                                    sales_stats.gross += si.grand_total || 0;
                                }
                            });
                        }
                        resolve(sales_stats);
                    }
                });
            });
        };
        
        // 2. Fetch Purchase Invoices (Input VAT)
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
                        fields: ['name', 'net_total', 'grand_total', 'total_taxes_and_charges'],
                        limit_page_length: 5000
                    },
                    callback: function(r) {
                        let purchase_stats = { docs: 0, taxable: 0, vat: 0, gross: 0 };
                        if (r.message) {
                            purchase_stats.docs = r.message.length;
                            r.message.forEach(pi => {
                                if (pi.total_taxes_and_charges > 0) {
                                    purchase_stats.taxable += pi.net_total || 0;
                                    purchase_stats.vat += pi.total_taxes_and_charges || 0;
                                    purchase_stats.gross += pi.grand_total || 0;
                                } else {
                                    purchase_stats.gross += pi.grand_total || 0;
                                }
                            });
                        }
                        resolve(purchase_stats);
                    }
                });
            });
        };
        
        Promise.all([get_sales(), get_purchases()]).then(results => {
            let sales = results[0];
            let purchases = results[1];
            
            frm.clear_table('vat_entries');
            frm.clear_table('total_entries');
            
            // Add Output VAT Row
            let r1 = frm.add_child('vat_entries');
            r1.category = 'Output VAT';
            r1.source = 'Sales Book';
            r1.documents = sales.docs;
            r1.taxable_amount = sales.taxable;
            r1.vat_amount = sales.vat;
            r1.gross_amount = sales.gross;
            
            // Add Input VAT Row
            let r2 = frm.add_child('vat_entries');
            r2.category = 'Input VAT';
            r2.source = 'Purchases Book';
            r2.documents = purchases.docs;
            r2.taxable_amount = purchases.taxable;
            r2.vat_amount = purchases.vat;
            r2.gross_amount = purchases.gross;
            
            // Add Summary Block Rows
            let s1 = frm.add_child('total_entries');
            s1.summary = 'Output VAT';
            s1.value = sales.vat;
            
            let s2 = frm.add_child('total_entries');
            s2.summary = 'Input VAT';
            s2.value = purchases.vat;
            
            let s3 = frm.add_child('total_entries');
            s3.summary = 'Net VAT Payable';
            s3.value = sales.vat - purchases.vat;
            
            frm.refresh_field('vat_entries');
            frm.refresh_field('total_entries');
            frappe.show_alert({message: __('VAT Summary generated successfully!'), indicator: 'green'});
        });
    }
});

frappe.ui.form.on("BIR VAT Summary", {company:function(frm){
        ["vat_entries", "total_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},from_date:function(frm){
        ["vat_entries", "total_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},to_date:function(frm){
        ["vat_entries", "total_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
}});

})();
