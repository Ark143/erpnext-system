frappe.pages["vehicle_analytics"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Vehicle Management Analytics"),
		single_column: true
	});

	page.company_field = page.add_field({
		fieldname: "company",
		label: __("Company / Branch"),
		fieldtype: "Select",
		options: [
			"All Companies",
			"Ultra MRF Dau Main",
			"Ultra MRF Dau Annex",
			"Ultra MRF San Fernando",
			"Wheel Core",
			"Ultra MRF Telebastagan",
			"Automan Car Care Center",
			"The Wheelhub",
			"ULTRA MRF",
			"Ultra MRF Warehouse Dau",
			"San Fernando Warehouse",
			"Ultra MRF Mexico Warehouse"
		],
		default: "All Companies",
		change: () => render_analytics_dashboard(page)
	});

	page.timespan_field = page.add_field({
		fieldname: "timespan",
		label: __("Timespan"),
		fieldtype: "Select",
		options: ["Last 30 Days", "This Year", "All Time"],
		default: "Last 30 Days",
		change: () => render_analytics_dashboard(page)
	});

	page.add_inner_button(__("Refresh Data"), () => {
		render_analytics_dashboard(page);
	});

	// Initial render
	render_analytics_dashboard(page);
};

function render_analytics_dashboard(page) {
	const company = page.company_field ? page.company_field.get_value() : "All Companies";
	const timespan = page.timespan_field ? page.timespan_field.get_value() : "Last 30 Days";

	if (!page.dashboard_body) {
		page.dashboard_body = $('<div class="dashboard-body"></div>').appendTo(page.main);
	}

	page.dashboard_body.html(`
		<div style="padding: 40px; text-align: center; color: var(--text-muted);">
			<i class="fa fa-spinner fa-spin fa-2x"></i>
			<div style="margin-top: 10px; font-weight: 600;">Loading Performance Analytics...</div>
		</div>
	`);

	frappe.call({
		method: "vehicle_management.vehicle_management.analytics.get_vehicle_management_analytics",
		args: {
			company: company,
			timespan: timespan
		},
		callback: (r) => {
			if (!r.message) {
				page.dashboard_body.html(`<div class="alert alert-warning">No data available for the selected filters.</div>`);
				return;
			}

			const data = r.message;
			const summary = data.summary || {};
			const top_services = data.top_services || [];
			const top_parts = data.top_parts || [];
			const top_tires_mags = data.top_tires_mags || [];
			const company_perf = data.company_performance || [];

			let html = `
			<div class="analytics-dashboard-container" style="padding: 10px 0; font-family: var(--font-stack);">
				<!-- 1. Top Executive KPI Cards -->
				<div class="row" style="margin-bottom: 20px;">
					<div class="col-sm-6 col-md-3 mb-3">
						<div class="card p-3" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
							<div class="d-flex justify-content-between align-items-center">
								<div>
									<div class="text-muted" style="font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Total Revenue</div>
									<div style="font-size: 20px; font-weight: 800; color: #1a56db; margin-top: 4px;">${format_currency(summary.total_revenue)}</div>
								</div>
								<div style="width: 42px; height: 42px; border-radius: 50%; background: #e1effe; display: flex; align-items: center; justify-content: center; color: #1a56db; font-size: 18px;">
									<i class="fa fa-money"></i>
								</div>
							</div>
							<div class="text-muted" style="font-size: 11px; margin-top: 6px;">Avg. Ticket: <strong>${format_currency(summary.avg_ticket)}</strong></div>
						</div>
					</div>

					<div class="col-sm-6 col-md-3 mb-3">
						<div class="card p-3" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
							<div class="d-flex justify-content-between align-items-center">
								<div>
									<div class="text-muted" style="font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Labor Sales</div>
									<div style="font-size: 20px; font-weight: 800; color: #046c4e; margin-top: 4px;">${format_currency(summary.total_labor)}</div>
								</div>
								<div style="width: 42px; height: 42px; border-radius: 50%; background: #def7ec; display: flex; align-items: center; justify-content: center; color: #046c4e; font-size: 18px;">
									<i class="fa fa-wrench"></i>
								</div>
							</div>
							<div class="text-muted" style="font-size: 11px; margin-top: 6px;">Services Performed: <strong>${top_services.length} types</strong></div>
						</div>
					</div>

					<div class="col-sm-6 col-md-3 mb-3">
						<div class="card p-3" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
							<div class="d-flex justify-content-between align-items-center">
								<div>
									<div class="text-muted" style="font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Parts & Tires Sales</div>
									<div style="font-size: 20px; font-weight: 800; color: #7e3af2; margin-top: 4px;">${format_currency(summary.total_parts)}</div>
								</div>
								<div style="width: 42px; height: 42px; border-radius: 50%; background: #edebfe; display: flex; align-items: center; justify-content: center; color: #7e3af2; font-size: 18px;">
									<i class="fa fa-cubes"></i>
								</div>
							</div>
							<div class="text-muted" style="font-size: 11px; margin-top: 6px;">Tires & Mags: <strong>${top_tires_mags.length} models</strong></div>
						</div>
					</div>

					<div class="col-sm-6 col-md-3 mb-3">
						<div class="card p-3" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
							<div class="d-flex justify-content-between align-items-center">
								<div>
									<div class="text-muted" style="font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Job Orders & Fleet</div>
									<div style="font-size: 20px; font-weight: 800; color: #c27803; margin-top: 4px;">${summary.total_jos} Orders</div>
								</div>
								<div style="width: 42px; height: 42px; border-radius: 50%; background: #fef08a; display: flex; align-items: center; justify-content: center; color: #c27803; font-size: 18px;">
									<i class="fa fa-car"></i>
								</div>
							</div>
							<div class="text-muted" style="font-size: 11px; margin-top: 6px;">Unique Vehicles: <strong>${summary.unique_vehicles}</strong></div>
						</div>
					</div>
				</div>

				<!-- 2. Charts Row -->
				<div class="row mb-4">
					<div class="col-md-6 mb-3">
						<div class="card p-3" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg);">
							<div style="font-weight: 700; font-size: 14px; margin-bottom: 12px;">
								<i class="fa fa-bar-chart text-primary"></i> Total Revenue by Company / Branch
							</div>
							<div id="chart_company_revenue" style="min-height: 240px;"></div>
						</div>
					</div>
					<div class="col-md-6 mb-3">
						<div class="card p-3" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg);">
							<div style="font-weight: 700; font-size: 14px; margin-bottom: 12px;">
								<i class="fa fa-pie-chart text-success"></i> Sales Split: Labor vs. Parts & Tires
							</div>
							<div id="chart_sales_split" style="min-height: 240px;"></div>
						</div>
					</div>
				</div>

				<!-- 3. Tables Row 1: Top Services & Top Tires/Mags -->
				<div class="row mb-4">
					<!-- Top Services -->
					<div class="col-lg-6 mb-3">
						<div class="card" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); overflow: hidden;">
							<div class="card-header bg-light d-flex justify-content-between align-items-center" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color);">
								<div style="font-weight: 700; font-size: 14px; color: var(--text-color);">
									<i class="fa fa-wrench text-success mr-1"></i> Top Selling Services & Labor
								</div>
								<span class="badge badge-success" style="border-radius: 10px;">Top ${top_services.length}</span>
							</div>
							<div class="table-responsive">
								<table class="table table-hover mb-0" style="font-size: 13px;">
									<thead class="thead-light">
										<tr>
											<th style="width: 8%; text-align: center;">#</th>
											<th style="width: 52%;">Service Description</th>
											<th style="width: 15%; text-align: center;">Times</th>
											<th style="width: 25%; text-align: right;">Total Sales</th>
										</tr>
									</thead>
									<tbody>
										${render_top_services_rows(top_services)}
									</tbody>
								</table>
							</div>
						</div>
					</div>

					<!-- Top Tires & Mags -->
					<div class="col-lg-6 mb-3">
						<div class="card" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); overflow: hidden;">
							<div class="card-header bg-light d-flex justify-content-between align-items-center" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color);">
								<div style="font-weight: 700; font-size: 14px; color: var(--text-color);">
									<i class="fa fa-circle-o-notch text-primary mr-1"></i> Top Selling Tires & Mags / Wheels
								</div>
								<span class="badge badge-primary" style="border-radius: 10px;">Top ${top_tires_mags.length}</span>
							</div>
							<div class="table-responsive">
								<table class="table table-hover mb-0" style="font-size: 13px;">
									<thead class="thead-light">
										<tr>
											<th style="width: 8%; text-align: center;">#</th>
											<th style="width: 52%;">Tire / Mags Specification</th>
											<th style="width: 15%; text-align: center;">Qty</th>
											<th style="width: 25%; text-align: right;">Total Sales</th>
										</tr>
									</thead>
									<tbody>
										${render_top_tires_rows(top_tires_mags)}
									</tbody>
								</table>
							</div>
						</div>
					</div>
				</div>

				<!-- 4. Tables Row 2: Company Performance Breakdown & General Parts -->
				<div class="row">
					<!-- Company Performance -->
					<div class="col-lg-7 mb-3">
						<div class="card" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); overflow: hidden;">
							<div class="card-header bg-light d-flex justify-content-between align-items-center" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color);">
								<div style="font-weight: 700; font-size: 14px; color: var(--text-color);">
									<i class="fa fa-building-o text-info mr-1"></i> Branch & Company Performance
								</div>
								<span class="badge badge-info" style="border-radius: 10px;">${company_perf.length} Branches</span>
							</div>
							<div class="table-responsive">
								<table class="table table-bordered table-hover mb-0" style="font-size: 13px;">
									<thead class="thead-light">
										<tr>
											<th>Branch / Company</th>
											<th class="text-center">JOs</th>
											<th class="text-right">Labor (PHP)</th>
											<th class="text-right">Parts (PHP)</th>
											<th class="text-right">Total Revenue</th>
										</tr>
									</thead>
									<tbody>
										${render_company_perf_rows(company_perf)}
									</tbody>
								</table>
							</div>
						</div>
					</div>

					<!-- Top General Parts -->
					<div class="col-lg-5 mb-3">
						<div class="card" style="border-radius: 10px; border: 1px solid var(--border-color); background: var(--card-bg); overflow: hidden;">
							<div class="card-header bg-light d-flex justify-content-between align-items-center" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color);">
								<div style="font-weight: 700; font-size: 14px; color: var(--text-color);">
									<i class="fa fa-cube text-warning mr-1"></i> Top Parts & Consumables
								</div>
								<span class="badge badge-warning" style="border-radius: 10px;">Top ${top_parts.length}</span>
							</div>
							<div class="table-responsive">
								<table class="table table-hover mb-0" style="font-size: 13px;">
									<thead class="thead-light">
										<tr>
											<th>Part Description</th>
											<th class="text-center">Qty</th>
											<th class="text-right">Total Sales</th>
										</tr>
									</thead>
									<tbody>
										${render_top_parts_rows(top_parts)}
									</tbody>
								</table>
							</div>
						</div>
					</div>
				</div>
			</div>
			`;

			page.dashboard_body.html(html);

			// Render Interactive Charts
			render_frappe_charts(company_perf, summary);
		}
	});
}

function render_top_services_rows(services) {
	if (!services || services.length === 0) {
		return `<tr><td colspan="4" class="text-center text-muted p-3">No service transactions found.</td></tr>`;
	}
	let html = "";
	services.forEach((s, idx) => {
		const rank_badge = idx === 0 ? "badge-warning" : (idx === 1 ? "badge-secondary" : (idx === 2 ? "badge-light" : "badge-light"));
		html += `
		<tr>
			<td class="text-center"><span class="badge ${rank_badge}" style="border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center;">${idx + 1}</span></td>
			<td>
				<div style="font-weight: 600; color: var(--text-color);">${s.service_name}</div>
				<div class="text-muted" style="font-size: 11px;">Total Work: ${s.total_hours.toFixed(1)} hrs</div>
			</td>
			<td class="text-center"><span class="badge badge-info" style="border-radius: 10px; font-weight: 600;">${s.count}x</span></td>
			<td class="text-right" style="font-weight: 700; color: #046c4e;">${format_currency(s.total_amount)}</td>
		</tr>`;
	});
	return html;
}

function render_top_tires_rows(tires) {
	if (!tires || tires.length === 0) {
		return `<tr><td colspan="4" class="text-center text-muted p-3">No tire or mags transactions recorded.</td></tr>`;
	}
	let html = "";
	tires.forEach((t, idx) => {
		const cat_badge = t.category === "Mags / Wheels" ? "badge-primary" : "badge-success";
		html += `
		<tr>
			<td class="text-center"><span class="badge badge-light" style="border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center;">${idx + 1}</span></td>
			<td>
				<div style="font-weight: 600; color: var(--text-color);">${t.item_name}</div>
				<div style="font-size: 11px; margin-top: 2px;">
					<span class="badge ${cat_badge}" style="font-size: 10px; padding: 2px 6px; border-radius: 8px;">${t.category}</span>
				</div>
			</td>
			<td class="text-center"><strong>${t.total_qty}</strong> <span class="text-muted" style="font-size: 11px;">${t.uom}</span></td>
			<td class="text-right" style="font-weight: 700; color: #1a56db;">${format_currency(t.total_amount)}</td>
		</tr>`;
	});
	return html;
}

function render_company_perf_rows(companies) {
	if (!companies || companies.length === 0) {
		return `<tr><td colspan="5" class="text-center text-muted p-3">No branch data available.</td></tr>`;
	}
	let html = "";
	companies.forEach(c => {
		html += `
		<tr>
			<td><strong style="color: var(--text-color);">${c.company}</strong></td>
			<td class="text-center"><span class="badge badge-secondary" style="border-radius: 10px; font-weight: 600;">${c.total_jos}</span></td>
			<td class="text-right">${format_currency(c.total_labor)}</td>
			<td class="text-right">${format_currency(c.total_parts)}</td>
			<td class="text-right" style="font-weight: 800; color: #1a56db;">${format_currency(c.total_revenue)}</td>
		</tr>`;
	});
	return html;
}

function render_top_parts_rows(parts) {
	if (!parts || parts.length === 0) {
		return `<tr><td colspan="3" class="text-center text-muted p-3">No parts sold.</td></tr>`;
	}
	let html = "";
	parts.slice(0, 7).forEach(p => {
		html += `
		<tr>
			<td>
				<div style="font-weight: 600; color: var(--text-color);">${p.item_name}</div>
			</td>
			<td class="text-center"><strong>${p.total_qty}</strong> ${p.uom}</td>
			<td class="text-right" style="font-weight: 700; color: #7e3af2;">${format_currency(p.total_amount)}</td>
		</tr>`;
	});
	return html;
}

function render_frappe_charts(company_perf, summary) {
	if (!company_perf || company_perf.length === 0) return;

	// Chart 1: Revenue by Branch
	const labels = company_perf.map(c => c.company.replace("Ultra MRF ", ""));
	const revenues = company_perf.map(c => c.total_revenue);

	new frappe.Chart("#chart_company_revenue", {
		data: {
			labels: labels,
			datasets: [
				{
					name: "Total Revenue",
					values: revenues
				}
			]
		},
		title: "",
		type: "bar",
		height: 220,
		colors: ["#1a56db"],
		tooltipOptions: {
			formatTooltipY: (d) => format_currency(d)
		}
	});

	// Chart 2: Labor vs Parts Split
	new frappe.Chart("#chart_sales_split", {
		data: {
			labels: ["Labor & Services", "Parts, Tires & Mags"],
			datasets: [
				{
					values: [summary.total_labor || 0, summary.total_parts || 0]
				}
			]
		},
		title: "",
		type: "donut",
		height: 220,
		colors: ["#046c4e", "#7e3af2"],
		tooltipOptions: {
			formatTooltipY: (d) => format_currency(d)
		}
	});
}
