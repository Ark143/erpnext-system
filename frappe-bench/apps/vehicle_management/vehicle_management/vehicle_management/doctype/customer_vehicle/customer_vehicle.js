// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Vehicle", {
	refresh(frm) {
		if (!frm.is_new()) {
			// Quick Action Buttons
			frm.add_custom_button(__("New Estimate"), () => {
				frappe.new_doc("Vehicle Estimate", {
					vehicle: frm.doc.name,
					plate_no: frm.doc.plate_no,
					customer: frm.doc.customer,
					customer_name: frm.doc.customer_name,
					contact_no: frm.doc.contact_no,
					email: frm.doc.email,
					make: frm.doc.make,
					model: frm.doc.model,
					year_model: frm.doc.year_model,
					vin: frm.doc.vin,
					engine_no: frm.doc.engine_no,
					color: frm.doc.color,
					mileage: frm.doc.current_mileage || frm.doc.latest_odometer,
					mileage_unit: frm.doc.mileage_unit || "km"
				});
			}, __("Create")).addClass("btn-primary");

			frm.add_custom_button(__("New Job Order"), () => {
				frappe.new_doc("Vehicle Job Order", {
					vehicle: frm.doc.name,
					plate_no: frm.doc.plate_no,
					customer: frm.doc.customer,
					customer_name: frm.doc.customer_name,
					contact_no: frm.doc.contact_no,
					mileage: frm.doc.current_mileage || frm.doc.latest_odometer,
					mileage_unit: frm.doc.mileage_unit || "km"
				});
			}, __("Create"));

			frm.add_custom_button(__("New Inspection"), () => {
				frappe.new_doc("Vehicle Inspection", {
					vehicle: frm.doc.name,
					plate_no: frm.doc.plate_no,
					customer: frm.doc.customer,
					customer_name: frm.doc.customer_name,
					mileage: frm.doc.current_mileage || frm.doc.latest_odometer
				});
			}, __("Create"));

			frm.add_custom_button(__("Service Reminder"), () => {
				frappe.new_doc("Vehicle Service Reminder", {
					vehicle: frm.doc.name,
					plate_no: frm.doc.plate_no,
					customer: frm.doc.customer,
					customer_name: frm.doc.customer_name,
					contact_no: frm.doc.contact_no
				});
			}, __("Create"));

			// Dashboard Indicators
			frm.dashboard.add_indicator(
				__("Status: {0}", [frm.doc.status || "Active"]),
				frm.doc.status === "Active" ? "green" : (frm.doc.status === "In Service" ? "blue" : "gray")
			);

			if (frm.doc.total_spent > 0) {
				frm.dashboard.add_indicator(
					__("Lifetime Invoiced: {0}", [format_currency(frm.doc.total_spent)]),
					"blue"
				);
			}

			if (frm.doc.unpaid_balance > 0) {
				frm.dashboard.add_indicator(
					__("Unpaid: {0}", [format_currency(frm.doc.unpaid_balance)]),
					"orange"
				);
			}

			// Render Transaction History Log
			render_vehicle_transaction_history(frm);
		}
	}
});

function render_vehicle_transaction_history(frm) {
	const field = frm.get_field("transaction_history_html");
	if (!field || !field.$wrapper) return;

	field.$wrapper.html(`
		<div style="padding: 24px; text-align: center; color: var(--text-muted);">
			<i class="fa fa-spinner fa-spin fa-2x"></i>
			<div style="margin-top: 8px; font-weight: 500;">Loading Vehicle Transaction History...</div>
		</div>
	`);

	frappe.call({
		method: "vehicle_management.vehicle_management.doctype.customer_vehicle.customer_vehicle.get_vehicle_transaction_history",
		args: { vehicle: frm.doc.name },
		callback: (r) => {
			if (!r.message) {
				field.$wrapper.html(`<div class="alert alert-info">No transaction history found.</div>`);
				return;
			}

			const data = r.message;
			const summary = data.summary || {};
			const estimates = data.estimates || [];
			const job_orders = data.job_orders || [];
			const invoices = data.invoices || [];
			const inspections = data.inspections || [];
			const quotations = data.quotations || [];
			const sales_orders = data.sales_orders || [];
			const reminders = data.service_reminders || [];

			// Update form fields
			frm.set_value("total_spent", summary.total_spent || 0);
			frm.set_value("total_visits", summary.total_job_orders || 0);
			frm.set_value("unpaid_balance", summary.outstanding_balance || 0);
			frm.set_value("latest_odometer", summary.latest_mileage || 0);

			const total_count = estimates.length + job_orders.length + invoices.length + inspections.length + quotations.length + sales_orders.length + reminders.length;

			let html = `
			<div class="vehicle-history-container" style="font-family: var(--font-stack);">
				<!-- Filter Pills Navigation -->
				<div class="d-flex flex-wrap align-items-center justify-content-between mb-3 pb-2" style="border-bottom: 1px solid var(--border-color); gap: 8px;">
					<ul class="nav nav-pills" id="v_history_tabs" role="tablist" style="gap: 6px;">
						<li class="nav-item">
							<a class="nav-link active btn btn-sm btn-default" id="tab_all" data-toggle="pill" href="#pane_all" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								All Activity (${total_count})
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link btn btn-sm btn-default" id="tab_est" data-toggle="pill" href="#pane_est" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								Estimates (${estimates.length})
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link btn btn-sm btn-default" id="tab_jo" data-toggle="pill" href="#pane_jo" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								Job Orders (${job_orders.length})
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link btn btn-sm btn-default" id="tab_inv" data-toggle="pill" href="#pane_inv" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								Sales Invoices (${invoices.length})
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link btn btn-sm btn-default" id="tab_insp" data-toggle="pill" href="#pane_insp" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								Inspections (${inspections.length})
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link btn btn-sm btn-default" id="tab_sales" data-toggle="pill" href="#pane_sales" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								Quotes & Orders (${quotations.length + sales_orders.length})
							</a>
						</li>
						<li class="nav-item">
							<a class="nav-link btn btn-sm btn-default" id="tab_rem" data-toggle="pill" href="#pane_rem" role="tab" style="border-radius: 20px; font-weight: 600; padding: 5px 14px;">
								Reminders (${reminders.length})
							</a>
						</li>
					</ul>

					<button class="btn btn-xs btn-default btn-history-refresh" title="Reload History" style="border-radius: 12px; font-weight: 500;">
						<i class="fa fa-refresh"></i> Refresh Log
					</button>
				</div>

				<!-- Tab Contents -->
				<div class="tab-content" id="v_history_content" style="margin-top: 12px;">
					<!-- PANE 1: ALL ACTIVITY -->
					<div class="tab-pane fade show active" id="pane_all" role="tabpanel">
						${render_all_activity_timeline(estimates, job_orders, invoices, inspections, quotations, sales_orders, reminders)}
					</div>

					<!-- PANE 2: ESTIMATES -->
					<div class="tab-pane fade" id="pane_est" role="tabpanel">
						${render_estimates_table(estimates)}
					</div>

					<!-- PANE 3: JOB ORDERS -->
					<div class="tab-pane fade" id="pane_jo" role="tabpanel">
						${render_job_orders_table(job_orders)}
					</div>

					<!-- PANE 4: INVOICES -->
					<div class="tab-pane fade" id="pane_inv" role="tabpanel">
						${render_invoices_table(invoices)}
					</div>

					<!-- PANE 5: INSPECTIONS -->
					<div class="tab-pane fade" id="pane_insp" role="tabpanel">
						${render_inspections_table(inspections)}
					</div>

					<!-- PANE 6: QUOTES & SALES ORDERS -->
					<div class="tab-pane fade" id="pane_sales" role="tabpanel">
						${render_sales_table(quotations, sales_orders)}
					</div>

					<!-- PANE 7: REMINDERS -->
					<div class="tab-pane fade" id="pane_rem" role="tabpanel">
						${render_reminders_table(reminders)}
					</div>
				</div>
			</div>
			`;

			field.$wrapper.html(html);

			// Bind Tab Switching & Refresh Buttons
			field.$wrapper.find("#v_history_tabs a").on("click", function (e) {
				e.preventDefault();
				field.$wrapper.find("#v_history_tabs a").removeClass("active").removeClass("btn-primary").addClass("btn-default");
				$(this).addClass("active").addClass("btn-primary").removeClass("btn-default");
				const target = $(this).attr("href");
				field.$wrapper.find(".tab-pane").removeClass("show active").hide();
				field.$wrapper.find(target).addClass("show active").fadeIn(150);
			});

			field.$wrapper.find(".btn-history-refresh").on("click", () => {
				render_vehicle_transaction_history(frm);
			});
		}
	});
}

function get_badge(text, color_cls = "secondary") {
	const colors = {
		"Completed": "badge-success",
		"Released": "badge-success",
		"Paid": "badge-success",
		"Passed": "badge-success",
		"Approved": "badge-success",
		"Invoiced": "badge-primary",
		"Converted to Job Order": "badge-primary",
		"In Progress": "badge-info",
		"Sent": "badge-info",
		"Partially Paid": "badge-warning",
		"Pending Parts": "badge-warning",
		"Needs Attention": "badge-warning",
		"Draft": "badge-secondary",
		"Open": "badge-info",
		"Ordered": "badge-info",
		"Unpaid": "badge-danger",
		"Failed": "badge-danger",
		"Declined": "badge-danger",
		"Overdue": "badge-danger",
		"Expired": "badge-warning",
		"Cancelled": "badge-dark"
	};
	const cls = colors[text] || `badge-${color_cls}`;
	return `<span class="badge ${cls}" style="font-size: 11px; padding: 4px 8px; border-radius: 10px; font-weight: 600;">${text}</span>`;
}

function render_all_activity_timeline(estimates, job_orders, invoices, inspections, quotations, sales_orders, reminders) {
	const events = [];

	estimates.forEach(est => {
		events.push({
			date: est.estimate_date,
			type: "Estimate",
			icon: "fa fa-calculator text-primary",
			title: `Estimate: <a href="/desk/vehicle-estimate/${est.name}" style="font-weight: 700;">${est.name}</a>`,
			status: est.status,
			amount: est.grand_total,
			details: `Labor: ${format_currency(est.total_labor)} | Parts: ${format_currency(est.total_parts)} ${est.job_order ? `| Converted to ${est.job_order}` : ""}`,
			sub_badge: ""
		});
	});

	job_orders.forEach(jo => {
		events.push({
			date: jo.job_order_date,
			type: "Job Order",
			icon: "fa fa-wrench text-primary",
			title: `Job Order: <a href="/desk/vehicle-job-order/${jo.name}" style="font-weight: 700;">${jo.name}</a>`,
			status: jo.status,
			amount: jo.grand_total,
			details: `Labor: ${format_currency(jo.total_labor)} | Parts: ${format_currency(jo.total_parts)} | Odometer: ${jo.mileage || "N/A"} ${jo.mileage_unit || "km"}`,
			sub_badge: jo.payment_status ? get_badge(jo.payment_status) : ""
		});
	});

	invoices.forEach(inv => {
		events.push({
			date: inv.posting_date,
			type: "Sales Invoice",
			icon: "fa fa-file-text-o text-success",
			title: `Sales Invoice: <a href="/desk/sales-invoice/${inv.name}" style="font-weight: 700;">${inv.name}</a>`,
			status: inv.status,
			amount: inv.grand_total,
			details: `Outstanding: ${format_currency(inv.outstanding_amount)} ${inv.custom_vehicle_job_order ? `| Linked to ${inv.custom_vehicle_job_order}` : ""}`,
			sub_badge: ""
		});
	});

	inspections.forEach(insp => {
		events.push({
			date: insp.inspection_date,
			type: "Inspection",
			icon: "fa fa-check-square-o text-info",
			title: `Vehicle Inspection: <a href="/desk/vehicle-inspection/${insp.name}" style="font-weight: 700;">${insp.name}</a>`,
			status: insp.overall_status || "Completed",
			amount: null,
			details: `Template: ${insp.inspection_template || "General"} | Inspector: ${insp.mechanic || "N/A"} | Odometer: ${insp.mileage || "N/A"} km`,
			sub_badge: ""
		});
	});

	quotations.forEach(q => {
		events.push({
			date: q.transaction_date,
			type: "Quotation",
			icon: "fa fa-file-text text-warning",
			title: `Quotation: <a href="/desk/quotation/${q.name}" style="font-weight: 700;">${q.name}</a>`,
			status: q.status,
			amount: q.grand_total,
			details: `Valid Till: ${q.valid_till || "N/A"}`,
			sub_badge: ""
		});
	});

	events.sort((a, b) => new Date(b.date) - new Date(a.date));

	if (events.length === 0) {
		return `
		<div style="padding: 36px; text-align: center; background: var(--bg-light-gray); border-radius: 8px; border: 1px dashed var(--border-color);">
			<i class="fa fa-car fa-3x" style="color: var(--text-muted); opacity: 0.5;"></i>
			<h5 style="margin-top: 12px; font-weight: 600;">No transactions recorded yet</h5>
			<p class="text-muted" style="margin-bottom: 0;">Create an Estimate, Job Order, Inspection, or Invoice to start logging this vehicle's history.</p>
		</div>`;
	}

	let html = `<div class="timeline-activity" style="display: flex; flex-direction: column; gap: 10px;">`;
	events.forEach(ev => {
		html += `
		<div class="card p-3" style="border: 1px solid var(--border-color); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); background: var(--card-bg);">
			<div class="d-flex justify-content-between align-items-start">
				<div class="d-flex align-items-center" style="gap: 12px;">
					<div style="width: 36px; height: 36px; border-radius: 50%; background: var(--bg-light-gray); display: flex; align-items: center; justify-content: center; font-size: 16px;">
						<i class="${ev.icon}"></i>
					</div>
					<div>
						<div style="font-size: 14px;">${ev.title}</div>
						<div class="text-muted" style="font-size: 12px; margin-top: 2px;">
							<i class="fa fa-calendar-o"></i> ${frappe.datetime.str_to_user(ev.date)} &bull; ${ev.details}
						</div>
					</div>
				</div>
				<div class="text-right" style="white-space: nowrap;">
					${ev.amount !== null ? `<div style="font-size: 14px; font-weight: 700; color: var(--text-color); margin-bottom: 4px;">${format_currency(ev.amount)}</div>` : ""}
					<div style="display: flex; gap: 4px; justify-content: flex-end;">
						${get_badge(ev.status)}
						${ev.sub_badge}
					</div>
				</div>
			</div>
		</div>`;
	});
	html += `</div>`;
	return html;
}

function render_estimates_table(estimates) {
	if (!estimates || estimates.length === 0) {
		return `<div class="p-4 text-center text-muted">No Estimates created for this vehicle.</div>`;
	}
	let html = `
	<div class="table-responsive">
		<table class="table table-bordered table-hover" style="font-size: 13px;">
			<thead class="thead-light">
				<tr>
					<th>Estimate #</th>
					<th>Date</th>
					<th>Valid Till</th>
					<th>Labor</th>
					<th>Parts</th>
					<th class="text-right">Estimated Total</th>
					<th class="text-center">Converted JO</th>
					<th class="text-center">Status</th>
				</tr>
			</thead>
			<tbody>`;
	estimates.forEach(est => {
		html += `
				<tr>
					<td><a href="/desk/vehicle-estimate/${est.name}" style="font-weight: 700;">${est.name}</a></td>
					<td>${frappe.datetime.str_to_user(est.estimate_date)}</td>
					<td>${est.valid_till ? frappe.datetime.str_to_user(est.valid_till) : "-"}</td>
					<td>${format_currency(est.total_labor)}</td>
					<td>${format_currency(est.total_parts)}</td>
					<td class="text-right" style="font-weight: 700;">${format_currency(est.grand_total)}</td>
					<td class="text-center">${est.job_order ? `<a href="/desk/vehicle-job-order/${est.job_order}">${est.job_order}</a>` : "-"}</td>
					<td class="text-center">${get_badge(est.status)}</td>
				</tr>`;
	});
	html += `</tbody></table></div>`;
	return html;
}

function render_job_orders_table(job_orders) {
	if (!job_orders || job_orders.length === 0) {
		return `<div class="p-4 text-center text-muted">No Job Orders found for this vehicle.</div>`;
	}
	let html = `
	<div class="table-responsive">
		<table class="table table-bordered table-hover" style="font-size: 13px;">
			<thead class="thead-light">
				<tr>
					<th>Job Order</th>
					<th>Date</th>
					<th>Odometer</th>
					<th>Services & Labor</th>
					<th>Parts / Materials</th>
					<th class="text-right">Grand Total</th>
					<th class="text-center">Status</th>
					<th class="text-center">Payment</th>
				</tr>
			</thead>
			<tbody>`;
	job_orders.forEach(jo => {
		const s_count = jo.services_list ? jo.services_list.length : 0;
		const p_count = jo.parts_list ? jo.parts_list.length : 0;
		html += `
				<tr>
					<td><a href="/desk/vehicle-job-order/${jo.name}" style="font-weight: 700;">${jo.name}</a></td>
					<td>${frappe.datetime.str_to_user(jo.job_order_date)}</td>
					<td>${jo.mileage ? `${jo.mileage} ${jo.mileage_unit || "km"}` : "-"}</td>
					<td>
						<strong>${format_currency(jo.total_labor)}</strong>
						<div class="text-muted" style="font-size: 11px;">${s_count} service item(s)</div>
					</td>
					<td>
						<strong>${format_currency(jo.total_parts)}</strong>
						<div class="text-muted" style="font-size: 11px;">${p_count} part(s)</div>
					</td>
					<td class="text-right" style="font-weight: 700;">${format_currency(jo.grand_total)}</td>
					<td class="text-center">${get_badge(jo.status)}</td>
					<td class="text-center">${jo.payment_status ? get_badge(jo.payment_status) : "-"}</td>
				</tr>`;
	});
	html += `</tbody></table></div>`;
	return html;
}

function render_invoices_table(invoices) {
	if (!invoices || invoices.length === 0) {
		return `<div class="p-4 text-center text-muted">No Sales Invoices found for this vehicle.</div>`;
	}
	let html = `
	<div class="table-responsive">
		<table class="table table-bordered table-hover" style="font-size: 13px;">
			<thead class="thead-light">
				<tr>
					<th>Invoice #</th>
					<th>Posting Date</th>
					<th>Linked Job Order</th>
					<th class="text-right">Grand Total</th>
					<th class="text-right">Outstanding</th>
					<th class="text-center">Status</th>
				</tr>
			</thead>
			<tbody>`;
	invoices.forEach(inv => {
		html += `
				<tr>
					<td><a href="/desk/sales-invoice/${inv.name}" style="font-weight: 700;">${inv.name}</a></td>
					<td>${frappe.datetime.str_to_user(inv.posting_date)}</td>
					<td>${inv.custom_vehicle_job_order ? `<a href="/desk/vehicle-job-order/${inv.custom_vehicle_job_order}">${inv.custom_vehicle_job_order}</a>` : "-"}</td>
					<td class="text-right" style="font-weight: 700;">${format_currency(inv.grand_total)}</td>
					<td class="text-right ${inv.outstanding_amount > 0 ? "text-danger font-weight-bold" : "text-muted"}">${format_currency(inv.outstanding_amount)}</td>
					<td class="text-center">${get_badge(inv.status)}</td>
				</tr>`;
	});
	html += `</tbody></table></div>`;
	return html;
}

function render_inspections_table(inspections) {
	if (!inspections || inspections.length === 0) {
		return `<div class="p-4 text-center text-muted">No Inspections recorded for this vehicle.</div>`;
	}
	let html = `
	<div class="table-responsive">
		<table class="table table-bordered table-hover" style="font-size: 13px;">
			<thead class="thead-light">
				<tr>
					<th>Inspection #</th>
					<th>Date</th>
					<th>Template</th>
					<th>Inspector / Mechanic</th>
					<th>Odometer</th>
					<th class="text-center">Result</th>
				</tr>
			</thead>
			<tbody>`;
	inspections.forEach(insp => {
		html += `
				<tr>
					<td><a href="/desk/vehicle-inspection/${insp.name}" style="font-weight: 700;">${insp.name}</a></td>
					<td>${frappe.datetime.str_to_user(insp.inspection_date)}</td>
					<td>${insp.inspection_template || "Standard"}</td>
					<td>${insp.mechanic || "-"}</td>
					<td>${insp.mileage ? `${insp.mileage} km` : "-"}</td>
					<td class="text-center">${get_badge(insp.overall_status || "Completed")}</td>
				</tr>`;
	});
	html += `</tbody></table></div>`;
	return html;
}

function render_sales_table(quotations, sales_orders) {
	const all = [];
	quotations.forEach(q => all.push({ doctype: "Quotation", name: q.name, date: q.transaction_date, amount: q.grand_total, status: q.status, jo: q.custom_vehicle_job_order }));
	sales_orders.forEach(so => all.push({ doctype: "Sales Order", name: so.name, date: so.transaction_date, amount: so.grand_total, status: so.status, jo: so.custom_vehicle_job_order }));
	all.sort((a, b) => new Date(b.date) - new Date(a.date));

	if (all.length === 0) {
		return `<div class="p-4 text-center text-muted">No Quotations or Sales Orders found for this vehicle.</div>`;
	}
	let html = `
	<div class="table-responsive">
		<table class="table table-bordered table-hover" style="font-size: 13px;">
			<thead class="thead-light">
				<tr>
					<th>Type</th>
					<th>Voucher #</th>
					<th>Date</th>
					<th>Linked Job Order</th>
					<th class="text-right">Grand Total</th>
					<th class="text-center">Status</th>
				</tr>
			</thead>
			<tbody>`;
	all.forEach(row => {
		const route = row.doctype === "Quotation" ? "quotation" : "sales-order";
		html += `
				<tr>
					<td><span class="badge badge-light">${row.doctype}</span></td>
					<td><a href="/desk/${route}/${row.name}" style="font-weight: 700;">${row.name}</a></td>
					<td>${frappe.datetime.str_to_user(row.date)}</td>
					<td>${row.jo ? `<a href="/desk/vehicle-job-order/${row.jo}">${row.jo}</a>` : "-"}</td>
					<td class="text-right" style="font-weight: 700;">${format_currency(row.amount)}</td>
					<td class="text-center">${get_badge(row.status)}</td>
				</tr>`;
	});
	html += `</tbody></table></div>`;
	return html;
}

function render_reminders_table(reminders) {
	if (!reminders || reminders.length === 0) {
		return `<div class="p-4 text-center text-muted">No Service Reminders scheduled for this vehicle.</div>`;
	}
	let html = `
	<div class="table-responsive">
		<table class="table table-bordered table-hover" style="font-size: 13px;">
			<thead class="thead-light">
				<tr>
					<th>Reminder #</th>
					<th>Service Type</th>
					<th>Due Date</th>
					<th>Due Mileage</th>
					<th>Message</th>
					<th class="text-center">Status</th>
				</tr>
			</thead>
			<tbody>`;
	reminders.forEach(rem => {
		html += `
				<tr>
					<td><a href="/desk/vehicle-service-reminder/${rem.name}" style="font-weight: 700;">${rem.name}</a></td>
					<td><strong>${rem.service_type || "General Service"}</strong></td>
					<td>${rem.due_date ? frappe.datetime.str_to_user(rem.due_date) : "-"}</td>
					<td>${rem.due_mileage ? `${rem.due_mileage} km` : "-"}</td>
					<td><span class="text-muted">${rem.reminder_message || "-"}</span></td>
					<td class="text-center">${get_badge(rem.status || "Pending")}</td>
				</tr>`;
	});
	html += `</tbody></table></div>`;
	return html;
}
