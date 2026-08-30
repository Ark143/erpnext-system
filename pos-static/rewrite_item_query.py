F = "/workspace/frappe-bench/apps/erpnext/erpnext/controllers/queries.py"
t = open(F).read()

start = t.index("def item_query(")
# find next top-level "def " after start
end = t.index("\ndef ", start + 10)
broken_func = t[start:end]

new_func = '''def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
\tdoctype = "Item"
\tconditions = []

\tif isinstance(filters, str):
\t\tfilters = json.loads(filters)

\t# Get searchfields from meta and use in Item Link field query
\tmeta = frappe.get_meta(doctype, cached=True)
\tsearchfields = meta.get_search_fields()

\tcolumns = ""
\textra_searchfields = [field for field in searchfields if field not in ["name", "description"]]

\tif extra_searchfields:
\t\tcolumns += ", " + ", ".join(extra_searchfields)

\tif "description" in searchfields:
\t\tcolumns += """, case when length("tabItem".description) > 40 then concat(substr("tabItem".description, 1, 40), '...') else "tabItem".description end as description"""

\tsearchfields = searchfields + [
\t\tfield
\t\tfor field in [
\t\t\tsearchfield or "name",
\t\t\t"item_code",
\t\t\t"item_group",
\t\t\t"item_name",
\t\t]
\t\tif field not in searchfields
\t]
\tsearchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

\tif filters and isinstance(filters, dict):
\t\tif filters.get("customer") or filters.get("supplier"):
\t\t\tparty_type = "Customer" if filters.get("customer") else "Supplier"
\t\t\tparty = filters.get("customer") or filters.get("supplier")
\t\t\tgroup = "Customer Group" if filters.get("customer") else "Supplier Group"
\t\t\titem_rules_list = frappe.get_all(
\t\t\t\t"Party Specific Item",
\t\t\t\tfilters={"party_type": party_type},
\t\t\t\tfields=["party", "restrict_based_on", "based_on_value"],
\t\t\t)

\t\t\tparty_group_rules_list = frappe.get_all(
\t\t\t\t"Party Specific Item",
\t\t\t\tfilters={"party_type": group},
\t\t\t\tfields=["party as party_group", "restrict_based_on", "based_on_value"],
\t\t\t)
\t\t\tcurrent_party_group = frappe.get_value(party_type, party, frappe.scrub(group))

\t\t\trestricted_items = defaultdict(set)
\t\t\tallowed_items = defaultdict(set)

\t\t\tfor rule in item_rules_list:
\t\t\t\trestrict_based_on = "name" if rule.restrict_based_on == "Item" else rule.restrict_based_on

\t\t\t\tif rule.party == party:
\t\t\t\t\tallowed_items[restrict_based_on].add(rule.based_on_value)
\t\t\t\telse:
\t\t\t\t\trestricted_items[restrict_based_on].add(rule.based_on_value)

\t\t\tfor rule in party_group_rules_list:
\t\t\t\trestrict_based_on = "name" if rule.restrict_based_on == "Item" else rule.restrict_based_on

\t\t\t\tif current_party_group == rule.party_group:
\t\t\t\t\tallowed_items[restrict_based_on].add(rule.based_on_value)
\t\t\t\telse:
\t\t\t\t\trestricted_items[restrict_based_on].add(rule.based_on_value)

\t\t\tfor field, restricted_values in restricted_items.items():
\t\t\t\tvalues_to_exclude = restricted_values - allowed_items[field]
\t\t\t\tif values_to_exclude:
\t\t\t\t\tfilters[scrub(field)] = ["not in", list(values_to_exclude)]

\t\t\tif filters.get("customer"):
\t\t\t\tdel filters["customer"]
\t\t\telse:
\t\t\t\tdel filters["supplier"]
\t\telse:
\t\t\tfilters.pop("customer", None)
\t\tfilters.pop("supplier", None)

\tdescription_cond = ""
\tif frappe.db.estimate_count(doctype) < 50000:
\t\t# scan description only if items are less than 50000
\t\tdescription_cond = "or \\"tabItem\\".description LIKE %(txt)s"

\treturn frappe.db.sql(
\t\t"""select
\t\t\t"tabItem".name {columns}
\t\tfrom "tabItem"
\t\twhere "tabItem".docstatus < 2
\t\t\tand "tabItem".disabled=0
\t\t\tand "tabItem".has_variants=0
\t\t\tand ("tabItem".end_of_life > %(today)s or coalesce("tabItem".end_of_life, '0000-00-00')='0000-00-00')
\t\t\tand ({scond} or "tabItem".item_code IN (select parent from "tabItem Barcode" where barcode LIKE %(txt)s)
\t\t\t\t{description_cond})
\t\t\t{fcond} {mcond}
\t\torder by
\t\t\tcase when locate(%(_txt)s, name) > 0 then locate(%(_txt)s, name) else 99999 end,
\t\t\tcase when locate(%(_txt)s, item_name) > 0 then locate(%(_txt)s, item_name) else 99999 end,
\t\t\tname, item_name
\t\tlimit %(page_len)s offset %(start)s """.format(
\t\t\tcolumns=columns,
\t\t\tscond=searchfields,
\t\t\tfcond=get_filters_cond(doctype, filters, conditions).replace("%", "%%"),
\t\t\tmcond=get_match_cond(doctype).replace("%", "%%"),
\t\t\tdescription_cond=description_cond,
\t\t),
\t\t{
\t\t\t"today": nowdate(),
\t\t\t"txt": "%%%s%%" % txt,
\t\t\t"_txt": txt.replace("%", ""),
\t\t\t"start": cint(start),
\t\t\t"page_len": cint(page_len),
\t\t},
\t\tas_dict=as_dict,
\t)
'''

t = t[:start] + new_func + t[end:]
open(F, "w").write(t)
print("replaced item_query; broken_func_len:", len(broken_func))
print("new contains case when locate:", "case when locate" in new_func)
print("new contains offset:", "offset %(start)s" in new_func)
