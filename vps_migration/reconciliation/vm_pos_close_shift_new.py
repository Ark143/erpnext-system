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

def vm_pos_close_shift():
    data = frappe.form_dict.get('data') or frappe.form_dict
    if isinstance(data, str):
        data = json.loads(data)
    user = recon_user()
    # Serialize this cashier's open/create/close actions. Invoice locks below also
    # prevent competing closings from reconciling the same invoice concurrently.
    frappe.get_doc('User', user, for_update=True)
    opening = recon_opening(user, name=data.get('opening_entry'), lock=True)
    if not opening:
        frappe.throw('No active shift exists for your account.')
    pending = recon_pending_closing(opening)
    if pending:
        frappe.throw('Closing entry ' + pending['name'] + ' already exists (' + pending['status'] + '). Open it to complete, retry or cancel it.')
    candidates = recon_candidates(opening)
    invoices = candidates['invoices']
    available = [i['name'] for i in invoices]
    selected = data.get('invoice_names')
    if isinstance(selected, str):
        selected = json.loads(selected)
    if selected is None:
        selected = available
    if not isinstance(selected, list) or any([not isinstance(n, str) for n in selected]):
        frappe.throw('Invoice selection must be a list of invoice names.')
    if len(selected) != len(set(selected)):
        frappe.throw('An invoice was selected more than once.')
    if any([name not in available for name in selected]):
        frappe.throw('An invoice is no longer eligible for this cashier and POS Profile. Refresh the closing summary.')
    if data.get('selection_mode', 'all') == 'all' and set(selected) != set(available):
        frappe.throw('The invoice list changed. Refresh the closing summary before submitting.')
    if available and not selected:
        frappe.throw('Select at least one invoice to reconcile.')
    for name in sorted(selected):
        frappe.get_doc('POS Invoice', name, for_update=True)
    # Re-read after acquiring locks: another request may have changed an invoice.
    fresh = recon_candidates(opening)['invoices']
    fresh_names = [i['name'] for i in fresh]
    if any([name not in fresh_names for name in selected]):
        frappe.throw('A selected invoice has just been reconciled. Refresh the closing summary.')
    if data.get('selection_mode', 'all') == 'all' and set(selected) != set(fresh_names):
        frappe.throw('The invoice list changed. Refresh the closing summary before submitting.')
    invoices = [i for i in fresh if i['name'] in selected]
    versions = data.get('invoice_versions') or {}
    if any([versions.get(i['name']) and str(versions[i['name']]) != str(i['modified']) for i in invoices]):
        frappe.throw('An invoice was updated. Refresh the closing summary before submitting.')
    summary = recon_summary(opening, invoices)
    if data.get('preview_only'):
        frappe.response['message'] = summary
        return
    counts = data.get('counted_amounts') or {}
    if isinstance(counts, str):
        counts = json.loads(counts)
    if not isinstance(counts, dict):
        frappe.throw('Enter the counted amount for each payment method.')
    # Compatibility for an already-open old terminal: cash count is supported,
    # but mixed-payment shifts require a refreshed reconciliation screen.
    if not counts and data.get('closing_amount') is not None and len(summary['payments']) == 1:
        counts[summary['payments'][0]['mode_of_payment']] = data['closing_amount']
    reconciliation = []
    cash_count = 0
    for payment in summary['payments']:
        mode = payment['mode_of_payment']
        raw = counts.get(mode)
        if raw is None or str(raw).strip() == '':
            frappe.throw('Enter the counted amount for ' + mode + '.')
        try:
            count = float(raw)
        except Exception:
            frappe.throw('Invalid counted amount for ' + mode + '.')
        if count != count or count == float('inf') or count == -float('inf'):
            frappe.throw('Invalid counted amount for ' + mode + '.')
        if payment['is_cash'] and count < 0:
            frappe.throw('Cash counted cannot be negative.')
        count = frappe.utils.flt(count, 2)
        reconciliation.append({'mode_of_payment': mode, 'opening_amount': payment['opening_amount'],
            'expected_amount': payment['expected_amount'], 'closing_amount': count,
            'difference': frappe.utils.flt(count - payment['expected_amount'], 2)})
        if payment['is_cash']:
            cash_count += count
    taxes = {}
    if selected:
        for tax in frappe.get_all('Sales Taxes and Charges',
            filters={'parent': ['in', selected], 'parenttype': 'POS Invoice'},
            fields=['account_head', 'tax_amount_after_discount_amount'], limit_page_length=0):
            account = tax['account_head']
            taxes[account] = taxes.get(account, 0) + frappe.utils.flt(tax['tax_amount_after_discount_amount'])
    closing = frappe.get_doc({'doctype': 'POS Closing Entry', 'company': opening.company,
        'pos_profile': opening.pos_profile, 'user': user, 'pos_opening_entry': opening.name,
        'period_start_date': opening.period_start_date, 'period_end_date': frappe.utils.now_datetime(),
        'posting_date': frappe.utils.nowdate(), 'grand_total': summary['total_sales'],
        'net_total': sum([frappe.utils.flt(i['net_total']) for i in invoices]),
        'total_quantity': sum([frappe.utils.flt(i['total_qty']) for i in invoices]),
        'total_taxes_and_charges': sum([frappe.utils.flt(i['total_taxes_and_charges']) for i in invoices]),
        'pos_invoices': [{'pos_invoice': i['name'], 'posting_date': i['posting_date'],
            'customer': i['customer'], 'grand_total': i['grand_total'],
            'is_return': i.get('is_return') or 0, 'return_against': i.get('return_against')} for i in invoices],
        'payment_reconciliation': reconciliation,
        'taxes': [{'account_head': k, 'amount': frappe.utils.flt(v, 2)} for k, v in taxes.items()]})
    closing.flags.ignore_permissions = True
    closing.insert(ignore_permissions=True)
    closing.submit()
    # ERPNext closes the opening entry only after consolidation succeeds.
    # Never mark it Closed manually, especially for queued/failed merge jobs.
    status = frappe.db.get_value('POS Closing Entry', closing.name, 'status') or closing.status
    frappe.response['message'] = {'name': closing.name, 'opening_entry': opening.name,
        'cashier': user, 'total_invoices': len(invoices), 'grand_total': summary['total_sales'],
        'opening_amount': summary['opening_amount'], 'closing_amount': frappe.utils.flt(cash_count, 2),
        'difference': frappe.utils.flt(cash_count - summary['expected_closing'], 2),
        'remaining_invoices': len(fresh) - len(invoices), 'status': status}

vm_pos_close_shift()
