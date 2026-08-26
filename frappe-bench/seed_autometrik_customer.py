import frappe

def seed_customer():
    frappe.init('site1.local')
    frappe.connect()
    frappe.set_user('Administrator')

    # Individual Customer
    cust_name = "Danilo Obra"
    if not frappe.db.exists("Customer", cust_name):
        doc = frappe.new_doc("Customer")
        doc.customer_name = cust_name
        doc.customer_type = "Individual"
        doc.customer_group = "Individual"
        doc.territory = "All Territories"
        
        # Autometrik custom fields
        doc.custom_first_name = "Danilo"
        doc.custom_last_name = "Obra"
        doc.custom_mobile_no = "09171234567"
        doc.custom_email_address = "danilo.obra@example.ph"
        doc.custom_address_text = "123 MacArthur Highway, Dau, Mabalacat, Pampanga"
        doc.custom_notes = "Regular customer. Preferred mechanic: Mark. Inquire about synthetic oil promo."
        
        doc.custom_labor_discount_rate = 10.0
        doc.custom_product_discount_rate = 5.0
        doc.custom_is_vat_exempt = 0
        doc.custom_is_zero_rated = 0
        doc.custom_allow_withholding_tax = 0
        
        doc.insert(ignore_permissions=True)
        print(f"Created Customer: {cust_name}")
    else:
        doc = frappe.get_doc("Customer", cust_name)
        doc.custom_first_name = "Danilo"
        doc.custom_last_name = "Obra"
        doc.custom_mobile_no = "09171234567"
        doc.custom_email_address = "danilo.obra@example.ph"
        doc.custom_address_text = "123 MacArthur Highway, Dau, Mabalacat, Pampanga"
        doc.custom_notes = "Regular customer. Preferred mechanic: Mark. Inquire about synthetic oil promo."
        doc.custom_labor_discount_rate = 10.0
        doc.custom_product_discount_rate = 5.0
        doc.save()
        print(f"Updated Customer: {cust_name}")

    # Corporate Customer
    corp_name = "Ultra MRF Dau Corp"
    if not frappe.db.exists("Customer", corp_name):
        corp = frappe.new_doc("Customer")
        corp.customer_name = corp_name
        corp.customer_type = "Company"
        corp.customer_group = "Commercial"
        corp.territory = "All Territories"
        corp.tax_id = "123-456-789-000"
        
        # Autometrik Corporate fields
        corp.custom_business_style = "Automotive Repair & Services"
        corp.custom_contact_person = "Danilo Obra (Operations Head)"
        corp.custom_office_no = "(045) 892-1234"
        corp.custom_office_fax = "(045) 892-1235"
        corp.custom_mobile_no = "09189876543"
        corp.custom_email_address = "admin@ultramrf.ph"
        corp.custom_address_text = "Dau Main Branch, Mabalacat City, Pampanga"
        
        corp.custom_labor_discount_rate = 15.0
        corp.custom_product_discount_rate = 10.0
        corp.custom_is_vat_exempt = 0
        corp.custom_is_zero_rated = 0
        corp.custom_allow_withholding_tax = 1
        corp.custom_withholding_tax_type = "2% (Purchases of Services)"
        
        corp.insert(ignore_permissions=True)
        print(f"Created Corporate Customer: {corp_name}")

    frappe.db.commit()

if __name__ == "__main__":
    seed_customer()
