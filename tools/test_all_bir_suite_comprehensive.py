import urllib.request
import urllib.parse
import json
import http.cookiejar
import traceback
import sys

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

VPS_BASE = 'http://38.247.138.224:10017'

print("=" * 80)
print("COMPREHENSIVE END-TO-END TEST SUITE: BIR MODULES & PRINT LAYOUTS")
print(f"Target: {VPS_BASE}")
print("=" * 80)

# Step 0: Login
login_data = urllib.parse.urlencode({'usr': 'Administrator', 'pwd': 'admin'}).encode()
res = op.open(urllib.request.Request(f'{VPS_BASE}/api/method/login', data=login_data, headers=H))
print(f"[OK] Logged in as Administrator: {res.getcode()}\n")

# Get active company
c_req = urllib.request.Request(f'{VPS_BASE}/api/resource/Company?limit_page_length=1', headers=H)
c_res = json.loads(op.open(c_req).read().decode('utf-8'))
COMPANY = c_res['data'][0]['name']
print(f"Using Test Company: {COMPANY}\n")

modules = [
    {
        'doctype': 'BIR Form 2307',
        'print_format': 'BIR Form 2307 Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'party_type': 'Customer',
            'party': 'Cash Customer',
            'payee_tin': '987-654-321-000',
            'payee_name': 'Fleet Logistics Hub Inc.',
            'payee_address': 'Dau, Mabalacat City, Pampanga',
            'payee_zip': '2010',
            'payor_tin': '123-456-789-000',
            'payor_name': COMPANY,
            'payor_address': 'MacArthur Highway, Dau, Pampanga',
            'payor_zip': '2010',
            'rows': [
                {
                    'atc': 'WC100',
                    'tax_rate': 2.0,
                    'income_payment': 'Professional / Service Fees',
                    'q1': 50000.0,
                    'q2': 0.0,
                    'q3': 0.0,
                    'total': 50000.0,
                    'tax_withheld': 1000.0
                }
            ]
        }
    },
    {
        'doctype': 'BIR Sales Journal',
        'print_format': 'BIR Sales Journal Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'line_of_business': 'Automotive & Tire Services',
            'sales_entries': [
                {
                    'date': '2026-06-15',
                    'payor': 'Metro Fleet Logistics',
                    'tin': '999-888-777-000',
                    'address': 'San Fernando, Pampanga',
                    'invoice_no': 'SINV-2026-0001',
                    'goods_services': 'Goods',
                    'discount_type': 'NONE',
                    'discount_amount': 0,
                    'vatable_sales': 100000.0,
                    'output_vat': 12000.0,
                    'zero_rated': 0.0,
                    'vat_exempt': 0.0,
                    'total_sales': 112000.0,
                    'w_tax': 1000.0,
                    'total_receivable': 111000.0,
                    'status_ref_date': 'PAID / SINV-2026-0001',
                    'payment_date': '06-20-2026',
                    'remarks': 'Michelin Tire Replacement'
                }
            ],
            'summary_entries': [
                {'summary': 'Documents', 'value': 1},
                {'summary': 'Total Taxable', 'value': 100000.0},
                {'summary': 'Total VAT', 'value': 12000.0},
                {'summary': 'Total Gross', 'value': 112000.0}
            ]
        }
    },
    {
        'doctype': 'BIR Purchases Book',
        'print_format': 'BIR Purchases Book Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'line_of_business': 'Automotive & Tire Services',
            'purchases_entries': [
                {
                    'date': '2026-05-10',
                    'supplier': 'Michelin Philippines Inc.',
                    'tin': '111-222-333-000',
                    'address': 'Makati City, Metro Manila',
                    'invoice_no': 'PINV-2026-0001',
                    'description': 'Tire Stock Importation',
                    'vatable_purchases': 200000.0,
                    'input_vat': 24000.0,
                    'zero_rated': 0.0,
                    'vat_exempt': 0.0,
                    'total_purchases': 224000.0,
                    'w_tax': 2000.0,
                    'total_payable': 222000.0
                }
            ]
        }
    },
    {
        'doctype': 'BIR Cash Receipt Journal',
        'print_format': 'BIR Cash Receipt Journal Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'line_of_business': 'Automotive & Tire Services',
            'crj_entries': [
                {
                    'date': '2026-06-20',
                    'customer': 'Metro Fleet Logistics',
                    'or_no': 'OR-2026-0001',
                    'ref_invoice': 'SINV-2026-0001',
                    'mode_of_payment': 'Bank Transfer - BDO',
                    'gross_amount': 112000.0,
                    'discount': 0.0,
                    'wtax': 1000.0,
                    'net_collected': 111000.0,
                    'remarks': 'Full settlement via BDO'
                }
            ],
            'summary_entries': [
                {'summary': 'Total Receipts', 'value': 111000.0}
            ]
        }
    },
    {
        'doctype': 'BIR Cash Disbursement Journal',
        'print_format': 'BIR Cash Disbursement Journal Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'line_of_business': 'Automotive & Tire Services',
            'cdj_entries': [
                {
                    'date': '2026-05-15',
                    'payee': 'Michelin Philippines Inc.',
                    'voucher_no': 'CV-2026-0001',
                    'ref_invoice': 'PINV-2026-0001',
                    'bank_account': 'BDO Current Account',
                    'check_no': 'CHK-889912',
                    'gross_amount': 224000.0,
                    'wtax': 2000.0,
                    'net_paid': 222000.0,
                    'remarks': 'Payment for inventory delivery'
                }
            ],
            'summary_entries': [
                {'summary': 'Total Disbursements', 'value': 222000.0}
            ]
        }
    },
    {
        'doctype': 'BIR General Journal',
        'print_format': 'BIR General Journal Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'entries': [
                {
                    'date': '2026-06-30',
                    'jv_no': 'JV-2026-0001',
                    'account': 'Accumulated Depreciation - Motor Vehicles',
                    'debit': 15000.0,
                    'credit': 0.0,
                    'explanation': 'Monthly depreciation entry'
                },
                {
                    'date': '2026-06-30',
                    'jv_no': 'JV-2026-0001',
                    'account': 'Depreciation Expense',
                    'debit': 0.0,
                    'credit': 15000.0,
                    'explanation': 'Monthly depreciation entry'
                }
            ]
        }
    },
    {
        'doctype': 'BIR General Ledger',
        'print_format': 'BIR General Ledger Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-01-01',
            'to_date': '2026-12-31',
            'account': 'Cash and Cash Equivalents',
            'tin': '123-456-789-000',
            'entries': [
                {
                    'posting_date': '2026-06-01',
                    'voucher_type': 'Opening Balance',
                    'voucher_no': 'OPEN-2026',
                    'debit': 500000.0,
                    'credit': 0.0,
                    'balance': 500000.0,
                    'remarks': 'Beginning balance'
                },
                {
                    'posting_date': '2026-06-20',
                    'voucher_type': 'Payment Entry',
                    'voucher_no': 'PE-2026-0001',
                    'debit': 111000.0,
                    'credit': 0.0,
                    'balance': 611000.0,
                    'remarks': 'Customer collection'
                }
            ]
        }
    },
    {
        'doctype': 'BIR VAT Summary',
        'print_format': 'BIR VAT Summary Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-06-01',
            'to_date': '2026-06-30',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'line_of_business': 'Automotive & Tire Services',
            'vat_entries': [
                {
                    'category': 'Output VAT',
                    'source': 'Sales Book',
                    'documents': 1,
                    'taxable_amount': 100000.0,
                    'vat_amount': 12000.0,
                    'gross_amount': 112000.0
                },
                {
                    'category': 'Input VAT',
                    'source': 'Purchases Book',
                    'documents': 1,
                    'taxable_amount': 200000.0,
                    'vat_amount': 24000.0,
                    'gross_amount': 224000.0
                }
            ],
            'total_entries': [
                {'summary': 'Output VAT', 'value': 12000.0},
                {'summary': 'Input VAT', 'value': 24000.0},
                {'summary': 'Net VAT Payable / (Excess Credit)', 'value': -12000.0}
            ]
        }
    },
    {
        'doctype': 'BIR Withholding Summary',
        'print_format': 'BIR Withholding Summary Print Format',
        'sample': {
            'company': COMPANY,
            'from_date': '2026-06-01',
            'to_date': '2026-06-30',
            'tin': '123-456-789-000',
            'rdo': '021B',
            'withholding_entries': [
                {
                    'document_type': 'Sales Invoice',
                    'doc_date': '2026-06-15',
                    'tax_date': '2026-06-15',
                    'doc_no': 'SINV-2026-0001',
                    'bp_code': 'CUST-001',
                    'bp_name': 'Metro Fleet Logistics',
                    'tin': '999-888-777-000',
                    'wt_code': 'WC100 - EWT',
                    'wt_rate': 2.0,
                    'wt_taxable': 100000.0,
                    'wt_amount': 2000.0,
                    'status': 'Posted'
                }
            ]
        }
    }
]

results = []

for idx, item in enumerate(modules, 1):
    dt = item['doctype']
    pf = item['print_format']
    sample = item['sample']
    
    print(f"\n[{idx}/9] TESTING: {dt}")
    print(f"      Print Format: {pf}")
    
    # 1. Test DocType existence
    try:
        req = urllib.request.Request(f'{VPS_BASE}/api/resource/DocType/{urllib.parse.quote(dt)}', headers=H)
        dt_res = json.loads(op.open(req).read().decode('utf-8'))
        print(f"      -> DocType Schema: OK ({len(dt_res.get('data', {}).get('fields', []))} fields)")
    except Exception as e:
        print(f"      -> [FAIL] DocType schema error: {e}")
        results.append({'module': dt, 'status': 'FAIL', 'error': str(e)})
        continue
        
    # 2. Test Client Script
    try:
        q = urllib.parse.quote(json.dumps([["dt", "=", dt]]))
        req = urllib.request.Request(f'{VPS_BASE}/api/resource/Client%20Script?filters={q}&fields={urllib.parse.quote(json.dumps(["name","enabled"]))}', headers=H)
        cs_res = json.loads(op.open(req).read().decode('utf-8'))
        cs_data = cs_res.get('data', [])
        if cs_data and cs_data[0].get('enabled'):
            print(f"      -> Client Script ({cs_data[0]['name']}): ACTIVE [OK]")
        else:
            print(f"      -> Client Script: Missing or disabled: {cs_data}")
    except Exception as e:
        print(f"      -> [WARN] Client script check: {e}")

    # 3. Test Record Creation (Insert & Readback)
    created_id = None
    try:
        payload = dict(sample)
        payload['doctype'] = dt
        req_data = urllib.parse.urlencode({'data': json.dumps(payload)}).encode('utf-8')
        req = urllib.request.Request(f'{VPS_BASE}/api/resource/{urllib.parse.quote(dt)}', data=req_data, headers=H)
        ins_res = json.loads(op.open(req).read().decode('utf-8'))
        created_id = ins_res.get('data', {}).get('name')
        print(f"      -> Record Created & Saved: {created_id} [OK]")
    except Exception as e:
        print(f"      -> [FAIL] Record creation error: {e}")
        results.append({'module': dt, 'status': 'FAIL', 'error': f"Record creation: {e}"})
        continue

    # 4. Test Print Format Render
    try:
        # Fetch fresh doc
        req = urllib.request.Request(f'{VPS_BASE}/api/resource/{urllib.parse.quote(dt)}/{urllib.parse.quote(created_id)}', headers=H)
        doc_res = json.loads(op.open(req).read().decode('utf-8'))
        fresh_doc = doc_res.get('data', {})
        
        print_url = f"{VPS_BASE}/api/method/frappe.www.printview.get_html_and_style?doc={urllib.parse.quote(json.dumps(fresh_doc))}&print_format={urllib.parse.quote(pf)}&doctype={urllib.parse.quote(dt)}"
        p_req = urllib.request.Request(print_url, headers=H)
        p_res = json.loads(op.open(p_req).read().decode('utf-8'))
        html = p_res.get('message', {}).get('html', '')
        
        if html and len(html) > 100:
            print(f"      -> Print Layout Render: SUCCESS ({len(html)} bytes HTML) [OK]")
            results.append({'module': dt, 'status': 'PASS', 'record': created_id, 'render_bytes': len(html)})
        else:
            print(f"      -> [FAIL] Print render produced empty/invalid HTML: {html[:100]}")
            results.append({'module': dt, 'status': 'FAIL', 'error': 'Empty HTML output'})
    except Exception as e:
        print(f"      -> [FAIL] Print render error: {e}")
        results.append({'module': dt, 'status': 'FAIL', 'error': f"Print render: {e}"})

print("\n" + "=" * 80)
print("FINAL TEST RESULTS SUMMARY")
print("=" * 80)
all_pass = True
for r in results:
    status_tag = "[PASS]" if r['status'] == 'PASS' else "[FAIL]"
    if r['status'] != 'PASS':
        all_pass = False
        print(f"{status_tag} {r['module']:<35} | Error: {r.get('error')}")
    else:
        print(f"{status_tag} {r['module']:<35} | Sample: {r.get('record')} | Render: {r.get('render_bytes')} bytes HTML")

print("=" * 80)
if all_pass:
    print(">>> 100% ALL 9 BIR MODULES AND PRINT LAYOUTS ARE FULLY WORKING! <<<")
else:
    print(">>> SOME MODULES HAD ISSUES. PLEASE CHECK ABOVE LOGS. <<<")
print("=" * 80)
