/* Payment-based cash journals. Filled into one Client Script per journal.
   All quantities are in company currency and come from non-cancelled GL entries.
   Tax breakdowns are left unclassified; invoice totals are never called cash. */
frappe.ui.form.on(BIR_DOCTYPE, {
    generate_report: async function(frm) {
        const outgoing = frm.doctype === 'BIR Cash Disbursement Journal' || frm.doc.doctype === 'BIR Cash Disbursement Journal';
        const fields = ['journal_entries', 'account_summary'];
        fields.forEach(f => { frm.clear_table(f); frm.refresh_field(f); });
        if (!frm.doc.company || !frm.doc.from_date || !frm.doc.to_date)
            return frappe.throw(__('Select a company and date range.'));
        if (frm.doc.from_date > frm.doc.to_date)
            return frappe.throw(__('From Date must be on or before To Date.'));
        const call = (method,args) => new Promise((resolve,reject) => frappe.call({method,args,
            callback:r=>resolve(r.message),error:reject}));
        const list = async (doctype,filters,columns) => {
            let rows=[];
            for(let start=0; ; start+=500) {
                const page=await call('frappe.client.get_list',{doctype,filters,fields:columns,
                    order_by:'name asc',limit_start:start,limit_page_length:500});
                rows=rows.concat(page || []);if(!page || page.length<500)return rows;
                if(start>=99500)throw new Error('Too many records. Narrow the date range.');
            }
        };
        try {
            const accounts=await list('Account',{company:frm.doc.company},['name','account_name','account_type']);
            const cashAccounts=new Set(accounts.filter(a=>['Cash','Bank'].includes(a.account_type)).map(a=>a.name));
            if(!cashAccounts.size)throw new Error('No Cash or Bank accounts are configured for this company.');
            const entries=await list('GL Entry',{company:frm.doc.company,is_cancelled:0,
                posting_date:['between',[frm.doc.from_date,frm.doc.to_date]]},
                ['name','posting_date','voucher_type','voucher_no','account','debit','credit','party','party_type','remarks']);
            const vouchers=new Map();
            entries.forEach(e=>{const key=JSON.stringify([e.voucher_type,e.voucher_no]);if(!vouchers.has(key))vouchers.set(key,[]);vouchers.get(key).push(e);});
            const accountTotals=new Map();let count=0;
            for(const lines of [...vouchers.values()].sort((a,b)=>a[0].posting_date.localeCompare(b[0].posting_date) || a[0].voucher_no.localeCompare(b[0].voucher_no))) {
                const cash=lines.filter(e=>cashAccounts.has(e.account));
                const net=cash.reduce((n,e)=>n+Number(e.debit || 0)-Number(e.credit || 0),0);
                // Internal bank/cash transfers net to zero and are not receipts/payments.
                if(Math.abs(net)<0.000001)continue;
                const isOut=net<0;if(isOut!==outgoing)continue;
                const first=lines[0],partyLine=lines.find(e=>e.party),amount=Math.abs(net);
                const row=frm.add_child('journal_entries');
                row.date=first.posting_date;row.invoice_no=first.voucher_no;
                row.status='POSTED';row.discount_type='';row.discount_amount=null;
                row.total=amount;
                const party=partyLine?.party || first.remarks || first.voucher_type;
                if(outgoing) {row.payee=party;row.nature=first.voucher_type;row.net_paid=amount;
                    row.vatable=null;row.input_vat=null;row.zero=null;row.exempt=null;row.ewt=null;}
                else {row.payor=party;row.rendered=first.voucher_type;row.net_cash=amount;
                    row.vatable=null;row.output_vat=null;row.zero_rated=null;row.vat_exempt=null;row.w_tax=null;
                    row.note='Actual net cash/bank movement; reference is the source voucher.';}
                for(const e of lines){if(!accountTotals.has(e.account))accountTotals.set(e.account,{debit:0,credit:0});
                    const total=accountTotals.get(e.account);total.debit+=Number(e.debit || 0);total.credit+=Number(e.credit || 0);}
                count++;
            }
            let debits=0,credits=0;
            for(const [account,amount] of [...accountTotals.entries()].sort((a,b)=>a[0].localeCompare(b[0]))) {
                const row=frm.add_child('account_summary');row.account_title=account;
                row.debit=amount.debit;row.credit=amount.credit;debits+=amount.debit;credits+=amount.credit;
            }
            if(count){const row=frm.add_child('account_summary');row.account_title='Total';row.debit=debits;row.credit=credits;}
            fields.forEach(f=>frm.refresh_field(f));
            frappe.msgprint(count+' posted cash/bank vouchers loaded. Tax and discount breakdowns are unclassified pending approved mappings; blank values must not be interpreted as zero.');
        } catch(error) {
            fields.forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});
            frappe.msgprint('Unable to generate the cash journal. '+(error.message || 'Check permissions and retry.'));
            throw error;
        }
    }
});
