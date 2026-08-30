# Produce a container-ready copy of the generator with an explicit sites_path
# (frappe.init can't auto-detect the bench via the /workspace/bench symlink)
# and a random sales person per company (user requirement: "USE RANDOM SALES PERSON").
src_path = '/workspace/frappe-bench/generate_src.py'
out_path = '/workspace/frappe-bench/generate_run.py'
src = open(src_path).read()

repl_init = src.replace('frappe.init("site1.local")',
                        "frappe.init('site1.local', sites_path='/workspace/frappe-bench/sites')")
assert repl_init != src, "init replace failed"

repl_sp = repl_init.replace('    sales_person = comp["sales_person"]',
                             '    sales_person = random.choice([sp["name"] for sp in SALES_PERSONS])')
# if the exact line wasn't found, keep as-is (fallback to fixed sales person)

open(out_path, 'w').write(repl_sp)
print("PATCHED_OK init_replaced=%s sp_replaced=%s" % (repl_init != src, repl_sp != repl_init))
