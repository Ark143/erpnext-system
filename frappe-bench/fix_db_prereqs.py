import sys, os
sys.path.insert(0, 'apps/frappe')
sys.path.insert(0, 'apps/erpnext')
os.chdir('sites')

import frappe

frappe.init('site1.local')
frappe.connect()

print("--- 1. Fixing database schema anomalies ---")
frappe.db.sql('ALTER TABLE "tabContact" ADD COLUMN IF NOT EXISTS is_billing_contact integer DEFAULT 0;')
frappe.db.sql('ALTER TABLE "tabContact" ADD COLUMN IF NOT EXISTS is_primary_contact integer DEFAULT 0;')
frappe.db.commit()
print("  + Fixed tabContact columns")

print("--- 2. Setting up Fiscal Years ---")
companies = [c.name for c in frappe.get_all('Company')]
for fy_year in ['2024', '2025', '2026', '2027']:
    if not frappe.db.exists('Fiscal Year', fy_year):
        fy = frappe.get_doc({
            'doctype': 'Fiscal Year',
            'year': fy_year,
            'year_start_date': f'{fy_year}-01-01',
            'year_end_date': f'{fy_year}-12-31',
            'companies': [{'company': comp} for comp in companies]
        })
        fy.insert(ignore_permissions=True)
        print(f"  + Created Fiscal Year: {fy_year}")
    else:
        fy = frappe.get_doc('Fiscal Year', fy_year)
        existing_comps = {c.company for c in fy.companies}
        for comp in companies:
            if comp not in existing_comps:
                fy.append('companies', {'company': comp})
        fy.save(ignore_permissions=True)
        print(f"  + Updated Fiscal Year: {fy_year}")

frappe.db.commit()
print("=== Database Prerequisites Complete! ===")
