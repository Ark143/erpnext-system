import frappe
from frappe.model.document import Document

class VehicleAppointment(Document):
    def validate(self):
        if self.customer and self.vehicle:
            owner = frappe.db.get_value("Customer Vehicle", self.vehicle, "customer")
            if owner != self.customer:
                frappe.throw("The selected vehicle does not belong to this Customer.")
        if self.plate_no:
            self.plate_no = self.plate_no.strip().upper()
