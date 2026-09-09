"""Build reviewable fixes from a fresh live BIR backup. Does not deploy."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT.parent / "backups/bir_fix_20260909"
OUT = ROOT / "bir_fixes"
OUT.mkdir(exist_ok=True)

HELPERS = r"""
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
"""

scripts = json.loads((BACKUP / "Client_Script.json").read_text())
for record in scripts:
    dt = record["dt"]
    meta = json.loads((ROOT.parent / "backups/bir_audit_20260909" / (dt.replace(" ", "_") + "_meta.json")).read_text())
    tables = [f["fieldname"] for f in meta["fields"] if f["fieldtype"] == "Table"]
    reset = "\n        " + json.dumps(tables) + ".forEach(f=>{frm.clear_table(f);frm.refresh_field(f);});\n"
    code = record["script"]
    if dt in ["BIR Cash Receipt Journal", "BIR Cash Disbursement Journal"]:
        code = (ROOT / "bir_cash_report.js").read_text().replace("BIR_DOCTYPE", json.dumps(dt))
    else:
        code = code.replace("generate_report: function(frm) {", "generate_report: async function(frm) {" + reset + "\n        if(frm.doc.from_date>frm.doc.to_date) return frappe.throw('From Date must be on or before To Date.');\n")
        code = code.replace("frappe.call({", "birCall({")
        if dt in ["BIR General Ledger", "BIR General Journal"]:
            code = code.replace("company: frm.doc.company,", "company: frm.doc.company,\n                    is_cancelled: 0,")
        if dt == "BIR General Journal":
            code = code.replace("// Render transactions into the child table", "// Render transactions into the child table")
            code = code.replace("Promise.all([get_pi_status(), get_si_status()]).then(() => {", "Promise.all([get_pi_status(), get_si_status(), birList({doctype:'Account',filters:{company:frm.doc.company},fields:['name','account_name','account_number']})]).then(results => {\n                        const birAccounts=Object.fromEntries(results[2].map(a=>[a.name,a]));")
            code = code.replace("invoice_statuses[tx.voucher_no] || 'PAID'", "invoice_statuses[tx.voucher_no] || 'POSTED'")
            code = code.replace("row.code = parts[0] || '';", "row.code = (birAccounts[post.account]||{}).account_number || '';")
            code = code.replace("row.account_title = parts[1] || '';", "row.account_title = (birAccounts[post.account]||{}).account_name || post.account;")
        if dt == "BIR General Ledger":
            code = code.replace("        birCall({", "        const birOpeningRows = await birList({doctype:'GL Entry', filters:{company:frm.doc.company,is_cancelled:0,posting_date:['<',frm.doc.from_date]},fields:['account','debit','credit']});\n        const birOpening={};birOpeningRows.forEach(r=>{birOpening[r.account]=(birOpening[r.account]||0)+Number(r.debit||0)-Number(r.credit||0);});\n        birCall({", 1)
            code = code.replace("if (r.message && r.message.length > 0)", "if ((r.message && r.message.length > 0) || Object.values(birOpening).some(v=>Math.abs(v)>0.000001))")
            code = code.replace("Object.keys(grouped).sort().forEach(account => {", "Object.keys(birOpening).forEach(a=>{if(Math.abs(birOpening[a])>0.000001 && !grouped[a])grouped[a]=[];});\n                    Object.keys(grouped).sort().forEach(account => {")
            code = code.replace("let running_balance = 0;", "let running_balance = birOpening[account] || 0;\n                        if(Math.abs(running_balance)>0.000001){const opening=frm.add_child('gl_entries');Object.assign(opening,{account,date:frm.doc.from_date,description:'Opening balance',debit:0,credit:0,balance:running_balance,indent:1,is_total_row:0});}")
        if dt == "BIR Form 2307":
            code = code.replace("// 1. Fetch Company details", "const start=new Date(frm.doc.from_date+'T00:00:00'),end=new Date(frm.doc.to_date+'T00:00:00');\n        if(start.getFullYear()!==end.getFullYear() || Math.floor(start.getMonth()/3)!==Math.floor(end.getMonth()/3)) return frappe.throw('Select dates within one calendar quarter.');\n        // 1. Fetch Company details")
            code = code.replace("comp.tax_id || '314-579-230-000'", "comp.tax_id || ''")
            code = code.replace("comp.billing_address || 'Davao City'", "comp.billing_address || ''")
            code = code.replace("'8000'", "''")
            code = code.replace("let start_date = frappe.datetime.str_to_obj(frm.doc.from_date);", "let start_date = frappe.datetime.str_to_obj(frm.doc.from_date); start_date.setMonth(Math.floor(start_date.getMonth()/3)*3); start_date.setDate(1);")
        code = HELPERS + "\n" + code
    # Clear stale results whenever reporting scope changes, before printing/saving.
    extra = "\nfrappe.ui.form.on(" + json.dumps(dt) + ", {" + ",".join(f"{field}:function(frm){{" + reset + "}" for field in ["company", "from_date", "to_date"]) + "});\n"
    code = "(() => {\n" + code + extra + "\n})();\n"
    record["script"] = code
    (OUT / (dt.replace(" ", "_") + ".js")).write_text(code, encoding="utf-8")
(OUT / "client_scripts.json").write_text(json.dumps(scripts, indent=2), encoding="utf-8")

formats = json.loads((BACKUP / "Print_Format.json").read_text())
import re
for record in formats:
    html = record["html"]
    if record['doc_type'] == 'BIR Form 2307':
        html = html.replace('/files/bir_2307_page1.png', '/files/bir_2307_restored_20260909.png')
    # Eliminate fabricated literals; retain values explicitly entered in the form.
    html = html.replace("'Davao City, Davao Del Sur'", "''").replace("'8000'", "''")
    html = html.replace("'orbyleofficial@gmail.com'", "''").replace("'09458269902'", "''")
    if record["doc_type"] != "BIR Form 2307":
        html = "{% set bir_company = frappe.get_doc('Company', doc.company) %}\n" + html
        html = re.sub(r"{{\s*doc\.tin(?:\s+or\s+[^}]+)?\s*}}", "{{ bir_company.tax_id or '' }}", html)
        html = html.replace("{{ doc.company }}", "{{ bir_company.company_name or doc.company }}")
        html += '''<style>
        .bir-table { width:100%; table-layout:fixed; }
        .bir-table th, .bir-table td { white-space:normal !important; overflow-wrap:anywhere; word-wrap:break-word; padding:3px 2px; }
        .bir-table thead { display:table-header-group; }
        .bir-table tr { page-break-inside:avoid; }
        @media print { .bir-table { font-size:7.5px; } }
        </style>'''
    if record["doc_type"] in ["BIR Cash Receipt Journal", "BIR Cash Disbursement Journal"]:
        # Cash vouchers are not necessarily invoices; do not mislabel references.
        html = html.replace("Invoice No.", "Source Voucher").replace("Invoice No", "Source Voucher").replace("INVOICE NO.", "SOURCE VOUCHER")
        html = re.sub(r'>\s*Invoice\s*<', '>Source Voucher<', html, flags=re.I)
        html = html.replace("{{ row.discount_type or 'NONE' }}", '—')
        html = html.replace("For the month of {{ from_date_obj.strftime('%B') | upper }} {{ from_date_obj.strftime('%Y') }}", "Period: {{ doc.from_date }} to {{ doc.to_date }}")
        html = '<p style="font-size:9px">Cash/bank movements from posted ledger entries. Source references may be payments, invoices or journal entries. Tax/discount breakdowns are unclassified until approved mappings are configured.</p>' + html
        for field in ['vatable','input_vat','output_vat','zero','zero_rated','exempt','vat_exempt','ewt','w_tax','discount_amount']:
            html = re.sub(r"{{\s*frappe\.utils\.fmt_money\(row\."+field+r"\s+or\s+0([^}]*)\)\s*}}", "—", html)
        for field in ['vatable','input_vat','output_vat','zero','zero_rated','exempt','vat_exempt','ewt','w_tax','discount_amount','discount']:
            html = re.sub(r'{{\s*"\{:,.2f\}"\.format\((?:row|totals)\.'+field+r'(?:\s+or\s+0)?\)\s*}}', '—', html)
    record["html"] = html
(OUT / "print_formats.json").write_text(json.dumps(formats, indent=2), encoding="utf-8")
print("Prepared", len(scripts), "scripts and", len(formats), "formats")
