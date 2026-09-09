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

frappe.ui.form.on('BIR General Ledger', {
    generate_report: async function(frm) {
        ["gl_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});

        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');

        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date) {
            frappe.throw(__('Please select Company, From Date, and To Date first.'));
            return;
        }
        
        const birOpeningRows = await birList({doctype:'GL Entry', filters:{company:frm.doc.company,is_cancelled:0,posting_date:['<',frm.doc.from_date]},fields:['account','debit','credit']});
        const birOpening={};birOpeningRows.forEach(r=>{birOpening[r.account]=(birOpening[r.account]||0)+Number(r.debit||0)-Number(r.credit||0);});
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
                order_by: 'account asc, posting_date asc, name asc'
            },
            callback: function(r) {
                if ((r.message && r.message.length > 0) || Object.values(birOpening).some(v=>Math.abs(v)>0.000001)) {
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
                    Object.keys(birOpening).forEach(a=>{if(Math.abs(birOpening[a])>0.000001 && !grouped[a])grouped[a]=[];});
                    Object.keys(grouped).sort().forEach(account => {
                        let entries = grouped[account];
                        let running_balance = birOpening[account] || 0;
                        if(Math.abs(running_balance)>0.000001){const opening=frm.add_child('gl_entries');Object.assign(opening,{account,date:frm.doc.from_date,description:'Opening balance',debit:0,credit:0,balance:running_balance,indent:1,is_total_row:0});}
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

frappe.ui.form.on("BIR General Ledger", {company:function(frm){
        ["gl_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},from_date:function(frm){
        ["gl_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
},to_date:function(frm){
        ["gl_entries"].forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
}});

})();
