frappe.pages["vehicle_pos"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Vehicle POS"),
		single_column: true
	});

	page.main.addClass("vehicle-pos-page");
	inject_pos_styles();

	const pos = new VehiclePOS(page);
	pos.render();
};

class VehiclePOS {
	constructor(page) {
		this.page = page;
		this.cart = [];
		this.customer = null;
		this.vehicle = null;
		this.company = null;
		this.payment_method = "Cash";
		this.category = null;
	}

	render() {
		this.page.main.empty();
		this.build_layout();
		this.load_companies();
		this.bind_global_keys();
	}

	build_layout() {
		const html = `
		<div class="vpos-app">
			<!-- LEFT SIDEBAR -->
			<aside class="vpos-side">
				<div class="vpos-brand">
					<div class="vpos-brand-logo">V</div>
					<div>
						<div class="vpos-brand-name">Vehicle POS</div>
						<div class="vpos-brand-sub">Management</div>
					</div>
				</div>
				<nav class="vpos-nav">
					<a class="vpos-nav-item" data-route="vehicle_analytics"><span class="vpos-nav-ic">▦</span> Dashboard</a>
					<a class="vpos-nav-item" data-route="vehicle_management"><span class="vpos-nav-ic">▤</span> Workspace</a>
					<a class="vpos-nav-item active"><span class="vpos-nav-ic">🛒</span> Point of Sale</a>
					<a class="vpos-nav-item" data-route="List/Customer Vehicle"><span class="vpos-nav-ic">🚗</span> Vehicles</a>
					<a class="vpos-nav-item" data-route="List/Vehicle POS Invoice"><span class="vpos-nav-ic">🧾</span> POS Invoices</a>
				</nav>
				<div class="vpos-side-foot">v1.0 · VMS</div>
			</aside>

			<!-- CENTER: DISCOVERY -->
			<section class="vpos-main">
				<div class="vpos-topbar">
					<div class="vpos-search-wrap">
						<span class="vpos-search-ic">🔍</span>
						<input class="vpos-search form-control" placeholder="Search parts, services, tires, lubricants..." />
					</div>
					<div class="vpos-company-wrap">
						<label>Branch</label>
						<select class="vpos-company form-control"></select>
					</div>
				</div>

				<div class="vpos-cats" id="vpos-cats"></div>

				<div class="vpos-products" id="vpos-products"></div>
			</section>

			<!-- RIGHT: ORDER -->
			<aside class="vpos-order">
				<div class="vpos-order-head">
					<div class="vpos-order-title">Current Ticket</div>
					<div class="vpos-order-meta">
						<div class="vpos-field">
							<label>Vehicle</label>
							<div class="vpos-vehicle-wrapper"></div>
						</div>
						<div class="vpos-field">
							<label>Customer</label>
							<div class="vpos-customer-display">Select a vehicle first...</div>
							<input type="hidden" class="vpos-customer" />
						</div>
					</div>
				</div>

				<div class="vpos-cart" id="vpos-cart"></div>

				<div class="vpos-totals">
					<div class="vpos-row"><span>Total Qty</span><span class="vpos-tqty">0</span></div>
					<div class="vpos-row"><span>Discount</span><span class="vpos-tdisc">₱0.00</span></div>
					<div class="vpos-row vpos-grand"><span>Total</span><span class="vpos-total">₱0.00</span></div>
				</div>

				<div class="vpos-tender">
					<div class="vpos-field">
						<label>Payment Method</label>
						<select class="vpos-paymethod form-control">
							<option>Cash</option>
							<option>Bank Transfer</option>
							<option>Credit Card</option>
							<option>GCash</option>
							<option>Maya</option>
							<option>Cheque</option>
						</select>
					</div>
					<div class="vpos-field">
						<label>Paid Amount</label>
						<input class="vpos-paid form-control" type="number" min="0" step="0.01" value="0" />
					</div>
					<div class="vpos-row vpos-change"><span>Change</span><span class="vpos-balance">₱0.00</span></div>
				</div>

				<div class="vpos-actions">
					<button class="btn vpos-clear">Clear</button>
					<button class="btn vpos-charge">Charge & Print</button>
				</div>
			</aside>
		</div>`;
		$(this.page.main).append(html);

		this.$ = (sel) => $(this.page.main).find(sel);
		this.bind_events();
	}

	bind_events() {
		const self = this;
		this.$(".vpos-search").on("keypress", (e) => { if (e.which === 13) self.search_items(); });
		this.$(".vpos-paid").on("input", () => self.update_totals());
		this.$(".vpos-paymethod").on("change", (e) => { self.payment_method = $(e.target).val(); });
		this.$(".vpos-clear").on("click", () => self.clear_all());
		this.$(".vpos-charge").on("click", () => self.charge());
		this.$(".vpos-nav-item[data-route]").on("click", (e) => {
			const r = $(e.currentTarget).attr("data-route");
			if (r) frappe.set_route(r.split("/"));
		});
		this.setup_vehicle_link();
	}

	setup_vehicle_link() {
		const self = this;
		this.vehicle_control = frappe.ui.form.make_control({
			parent: this.$(".vpos-vehicle-wrapper"),
			df: {
				fieldtype: "Link",
				options: "Customer Vehicle",
				fieldname: "vehicle",
				placeholder: "Plate / vehicle...",
				onchange: () => self.on_vehicle_change(this.vehicle_control.get_value())
			},
			render_input: true
		});
	}

	on_vehicle_change(vehicle) {
		const self = this;
		this.vehicle = vehicle || null;
		if (!vehicle) {
			this.customer = null;
			this.$(".vpos-customer").val("");
			this.$(".vpos-customer-display").text("Select a vehicle first...");
			return;
		}
		frappe.db.get_value("Customer Vehicle", vehicle, ["customer", "customer_name", "plate_no"]).then((r) => {
			if (r && r.customer) {
				self.customer = r.customer;
				const label = r.customer_name ? `${r.customer} — ${r.customer_name}` : r.customer;
				self.$(".vpos-customer").val(r.customer);
				self.$(".vpos-customer-display").text(label);
			} else {
				self.customer = null;
				self.$(".vpos-customer").val("");
				self.$(".vpos-customer-display").text("");
				frappe.msgprint(__("Selected Customer Vehicle has no linked Customer."));
			}
		});
	}

	bind_global_keys() {
		const self = this;
		$(this.page.main).on("keydown", ".vpos-search", (e) => {
			if (e.key === "F2") { e.preventDefault(); self.search_items(); }
		});
	}

	load_companies() {
		const self = this;
		frappe.call({
			method: "frappe.client.get_list",
			args: { doctype: "Company", filters: { is_group: 0 }, fields: ["name"], limit_page_length: 50, order_by: "name asc" },
			callback: (r) => {
				const cos = (r.message || []).map(c => c.name);
				const sel = self.$(".vpos-company").empty();
				cos.forEach(c => sel.append(`<option>${c}</option>`));
				self.company = cos[0];
				sel.on("change", (e) => { self.company = $(e.target).val(); });
				self.load_categories();
				self.search_items();
			}
		});
	}

	load_categories() {
		const self = this;
		frappe.call({
			method: "frappe.client.get_list",
			args: { doctype: "Item Group", filters: [["Item Group", "is_group", "=", 0]], fields: ["name"], limit_page_length: 30, order_by: "name asc" },
			callback: (r) => {
				const groups = (r.message || []).map(g => g.name);
				const box = self.$("#vpos-cats").empty();
				box.append(`<button class="vpos-cat active" data-cat="">All</button>`);
				groups.forEach(g => box.append(`<button class="vpos-cat" data-cat="${g}">${g}</button>`));
				box.find(".vpos-cat").on("click", (e) => {
					box.find(".vpos-cat").removeClass("active");
					const btn = $(e.currentTarget).addClass("active");
					self.category = btn.attr("data-cat") || null;
					self.search_items();
				});
			}
		});
	}

	search_items() {
		const self = this;
		const txt = this.$(".vpos-search").val();
		const filters = [["Item", "disabled", "=", 0], ["Item", "is_sales_item", "=", 1]];
		if (this.category) filters.push(["Item", "item_group", "=", this.category]);
		const args = {
			doctype: "Item",
			filters: filters,
			or_filters: txt
				? [["Item", "name", "like", `%${txt}%`], ["Item", "item_name", "like", `%${txt}%`]]
				: [],
			fields: ["name", "item_name", "standard_rate", "stock_uom"],
			limit_page_length: 80,
			order_by: "item_name asc"
		};
		frappe.call({
			method: "frappe.client.get_list",
			args: args,
			callback: (r) => self.render_products(r.message || [])
		});
	}

	render_products(items) {
		const self = this;
		const box = this.$("#vpos-products").empty();
		if (!items.length) { box.append(`<div class="vpos-empty">No items found.</div>`); return; }
		items.forEach(it => {
			const name = it.item_name || it.name;
			const rate = flt(it.standard_rate) || 0;
			const inCart = this.cart.find(c => c.item_code === it.name);
			const card = $(`
				<div class="vpos-prod" data-code="${it.name}" data-rate="${rate}" data-uom="${it.stock_uom}">
					<div class="vpos-prod-thumb">${name.charAt(0).toUpperCase()}</div>
					<div class="vpos-prod-name">${name}</div>
					<div class="vpos-prod-code">${it.name}</div>
					<div class="vpos-prod-foot">
						<div class="vpos-prod-rate">₱${rate.toLocaleString("en-US", {minimumFractionDigits: 2})}</div>
						<button class="vpos-add">+ ADD</button>
					</div>
					${inCart ? `<div class="vpos-prod-badge">${inCart.qty} in cart</div>` : ``}
				</div>`);
			card.find(".vpos-add").on("click", () => self.add_to_cart(it.name, name, rate, it.stock_uom));
			box.append(card);
		});
	}

	add_to_cart(code, name, rate, uom) {
		const existing = this.cart.find(c => c.item_code === code);
		if (existing) {
			existing.qty += 1;
		} else {
			this.cart.push({ item_code: code, item_name: name, qty: 1, rate: rate, uom: uom, discount_amount: 0 });
		}
		this.render_cart();
		this.update_totals();
		this.search_items();
	}

	render_cart() {
		const self = this;
		const box = this.$("#vpos-cart").empty();
		this.$(".vpos-cart-count").text(this.cart.length);
		if (!this.cart.length) { box.append(`<div class="vpos-empty">Cart is empty.<br/>Add items from the catalog →</div>`); return; }
		this.cart.forEach((c, i) => {
			const amt = flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
			const row = $(`
				<div class="vpos-cart-row" data-idx="${i}">
					<div class="vpos-cart-info">
						<div class="vpos-cart-name">${c.item_name}</div>
						<div class="vpos-cart-meta">₱${flt(c.rate).toLocaleString("en-US",{minimumFractionDigits:2})} · ${c.uom || ""}</div>
					</div>
					<div class="vpos-qty">
						<button class="vpos-dec">−</button>
						<input class="vpos-qty-in" type="number" min="1" value="${c.qty}" />
						<button class="vpos-inc">+</button>
					</div>
					<div class="vpos-cart-amt">₱${amt.toLocaleString("en-US",{minimumFractionDigits:2})}</div>
					<button class="vpos-remove" title="Remove">×</button>
				</div>`);
			row.find(".vpos-inc").on("click", () => { c.qty += 1; self.render_cart(); self.update_totals(); });
			row.find(".vpos-dec").on("click", () => { c.qty = Math.max(1, c.qty - 1); self.render_cart(); self.update_totals(); });
			row.find(".vpos-qty-in").on("change", (e) => { c.qty = Math.max(1, parseInt($(e.target).val()) || 1); self.render_cart(); self.update_totals(); });
			row.find(".vpos-remove").on("click", () => { self.cart.splice(i, 1); self.render_cart(); self.update_totals(); self.search_items(); });
			box.append(row);
		});
	}

	update_totals() {
		let tqty = 0, tdisc = 0, total = 0;
		this.cart.forEach(c => {
			tqty += flt(c.qty);
			tdisc += flt(c.discount_amount);
			total += flt(c.qty) * flt(c.rate) - flt(c.discount_amount);
		});
		this.$(".vpos-tqty").text(tqty);
		this.$(".vpos-tdisc").text("₱" + tdisc.toLocaleString("en-US", { minimumFractionDigits: 2 }));
		this.$(".vpos-total").text("₱" + total.toLocaleString("en-US", { minimumFractionDigits: 2 }));
		const paid = flt(this.$(".vpos-paid").val()) || 0;
		const change = flt(paid - total);
		this.$(".vpos-balance").text("₱" + change.toLocaleString("en-US", { minimumFractionDigits: 2 }));
		this._total = total;
	}

	clear_all() {
		this.cart = [];
		this.customer = null;
		this.vehicle = null;
		this.$(".vpos-customer").val("");
		this.$(".vpos-customer-display").text("Select a vehicle first...");
		if (this.vehicle_control) this.vehicle_control.set_value("");
		this.$(".vpos-paid").val(0);
		this.update_totals();
		this.render_cart();
		this.search_items();
	}

	charge() {
		const self = this;
		const total = this._total || 0;
		const paid = flt(this.$(".vpos-paid").val()) || 0;
		if (!this.cart.length) { frappe.msgprint("Cart is empty."); return; }
		if (!this.vehicle) { frappe.msgprint("Please select a Customer Vehicle."); return; }
		if (!this.customer) { frappe.msgprint("Selected Customer Vehicle has no linked Customer."); return; }
		if (!this.company) { frappe.msgprint("Please select a Branch / Company."); return; }
		if (paid < total) { frappe.msgprint("Paid Amount is less than Total."); return; }

		frappe.confirm(`Charge ₱${total.toLocaleString("en-US",{minimumFractionDigits:2})} (Change ₱${(paid-total).toLocaleString("en-US",{minimumFractionDigits:2})})?`,
			() => self.submit_invoice(total, paid));
	}

	submit_invoice(total, paid) {
		const self = this;
		const items = this.cart.map(c => ({
			item_code: c.item_code,
			qty: c.qty,
			rate: c.rate,
			discount_amount: c.discount_amount,
			uom: c.uom
		}));
		frappe.call({
			method: "vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice.create_from_pos",
			args: {
				data: {
					customer: self.customer,
					vehicle: self.vehicle || null,
					company: self.company,
					paid_amount: paid,
					payment_method: self.payment_method,
					items: items
				}
			},
			freeze: true,
			freeze_message: "Creating POS Invoice...",
			callback: (r) => {
				if (r.message && r.message.name) {
					frappe.show_alert("POS Invoice " + r.message.name + " created", 5);
					self.cart = [];
					self.render_cart();
					self.update_totals();
					self.$(".vpos-paid").val(0);
					if (r.message.pos_invoice) {
						window.open(`/desk#Form/POS Invoice/${r.message.pos_invoice}`, "_blank");
					}
				}
			}
		});
	}
}

function inject_pos_styles() {
	if ($("#vpos-custom-styles").length) return;
	$(`
	<style id="vpos-custom-styles">
		.vehicle-pos-page { background: #e0f2f1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
		.vehicle-pos-page .page-head, .vehicle-pos-page .page-head .title { display: none !important; }
		.vehicle-pos-page .layout-main-section { padding: 0 !important; margin: 0 !important; }
		.vehicle-pos-page .page-content { padding: 0 !important; }
		.vpos-app { display: flex; height: calc(100vh - 46px); min-height: 520px; }

		/* SIDEBAR */
		.vpos-side { flex: 0 0 220px; background: #ffffff; border-right: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 16px 12px; }
		.vpos-brand { display: flex; align-items: center; gap: 10px; padding: 6px 6px 16px; }
		.vpos-brand-logo { width: 38px; height: 38px; border-radius: 10px; background: #16a34a; color: #fff; font-weight: 800; font-size: 20px; display: flex; align-items: center; justify-content: center; }
		.vpos-brand-name { font-weight: 800; font-size: 15px; color: #0f2e2a; line-height: 1.1; }
		.vpos-brand-sub { font-size: 11px; color: #6b9080; }
		.vpos-nav { display: flex; flex-direction: column; gap: 4px; margin-top: 8px; }
		.vpos-nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: #3d5a54; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; }
		.vpos-nav-item:hover { background: #f0faf8; }
		.vpos-nav-item.active { background: #16a34a; color: #fff; }
		.vpos-nav-ic { font-size: 14px; }
		.vpos-side-foot { margin-top: auto; font-size: 11px; color: #9bbdb4; padding: 8px 6px 0; }

		/* MAIN */
		.vpos-main { flex: 1 1 auto; display: flex; flex-direction: column; min-width: 0; padding: 14px 16px; gap: 12px; }
		.vpos-topbar { display: flex; gap: 12px; align-items: flex-end; }
		.vpos-search-wrap { flex: 1; position: relative; }
		.vpos-search-ic { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 14px; opacity: .6; }
		.vpos-search { padding-left: 34px !important; height: 42px; border-radius: 10px; border: 1px solid #cfeee9; background: #fff; }
		.vpos-company-wrap { display: flex; flex-direction: column; gap: 3px; }
		.vpos-company-wrap label { font-size: 10px; color: #6b9080; font-weight: 700; text-transform: uppercase; }
		.vpos-company { height: 42px; border-radius: 10px; border: 1px solid #cfeee9; background: #fff; min-width: 150px; }

		.vpos-cats { display: flex; gap: 8px; flex-wrap: wrap; }
		.vpos-cat { border: 1px solid #bfe3dd; background: #fff; color: #2f564f; padding: 7px 14px; border-radius: 999px; font-size: 12px; font-weight: 600; cursor: pointer; transition: .12s; }
		.vpos-cat:hover { border-color: #16a34a; }
		.vpos-cat.active { background: #16a34a; color: #fff; border-color: #16a34a; }

		.vpos-products { flex: 1; overflow-y: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; align-content: start; padding: 4px 4px 8px; }
		.vpos-prod { background: #fff; border: 1px solid #d7ecea; border-radius: 14px; padding: 12px; position: relative; display: flex; flex-direction: column; gap: 4px; transition: .12s; }
		.vpos-prod:hover { border-color: #16a34a; box-shadow: 0 6px 16px rgba(22,163,74,.16); transform: translateY(-2px); }
		.vpos-prod-thumb { width: 42px; height: 42px; border-radius: 10px; background: #e8f7f3; color: #16a34a; font-weight: 800; font-size: 18px; display: flex; align-items: center; justify-content: center; margin-bottom: 4px; }
		.vpos-prod-name { font-weight: 700; font-size: 13px; color: #12332e; line-height: 1.2; }
		.vpos-prod-code { font-size: 10px; color: #9bbdb4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
		.vpos-prod-foot { display: flex; align-items: center; justify-content: space-between; margin-top: 6px; }
		.vpos-prod-rate { color: #16a34a; font-weight: 800; font-size: 13px; }
		.vpos-add { border: none; background: #16a34a; color: #fff; font-weight: 700; font-size: 11px; padding: 6px 12px; border-radius: 999px; cursor: pointer; transition: .12s; }
		.vpos-add:hover { background: #15803d; }
		.vpos-prod-badge { position: absolute; top: 8px; right: 8px; background: #16a34a; color: #fff; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 999px; }
		.vpos-empty { color: #6b9080; padding: 30px; text-align: center; grid-column: 1/-1; font-size: 13px; }

		/* ORDER PANEL */
		.vpos-order { flex: 0 0 380px; background: #ffffff; border-left: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 14px; gap: 12px; }
		.vpos-order-head { border-bottom: 1px solid #eef6f4; padding-bottom: 12px; }
		.vpos-order-title { font-weight: 800; font-size: 15px; color: #0f2e2a; margin-bottom: 10px; }
		.vpos-order-meta { display: flex; flex-direction: column; gap: 8px; }
		.vpos-field { display: flex; flex-direction: column; gap: 3px; }
		.vpos-field label { font-size: 10px; color: #6b9080; font-weight: 700; text-transform: uppercase; }
		.vpos-customer-display { background: #f1faf8; color: #12332e; min-height: 34px; padding: 7px 10px; border: 1px solid #d7ecea; border-radius: 8px; cursor: default; user-select: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; font-weight: 600; }
		.vpos-customer-display:empty::before { content: "Select a vehicle first..."; color: #9bbdb4; font-weight: 400; }

		.vpos-cart { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; min-height: 60px; }
		.vpos-cart-row { display: flex; align-items: center; gap: 8px; background: #f7fbfa; border: 1px solid #eef6f4; border-radius: 10px; padding: 8px 10px; }
		.vpos-cart-info { flex: 1; min-width: 0; }
		.vpos-cart-name { font-weight: 700; font-size: 12px; color: #12332e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
		.vpos-cart-meta { font-size: 10px; color: #9bbdb4; }
		.vpos-qty { display: flex; align-items: center; gap: 4px; }
		.vpos-qty button { width: 24px; height: 24px; border-radius: 6px; border: 1px solid #cfeee9; background: #fff; color: #16a34a; font-weight: 800; cursor: pointer; line-height: 1; }
		.vpos-qty-in { width: 44px; text-align: center; border: 1px solid #cfeee9; border-radius: 6px; height: 24px; }
		.vpos-cart-amt { font-weight: 800; font-size: 12px; min-width: 72px; text-align: right; color: #12332e; }
		.vpos-remove { border: none; background: transparent; color: #ef4444; font-size: 18px; cursor: pointer; line-height: 1; }

		.vpos-totals { background: #f1faf8; border: 1px solid #d7ecea; border-radius: 10px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; }
		.vpos-row { display: flex; justify-content: space-between; font-size: 13px; color: #2f564f; }
		.vpos-grand { font-weight: 800; font-size: 17px; color: #0f2e2a; margin-top: 2px; }

		.vpos-tender { border-top: 1px solid #eef6f4; padding-top: 10px; display: flex; flex-direction: column; gap: 6px; }
		.vpos-tender .form-control { height: 38px; border-radius: 8px; border: 1px solid #cfeee9; }
		.vpos-change { font-weight: 700; color: #16a34a; }

		.vpos-actions { display: flex; gap: 8px; margin-top: 4px; }
		.vpos-clear { background: #fff; border: 1px solid #cfeee9; color: #3d5a54; font-weight: 700; border-radius: 10px; padding: 12px; flex: 0 0 90px; cursor: pointer; }
		.vpos-clear:hover { background: #f0faf8; }
		.vpos-charge { flex: 1; background: #16a34a; border: none; color: #fff; font-weight: 800; font-size: 14px; border-radius: 10px; padding: 12px; cursor: pointer; transition: .12s; }
		.vpos-charge:hover { background: #15803d; }
	</style>`).appendTo("head");
}
