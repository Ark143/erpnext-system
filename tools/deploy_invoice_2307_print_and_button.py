import requests
import json

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

# ── 1. JINJA TEMPLATE FOR PURCHASE INVOICE (BIR 2307) ──────────────────────────

PURCHASE_INVOICE_2307_HTML = r'''
<div class="bir-2307-container">
    <style>
        html, body, .print-format, .print-format-builder, .print-preview, .print-format-builder-body, [data-doctype="Purchase Invoice"] {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }
        .print-heading, .print-format-builder-header, .print-format-builder-footer, .page-break-header, .page-break-footer, .page-break {
            display: none !important;
        }
        .bir-2307-container {
            width: 8.5in;
            height: 11in;
            position: absolute;
            top: 0;
            left: 0;
            background-image: url("/files/bir_2307_restored_20260909.png");
            background-size: 100% 100% !important;
            background-repeat: no-repeat;
            font-family: Arial, sans-serif;
            color: #000;
            box-sizing: border-box;
        }
        .field-val {
            position: absolute;
            font-size: 11px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        .date-digit {
            position: absolute;
            width: 1.8%;
            text-align: center;
            font-size: 11.5px;
            font-weight: bold;
            top: 11.8%;
        }
        .tin-digit {
            position: absolute;
            width: 1.6%;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
        }
        .table-overlay {
            position: absolute;
            left: 2.90%;
            top: 39.6%;
            width: 94.67%;
            height: 14.38%;
        }
        .overlay-row {
            position: absolute;
            width: 100%;
            display: flex;
            height: 6.74%;
            align-items: center;
        }
        .col-nature { width: 28.0%; padding-left: 3px; font-size: 8.5px; overflow: hidden; white-space: wrap; text-overflow: ellipsis; text-align: left; }
        .col-atc { width: 7.5%; text-align: center; font-size: 9.5px; font-weight: bold; padding-right: 15px; }
        .col-m1 { width: 12.5%; text-align: right; padding-right: 22px; font-size: 9.5px; }
        .col-m2 { width: 14.5%; text-align: right; padding-right: 22px; font-size: 9.5px; }
        .col-m3 { width: 14.5%; text-align: right; padding-right: 22px; font-size: 9.5px; }
        .col-total { width: 10.0%; text-align: right; padding-right: 22px; font-size: 9.5px; font-weight: bold; }
        .col-withheld { width: 10.0%; text-align: right; padding-right: 15px; font-size: 9.5px; font-weight: bold; }
        .totals-overlay {
            position: absolute;
            left: 2.90%;
            top: 53.75%;
            width: 94.67%;
            display: flex;
            height: 1.33%;
            align-items: center;
            font-weight: bold;
        }
        @media print {
            @page { size: letter portrait; margin: 0; }
            body { margin: 0; padding: 0; }
            .bir-2307-container { width: 8.5in; height: 11in; page-break-before: avoid; page-break-after: avoid; }
        }
    </style>

    <!-- Calculate Quarter Dates from doc.posting_date -->
    {% set pdate = frappe.utils.getdate(doc.posting_date) if doc.posting_date else frappe.utils.nowdate() %}
    {% set pyear = pdate.year %}
    {% set pmonth = pdate.month %}
    {% if pmonth <= 3 %}
        {% set f_month = "01" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "03" %}{% set t_day = "31" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth %}
    {% elif pmonth <= 6 %}
        {% set f_month = "04" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "06" %}{% set t_day = "30" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth - 3 %}
    {% elif pmonth <= 9 %}
        {% set f_month = "07" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "09" %}{% set t_day = "30" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth - 6 %}
    {% else %}
        {% set f_month = "10" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "12" %}{% set t_day = "31" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth - 9 %}
    {% endif %}

    <!-- From Date -->
    <div class="date-digit" style="left: 25.35%;">{{ f_month[0] }}</div>
    <div class="date-digit" style="left: 27.31%;">{{ f_month[1] }}</div>
    <div class="date-digit" style="left: 29.24%;">{{ f_day[0] }}</div>
    <div class="date-digit" style="left: 31.20%;">{{ f_day[1] }}</div>
    <div class="date-digit" style="left: 33.73%;">{{ f_year[0] }}</div>
    <div class="date-digit" style="left: 35.69%;">{{ f_year[1] }}</div>
    <div class="date-digit" style="left: 37.65%;">{{ f_year[2] }}</div>
    <div class="date-digit" style="left: 39.61%;">{{ f_year[3] }}</div>

    <!-- To Date -->
    <div class="date-digit" style="left: 66.16%;">{{ t_month[0] }}</div>
    <div class="date-digit" style="left: 68.12%;">{{ t_month[1] }}</div>
    <div class="date-digit" style="left: 70.04%;">{{ t_day[0] }}</div>
    <div class="date-digit" style="left: 72.00%;">{{ t_day[1] }}</div>
    <div class="date-digit" style="left: 74.53%;">{{ t_year[0] }}</div>
    <div class="date-digit" style="left: 76.49%;">{{ t_year[1] }}</div>
    <div class="date-digit" style="left: 78.45%;">{{ t_year[2] }}</div>
    <div class="date-digit" style="left: 80.41%;">{{ t_year[3] }}</div>

    <!-- Payee (Supplier) Info -->
    {% set supp_tin = (frappe.db.get_value("Supplier", doc.supplier, "tax_id") if doc.supplier else "") or doc.tax_id or "000000000000" %}
    {% set payee_tin_clean = supp_tin | replace("-", "") | replace(" ", "") %}
    {% set tin_lefts = [34.4, 36.4, 38.4, 42.75, 44.75, 46.75, 50.75, 52.75, 54.75, 59.75, 61.75, 63.75] %}
    {% for i in range(12) %}
        <div class="tin-digit" style="left: {{ tin_lefts[i] }}%; top: 14.8%;">
            {{ payee_tin_clean[i] if i < payee_tin_clean|length else '0' }}
        </div>
    {% endfor %}
    <div class="field-val" style="left: 15.5%; top: 18%; width: 90.5%; height: 1.44%;">{{ doc.supplier_name or doc.supplier or '' }}</div>
    <div class="field-val" style="left: 15.5%; top: 20.6%; width: 81.1%; height: 1.44%; font-size: 9.5px; font-weight: normal;">{{ doc.address_display or doc.billing_address or '' }}</div>
    <div class="field-val" style="left: 87.84%; top: 20.6%; width: 8.63%; height: 1.44%; justify-content: center;"></div>

    <!-- Payor (Company) Info -->
    {% set comp_tin = (frappe.db.get_value("Company", doc.company, "tax_id") if doc.company else "") or "000000000000" %}
    {% set payor_tin_clean = comp_tin | replace("-", "") | replace(" ", "") %}
    {% for i in range(12) %}
        <div class="tin-digit" style="left: {{ tin_lefts[i] }}%; top: 27%;">
            {{ payor_tin_clean[i] if i < payor_tin_clean|length else '0' }}
        </div>
    {% endfor %}
    <div class="field-val" style="left: 15.5%; top: 29.8%; width: 92.5%; height: 1.44%;">{{ doc.company or '' }}</div>
    <div class="field-val" style="left: 5.5%; top: 32.8%; width: 83.1%; height: 1.44%; font-size: 9.5px; font-weight: normal;">{{ doc.company_address_display or doc.company_address or "" }}</div>
    <div class="field-val" style="left: 87.84%; top: 32.8%; width: 8.63%; height: 1.44%; justify-content: center;"></div>

    <!-- Part III Table Rows Overlay (Filtered for EWT / Withholding Taxes) -->
    <div class="table-overlay">
        {% set totals = {'m1': 0.0, 'm2': 0.0, 'm3': 0.0, 'total': 0.0, 'withheld': 0.0} %}
        {% set row_tops = [0.0, 9.67, 19.33, 28.67, 38.33, 47.67, 57.33, 66.67, 76.33, 85.67] %}
        {% set wtax_rows = [] %}
        {% for tax in doc.taxes %}
            {% if tax.add_deduct_tax == 'Deduct' or tax.is_tax_withholding_account == 1 or 'withholding' in (tax.account_head or '')|lower or 'ewt' in (tax.account_head or '')|lower or 'wtax' in (tax.account_head or '')|lower %}
                {% set _ = wtax_rows.append(tax) %}
            {% endif %}
        {% endfor %}

        <!-- If no tax row explicitly marked as deduct, look for tax rows with negative rate/amount -->
        {% if not wtax_rows %}
            {% for tax in doc.taxes %}
                {% if (tax.tax_amount and tax.tax_amount < 0) or (tax.rate and tax.rate < 0) %}
                    {% set _ = wtax_rows.append(tax) %}
                {% endif %}
            {% endfor %}
        {% endif %}

        {% for row in wtax_rows %}
            {% if loop.index0 < 10 %}
                {% set tax_amt = (row.tax_amount|abs) if row.tax_amount else 0.0 %}
                {% set base_amt = (doc.base_net_total or doc.net_total or 0.0) %}
                {% set desc = row.description or row.account_head or 'Expanded Withholding Tax' %}
                {% set atc = 'WI158' if 'service' in desc|lower else 'WI160' if 'good' in desc|lower else 'WI100' if 'rent' in desc|lower else 'WI158' %}
                <div class="overlay-row" style="top: {{ row_tops[loop.index0] }}%;">
                    <div class="col-nature">{{ desc }}</div>
                    <div class="col-atc">{{ atc }}</div>
                    <div class="col-m1">{{ "{:,.2f}".format(base_amt) if m_idx == 1 else '' }}</div>
                    <div class="col-m2">{{ "{:,.2f}".format(base_amt) if m_idx == 2 else '' }}</div>
                    <div class="col-m3">{{ "{:,.2f}".format(base_amt) if m_idx == 3 else '' }}</div>
                    <div class="col-total">{{ "{:,.2f}".format(base_amt) }}</div>
                    <div class="col-withheld">{{ "{:,.2f}".format(tax_amt) }}</div>
                </div>
                {% if m_idx == 1 %}
                    {% set _ = totals.update({'m1': totals.m1 + base_amt}) %}
                {% elif m_idx == 2 %}
                    {% set _ = totals.update({'m2': totals.m2 + base_amt}) %}
                {% else %}
                    {% set _ = totals.update({'m3': totals.m3 + base_amt}) %}
                {% endif %}
                {% set _ = totals.update({'total': totals.total + base_amt, 'withheld': totals.withheld + tax_amt}) %}
            {% endif %}
        {% endfor %}
    </div>

    <!-- Totals Line -->
    <div class="totals-overlay">
        <div class="col-nature" style="font-weight: bold; font-size: 8px; padding-left: 5px;"></div>
        <div class="col-atc">&nbsp;</div>
        <div class="col-m1">{{ "{:,.2f}".format(totals.m1) if totals.m1 else '' }}</div>
        <div class="col-m2">{{ "{:,.2f}".format(totals.m2) if totals.m2 else '' }}</div>
        <div class="col-m3">{{ "{:,.2f}".format(totals.m3) if totals.m3 else '' }}</div>
        <div class="col-total">{{ "{:,.2f}".format(totals.total) if totals.total else '' }}</div>
        <div class="col-withheld">{{ "{:,.2f}".format(totals.withheld) if totals.withheld else '' }}</div>
    </div>
</div>
'''

# ── 2. JINJA TEMPLATE FOR SALES INVOICE (BIR 2307) ─────────────────────────────

SALES_INVOICE_2307_HTML = r'''
<div class="bir-2307-container">
    <style>
        html, body, .print-format, .print-format-builder, .print-preview, .print-format-builder-body, [data-doctype="Sales Invoice"] {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }
        .print-heading, .print-format-builder-header, .print-format-builder-footer, .page-break-header, .page-break-footer, .page-break {
            display: none !important;
        }
        .bir-2307-container {
            width: 8.5in;
            height: 11in;
            position: absolute;
            top: 0;
            left: 0;
            background-image: url("/files/bir_2307_restored_20260909.png");
            background-size: 100% 100% !important;
            background-repeat: no-repeat;
            font-family: Arial, sans-serif;
            color: #000;
            box-sizing: border-box;
        }
        .field-val {
            position: absolute;
            font-size: 11px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        .date-digit {
            position: absolute;
            width: 1.8%;
            text-align: center;
            font-size: 11.5px;
            font-weight: bold;
            top: 11.8%;
        }
        .tin-digit {
            position: absolute;
            width: 1.6%;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
        }
        .table-overlay {
            position: absolute;
            left: 2.90%;
            top: 39.6%;
            width: 94.67%;
            height: 14.38%;
        }
        .overlay-row {
            position: absolute;
            width: 100%;
            display: flex;
            height: 6.74%;
            align-items: center;
        }
        .col-nature { width: 28.0%; padding-left: 3px; font-size: 8.5px; overflow: hidden; white-space: wrap; text-overflow: ellipsis; text-align: left; }
        .col-atc { width: 7.5%; text-align: center; font-size: 9.5px; font-weight: bold; padding-right: 15px; }
        .col-m1 { width: 12.5%; text-align: right; padding-right: 22px; font-size: 9.5px; }
        .col-m2 { width: 14.5%; text-align: right; padding-right: 22px; font-size: 9.5px; }
        .col-m3 { width: 14.5%; text-align: right; padding-right: 22px; font-size: 9.5px; }
        .col-total { width: 10.0%; text-align: right; padding-right: 22px; font-size: 9.5px; font-weight: bold; }
        .col-withheld { width: 10.0%; text-align: right; padding-right: 15px; font-size: 9.5px; font-weight: bold; }
        .totals-overlay {
            position: absolute;
            left: 2.90%;
            top: 53.75%;
            width: 94.67%;
            display: flex;
            height: 1.33%;
            align-items: center;
            font-weight: bold;
        }
        @media print {
            @page { size: letter portrait; margin: 0; }
            body { margin: 0; padding: 0; }
            .bir-2307-container { width: 8.5in; height: 11in; page-break-before: avoid; page-break-after: avoid; }
        }
    </style>

    <!-- Calculate Quarter Dates from doc.posting_date -->
    {% set pdate = frappe.utils.getdate(doc.posting_date) if doc.posting_date else frappe.utils.nowdate() %}
    {% set pyear = pdate.year %}
    {% set pmonth = pdate.month %}
    {% if pmonth <= 3 %}
        {% set f_month = "01" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "03" %}{% set t_day = "31" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth %}
    {% elif pmonth <= 6 %}
        {% set f_month = "04" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "06" %}{% set t_day = "30" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth - 3 %}
    {% elif pmonth <= 9 %}
        {% set f_month = "07" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "09" %}{% set t_day = "30" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth - 6 %}
    {% else %}
        {% set f_month = "10" %}{% set f_day = "01" %}{% set f_year = pyear|string %}
        {% set t_month = "12" %}{% set t_day = "31" %}{% set t_year = pyear|string %}
        {% set m_idx = pmonth - 9 %}
    {% endif %}

    <!-- From Date -->
    <div class="date-digit" style="left: 25.35%;">{{ f_month[0] }}</div>
    <div class="date-digit" style="left: 27.31%;">{{ f_month[1] }}</div>
    <div class="date-digit" style="left: 29.24%;">{{ f_day[0] }}</div>
    <div class="date-digit" style="left: 31.20%;">{{ f_day[1] }}</div>
    <div class="date-digit" style="left: 33.73%;">{{ f_year[0] }}</div>
    <div class="date-digit" style="left: 35.69%;">{{ f_year[1] }}</div>
    <div class="date-digit" style="left: 37.65%;">{{ f_year[2] }}</div>
    <div class="date-digit" style="left: 39.61%;">{{ f_year[3] }}</div>

    <!-- To Date -->
    <div class="date-digit" style="left: 66.16%;">{{ t_month[0] }}</div>
    <div class="date-digit" style="left: 68.12%;">{{ t_month[1] }}</div>
    <div class="date-digit" style="left: 70.04%;">{{ t_day[0] }}</div>
    <div class="date-digit" style="left: 72.00%;">{{ t_day[1] }}</div>
    <div class="date-digit" style="left: 74.53%;">{{ t_year[0] }}</div>
    <div class="date-digit" style="left: 76.49%;">{{ t_year[1] }}</div>
    <div class="date-digit" style="left: 78.45%;">{{ t_year[2] }}</div>
    <div class="date-digit" style="left: 80.41%;">{{ t_year[3] }}</div>

    <!-- Payee (Company) Info -->
    {% set comp_tin = frappe.db.get_value("Company", doc.company, "tax_id") or "000000000000" %}
    {% set payee_tin_clean = comp_tin | replace("-", "") | replace(" ", "") %}
    {% set tin_lefts = [34.4, 36.4, 38.4, 42.75, 44.75, 46.75, 50.75, 52.75, 54.75, 59.75, 61.75, 63.75] %}
    {% for i in range(12) %}
        <div class="tin-digit" style="left: {{ tin_lefts[i] }}%; top: 14.8%;">
            {{ payee_tin_clean[i] if i < payee_tin_clean|length else '0' }}
        </div>
    {% endfor %}
    <div class="field-val" style="left: 15.5%; top: 18%; width: 90.5%; height: 1.44%;">{{ doc.company }}</div>
    <div class="field-val" style="left: 15.5%; top: 20.6%; width: 81.1%; height: 1.44%; font-size: 9.5px; font-weight: normal;">{{ doc.company_address_display or doc.company_address or "" }}</div>
    <div class="field-val" style="left: 87.84%; top: 20.6%; width: 8.63%; height: 1.44%; justify-content: center;"></div>

    <!-- Payor (Customer) Info -->
    {% set cust_tin = frappe.db.get_value("Customer", doc.customer, "tax_id") or doc.tax_id or "000000000000" %}
    {% set payor_tin_clean = cust_tin | replace("-", "") | replace(" ", "") %}
    {% for i in range(12) %}
        <div class="tin-digit" style="left: {{ tin_lefts[i] }}%; top: 27%;">
            {{ payor_tin_clean[i] if i < payor_tin_clean|length else '0' }}
        </div>
    {% endfor %}
    <div class="field-val" style="left: 15.5%; top: 29.8%; width: 92.5%; height: 1.44%;">{{ doc.customer_name or doc.customer }}</div>
    <div class="field-val" style="left: 5.5%; top: 32.8%; width: 83.1%; height: 1.44%; font-size: 9.5px; font-weight: normal;">{{ doc.address_display or doc.customer_address or '' }}</div>
    <div class="field-val" style="left: 87.84%; top: 32.8%; width: 8.63%; height: 1.44%; justify-content: center;"></div>

    <!-- Part III Table Rows Overlay (Filtered for CWT / Withholding Taxes) -->
    <div class="table-overlay">
        {% set totals = {'m1': 0.0, 'm2': 0.0, 'm3': 0.0, 'total': 0.0, 'withheld': 0.0} %}
        {% set row_tops = [0.0, 9.67, 19.33, 28.67, 38.33, 47.67, 57.33, 66.67, 76.33, 85.67] %}
        {% set wtax_rows = [] %}
        {% for tax in doc.taxes %}
            {% if (tax.rate and tax.rate < 0) or (tax.tax_amount and tax.tax_amount < 0) or 'cwt' in (tax.account_head or '')|lower or 'withholding' in (tax.account_head or '')|lower or tax.is_tax_withholding_account == 1 %}
                {% set _ = wtax_rows.append(tax) %}
            {% endif %}
        {% endfor %}

        {% for row in wtax_rows %}
            {% if loop.index0 < 10 %}
                {% set tax_amt = (row.tax_amount|abs) if row.tax_amount else 0.0 %}
                {% set base_amt = (doc.base_net_total or doc.net_total or 0.0) %}
                {% set desc = row.description or row.account_head or 'Creditable Withholding Tax' %}
                {% set atc = 'WC158' if 'service' in desc|lower else 'WC160' if 'good' in desc|lower else 'WC158' %}
                <div class="overlay-row" style="top: {{ row_tops[loop.index0] }}%;">
                    <div class="col-nature">{{ desc }}</div>
                    <div class="col-atc">{{ atc }}</div>
                    <div class="col-m1">{{ "{:,.2f}".format(base_amt) if m_idx == 1 else '' }}</div>
                    <div class="col-m2">{{ "{:,.2f}".format(base_amt) if m_idx == 2 else '' }}</div>
                    <div class="col-m3">{{ "{:,.2f}".format(base_amt) if m_idx == 3 else '' }}</div>
                    <div class="col-total">{{ "{:,.2f}".format(base_amt) }}</div>
                    <div class="col-withheld">{{ "{:,.2f}".format(tax_amt) }}</div>
                </div>
                {% if m_idx == 1 %}
                    {% set _ = totals.update({'m1': totals.m1 + base_amt}) %}
                {% elif m_idx == 2 %}
                    {% set _ = totals.update({'m2': totals.m2 + base_amt}) %}
                {% else %}
                    {% set _ = totals.update({'m3': totals.m3 + base_amt}) %}
                {% endif %}
                {% set _ = totals.update({'total': totals.total + base_amt, 'withheld': totals.withheld + tax_amt}) %}
            {% endif %}
        {% endfor %}
    </div>

    <!-- Totals Line -->
    <div class="totals-overlay">
        <div class="col-nature" style="font-weight: bold; font-size: 8px; padding-left: 5px;"></div>
        <div class="col-atc">&nbsp;</div>
        <div class="col-m1">{{ "{:,.2f}".format(totals.m1) if totals.m1 else '' }}</div>
        <div class="col-m2">{{ "{:,.2f}".format(totals.m2) if totals.m2 else '' }}</div>
        <div class="col-m3">{{ "{:,.2f}".format(totals.m3) if totals.m3 else '' }}</div>
        <div class="col-total">{{ "{:,.2f}".format(totals.total) if totals.total else '' }}</div>
        <div class="col-withheld">{{ "{:,.2f}".format(totals.withheld) if totals.withheld else '' }}</div>
    </div>
</div>
'''

# ── 3. UPSERT PRINT FORMATS ───────────────────────────────────────────────────

def upsert_print_format(name, doctype, html):
    payload = {
        "doctype": "Print Format",
        "name": name,
        "doc_type": doctype,
        "format_data": "",
        "html": html,
        "print_format_type": "Jinja",
        "custom_format": 1,
        "standard": "No",
        "disabled": 0
    }
    check = s.get(f"{BASE}/api/resource/Print%20Format/{requests.utils.quote(name)}")
    if check.status_code == 200:
        r = s.put(f"{BASE}/api/resource/Print%20Format/{requests.utils.quote(name)}", json=payload)
        print(f"[upd] Print Format: {name} ({doctype}) -> {r.status_code}")
    else:
        r = s.post(f"{BASE}/api/resource/Print%20Format", json=payload)
        print(f"[+] Created Print Format: {name} ({doctype}) -> {r.status_code}")

upsert_print_format("BIR 2307 - Purchase Invoice", "Purchase Invoice", PURCHASE_INVOICE_2307_HTML)
upsert_print_format("BIR 2307 - Sales Invoice", "Sales Invoice", SALES_INVOICE_2307_HTML)

# ── 4. UPSERT CLIENT SCRIPTS FOR DIRECT 2307 PRINT BUTTON ─────────────────────

PI_CLIENT_SCRIPT = r'''
frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Print BIR 2307'), function() {
                var url = frappe.urllib.get_full_url(
                    '/printview?doctype=Purchase%20Invoice&name=' + encodeURIComponent(frm.doc.name) +
                    '&format=BIR%202307%20-%20Purchase%20Invoice&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en'
                );
                window.open(url, '_blank');
            }, __('Actions'));
            
            // Also add directly to custom buttons if submitted
            if (frm.doc.docstatus === 1) {
                frm.page.add_inner_button(__('BIR 2307 Certificate'), function() {
                    var url = frappe.urllib.get_full_url(
                        '/printview?doctype=Purchase%20Invoice&name=' + encodeURIComponent(frm.doc.name) +
                        '&format=BIR%202307%20-%20Purchase%20Invoice&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en'
                    );
                    window.open(url, '_blank');
                });
            }
        }
    }
});
'''

SI_CLIENT_SCRIPT = r'''
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Print BIR 2307'), function() {
                var url = frappe.urllib.get_full_url(
                    '/printview?doctype=Sales%20Invoice&name=' + encodeURIComponent(frm.doc.name) +
                    '&format=BIR%202307%20-%20Sales%20Invoice&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en'
                );
                window.open(url, '_blank');
            }, __('Actions'));
            
            // Also add directly to custom buttons if submitted
            if (frm.doc.docstatus === 1) {
                frm.page.add_inner_button(__('BIR 2307 Certificate'), function() {
                    var url = frappe.urllib.get_full_url(
                        '/printview?doctype=Sales%20Invoice&name=' + encodeURIComponent(frm.doc.name) +
                        '&format=BIR%202307%20-%20Sales%20Invoice&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en'
                    );
                    window.open(url, '_blank');
                });
            }
        }
    }
});
'''

def upsert_client_script(name, dt, script):
    payload = {
        "doctype": "Client Script",
        "name": name,
        "dt": dt,
        "view": "Form",
        "script": script,
        "enabled": 1
    }
    check = s.get(f"{BASE}/api/resource/Client%20Script/{requests.utils.quote(name)}")
    if check.status_code == 200:
        r = s.put(f"{BASE}/api/resource/Client%20Script/{requests.utils.quote(name)}", json=payload)
        print(f"[upd] Client Script: {name} -> {r.status_code}")
    else:
        r = s.post(f"{BASE}/api/resource/Client%20Script", json=payload)
        print(f"[+] Created Client Script: {name} -> {r.status_code}")

upsert_client_script("Print BIR 2307 - Purchase Invoice", "Purchase Invoice", PI_CLIENT_SCRIPT)
upsert_client_script("Print BIR 2307 - Sales Invoice", "Sales Invoice", SI_CLIENT_SCRIPT)

print("\nSUCCESS: BIR 2307 Direct Printing & Buttons successfully deployed to Purchase Invoice and Sales Invoice!")

