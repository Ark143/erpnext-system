"""
Script to create the custom Print Format "Autometrik Estimate" for Vehicle Estimate,
set it as the default print format, and verify.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, flt
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

os.chdir(os.path.join(os.path.dirname(__file__), "sites"))
frappe.init("site1.local")
frappe.connect()

PRINT_FORMAT_NAME = "Autometrik Estimate"

HTML_TEMPLATE = """
{% set customer_doc = frappe.get_doc("Customer", doc.customer) if doc.customer and frappe.db.exists("Customer", doc.customer) else None %}
{% set vehicle_doc = frappe.get_doc("Customer Vehicle", doc.vehicle) if doc.vehicle and frappe.db.exists("Customer Vehicle", doc.vehicle) else None %}

{% set cust_name = doc.customer_name or (customer_doc.customer_name if customer_doc else doc.customer) %}
{% set cust_mobile = doc.contact_no or (customer_doc.custom_mobile_no if customer_doc else "") or (customer_doc.mobile_no if customer_doc else "") %}
{% set cust_address = (customer_doc.custom_address_text if customer_doc else "") or (customer_doc.primary_address if customer_doc else "") %}

{% set veh_plate = doc.plate_no or (vehicle_doc.plate_no if vehicle_doc else "N/A") %}
{% set veh_vin = (vehicle_doc.vin if vehicle_doc else "") or doc.vin or "N/A" %}
{% set veh_model = "" %}
{% if vehicle_doc %}
    {% set veh_model = ((vehicle_doc.make or "") ~ " " ~ (vehicle_doc.model or "") ~ " " ~ (vehicle_doc.year_model or "") ~ " " ~ (vehicle_doc.transmission or "")) | trim %}
{% endif %}
{% if not veh_model and doc.vehicle %}
    {% set veh_model = doc.vehicle %}
{% endif %}

{% set total_labor = doc.total_labor or 0.0 %}
{% set total_parts = doc.total_parts or 0.0 %}

<div class="estimate-container">
  <!-- Header: Logo & Company on Left, Estimate Title & Meta on Right -->
  <table class="header-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <img src="/files/ultra_mrf_logo.png" style="max-height: 55px; max-width: 220px; object-fit: contain;" alt="ULTRA MRF" />
        <div class="company-title">{{ doc.company or "ULTRA MRF DAU MAIN" }}</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: right;">
        <div class="estimate-title">ESTIMATE / QUOTATION</div>
        <div class="doc-meta">
          <div class="meta-id">{{ doc.name }}</div>
          <div><b>Date:</b> {{ frappe.utils.formatdate(doc.estimate_date or doc.creation, "M/d/yyyy") }}</div>
          {% if doc.valid_till %}
          <div><b>Valid Until:</b> {{ frappe.utils.formatdate(doc.valid_till, "M/d/yyyy") }}</div>
          {% endif %}
        </div>
      </td>
    </tr>
  </table>

  <!-- Customer & Vehicle Info Box (2 Columns) -->
  <table class="info-table">
    <tr>
      <td style="width: 50%; vertical-align: top; padding-right: 15px;">
        <table class="inner-info-table">
          <tr>
            <td class="info-label">Customer:</td>
            <td class="info-val font-bold">{{ cust_name }}</td>
          </tr>
          <tr>
            <td class="info-label">Contact No:</td>
            <td class="info-val">{{ cust_mobile or "" }}</td>
          </tr>
          <tr>
            <td class="info-label">Address:</td>
            <td class="info-val">{{ cust_address or "" }}</td>
          </tr>
          {% if doc.service_advisor %}
          <tr>
            <td class="info-label">Estimator:</td>
            <td class="info-val">{{ doc.service_advisor }}</td>
          </tr>
          {% endif %}
        </table>
      </td>
      <td style="width: 50%; vertical-align: top; padding-left: 15px; border-left: 1px solid #ddd;">
        <table class="inner-info-table">
          <tr>
            <td class="info-label">Plate / CS No:</td>
            <td class="info-val font-bold">{{ veh_plate }}</td>
          </tr>
          <tr>
            <td class="info-label">Vehicle:</td>
            <td class="info-val font-bold">{{ veh_model }}</td>
          </tr>
          <tr>
            <td class="info-label">VIN / Chassis:</td>
            <td class="info-val">{{ veh_vin }}</td>
          </tr>
          <tr>
            <td class="info-label">Mileage:</td>
            <td class="info-val">{% if doc.mileage %}{{ "{:,.0f}".format(doc.mileage) }} {{ doc.mileage_unit or "km" }}{% else %}N/A{% endif %}</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>

  {% if doc.customer_complaint %}
  <!-- Customer Request / Complaint -->
  <div class="section-box" style="margin-top: 10px; margin-bottom: 12px; padding: 6px 10px; background: #fafafa; border: 1px solid #eee; border-radius: 4px;">
    <div style="font-size: 8pt; font-weight: bold; color: #555; text-transform: uppercase;">Customer Request / Stated Scope:</div>
    <div style="font-size: 9pt; color: #222; margin-top: 2px;">{{ doc.customer_complaint }}</div>
  </div>
  {% endif %}

  <!-- 1. Labor & Services Table -->
  <div class="section-title">1. ESTIMATED LABOR & SERVICES</div>
  <table class="items-table">
    <thead>
      <tr>
        <th style="width: 5%; text-align: center;">#</th>
        <th style="width: 55%; text-align: left;">Item Description / Scope</th>
        <th style="width: 12%; text-align: right;">Hours</th>
        <th style="width: 13%; text-align: right;">Rate (PHP)</th>
        <th style="width: 15%; text-align: right;">Total Amount</th>
      </tr>
    </thead>
    <tbody>
      {% set service_rows = doc.get("services") or [] %}
      {% if service_rows %}
        {% for row in service_rows %}
        <tr>
          <td style="text-align: center;">{{ loop.index }}</td>
          <td style="text-align: left;">
            <div class="item-name">{{ row.description or row.service_item }}</div>
            {% if row.mechanic %}
            <div class="item-sub">Mechanic: {{ row.mechanic }}</div>
            {% endif %}
          </td>
          <td style="text-align: right;">{{ "{:,.1f}".format(row.hours or 1.0) }}</td>
          <td style="text-align: right;">{{ "{:,.2f}".format(row.rate or 0.0) }}</td>
          <td style="text-align: right;" class="font-bold">{{ "{:,.2f}".format(row.total_amount or 0.0) }}</td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="5" style="text-align: center; color: #888; font-style: italic;">No labor services specified.</td>
        </tr>
      {% endif %}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="4" style="text-align: right; font-weight: bold;">Labor Subtotal:</td>
        <td style="text-align: right; font-weight: bold;">{{ "{:,.2f}".format(total_labor) }}</td>
      </tr>
    </tfoot>
  </table>

  <!-- 2. Parts & Materials Table -->
  <div class="section-title" style="margin-top: 15px;">2. ESTIMATED PARTS & MATERIALS</div>
  <table class="items-table">
    <thead>
      <tr>
        <th style="width: 5%; text-align: center;">#</th>
        <th style="width: 55%; text-align: left;">Part Description</th>
        <th style="width: 12%; text-align: right;">Qty</th>
        <th style="width: 13%; text-align: right;">Unit Price</th>
        <th style="width: 15%; text-align: right;">Total Amount</th>
      </tr>
    </thead>
    <tbody>
      {% set part_rows = doc.get("parts") or [] %}
      {% if part_rows %}
        {% for row in part_rows %}
        <tr>
          <td style="text-align: center;">{{ loop.index }}</td>
          <td style="text-align: left;">
            <div class="item-name">{{ row.item_name or row.item_code or row.part_no }}</div>
            {% if row.part_no %}
            <div class="item-sub">Part No: {{ row.part_no }}</div>
            {% endif %}
          </td>
          <td style="text-align: right;">{{ "{:,.0f}".format(row.qty or 1) }} {{ row.uom or "PC" }}</td>
          <td style="text-align: right;">{{ "{:,.2f}".format(row.rate or 0.0) }}</td>
          <td style="text-align: right;" class="font-bold">{{ "{:,.2f}".format(row.amount or 0.0) }}</td>
        </tr>
        {% endfor %}
      {% else %}
        <tr>
          <td colspan="5" style="text-align: center; color: #888; font-style: italic;">No parts or materials required.</td>
        </tr>
      {% endif %}
    </tbody>
    <tfoot>
      <tr>
        <td colspan="4" style="text-align: right; font-weight: bold;">Parts Subtotal:</td>
        <td style="text-align: right; font-weight: bold;">{{ "{:,.2f}".format(total_parts) }}</td>
      </tr>
    </tfoot>
  </table>

  <!-- Totals Section -->
  <table class="totals-table">
    <tr>
      <td class="totals-label">Labor Subtotal:</td>
      <td class="totals-val">{{ "{:,.2f}".format(total_labor) }}</td>
    </tr>
    <tr>
      <td class="totals-label">Parts Subtotal:</td>
      <td class="totals-val">{{ "{:,.2f}".format(total_parts) }}</td>
    </tr>
    <tr>
      <td class="totals-label" style="border-top: 1px solid #ccc;">Subtotal:</td>
      <td class="totals-val" style="border-top: 1px solid #ccc; font-weight: bold;">{{ "{:,.2f}".format(doc.net_total or (total_labor + total_parts)) }}</td>
    </tr>
    {% if doc.discount_amount and doc.discount_amount > 0 %}
    <tr>
      <td class="totals-label" style="color: #c00;">Discount:</td>
      <td class="totals-val" style="color: #c00; font-weight: bold;">-{{ "{:,.2f}".format(doc.discount_amount) }}</td>
    </tr>
    {% endif %}
    <tr class="grand-total-row">
      <td class="totals-label" style="font-size: 11pt; font-weight: bold; border-top: 2px solid #222;">Total Estimated:</td>
      <td class="totals-val" style="font-size: 11pt; font-weight: bold; border-top: 2px solid #222;">PHP {{ "{:,.2f}".format(doc.grand_total or 0.0) }}</td>
    </tr>
  </table>

  <div style="clear: both;"></div>

  {% if doc.terms_and_conditions %}
  <div style="margin-top: 20px; font-size: 7.5pt; color: #555; line-height: 1.35; border-top: 1px solid #eee; padding-top: 8px;">
    <strong>TERMS & CONDITIONS:</strong><br>
    {{ doc.terms_and_conditions | replace('\n', '<br>') }}
  </div>
  {% endif %}

  <!-- Signatures -->
  <table class="sig-table">
    <tr>
      <td style="width: 45%;">
        <div class="sig-line"></div>
        <div class="sig-name">Prepared / Estimated By</div>
      </td>
      <td style="width: 10%;"></td>
      <td style="width: 45%;">
        <div class="sig-line"></div>
        <div class="sig-name">Customer Acceptance / Approval</div>
      </td>
    </tr>
  </table>
</div>
"""

CSS_STYLES = """
@page {
  size: A4 portrait;
  margin: 12mm 15mm 15mm 15mm;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 8.5pt;
  color: #111;
  line-height: 1.35;
}

.estimate-container {
  width: 100%;
  max-width: 100%;
}

.header-table {
  width: 100%;
  margin-bottom: 12px;
  border-collapse: collapse;
}

.company-title {
  font-size: 9pt;
  font-weight: bold;
  color: #333;
  margin-top: 3px;
  letter-spacing: 0.5px;
}

.estimate-title {
  font-size: 16pt;
  font-weight: 900;
  color: #1a56db;
  letter-spacing: 1px;
}

.doc-meta {
  font-size: 8.5pt;
  color: #444;
  margin-top: 2px;
}

.meta-id {
  font-size: 11pt;
  font-weight: bold;
  color: #111;
  margin-bottom: 2px;
}

.info-table {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 8px 10px;
  background-color: #f9fafb;
  margin-bottom: 12px;
  border-collapse: separate;
}

.inner-info-table {
  width: 100%;
  border-collapse: collapse;
}

.inner-info-table td {
  padding: 2px 4px;
  font-size: 8.5pt;
  vertical-align: top;
}

.info-label {
  width: 32%;
  color: #4b5563;
  font-weight: 500;
}

.info-val {
  width: 68%;
  color: #111;
}

.font-bold {
  font-weight: 700;
}

.section-title {
  font-size: 8.5pt;
  font-weight: 800;
  color: #1f2937;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  border-bottom: 1.5px solid #1a56db;
  padding-bottom: 2px;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 8px;
}

.items-table th {
  background-color: #f3f4f6;
  border-top: 1px solid #d1d5db;
  border-bottom: 1px solid #d1d5db;
  padding: 5px 6px;
  font-size: 8pt;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
}

.items-table td {
  border-bottom: 1px solid #e5e7eb;
  padding: 5px 6px;
  font-size: 8.5pt;
  vertical-align: middle;
}

.items-table tfoot td {
  border-top: 1.5px solid #d1d5db;
  border-bottom: none;
  padding: 4px 6px;
  font-size: 8.5pt;
  background-color: #fafafa;
}

.item-name {
  font-weight: 600;
  color: #111;
}

.item-sub {
  font-size: 7.5pt;
  color: #6b7280;
  margin-top: 1px;
}

.totals-table {
  width: 42%;
  float: right;
  border-collapse: collapse;
  margin-top: 10px;
  margin-bottom: 15px;
}

.totals-table td {
  padding: 3px 6px;
  font-size: 8.5pt;
}

.totals-label {
  text-align: right;
  color: #4b5563;
  width: 55%;
}

.totals-val {
  text-align: right;
  font-weight: 600;
  width: 45%;
}

.grand-total-row td {
  background-color: #f9fafb;
}

.sig-table {
  width: 100%;
  margin-top: 35px;
  border-collapse: collapse;
}

.sig-line {
  border-top: 1px solid #4b5563;
  width: 85%;
  margin: 0 auto;
}

.sig-name {
  text-align: center;
  font-size: 8pt;
  font-weight: 600;
  color: #374151;
  margin-top: 4px;
}
"""

# 1. Create or Update Print Format
if frappe.db.exists("Print Format", PRINT_FORMAT_NAME):
	pf = frappe.get_doc("Print Format", PRINT_FORMAT_NAME)
	pf.html = HTML_TEMPLATE
	pf.css = CSS_STYLES
	pf.save(ignore_permissions=True)
	print(f"Updated Print Format '{PRINT_FORMAT_NAME}'.")
else:
	pf = frappe.get_doc({
		"doctype": "Print Format",
		"name": PRINT_FORMAT_NAME,
		"doc_type": "Vehicle Estimate",
		"format_data": None,
		"html": HTML_TEMPLATE,
		"css": CSS_STYLES,
		"print_format_type": "Jinja",
		"custom_format": 1,
		"standard": "No",
		"module": "Vehicle Management",
		"disabled": 0
	})
	pf.insert(ignore_permissions=True)
	print(f"Created Print Format '{PRINT_FORMAT_NAME}'.")

# 2. Make it Default Print Format for Vehicle Estimate
make_property_setter(
	doctype="Vehicle Estimate",
	fieldname=None,
	property="default_print_format",
	value=PRINT_FORMAT_NAME,
	property_type="Data",
	for_doctype=True
)
print(f"Set '{PRINT_FORMAT_NAME}' as default print format for Vehicle Estimate.")

frappe.db.commit()
frappe.clear_cache()
print("Setup complete!")
