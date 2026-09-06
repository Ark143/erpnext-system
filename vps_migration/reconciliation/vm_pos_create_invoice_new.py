# Shared source prepended to the POS reconciliation Server Scripts.
# No imports: compatible with Frappe Server Script safe_exec.

def recon_user():
    user = frappe.session.user
    if not user or user == 'Guest':
        frappe.throw('Please sign in before using POS reconciliation.')
    return user


def recon_states(invoices):
    names = [i['name'] for i in invoices]
    refs = []
    if names:
        refs = frappe.get_all('POS Invoice Reference',
            filters={'pos_invoice': ['in', names], 'parenttype': 'POS Closing Entry'},
            fields=['pos_invoice', 'parent'], limit_page_length=0)
    parents = list(set([r['parent'] for r in refs]))
    closings = {}
    if parents:
        for row in frappe.get_all('POS Closing Entry',
            filters={'name': ['in', parents], 'docstatus': ['<', 2]},
            fields=['name', 'status', 'docstatus', 'pos_opening_entry'], limit_page_length=0):
            closings[row['name']] = row
    links = {}
    for ref in refs:
        closing = closings.get(ref['parent'])
        if closing:
            previous = links.get(ref['pos_invoice'])
            if not previous or closing['docstatus'] > previous['docstatus']:
                links[ref['pos_invoice']] = closing
    result = {}
    for invoice in invoices:
        closing = links.get(invoice['name'])
        status = 'Not reconciled'
        reconciled = False
        if invoice.get('docstatus') == 2:
            status = 'Cancelled'
        elif invoice.get('docstatus') == 0:
            status = 'Draft invoice'
        elif closing:
            if closing['docstatus'] == 0:
                status = 'Closing draft'
            elif closing.get('status') == 'Failed':
                status = 'Closing failed'
            elif closing.get('status') == 'Queued':
                status = 'Closing in progress'
            elif closing.get('status') == 'Submitted':
                status = 'Reconciled'
                reconciled = True
            else:
                status = 'Closing in progress'
        elif invoice.get('consolidated_invoice'):
            status = 'Consolidated'
            reconciled = True
        result[invoice['name']] = {
            'reconciliation_status': status, 'is_reconciled': reconciled,
            'closing_entry': closing['name'] if closing else None,
            'closing_status': closing.get('status') if closing else None,
            'closing_opening_entry': closing.get('pos_opening_entry') if closing else None,
            'eligible_for_closing': status == 'Not reconciled'
        }
    return result


def recon_opening(user, company=None, name=None, lock=False):
    if name:
        doc = frappe.get_doc('POS Opening Entry', name, for_update=lock)
        if doc.user != user:
            frappe.throw('This shift belongs to another cashier.')
        if company and doc.company != company:
            frappe.throw('The selected shift belongs to another branch.')
        if doc.docstatus != 1 or doc.status != 'Open':
            frappe.throw('This shift is no longer open. Refresh the POS.')
        if frappe.utils.get_date_str(doc.period_start_date) != frappe.utils.today():
            frappe.db.set_value('POS Opening Entry', doc.name, {
                'posting_date': frappe.utils.today(),
                'period_start_date': frappe.utils.now_datetime()
            })
            frappe.db.commit()
            doc.reload()
        return doc
    filters = {'user': user, 'status': 'Open', 'docstatus': 1}
    if company:
        filters['company'] = company
    rows = frappe.get_all('POS Opening Entry', filters=filters,
        fields=['name'], order_by='period_start_date asc', limit_page_length=0)
    if len(rows) > 1:
        frappe.throw('Multiple open shifts exist for this cashier. Resolve them in POS Opening Entry first.')
    return recon_opening(user, company, rows[0]['name'], lock) if rows else None


def recon_pending_closing(opening):
    rows = frappe.get_all('POS Closing Entry',
        filters={'pos_opening_entry': opening.name, 'docstatus': ['<', 2]},
        fields=['name', 'status', 'docstatus'], order_by='creation desc', limit_page_length=1)
    return rows[0] if rows else None


def recon_candidates(opening):
    # Recover earlier unpaid reconciliation work as well as this shift's invoices.
    # ERPNext requires the same cashier, company and POS Profile on a closing entry.
    rows = frappe.get_all('POS Invoice',
        filters={'owner': opening.user, 'company': opening.company, 'docstatus': 1,
                 'posting_date': ['<=', frappe.utils.today()]},
        fields=['name', 'owner', 'company', 'pos_profile', 'posting_date', 'posting_time',
                'customer', 'customer_name', 'docstatus', 'consolidated_invoice',
                'grand_total', 'net_total', 'total_qty', 'total_taxes_and_charges',
                'change_amount', 'account_for_change_amount', 'is_return', 'return_against',
                'modified'], order_by='posting_date asc, posting_time asc, name asc', limit_page_length=0)
    states = recon_states(rows)
    eligible = []
    excluded = []
    for row in rows:
        state = states[row['name']]
        row.update(state)
        if state['eligible_for_closing']:
            if row.get('pos_profile') == opening.pos_profile:
                stamp = str(row['posting_date']) + ' ' + str(row.get('posting_time') or '00:00:00')
                if frappe.utils.get_datetime(stamp) <= frappe.utils.now_datetime():
                    row['earlier_invoice'] = frappe.utils.get_datetime(stamp) < frappe.utils.get_datetime(opening.period_start_date)
                    eligible.append(row)
            else:
                excluded.append({'name': row['name'], 'pos_profile': row.get('pos_profile'),
                                 'grand_total': row['grand_total'], 'reason': 'Different POS Profile'})
    return {'invoices': eligible, 'other_profile_invoices': excluded}


def recon_payment_data(invoices, opening):
    names = [i['name'] for i in invoices]
    modes = {}
    for row in frappe.get_all('Mode of Payment', fields=['name', 'type'], limit_page_length=0):
        modes[row['name']] = row.get('type') or ''
    details = []
    if names:
        details = frappe.get_all('Sales Invoice Payment',
            filters={'parent': ['in', names], 'parenttype': 'POS Invoice'},
            fields=['parent', 'mode_of_payment', 'account', 'amount'],
            order_by='parent asc, idx asc', limit_page_length=0)
    by_invoice = {}
    for row in details:
        by_invoice.setdefault(row['parent'], []).append(row)
    totals = {}
    for row in opening.balance_details:
        mode = row.mode_of_payment
        totals.setdefault(mode, {'mode_of_payment': mode, 'is_cash': modes.get(mode) == 'Cash',
            'opening_amount': 0, 'collected_amount': 0})
        totals[mode]['opening_amount'] = totals[mode]['opening_amount'] + frappe.utils.flt(row.opening_amount)
    for invoice in invoices:
        payments = by_invoice.get(invoice['name'], [])
        change = frappe.utils.flt(invoice.get('change_amount'))
        change_account = invoice.get('account_for_change_amount')
        change_index = None
        if change:
            for idx, payment in enumerate(payments):
                if change_account and payment.get('account') == change_account:
                    change_index = idx
                    break
            if change_index is None:
                for idx, payment in enumerate(payments):
                    if modes.get(payment['mode_of_payment']) == 'Cash':
                        change_index = idx
                        break
            if change_index is None:
                frappe.throw('Cannot allocate change for invoice ' + invoice['name'] + '. Check its payment rows.')
        amounts = {}
        for idx, payment in enumerate(payments):
            mode = payment['mode_of_payment']
            amount = frappe.utils.flt(payment['amount']) - (change if idx == change_index else 0)
            amounts[mode] = amounts.get(mode, 0) + amount
            totals.setdefault(mode, {'mode_of_payment': mode, 'is_cash': modes.get(mode) == 'Cash',
                'opening_amount': 0, 'collected_amount': 0})
            totals[mode]['collected_amount'] = totals[mode]['collected_amount'] + amount
        invoice['payment_amounts'] = amounts
        invoice['cash_collected'] = frappe.utils.flt(sum([v for k, v in amounts.items() if modes.get(k) == 'Cash']), 2)
        invoice['collected_amount'] = frappe.utils.flt(sum(amounts.values()), 2)
    result = []
    for mode in sorted(totals):
        row = totals[mode]
        row['opening_amount'] = frappe.utils.flt(row['opening_amount'], 2)
        row['collected_amount'] = frappe.utils.flt(row['collected_amount'], 2)
        row['expected_amount'] = frappe.utils.flt(row['opening_amount'] + row['collected_amount'], 2)
        result.append(row)
    return result


def recon_summary(opening, invoices):
    payments = recon_payment_data(invoices, opening)
    return {
        'invoices': invoices, 'payments': payments,
        'total_invoices': len(invoices),
        'total_sales': frappe.utils.flt(sum([frappe.utils.flt(i['grand_total']) for i in invoices]), 2),
        'total_collected': frappe.utils.flt(sum([p['collected_amount'] for p in payments]), 2),
        'opening_amount': frappe.utils.flt(sum([p['opening_amount'] for p in payments if p['is_cash']]), 2),
        'cash_collected': frappe.utils.flt(sum([p['collected_amount'] for p in payments if p['is_cash']]), 2),
        'expected_closing': frappe.utils.flt(sum([p['expected_amount'] for p in payments if p['is_cash']]), 2),
        'earlier_invoice_count': len([i for i in invoices if i.get('earlier_invoice')])
    }


def vm_pos_create_invoice():
    d = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(d, str):
        d = json.loads(d)
    
    company = d.get('company') or frappe.db.get_default('Company') or frappe.db.get_default('company') or 'ULTRA MRF'
    if company in ['All Branches', 'All', 'null', 'undefined', '', None]:
        company = 'ULTRA MRF'
    
    user = recon_user()
    frappe.get_doc('User', user, for_update=True)
    opening = recon_opening(user, company, d.get('opening_entry'), lock=True)
    if not opening:
        frappe.throw('Open a POS shift for your account before charging an invoice.')
    if recon_pending_closing(opening):
        frappe.throw('This shift has a pending closing entry. Complete it before making another sale.')
    if d.get('pos_profile') and d.get('pos_profile') != opening.pos_profile:
        frappe.throw('Your POS profile changed. Refresh the terminal before charging.')

    # 1. Resolve Customer and Vehicle
    cust = (d.get('customer') or '').strip()
    veh = (d.get('vehicle') or '').strip()
    plate = ''
    
    # If customer is formatted as "CODE — NAME", extract code
    if '—' in cust:
        cust = cust.split('—')[0].strip()
    elif ' - ' in cust:
        cust = cust.split(' - ')[0].strip()
        
    real_veh_doc = ''
    if veh:
        if frappe.db.exists('Customer Vehicle', veh):
            real_veh_doc = veh
            veh_row = frappe.db.get_value('Customer Vehicle', veh, ['customer', 'plate_no'], as_dict=True)
            if veh_row:
                if not cust and veh_row.get('customer'):
                    cust = veh_row['customer']
                plate = veh_row.get('plate_no') or veh
        else:
            # Check if veh is a plate number in DB
            match_veh = frappe.db.get_value('Customer Vehicle', {'plate_no': veh}, 'name')
            if match_veh:
                real_veh_doc = match_veh
                plate = veh
            else:
                # Store as plate text only, do not set link field to invalid ID
                plate = str(veh)
                real_veh_doc = ''

    # Validate or find customer
    if cust and not frappe.db.exists('Customer', cust):
        real_cust = frappe.db.get_value('Customer', {'customer_name': cust}, 'name')             or frappe.db.get_value('Customer', {'customer_name': ['like', f'%{cust}%']}, 'name')
        if real_cust:
            cust = real_cust
        else:
            # Auto-create customer with this name
            try:
                cg = frappe.db.get_value('Customer Group', {'is_group': 0}, 'name') or 'Individual'
                terr = frappe.db.get_value('Territory', {'is_group': 0}, 'name') or 'Philippines'
                c_doc = frappe.get_doc({
                    'doctype': 'Customer',
                    'customer_name': cust,
                    'customer_type': 'Individual',
                    'customer_group': cg,
                    'territory': terr
                })
                c_doc.insert(ignore_permissions=True)
                cust = c_doc.name
            except Exception:
                cust = ''
            
    if not cust or not frappe.db.exists('Customer', cust):
        # Fallback to default walk-in customer or first customer
        cust = frappe.db.get_value('Customer', {'customer_name': ['like', '%Cash%']}, 'name')             or frappe.db.get_value('Customer', {'customer_name': ['like', '%Walk%']}, 'name')             or frappe.db.get_value('Customer', {}, 'name')

    # Use the cashier's current profile so this invoice can be reconciled.
    profile_name = opening.pos_profile

    # 3. Resolve Mode of Payment
    method = (d.get('payment_method') or 'Cash').strip()
    mop_map = {
        'Cash': 'Cash',
        'Card': 'Card' if frappe.db.exists('Mode of Payment', 'Card') else 'Credit Card',
        'Credit Card': 'Credit Card',
        'Debit Card': 'Credit Card',
        'GCash': 'GCash' if frappe.db.exists('Mode of Payment', 'GCash') else 'Cash',
        'Maya': 'Maya' if frappe.db.exists('Mode of Payment', 'Maya') else 'Cash',
        'BDO': 'BDO' if frappe.db.exists('Mode of Payment', 'BDO') else 'Wire Transfer',
        'Bank Transfer': 'Bank Transfer' if frappe.db.exists('Mode of Payment', 'Bank Transfer') else 'Wire Transfer',
        'Wire Transfer': 'Wire Transfer',
        'Check': 'Check',
        'Cheque': 'Check'
    }
    mop = mop_map.get(method, method)
    if not frappe.db.exists('Mode of Payment', mop):
        mop = 'Cash'

    # Ensure this mode of payment is present in the POS Profile
    prof_doc = frappe.get_doc('POS Profile', profile_name)
    existing_mops = [p.mode_of_payment for p in prof_doc.payments]
    if mop not in existing_mops:
        prof_doc.append('payments', {
            'mode_of_payment': mop,
            'default': 0,
            'allow_in_returns': 1
        })
        prof_doc.save(ignore_permissions=True)


    # 5. Prepare items with link resolution
    items = []
    default_sales_item = frappe.db.get_value('Item', {'is_sales_item': 1, 'disabled': 0}, 'name')
    
    for it in (d.get('items') or []):
        raw_code = (it.get('item_code') or it.get('code') or '').strip()
        clean_code = raw_code.rstrip('.').strip()
        
        # Check if item exists by exact code
        if frappe.db.exists('Item', raw_code):
            real_code = raw_code
        elif frappe.db.exists('Item', clean_code):
            real_code = clean_code
        else:
            # Search by name or item_name
            real_code = frappe.db.get_value('Item', {'item_name': clean_code}, 'name')                 or frappe.db.get_value('Item', {'item_name': ['like', f'{clean_code[:12]}%']}, 'name')                 or frappe.db.get_value('Item', {'name': ['like', f'{clean_code[:12]}%']}, 'name')                 or default_sales_item
                
        uom = it.get('uom')
        if not uom or not frappe.db.exists('UOM', uom):
            uom = frappe.db.get_value('Item', real_code, 'stock_uom') or 'Nos'
            if not frappe.db.exists('UOM', uom):
                uom = frappe.db.get_value('UOM', {}, 'name')
                
        items.append({
            'item_code': real_code,
            'qty': float(it.get('qty') or 1),
            'rate': float(it.get('rate') or 0),
            'discount_amount': float(it.get('discount_amount') or 0),
            'uom': uom
        })

    # 6. Create and Submit POS Invoice
    paid_amount = float(d.get('paid_amount') or 0)
    inv = frappe.get_doc({
        'doctype': 'POS Invoice',
        'naming_series': 'ACC-PSINV-.YYYY.-',
        'company': company,
        'customer': cust,
        'posting_date': frappe.utils.nowdate(),
        'pos_profile': profile_name,
        'items': items,
        'payments': [{
            'mode_of_payment': mop,
            'amount': paid_amount
        }],
        'custom_customer_vehicle': real_veh_doc,
        'custom_plate_no': plate,
        'remarks': (d.get('remarks') or d.get('notes') or '').strip()
    })
    inv.insert(ignore_permissions=True)
    inv.submit()


    frappe.response['message'] = {
        'name': inv.name,
        'pos_invoice': inv.name,
        'grand_total': inv.grand_total,
        'paid_amount': inv.paid_amount,
        'payment_method': mop,
        'status': inv.status
    }

vm_pos_create_invoice()
