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

frappe.ui.form.on('BIR Form 2307', {
    generate_report: async function(frm) {
        ["withholding_details"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});

        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');

        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date || !frm.doc.party) {
            frappe.throw(__('Please select Company, Date range, Party Type and Party first.'));
            return;
        }
        
        const start=new Date(frm.doc.from_date+'T00:00:00'),end=new Date(frm.doc.to_date+'T00:00:00');
        if(start.getFullYear()!==end.getFullYear() || Math.floor(start.getMonth()/3)!==Math.floor(end.getMonth()/3)) return frappe.throw('Select dates within one calendar quarter.');
        // 1. Fetch Company details
        let get_company_details = function() {
            return new Promise((resolve) => {
                birCall({
                    method: 'frappe.client.get',
                    args: { doctype: 'Company', name: frm.doc.company },
                    callback: function(r) { resolve(r.message || {}); }
                });
            });
        };
        
        // 2. Fetch Party details
        let get_party_details = function() {
            return new Promise((resolve) => {
                birCall({
                    method: 'frappe.client.get',
                    args: { doctype: frm.doc.party_type, name: frm.doc.party },
                    callback: function(r) { resolve(r.message || {}); }
                });
            });
        };
        
        // 3. Fetch Invoices list
        let get_invoices = function() {
            return new Promise((resolve) => {
                let dt = frm.doc.party_type === 'Customer' ? 'Sales Invoice' : 'Purchase Invoice';
                let party_field = frm.doc.party_type === 'Customer' ? 'customer' : 'supplier';
                let filters = {
                    company: frm.doc.company,
                    posting_date: ['between', [frm.doc.from_date, frm.doc.to_date]],
                    docstatus: 1
                };
                filters[party_field] = frm.doc.party;
                
                birCall({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: dt,
                        filters: filters,
                        fields: ['name', 'posting_date', 'net_total'],
                        limit_page_length: 5000
                    },
                    callback: function(r) { resolve(r.message || []); }
                });
            });
        };
        
        Promise.all([get_company_details(), get_party_details(), get_invoices()]).then(results => {
            let comp = results[0];
            let party = results[1];
            let invoices = results[2];
            
            // Set Payee and Payor info
            let clean_address = function(addr) {
                return (addr || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
            };
            
            if (frm.doc.party_type === 'Customer') {
                // Payee is Company, Payor is Customer
                frm.set_value('payee_name', comp.company_name);
                frm.set_value('payee_tin', comp.tax_id || '');
                frm.set_value('payee_address', clean_address(comp.billing_address || ''));
                frm.set_value('payee_zip', '');
                
                frm.set_value('payor_name', party.customer_name);
                frm.set_value('payor_tin', party.tax_id || '');
                frm.set_value('payor_address', clean_address(party.primary_address || ''));
                frm.set_value('payor_zip', '');
            } else {
                // Payee is Supplier, Payor is Company
                frm.set_value('payee_name', party.supplier_name);
                frm.set_value('payee_tin', party.tax_id || '');
                frm.set_value('payee_address', clean_address(party.primary_address || ''));
                frm.set_value('payee_zip', '');
                
                frm.set_value('payor_name', comp.company_name);
                frm.set_value('payor_tin', comp.tax_id || '');
                frm.set_value('payor_address', clean_address(comp.billing_address || ''));
                frm.set_value('payor_zip', '');
            }
            
            if (invoices.length === 0) {
                frm.clear_table('withholding_details');
                frm.refresh_field('withholding_details');
                frappe.show_alert({message: __('No invoices found in this period.'), indicator: 'orange'});
                return;
            }
            
            let inv_names = invoices.map(i => i.name);
            let inv_map = {};
            invoices.forEach(i => { inv_map[i.name] = i; });
            
            // 4. Fetch GL Entries for withholding
            birCall({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'GL Entry',
                    filters: { voucher_no: ['in', inv_names] },
                    fields: ['voucher_no', 'account', 'debit', 'credit', 'posting_date'],
                    limit_page_length: 5000
                },
                callback: function(gl_res) {
                    let grouped_data = {};
                    let start_date = frappe.datetime.str_to_obj(frm.doc.from_date); start_date.setMonth(Math.floor(start_date.getMonth()/3)*3); start_date.setDate(1);
                    let start_month = start_date.getMonth() + 1; // 1-12
                    
                    if (gl_res.message) {
                        gl_res.message.forEach(gl => {
                            let head = (gl.account || '').toLowerCase();
                            if (head.includes('ewt') || head.includes('withholding') || head.includes('creditable') || head.includes('tds')) {
                                let inv = inv_map[gl.voucher_no];
                                if (!inv) return;
                                
                                let amt = Math.abs((gl.debit || 0) - (gl.credit || 0));
                                let rate = Math.round((amt / (inv.net_total || 1)) * 100 * 100) / 100;
                                
                                // Determine ATC code and description based on rate
                                let atc = 'WI150';
                                let desc = 'Professional fees paid to medical practitioners / consultants';
                                if (rate === 5.0) {
                                    atc = 'WI100';
                                    desc = 'Rentals: On gross rental or lease of real property';
                                } else if (rate === 1.0) {
                                    atc = 'WI152';
                                    desc = 'Income payments to certain contractors';
                                }
                                
                                // Determine Month index (0, 1, 2)
                                let post_date = frappe.datetime.str_to_obj(gl.posting_date);
                                let m = post_date.getMonth() + 1;
                                let month_idx = m - start_month;
                                if (month_idx < 0 || month_idx > 2) month_idx = 0; // fallback
                                
                                if (!grouped_data[atc]) {
                                    grouped_data[atc] = {
                                        desc: desc,
                                        month_1: 0,
                                        month_2: 0,
                                        month_3: 0,
                                        total_income: 0,
                                        tax_withheld: 0
                                    };
                                }
                                
                                // Split income payment base and tax withheld
                                if (month_idx === 0) {
                                    grouped_data[atc].month_1 += inv.net_total || 0;
                                } else if (month_idx === 1) {
                                    grouped_data[atc].month_2 += inv.net_total || 0;
                                } else if (month_idx === 2) {
                                    grouped_data[atc].month_3 += inv.net_total || 0;
                                }
                                
                                grouped_data[atc].total_income += inv.net_total || 0;
                                grouped_data[atc].tax_withheld += amt;
                            }
                        });
                    }
                    
                    frm.clear_table('withholding_details');
                    
                    Object.keys(grouped_data).forEach(atc => {
                        let gd = grouped_data[atc];
                        let row = frm.add_child('withholding_details');
                        row.nature_of_payment = gd.desc;
                        row.atc = atc;
                        row.month_1 = gd.month_1;
                        row.month_2 = gd.month_2;
                        row.month_3 = gd.month_3;
                        row.total_income = gd.total_income;
                        row.tax_withheld = gd.tax_withheld;
                    });
                    
                    frm.refresh_field('withholding_details');
                    frappe.show_alert({message: __('BIR Form 2307 data populated successfully!'), indicator: 'green'});
                }
            });
        });
    }
});

frappe.ui.form.on("BIR Form 2307", {company:function(frm){
        ["withholding_details"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},from_date:function(frm){
        ["withholding_details"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},to_date:function(frm){
        ["withholding_details"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
}});

})();
