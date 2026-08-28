import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')
import frappe
from frappe.utils import nowdate

frappe.init(site='erp.localhost')
frappe.connect()

company = "Ultra MRF Dau Annex"
item = frappe.db.get_value("Item", {"is_sales_item": 1}, "name")
customer = frappe.db.get_value("Customer", {}, "name")

print(f"Testing POS Invoice with Item: {item}, Customer: {customer}")

si = frappe.new_doc("Sales Invoice")
si.company = company
si.customer = customer
si.is_pos = 1
si.pos_profile = "JM"
si.posting_date = nowdate()
si.set_missing_values()

si.append("items", {
    "item_code": item,
    "qty": 1,
    "rate": 500.0,
    "income_account": frappe.db.get_value("Account", {"company": company, "account_type": "Income Account", "is_group": 0}, "name") or "Sales - UMDA",
    "expense_account": frappe.db.get_value("Account", {"company": company, "account_type": "Cost of Goods Sold", "is_group": 0}, "name") or "Cost of Goods Sold - UMDA",
    "cost_center": frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name") or "Main - UMDA"
})

si.set_missing_values()
si.calculate_taxes_and_totals()

# Set payments
si.append("payments", {
    "mode_of_payment": "Cash",
    "amount": si.grand_total,
    "account": "Cash - UMDA" if frappe.db.exists("Account", "Cash - UMDA") else frappe.db.get_value("Account", {"company": company, "account_type": "Cash"}, "name")
})

si.insert()
si.submit()
print(f"SUCCESS: Created & Submitted POS Sales Invoice: {si.name} with Total: ₱{si.grand_total}")
