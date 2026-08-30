import frappe

frappe.init(site="erp.localhost")
frappe.connect()

print("DB type:", frappe.db.db_type)

tests = [
    (
        "boot.py party_account_types",
        """ select name, coalesce(account_type, '') from `tabParty Type`""",
        None,
    ),
    (
        "location.py get_children (coalesce + '')",
        f"""select name as value, is_group as expandable
            from `tabLocation` comp
            where coalesce(parent_location, '')={frappe.db.escape('')}""",
        None,
    ),
    (
        "company.py get_children (coalesce + '')",
        f"""select name as value, is_group as expandable
            from `tabCompany` comp
            where coalesce(parent_company, '')={frappe.db.escape('')}""",
        None,
    ),
    (
        "company.py get_default_company_address",
        """ SELECT addr.name, addr.is_primary_address
            FROM `tabAddress` addr, `tabDynamic Link` dl
            WHERE dl.parent = addr.name and dl.link_doctype = 'Company' and
            dl.link_name = %s and coalesce(addr.disabled, 0) = 0""",
        ("_dummy_",),
    ),
    (
        "activity_cost.py duplicate check",
        """select name from `tabActivity Cost` where coalesce(employee, '')='' and activity_type= %s and name != %s""",
        ("_dummy_", "_dummy_"),
    ),
    (
        "asset.py booked_fixed_asset",
        """ select name from `tabAsset`
            where asset_category = %s and coalesce(booked_fixed_asset, 0) = 0
            and available_for_use_date = %s and docstatus = 1""",
        ("_dummy_", frappe.utils.nowdate()),
    ),
    (
        "work_order.py get_item_details (zero-date -> 0001-01-01)",
        """select stock_uom, description, item_name, allow_alternative_item,
            include_item_in_manufacturing
            from `tabItem`
            where disabled=0
            and (end_of_life is null or end_of_life='0001-01-01' or end_of_life > %s)
            and name=%s""",
        (frappe.utils.nowdate(), "_dummy_"),
    ),
    (
        "job_card.py get_job_details",
        """ SELECT `tabJob Card`.name, `tabJob Card`.work_order,
            `tabJob Card`.status, coalesce(`tabJob Card`.remarks, ''),
            min(`tabJob Card Time Log`.from_time) as from_time,
            max(`tabJob Card Time Log`.to_time) as to_time
            FROM `tabJob Card` , `tabJob Card Time Log`
            WHERE `tabJob Card`.name = `tabJob Card Time Log`.parent
            group by `tabJob Card`.name""",
        None,
    ),
    (
        "utilities/naming.py update ... coalesce (SELECT-form probe)",
        """select name from `tabCustomer` where coalesce(naming_series, '')=''""",
        None,
    ),
]

ok = fail = 0
for label, q, vals in tests:
    try:
        rows = frappe.db.sql(q, vals) if vals else frappe.db.sql(q)
        print(f"  PASS  {label}  -> {len(rows)} row(s)")
        ok += 1
    except Exception as exc:
        print(f"  FAIL  {label}\n          {type(exc).__name__}: {str(exc)[:300]}")
        fail += 1

print(f"\nRESULT: {ok} passed, {fail} failed")

# Prove the OLD MySQL forms would actually have failed on Postgres
print("\n--- control: pre-fix MySQL forms against Postgres ---")
for label, q in [
    ("ifnull()", "select coalesce(1,1) as a, ifnull(name, '') from `tabParty Type` limit 1"),
    ('empty "" literal', """select name from `tabCompany` where coalesce(parent_company, "")=''"""),
    ("zero date", "select name from `tabItem` where end_of_life='0000-00-00' limit 1"),
]:
    try:
        frappe.db.sql(q)
        print(f"  (no error) {label}")
    except Exception as exc:
        frappe.db.rollback()
        print(f"  errors as expected -> {label}: {type(exc).__name__}: {str(exc)[:140]}")

frappe.destroy()
