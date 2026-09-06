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

user = recon_user()
company = frappe.form_dict.get('company') or frappe.db.get_default('Company') or frappe.db.get_default('company')
if company in ['All Branches', 'All', 'null', 'undefined', 'None']:
    company = None
opening = recon_opening(user, company, frappe.form_dict.get('opening_entry'))
if opening:
    candidates = recon_candidates(opening)
    shift = recon_summary(opening, candidates['invoices'])
    shift.update({'name': opening.name, 'user': opening.user, 'company': opening.company,
        'pos_profile': opening.pos_profile, 'period_start_date': str(opening.period_start_date),
        'mode_of_payment': ([p['mode_of_payment'] for p in shift['payments'] if p['is_cash']] or ['Cash'])[0],
        'status': opening.status, 'other_profile_invoices': candidates['other_profile_invoices'],
        'pending_closing': recon_pending_closing(opening)})
    frappe.response['message'] = {'has_open_shift': True, 'shift': shift}
else:
    filters = {'disabled': 0}
    if company:
        filters['company'] = company
    profiles = frappe.get_all('POS Profile', filters=filters, fields=['name', 'company'], limit_page_length=0)
    allowed = []
    for profile in profiles:
        users = frappe.get_all('POS Profile User', filters={'parent': profile['name'], 'parenttype': 'POS Profile'}, fields=['user'], limit_page_length=0)
        if not users or user == 'Administrator' or user in [p['user'] for p in users]:
            allowed.append(profile)
    mops = frappe.get_all('Mode of Payment', filters={'enabled': 1}, fields=['name', 'type'], order_by='type asc', limit_page_length=0)
    frappe.response['message'] = {'has_open_shift': False, 'shift': None, 'profiles': allowed,
        'modes_of_payment': mops, 'company': company,
        'companies': sorted(set([p['company'] for p in allowed])), 'default_company': company}
