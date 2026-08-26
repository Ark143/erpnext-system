/**
 * vehicle_transaction.js
 *
 * Client script injected into Quotation, Sales Order, Delivery Note, and Sales Invoice.
 * Adds a "Vehicle Details" tab that:
 *  - Populates with the customer's vehicles on customer change
 *  - Lets the user select a specific vehicle plate
 *  - Fetches and displays all vehicle details from Customer Vehicle
 */

(function () {
    const VEHICLE_DOCTYPES = [
        "Quotation",
        "Sales Order",
        "Delivery Note",
        "Sales Invoice",
    ];

    // ─────────────────────────────────────────────
    // Common setup for all transactional documents
    // ─────────────────────────────────────────────

    function setup_vehicle_tab(frm) {
        // Fetch vehicles when customer changes
        const customer_field = frm.doctype === "Quotation"
            ? "party_name"
            : "customer";

        frm.fields_dict[customer_field]?.df?.onchange;
        frm.set_query("custom_vehicle_plate", function () {
            const customer = frm.doc[customer_field];
            return {
                doctype: "Customer Vehicle",
                filters: customer
                    ? { customer: customer, status: ["in", ["Active", "In Service"]] }
                    : {},
            };
        });
    }

    function fetch_vehicle_details(frm) {
        const plate = frm.doc.custom_vehicle_plate;
        if (!plate) {
            clear_vehicle_fields(frm);
            return;
        }

        frappe.db.get_doc("Customer Vehicle", plate).then((vehicle) => {
            frm.set_value("custom_vehicle_make", vehicle.make || "");
            frm.set_value("custom_vehicle_model", vehicle.model || "");
            frm.set_value("custom_vehicle_year", vehicle.year_model || "");
            frm.set_value("custom_vehicle_color", vehicle.color || "");
            frm.set_value("custom_vehicle_vin", vehicle.vin || "");
            frm.set_value("custom_vehicle_engine_no", vehicle.engine_no || "");
            frm.set_value("custom_vehicle_transmission", vehicle.transmission || "");
            frm.set_value("custom_vehicle_fuel_type", vehicle.fuel_type || "");
            frm.set_value("custom_vehicle_mileage", vehicle.current_mileage || 0);
            frm.set_value("custom_vehicle_mileage_unit", vehicle.mileage_unit || "km");
            frm.set_value("custom_vehicle_registration_type", vehicle.registration_type || "");
            frm.set_value("custom_vehicle_insurance_company", vehicle.insurance_company || "");
            frm.set_value("custom_vehicle_insurance_expiry", vehicle.insurance_expiry_date || "");
            frm.set_value("custom_vehicle_notes", vehicle.notes || "");
        });
    }

    function clear_vehicle_fields(frm) {
        const fields = [
            "custom_vehicle_plate", "custom_vehicle_make", "custom_vehicle_model",
            "custom_vehicle_year", "custom_vehicle_color", "custom_vehicle_vin",
            "custom_vehicle_engine_no", "custom_vehicle_transmission", "custom_vehicle_fuel_type",
            "custom_vehicle_mileage", "custom_vehicle_mileage_unit",
            "custom_vehicle_registration_type", "custom_vehicle_insurance_company",
            "custom_vehicle_insurance_expiry", "custom_vehicle_notes",
        ];
        fields.forEach(f => frm.set_value(f, ""));
    }

    function populate_vehicles_on_customer(frm) {
        const customer_field = frm.doctype === "Quotation" ? "party_name" : "customer";
        const customer = frm.doc[customer_field];

        if (!customer) {
            clear_vehicle_fields(frm);
            frm.set_value("custom_vehicle_plate", "");
            return;
        }

        // If only one vehicle, auto-select it
        frappe.db.get_list("Customer Vehicle", {
            filters: { customer: customer, status: ["in", ["Active", "In Service"]] },
            fields: ["name", "make", "model", "year_model"],
            limit: 10,
        }).then((vehicles) => {
            if (vehicles.length === 1) {
                frm.set_value("custom_vehicle_plate", vehicles[0].name);
                fetch_vehicle_details(frm);
            }
        });
    }

    // ─────────────────────────────────────────────
    // Register on each doctype
    // ─────────────────────────────────────────────

    VEHICLE_DOCTYPES.forEach((doctype) => {
        frappe.ui.form.on(doctype, {
            refresh(frm) {
                setup_vehicle_tab(frm);
                if (frm.doc.custom_vehicle_plate) {
                    // Display a quick link to the vehicle record
                    frm.add_custom_button(
                        __("View Vehicle"),
                        () => frappe.set_route("Form", "Customer Vehicle", frm.doc.custom_vehicle_plate),
                        __("Vehicle")
                    );
                }
            },

            customer(frm) {
                populate_vehicles_on_customer(frm);
            },

            // Quotation uses party_name for the customer
            party_name(frm) {
                if (frm.doctype === "Quotation" && frm.doc.quotation_to === "Customer") {
                    populate_vehicles_on_customer(frm);
                }
            },

            custom_vehicle_plate(frm) {
                fetch_vehicle_details(frm);
            },
        });
    });
})();
