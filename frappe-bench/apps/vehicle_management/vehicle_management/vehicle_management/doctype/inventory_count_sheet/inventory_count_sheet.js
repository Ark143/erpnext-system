// Copyright (c) 2026, Autometrik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inventory Count Sheet", {

	// ─── FORM SETUP ────────────────────────────────────────────────────────────

	setup(frm) {
		// Colour-code the count_status indicator column in the child grid
		if (frm.fields_dict["items"] && frm.fields_dict["items"].grid) {
			frm.fields_dict["items"].grid.get_field("count_status").df.formatter =
				function (value) {
					const colours = {
						"Matched":  "green",
						"Over":     "blue",
						"Short":    "red",
						"Pending":  "orange",
						"New Item": "purple",
					};
					const c = colours[value] || "gray";
					return `<span class="indicator-pill ${c}">${value || "—"}</span>`;
				};
		}
	},

	onload(frm) {
		_add_custom_buttons(frm);

		if (frm.doc.docstatus === 1) {
			frm.set_df_property("items", "read_only", 1);
		}
	},

	refresh(frm) {
		_add_custom_buttons(frm);
		_render_kpi_banner(frm);
		_apply_row_colours(frm);

		if (frm.doc.docstatus === 0) {
			_inject_scan_bar(frm);
		}
	},

	// ─── FIELD TRIGGERS ────────────────────────────────────────────────────────

	warehouse(frm) {
		if (frm.doc.warehouse && (!frm.doc.items || frm.doc.items.length === 0)) {
			// Offer to load items from selected warehouse
			_load_warehouse_items(frm, [frm.doc.warehouse]);
		}
	},

	count_type(frm) {
		if (frm.doc.count_type === "Cycle Count (Spot Check)" && frm.doc.bin_filter && (!frm.doc.items || frm.doc.items.length === 0)) {
			_show_get_items_dialog(frm);
		}
	},
});

frappe.ui.form.on("Inventory Count Sheet Item", {
	physical_qty(frm, cdt, cdn) {
		_recalculate_row(frm, cdt, cdn);
	},

	system_qty(frm, cdt, cdn) {
		_recalculate_row(frm, cdt, cdn);
	},

	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const wh = row.warehouse || frm.doc.warehouse;
		if (!row.item_code || !wh) return;

		// Fetch live system qty from Bin table
		frappe.call({
			method: "vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_stock_qty",
			args: { item_code: row.item_code, warehouse: wh },
			callback(r) {
				if (r.message !== undefined) {
					frappe.model.set_value(cdt, cdn, "system_qty", r.message);
					_recalculate_row(frm, cdt, cdn);
				}
			},
		});
	},
});


// ─── PRIVATE HELPERS ───────────────────────────────────────────────────────────

function _recalculate_row(frm, cdt, cdn) {
	const row      = locals[cdt][cdn];
	const physical = parseFloat(row.physical_qty);
	const system   = parseFloat(row.system_qty) || 0;

	if (isNaN(physical)) {
		frappe.model.set_value(cdt, cdn, "count_status", "Pending");
		frappe.model.set_value(cdt, cdn, "variance_qty", 0);
		return;
	}

	const variance = physical - system;
	frappe.model.set_value(cdt, cdn, "variance_qty", variance);

	let status = "Matched";
	if (system === 0 && physical > 0) {
		status = "New Item";
	} else if (variance > 0) {
		status = "Over";
	} else if (variance < 0) {
		status = "Short";
	}

	frappe.model.set_value(cdt, cdn, "count_status", status);
	_apply_row_colours(frm);
	_update_kpi_banner(frm);
}

function _add_custom_buttons(frm) {
	frm.clear_custom_buttons();

	if (frm.doc.docstatus === 0) {
		// Prominent Primary button directly on the form header
		frm.add_custom_button(__("Get Items from Warehouse"), () => {
			_show_get_items_dialog(frm);
		}).addClass("btn-primary");

		frm.add_custom_button(__("Clear All Counts"), () => {
			frappe.confirm(__("This will clear all physical count entries. Are you sure?"), () => {
				(frm.doc.items || []).forEach(row => {
					frappe.model.set_value(row.doctype, row.name, "physical_qty", null);
					frappe.model.set_value(row.doctype, row.name, "variance_qty", 0);
					frappe.model.set_value(row.doctype, row.name, "count_status", "Pending");
				});
				frm.refresh_field("items");
				_render_kpi_banner(frm);
				frappe.show_alert({ message: __("All physical counts cleared."), indicator: "orange" });
			});
		}, __("Actions"));
	}

	frm.add_custom_button(__("Export to CSV"), () => _export_csv(frm), __("Actions"));
	frm.add_custom_button(__("Print Count Sheet"), () => frappe.utils.print(
		frm.doctype, frm.docname, null, frm.doc.language
	), __("Actions"));
}

function _show_get_items_dialog(frm) {
	const default_company = frm.doc.company || frappe.defaults.get_default("Company") || "ULTRA MRF";
	
	const d = new frappe.ui.Dialog({
		title: __("Get Items from Warehouse(s)"),
		fields: [
			{
				label: __("Company"),
				fieldname: "company",
				fieldtype: "Link",
				options: "Company",
				default: default_company,
				reqd: 1,
				onchange: function() {
					_reload_warehouse_options(d);
				}
			},
			{
				fieldtype: "Section Break",
				label: __("Warehouse Selection")
			},
			{
				label: __("Select All Warehouses in Company"),
				fieldname: "select_all_warehouses",
				fieldtype: "Check",
				default: 0,
				onchange: function() {
					const all = d.get_value("select_all_warehouses");
					d.set_df_property("warehouse", "hidden", all);
					d.set_df_property("multi_warehouses", "hidden", all);
				}
			},
			{
				label: __("Primary / Group Warehouse"),
				fieldname: "warehouse",
				fieldtype: "Link",
				options: "Warehouse",
				default: frm.doc.warehouse,
				description: __("Select a specific warehouse or a Parent Group Warehouse (e.g. All Warehouses - UM) to include all child stores."),
				get_query: function() {
					return {
						filters: {
							company: d.get_value("company") || default_company
						}
					};
				}
			},
			{
				fieldtype: "Section Break",
				label: __("Filters")
			},
			{
				label: __("Item Group"),
				fieldname: "item_group",
				fieldtype: "Link",
				options: "Item Group"
			},
			{
				label: __("Bin / Location Filter"),
				fieldname: "bin_filter",
				fieldtype: "Data",
				default: frm.doc.bin_filter
			},
			{
				label: __("Ignore Zero Stock (Only Count In-Stock Items)"),
				fieldname: "ignore_empty_stock",
				fieldtype: "Check",
				default: 1
			}
		],
		primary_action_label: __("Fetch Stock Items"),
		primary_action: function(values) {
			d.hide();
			_fetch_items_from_server(frm, values);
		}
	});

	d.show();
}

function _reload_warehouse_options(dialog) {
	// Utility hook when company changes
}

function _fetch_items_from_server(frm, values) {
	frappe.show_progress(__("Fetching items…"), 20, 100);

	frappe.call({
		method: "vehicle_management.vehicle_management.doctype.inventory_count_sheet.inventory_count_sheet.get_warehouse_items",
		args: {
			company: values.company,
			warehouse: values.warehouse || null,
			select_all: values.select_all_warehouses ? 1 : 0,
			item_group: values.item_group || null,
			bin_filter: values.bin_filter || null,
			ignore_empty_stock: values.ignore_empty_stock ? 1 : 0,
		},
		callback(r) {
			frappe.hide_progress();
			const items = r.message || [];
			if (!items.length) {
				frappe.msgprint(__("No stock items found for the selected warehouse criteria."));
				return;
			}

			const existing = (frm.doc.items || []).length;
			const applyItems = () => {
				frm.clear_table("items");
				items.forEach(item => {
					const row = frm.add_child("items");
					row.item_code    = item.item_code;
					row.item_name    = item.item_name;
					row.warehouse    = item.warehouse;
					row.uom          = item.uom;
					row.item_group   = item.item_group;
					row.bin_location = item.bin_location || "";
					row.system_qty   = item.system_qty;
					row.physical_qty = null;
					row.variance_qty = 0;
					row.count_status = "Pending";
				});

				if (values.warehouse) {
					frm.set_value("warehouse", values.warehouse);
				}
				if (values.company) {
					frm.set_value("company", values.company);
				}

				frm.refresh_field("items");
				_apply_row_colours(frm);
				_render_kpi_banner(frm);
				frappe.show_alert({
					message: __("Loaded {0} items into count sheet.", [items.length]),
					indicator: "green"
				});
			};

			if (existing > 0) {
				frappe.confirm(
					__("This will replace the existing {0} count lines. Continue?", [existing]),
					applyItems
				);
			} else {
				applyItems();
			}
		}
	});
}

function _load_warehouse_items(frm, warehouses) {
	_fetch_items_from_server(frm, {
		company: frm.doc.company || "ULTRA MRF",
		warehouse: warehouses && warehouses.length ? warehouses[0] : frm.doc.warehouse,
		select_all_warehouses: 0,
		ignore_empty_stock: 1
	});
}

// ─── KPI BANNER ───────────────────────────────────────────────────────────────

function _render_kpi_banner(frm) {
	frm.layout.wrapper.find(".ic-kpi-banner").remove();

	const stats = _compute_stats(frm);

	const banner = $(`
		<div class="ic-kpi-banner" style="
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
			gap: 10px;
			margin: 12px 0 16px 0;
		">
			${_kpi_card("Total SKUs",   stats.total,    "#6366f1")}
			${_kpi_card("Counted",      stats.counted,  "#22c55e")}
			${_kpi_card("Uncounted",    stats.uncounted,"#f59e0b")}
			${_kpi_card("Variances",    stats.variance, "#ef4444")}
			${_kpi_card("Matched",      stats.matched,  "#3b82f6")}
			${_kpi_card("Accuracy",     stats.accuracy, "#8b5cf6")}
		</div>
	`);

	const insertTarget = frm.layout.wrapper.find(".form-page > .frappe-card, .layout-main-section").first();
	if (insertTarget.length) {
		banner.prependTo(insertTarget);
	}
}

function _kpi_card(label, value, colour) {
	return `
		<div style="
			background: var(--card-bg, #fff);
			border: 1px solid var(--border-color, #e5e7eb);
			border-top: 3px solid ${colour};
			border-radius: 8px;
			padding: 12px 14px;
			text-align: center;
		">
			<div style="font-size: 10px; color: var(--text-muted); text-transform: uppercase;
				letter-spacing: 0.07em; font-family: monospace; margin-bottom: 6px;">${label}</div>
			<div style="font-size: 22px; font-weight: 700; color: ${colour}; font-family: monospace;">${value}</div>
		</div>
	`;
}

function _update_kpi_banner(frm) {
	_render_kpi_banner(frm);
}

function _compute_stats(frm) {
	const items    = frm.doc.items || [];
	const total    = items.length;
	const counted  = items.filter(r => r.count_status !== "Pending").length;
	const matched  = items.filter(r => r.count_status === "Matched").length;
	const variance = items.filter(r => ["Over","Short","New Item"].includes(r.count_status)).length;
	const uncounted = total - counted;
	const accuracy = counted > 0 ? Math.round((matched / counted) * 100) + "%" : "—";
	return { total, counted, uncounted, matched, variance, accuracy };
}

// ─── ROW COLOURS ──────────────────────────────────────────────────────────────

function _apply_row_colours(frm) {
	setTimeout(() => {
		const grid = frm.fields_dict["items"] && frm.fields_dict["items"].grid;
		if (!grid) return;

		(frm.doc.items || []).forEach((row, idx) => {
			const $row = grid.wrapper.find(`.grid-row[data-idx="${idx + 1}"]`);
			if (!$row.length) return;

			$row.css("background-color", "");

			const colours = {
				"Matched":  "rgba(34,197,94,0.07)",
				"Over":     "rgba(59,130,246,0.07)",
				"Short":    "rgba(239,68,68,0.08)",
				"Pending":  "rgba(245,158,11,0.06)",
				"New Item": "rgba(168,85,247,0.07)",
			};
			if (colours[row.count_status]) {
				$row.css("background-color", colours[row.count_status]);
			}
		});
	}, 80);
}

// ─── SCAN BAR ─────────────────────────────────────────────────────────────────

function _inject_scan_bar(frm) {
	if (frm.layout.wrapper.find(".ic-scan-bar").length) return;

	const bar = $(`
		<div class="ic-scan-bar" style="
			display: flex; gap: 8px; align-items: center;
			flex-wrap: wrap;
			padding: 10px 14px;
			background: var(--card-bg, #fff);
			border: 1px solid var(--border-color, #e5e7eb);
			border-radius: 8px;
			margin-bottom: 12px;
		">
			<span style="font-size:18px;">⚡</span>
			<input id="ic-scan-input" type="text" placeholder="${__("Scan barcode or type Item Code + Enter…")}"
				autocomplete="off" spellcheck="false"
				style="flex:1; min-width:200px; border:1.5px solid #3b82f6;
					border-radius:6px; padding:7px 12px; font-family:monospace;
					font-size:13px; outline:none; box-shadow:0 0 0 3px rgba(59,130,246,0.12);"
			/>
			<input id="ic-scan-qty" type="number" value="1" min="0.001" step="any"
				title="${__("Quantity to set")}"
				style="width:70px; border:1px solid var(--border-color,#e5e7eb);
					border-radius:6px; padding:7px 8px; font-family:monospace;
					text-align:right;"
			/>
			<button class="btn btn-primary btn-sm" id="ic-scan-add">
				+ ${__("Add / Update")}
			</button>
			<button class="btn btn-default btn-sm" id="ic-scan-clear">
				✕ ${__("Clear")}
			</button>
		</div>
	`);

	const itemsField = frm.fields_dict["items"] && frm.fields_dict["items"].wrapper;
	if (itemsField) {
		bar.insertBefore($(itemsField));
	}

	bar.find("#ic-scan-add").on("click", () => _process_scan(frm));
	bar.find("#ic-scan-clear").on("click", () => {
		bar.find("#ic-scan-input").val("").focus();
	});
	bar.find("#ic-scan-input").on("keydown", e => {
		if (e.key === "Enter") { e.preventDefault(); _process_scan(frm); }
	});
}

function _process_scan(frm) {
	const input    = $("#ic-scan-input");
	const qtyInput = $("#ic-scan-qty");
	const code     = (input.val() || "").trim().toUpperCase();
	const qty      = parseFloat(qtyInput.val()) || 1;

	if (!code) {
		frappe.show_alert({ message: __("Please enter or scan an Item Code."), indicator: "orange" });
		return;
	}

	// Find matching row
	const existing = (frm.doc.items || []).find(
		r => (r.item_code || "").toUpperCase() === code ||
			(r.barcode   || "").toUpperCase() === code
	);

	if (existing) {
		frappe.model.set_value(existing.doctype, existing.name, "physical_qty", qty);
		_recalculate_row(frm, existing.doctype, existing.name);
		frm.refresh_field("items");
		frappe.show_alert({
			message: __("Updated: {0} → {1}", [existing.item_code, qty]),
			indicator: "green",
		});
	} else {
		frappe.db.get_value("Item", code, ["item_name", "stock_uom", "item_group", "barcode"])
			.then(r => {
				const item = r.message;
				const row  = frm.add_child("items");

				row.item_code    = code;
				row.item_name    = item ? item.item_name : "(Unknown — verify item)";
				row.warehouse    = frm.doc.warehouse || "";
				row.uom          = item ? item.stock_uom : "PCS";
				row.item_group   = item ? item.item_group : "";
				row.bin_location = frm.doc.bin_filter || "";
				row.system_qty   = 0;
				row.physical_qty = qty;
				row.variance_qty = qty;
				row.count_status = "New Item";

				frm.refresh_field("items");
				_apply_row_colours(frm);
				_render_kpi_banner(frm);
				frappe.show_alert({
					message: __("New item added: {0} × {1}", [code, qty]),
					indicator: "blue",
				});
			});
	}

	input.val("").focus();
}

// ─── CSV EXPORT ───────────────────────────────────────────────────────────────

function _export_csv(frm) {
	const items = frm.doc.items || [];
	const rows  = [
		["INVENTORY COUNT SHEET", frm.doc.name],
		["Branch", frm.doc.company || "", "Date", frm.doc.count_date || ""],
		["Warehouse", frm.doc.warehouse || "", "Type", frm.doc.count_type || ""],
		[],
		["#", "Warehouse", "Item Code", "Item Name", "Bin", "UOM",
		 "System Qty", "Physical Count", "Variance", "Status", "Remarks"],
		...items.map((r, i) => [
			i + 1,
			r.warehouse || "",
			r.item_code,
			`"${(r.item_name || "").replace(/"/g, '""')}"`,
			r.bin_location || "",
			r.uom,
			r.system_qty !== undefined ? r.system_qty : "",
			r.physical_qty !== undefined && r.physical_qty !== null ? r.physical_qty : "",
			r.variance_qty !== undefined ? r.variance_qty : "",
			r.count_status,
			`"${(r.remarks || "").replace(/"/g, '""')}"`,
		]),
	];

	const csv  = rows.map(r => r.join(",")).join("\n");
	const blob = new Blob([csv], { type: "text/csv" });
	const a    = document.createElement("a");
	a.href     = URL.createObjectURL(blob);
	a.download = `InventoryCountSheet_${frm.doc.name}_${frm.doc.count_date || "draft"}.csv`;
	a.click();
	frappe.show_alert({ message: __("CSV exported successfully."), indicator: "green" });
}
