"""
Script to create the custom Print Format "Autometrik Job Order" for Vehicle Job Order,
set it as the default print format, and create a sample transaction matching the screenshot.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "frappe"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "erpnext"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "vehicle_management"))

import frappe
from frappe.utils import nowdate, flt
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

frappe.init("site1.local")
frappe.connect()

PRINT_FORMAT_NAME = "Autometrik Job Order"

HTML_TEMPLATE = """
{% set customer_doc = frappe.get_doc("Customer", doc.customer) if doc.customer and frappe.db.exists("Customer", doc.customer) else None %}
{% set vehicle_doc = frappe.get_doc("Customer Vehicle", doc.vehicle) if doc.vehicle and frappe.db.exists("Customer Vehicle", doc.vehicle) else None %}

{% set cust_name = doc.customer_name or (customer_doc.customer_name if customer_doc else doc.customer) %}
{% set cust_mobile = doc.contact_no or (customer_doc.custom_mobile_no if customer_doc else "") or (customer_doc.mobile_no if customer_doc else "") %}
{% set cust_address = (customer_doc.custom_address_text if customer_doc else "") or (customer_doc.primary_address if customer_doc else "") %}

{% set veh_plate = doc.plate_no or (vehicle_doc.plate_no if vehicle_doc else "N/A") %}
{% set veh_vin = (vehicle_doc.vin if vehicle_doc else "") or "N/A" %}
{% set veh_model = "" %}
{% if vehicle_doc %}
    {% set veh_model = ((vehicle_doc.make or "") ~ " " ~ (vehicle_doc.model or "") ~ " " ~ (vehicle_doc.year_model or "") ~ " " ~ (vehicle_doc.transmission or "")) | trim %}
{% endif %}
{% if not veh_model and doc.vehicle %}
    {% set veh_model = doc.vehicle %}
{% endif %}

{% set total_labor = doc.total_labor or 0.0 %}
{% set total_parts = doc.total_parts or 0.0 %}

<div class="job-order-container">
  <!-- Header: Logo & Company on Left, Job Order Title & Meta on Right -->
  <table class="header-table">
    <tr>
      <td style="width: 50%; vertical-align: top;">
        <img src="/files/ultra_mrf_logo.png" style="max-height: 55px; max-width: 220px; object-fit: contain;" alt="ULTRA MRF" />
        <div class="company-title">{{ doc.company or "ULTRA MRF DAU MAIN" }}</div>
      </td>
      <td style="width: 50%; vertical-align: top; text-align: right;">
        <div class="job-order-title">JOB ORDER</div>
        <div class="doc-meta">
          <div class="meta-id">{{ doc.name }}</div>
          <div><b>Date:</b> {{ frappe.utils.formatdate(doc.job_order_date or doc.creation, "M/d/yyyy") }}{% if doc.posting_time %} {{ doc.posting_time }}{% endif %}</div>
          {% if doc.time_in %}
          <div><b>Time In:</b> {{ frappe.utils.format_datetime(doc.time_in, "M/d/yyyy h:mm a") }}</div>
          {% endif %}
          {% if doc.time_out %}
          <div><b>Time Out:</b> {{ frappe.utils.format_datetime(doc.time_out, "M/d/yyyy h:mm a") }}</div>
          {% endif %}
        </div>
      </td>
    </tr>
  </table>

  <!-- Customer & Vehicle Info Section -->
  <table class="info-table">
    <tr>
      <!-- Column 1: Customer Details -->
      <td style="width: 48%; vertical-align: top; padding-right: 15px;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td class="info-label" style="width: 110px;">CUSTOMER</td>
            <td class="info-value" style="font-weight: bold; text-transform: uppercase;">{{ cust_name or "N/A" }}</td>
          </tr>
          {% if cust_address %}
          <tr>
            <td class="info-label"></td>
            <td class="info-value" style="text-transform: uppercase;">{{ cust_address }}</td>
          </tr>
          {% endif %}
          {% if cust_mobile %}
          <tr>
            <td class="info-label"></td>
            <td class="info-value">{{ cust_mobile }}</td>
          </tr>
          {% endif %}
        </table>
      </td>

      <!-- Column 2: Vehicle & Mileage Details -->
      <td style="width: 52%; vertical-align: top;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td class="info-label" style="width: 130px;">PLATE NO</td>
            <td class="info-value" style="font-weight: bold; width: 120px;">{{ veh_plate }}</td>
            <td class="info-label" style="width: 75px;">MILEAGE</td>
            <td class="info-value" style="font-weight: bold;">
              {% if doc.mileage %}
                {{ (doc.mileage | int) if (doc.mileage % 1 == 0) else doc.mileage }} {{ (doc.mileage_unit or "KM") | upper }}
              {% else %}
                N/A
              {% endif %}
            </td>
          </tr>
          <tr>
            <td class="info-label">VIN</td>
            <td class="info-value" colspan="3">{{ veh_vin }}</td>
          </tr>
          <tr>
            <td class="info-label">VEHICLE MODEL</td>
            <td class="info-value" colspan="3" style="text-transform: uppercase;">{{ veh_model or "N/A" }}</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>

  <!-- 1. LABOR TABLE -->
  {% if doc.services %}
  <div class="items-section">
    <div class="section-header">LABOR</div>
    <table class="data-table">
      <thead>
        <tr>
          <th style="width: 40px;" class="text-center">No</th>
          <th>Service</th>
          <th style="width: 140px;" class="text-right">Amount</th>
        </tr>
      </thead>
      <tbody>
        {% for row in doc.services %}
        <tr>
          <td class="text-center">{{ loop.index }}</td>
          <td style="text-transform: uppercase;">{{ row.description or row.service_item }}</td>
          <td class="text-right">{{ frappe.utils.fmt_money(row.total_amount or ((row.hours or 1.0) * (row.rate or 0.0) - (row.discount_amount or 0.0)), currency="PHP") }}</td>
        </tr>
        {% endfor %}
        <tr class="total-row">
          <td colspan="2" class="text-right" style="padding-right: 15px;">Total</td>
          <td class="text-right">{{ frappe.utils.fmt_money(doc.total_labor, currency="PHP") }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  {% endif %}

  <!-- 2. PARTS & MATERIALS TABLE -->
  {% if doc.parts %}
  <div class="items-section">
    <div class="section-header">PARTS &amp; MATERIALS</div>
    <table class="data-table">
      <thead>
        <tr>
          <th style="width: 40px;" class="text-center">No</th>
          <th>Item</th>
          <th style="width: 80px;" class="text-center">Qty</th>
          <th style="width: 120px;" class="text-right">Price</th>
          <th style="width: 140px;" class="text-right">Amount</th>
        </tr>
      </thead>
      <tbody>
        {% for row in doc.parts %}
        <tr>
          <td class="text-center">{{ loop.index }}</td>
          <td style="text-transform: uppercase;">{{ row.item_name or row.item_code or row.part_no }}</td>
          <td class="text-center">{{ (row.qty | int) if (row.qty % 1 == 0) else row.qty }}{{ (row.uom or "PC") | upper }}</td>
          <td class="text-right">{{ frappe.utils.fmt_money(row.rate, currency="PHP") }}</td>
          <td class="text-right">{{ frappe.utils.fmt_money(row.amount or ((row.qty or 1.0) * (row.rate or 0.0) - (row.discount_amount or 0.0)), currency="PHP") }}</td>
        </tr>
        {% endfor %}
        <tr class="total-row">
          <td colspan="4" class="text-right" style="padding-right: 15px;">Total</td>
          <td class="text-right">{{ frappe.utils.fmt_money(doc.total_parts, currency="PHP") }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  {% endif %}

  <!-- REMARKS BOX -->
  <div class="remarks-box">
    <div class="remarks-header">REMARKS</div>
    <div class="remarks-body">
      {{ doc.remarks or doc.customer_complaint or "CASH" }}
    </div>
  </div>

  <!-- TOTALS SUMMARY SECTION -->
  <div style="width: 100%; overflow: hidden;">
    <table class="summary-table">
      <tr>
        <td class="summary-label">SUBTOTAL</td>
        <td class="summary-value">{{ frappe.utils.fmt_money(doc.net_total or (doc.total_labor + doc.total_parts), currency="PHP") }}</td>
      </tr>
      {% if doc.discount_amount and doc.discount_amount > 0 %}
      <tr>
        <td class="summary-label">DISCOUNT</td>
        <td class="summary-value">{{ frappe.utils.fmt_money(doc.discount_amount, currency="PHP") }}</td>
      </tr>
      {% endif %}
      <tr class="total-due-row">
        <td class="summary-label" style="font-size: 14px; font-weight: 900;">TOTAL AMOUNT DUE</td>
        <td class="summary-value" style="font-size: 14px; font-weight: 900;">{{ frappe.utils.fmt_money(doc.grand_total or (doc.net_total - (doc.discount_amount or 0.0)), currency="PHP") }}</td>
      </tr>
    </table>
  </div>

  <!-- SIGNATURES SECTION (3 Columns) -->
  <table class="signature-section">
    <tr>
      <td style="width: 30%; text-align: center; vertical-align: bottom;">
        <div class="sig-title">PREPARED BY</div>
        <div class="sig-line">SIGNATURE OVER PRINTED NAME</div>
      </td>
      <td style="width: 5%;"></td>
      <td style="width: 30%; text-align: center; vertical-align: bottom;">
        <div class="sig-title">APPROVED BY</div>
        <div class="sig-line">SIGNATURE OVER PRINTED NAME</div>
      </td>
      <td style="width: 5%;"></td>
      <td style="width: 30%; text-align: center; vertical-align: bottom;">
        <div class="sig-title">ACKNOWLEDGED BY</div>
        <div class="sig-line">SIGNATURE OVER PRINTED NAME</div>
      </td>
    </tr>
  </table>

  <!-- LEGAL TERMS & ACKNOWLEDGEMENT -->
  <div class="legal-section">
    <div class="legal-title">Customer's/Driver's/Assignee's Acknowledgement</div>
    <div class="legal-text">
      I hereby authorize the above repair jobs to be carried out, including the use of necessary parts and materials, and agree to pay the corresponding amount upon completion. I further agree to pay interest at a rate of 3% per month on all overdue accounts. In the event that the account is endorsed to an attorney for collection, I agree to pay an additional 25% of the amount due, but in no case less than ten thousand pesos (10,000.00), as attorney's fees and litigation costs. I also agree to the additional terms and conditions stated on the reverse side of this document. Any and all civil and/or administrative actions arising out of this transaction shall be filed in the proper courts of Mabalacat City, Pampanga, to the exclusion of all other venues.
    </div>
  </div>
</div>

<style>
  @media print {
    .job-order-container {
      padding: 0;
      font-size: 11.5px;
    }
  }
  .job-order-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    color: #111;
    font-size: 12.5px;
    line-height: 1.35;
    padding: 10px;
    background: #fff;
  }
  .header-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }
  .company-title {
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-top: 8px;
    color: #000;
  }
  .job-order-title {
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    text-align: right;
    margin-bottom: 3px;
    color: #000;
  }
  .doc-meta {
    text-align: right;
    font-size: 12.5px;
    color: #111;
  }
  .doc-meta .meta-id {
    font-weight: bold;
    margin-bottom: 2px;
  }

  .info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 18px;
  }
  .info-table td {
    vertical-align: top;
    padding: 2px 0;
  }
  .info-label {
    font-weight: 900;
    font-size: 12px;
    text-transform: uppercase;
    color: #000;
  }
  .info-value {
    font-size: 12px;
    color: #222;
  }

  .items-section {
    margin-bottom: 15px;
  }
  .section-header {
    background-color: #f2f2f2;
    padding: 5px 10px;
    font-weight: 900;
    font-size: 12px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    border: 1px solid #d0d0d0;
    border-bottom: none;
    color: #000;
  }
  .data-table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #d0d0d0;
  }
  .data-table th {
    font-weight: 900;
    font-size: 11.5px;
    text-transform: capitalize;
    padding: 5px 10px;
    border-bottom: 1px solid #d0d0d0;
    background-color: #fafafa;
    text-align: left;
  }
  .data-table td {
    padding: 5px 10px;
    font-size: 12px;
    border-bottom: 1px solid #eee;
  }
  .data-table .text-right {
    text-align: right;
  }
  .data-table .text-center {
    text-align: center;
  }
  .total-row td {
    font-weight: 900;
    border-top: 1px solid #ccc;
    border-bottom: none;
    background-color: #fff;
  }

  .remarks-box {
    margin-top: 12px;
    margin-bottom: 16px;
  }
  .remarks-header {
    background-color: #f2f2f2;
    padding: 4px 10px;
    font-weight: 900;
    font-size: 11.5px;
    text-transform: uppercase;
    border: 1px solid #d0d0d0;
    border-bottom: none;
    color: #000;
  }
  .remarks-body {
    padding: 6px 10px;
    border: 1px solid #d0d0d0;
    font-size: 11.5px;
    background-color: #fff;
  }

  .summary-table {
    float: right;
    width: 300px;
    margin-bottom: 25px;
    border-collapse: collapse;
  }
  .summary-table td {
    padding: 3px 6px;
  }
  .summary-label {
    text-align: right;
    font-weight: 900;
    font-size: 12.5px;
    text-transform: uppercase;
  }
  .summary-value {
    text-align: right;
    font-size: 12.5px;
    font-weight: bold;
  }
  .total-due-row td {
    padding-top: 6px;
    border-top: 1px solid #ccc;
  }

  .signature-section {
    clear: both;
    width: 100%;
    margin-top: 30px;
    margin-bottom: 25px;
    border-collapse: collapse;
  }
  .sig-title {
    font-size: 11px;
    font-weight: 900;
    margin-bottom: 40px;
    text-transform: uppercase;
    text-align: center;
  }
  .sig-line {
    border-top: 1px solid #111;
    padding-top: 4px;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: center;
    font-weight: 500;
  }

  .legal-section {
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px dotted #ccc;
  }
  .legal-title {
    font-size: 11px;
    font-weight: 900;
    margin-bottom: 3px;
  }
  .legal-text {
    font-size: 9.5px;
    line-height: 1.35;
    color: #333;
    text-align: justify;
  }
</style>
"""

print("=== Creating Print Format for Vehicle Job Order ===")

if frappe.db.exists("Print Format", PRINT_FORMAT_NAME):
    doc = frappe.get_doc("Print Format", PRINT_FORMAT_NAME)
    doc.html = HTML_TEMPLATE
    doc.save(ignore_permissions=True)
    print(f"  UPDATED Print Format: {PRINT_FORMAT_NAME}")
else:
    doc = frappe.get_doc({
        "doctype": "Print Format",
        "name": PRINT_FORMAT_NAME,
        "doc_type": "Vehicle Job Order",
        "format_data": None,
        "custom_format": 1,
        "print_format_type": "Jinja",
        "raw_printing": 0,
        "html": HTML_TEMPLATE,
        "disabled": 0,
        "standard": "No",
        "default_print_language": "en"
    })
    doc.insert(ignore_permissions=True)
    print(f"  CREATED Print Format: {PRINT_FORMAT_NAME}")

make_property_setter("Vehicle Job Order", None, "default_print_format", PRINT_FORMAT_NAME, "Data")
frappe.db.commit()


# ─────────────────────────────────────────────────────────
# Create Sample Transaction (Vehicle Job Order) matching the screenshot
# ─────────────────────────────────────────────────────────
print("\n=== Creating Sample Vehicle Job Order Transaction ===")

customer_name = "BENNY DEL ROSARIO"
plate_no = "RKH344"

# 1. Ensure Customer exists with address & mobile
if not frappe.db.exists("Customer", customer_name):
    cust = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "customer_type": "Individual",
        "custom_address_text": "TARLAC",
        "custom_mobile_no": "09325743377"
    })
    cust.insert(ignore_permissions=True)
else:
    frappe.db.set_value("Customer", customer_name, {
        "custom_address_text": "TARLAC",
        "custom_mobile_no": "09325743377"
    })

# 2. Ensure Customer Vehicle exists
if not frappe.db.exists("Customer Vehicle", plate_no):
    veh = frappe.get_doc({
        "doctype": "Customer Vehicle",
        "plate_no": plate_no,
        "customer": customer_name,
        "make": "Mitsubishi",
        "model": "Mitsubishi-Montero Sport",
        "year_model": 2010,
        "vin": "N/A",
        "current_mileage": 110684,
        "mileage_unit": "km",
        "transmission": "Automatic",
        "fuel_type": "Diesel",
        "status": "Active"
    })
    veh.insert(ignore_permissions=True)
    print(f"  Created Customer Vehicle: {plate_no}")
else:
    frappe.db.set_value("Customer Vehicle", plate_no, {
        "customer": customer_name,
        "make": "Mitsubishi",
        "model": "Mitsubishi-Montero Sport",
        "year_model": 2010,
        "vin": "N/A",
        "current_mileage": 110684,
        "mileage_unit": "km"
    })

# 4. Ensure Services exist
service_1 = "WHEEL ALIGNMENT (TOE-IN, TOE-OUT)"
service_2 = "MISCELLANEOUS"

for s_name, rate in [(service_1, 870.0), (service_2, 150.0)]:
    if not frappe.db.exists("Item", s_name):
        doc = frappe.get_doc({
            "doctype": "Item",
            "item_code": s_name,
            "item_name": s_name,
            "item_group": "TIRE / WHEEL SERVICES",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "stock_uom": "Nos",
            "standard_rate": rate
        })
        doc.insert(ignore_permissions=True)
        print(f"  Created Service Item: {s_name}")

# 5. Ensure Part exists
part_1 = "STRL-CAR PROTECT KIT (CAR CLEAN SET)"
if not frappe.db.exists("Item", part_1):
    doc = frappe.get_doc({
        "doctype": "Item",
        "item_code": part_1,
        "item_name": part_1,
        "item_group": "All Item Groups",
        "is_stock_item": 1,
        "is_sales_item": 1,
        "stock_uom": "PC",
        "standard_rate": 105.0,
        "custom_sell_price": 105.0
    })
    doc.insert(ignore_permissions=True)
    print(f"  Created Stock Item: {part_1}")

# 6. Create the sample Vehicle Job Order
jo = frappe.get_doc({
    "doctype": "Vehicle Job Order",
    "naming_series": "JO-.YYYY.-.#####",
    "company": "Ultra MRF Dau Main",
    "job_order_date": "2026-08-23",
    "vehicle": plate_no,
    "plate_no": plate_no,
    "customer": customer_name,
    "customer_name": customer_name,
    "contact_no": "09325743377",
    "mileage": 110684,
    "mileage_unit": "km",
    "status": "Completed",
    "remarks": "CASH",
    "services": [
        {
            "service_item": service_1,
            "description": service_1,
            "hours": 1.0,
            "rate": 870.0,
            "discount_amount": 0.0,
            "total_amount": 870.0
        },
        {
            "service_item": service_2,
            "description": service_2,
            "hours": 1.0,
            "rate": 150.0,
            "discount_amount": 0.0,
            "total_amount": 150.0
        }
    ],
    "parts": [
        {
            "item_code": part_1,
            "item_name": part_1,
            "qty": 1.0,
            "uom": "PC",
            "rate": 105.0,
            "discount_amount": 0.0,
            "amount": 105.0
        }
    ],
    "discount_amount": 125.0
})

jo.insert(ignore_permissions=True)
frappe.db.commit()

print(f"\nCreated Sample Vehicle Job Order: {jo.name}")
print(f"  Customer: {jo.customer_name}")
print(f"  Vehicle: {jo.vehicle}")
print(f"  Labor Total: PHP {jo.total_labor:,.2f}")
print(f"  Parts Total: PHP {jo.total_parts:,.2f}")
print(f"  Subtotal: PHP {jo.net_total:,.2f}")
print(f"  Discount: PHP {jo.discount_amount:,.2f}")
print(f"  Grand Total: PHP {jo.grand_total:,.2f}")
print("\nDone!")
