F = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/doctype/vehicle_pos_invoice/vehicle_pos_invoice.py"
t = open(F).read()

old = '''\t\tlinked_customer = frappe.db.get_value("Customer Vehicle", self.vehicle, "customer")
\t\tif not linked_customer:
\t\t\tfrappe.throw(_("Selected Customer Vehicle has no linked Customer."))
\t\tif self.customer and self.customer != linked_customer:'''

new = '''\t\tlinked_customer = frappe.db.get_value("Customer Vehicle", self.vehicle, "customer")
\t\tif linked_customer:
\t\t\tlinked_customer = " ".join(str(linked_customer).split())
\t\tif self.customer:
\t\t\tself.customer = " ".join(str(self.customer).split())
\t\tif not linked_customer:
\t\t\tfrappe.throw(_("Selected Customer Vehicle has no linked Customer."))
\t\tif self.customer and self.customer != linked_customer:'''

if old in t and "join(str(linked_customer)" not in t:
    t = t.replace(old, new, 1)
    open(F, "w").write(t)
    print("patched validate_vehicle_customer:", "join(str(linked_customer)" in t)
else:
    print("anchor not found or already patched; old_in=", old in t)
