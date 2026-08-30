import frappe, traceback
frappe.init("")
try:
    from frappe.build import bundle
    bundle("production", apps=None, hard_link=False, verbose=True, skip_frappe=False, save_metafiles=False)
    print("BUNDLE DONE")
except Exception:
    traceback.print_exc()
