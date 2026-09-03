frappe.pages["vehicle_pos"].on_page_load = function (wrapper) {
	inject_pos_styles();

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Vehicle POS"),
		single_column: true
	});

	page.main.addClass("vehicle-pos-page");

	const boot = () => {
		const pos = new VehiclePOS(page);
		pos.render();
	};

	// jsQR is required for QR badge login; load it once from CDN if absent.
	if (window.jsQR) { boot(); return; }
	const s = document.createElement("script");
	s.src = "https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js";
	s.onload = boot;
	s.onerror = () => { boot(); };  // fall back to credential-only login if CDN blocked
	document.head.appendChild(s);
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
		this.cashier = null;
		this.cashier_user = null;
		this.logged_in = false;
	}

	render() {
		this.page.main.empty();
		if (!this.logged_in) {
			this.build_login();
			return;
		}
		this.build_layout();
		this.load_companies();
		this.bind_global_keys();
	}

	build_login() {
		const self = this;
		const html = `
		<div class="vpos-login" id="vpos-login">
			<div class="vpos-login-card">
				<div class="vpos-login-logo">V</div>
				<div class="vpos-login-title">Vehicle POS</div>
				<div class="vpos-login-sub">Cashier Sign-In</div>
				<input class="vpos-li vpos-li-user" placeholder="User ID / Email" autocomplete="username" />
				<input class="vpos-li vpos-li-pass" type="password" placeholder="Password" autocomplete="current-password" />
				<button class="vpos-li-btn" id="vpos-li-go">Sign In</button>
				<div class="vpos-li-or">— or scan your QR badge —</div>
				<button class="vpos-li-qr" id="vpos-li-scan">&#128247; Scan QR Code (camera)</button>
				<label class="vpos-li-up"><input type="file" accept="image/*" id="vpos-li-file" style="display:none" />&#128247; Upload QR image to log in</label>
				<div class="vpos-li-or">— or paste badge code —</div>
				<input class="vpos-li vpos-li-code" id="vpos-li-code" placeholder="user|password" />
				<button class="vpos-li-qr" id="vpos-li-codego">Use code</button>
				<div class="vpos-li-err" id="vpos-li-err"></div>
				<video id="vpos-video" playsinline style="display:none;width:100%;border-radius:12px;margin-top:10px"></video>
			</div>
		</div>`;
		this.page.main.append(html);
		this.page.main.find("#vpos-li-go").on("click", () => self.do_login(
			self.page.main.find(".vpos-li-user").val(), self.page.main.find(".vpos-li-pass").val()));
		this.page.main.find("#vpos-li-scan").on("click", () => self.open_scanner());
		this.page.main.find("#vpos-li-file").on("change", (e) => self.decode_image(e.target.files[0]));
		this.page.main.find("#vpos-li-codego").on("click", () => {
			const c = (self.page.main.find("#vpos-li-code").val() || "").trim();
			self.apply_qr(c);
		});
		// allow Enter on password field
		this.page.main.find(".vpos-li-pass").on("keypress", (e) => {
			if (e.which === 13) self.page.main.find("#vpos-li-go").trigger("click");
		});
	}

	apply_qr(data) {
		if (!data) return;
		const parts = String(data).split("|");
		const u = this.page.main.find(".vpos-li-user");
		const p = this.page.main.find(".vpos-li-pass");
		if (u.length) u.val(parts[0] || "");
		if (p.length) p.val(parts[1] || "");
		this.do_login(parts[0] || "", parts[1] || "");
	}

	do_login(usr, pwd) {
		const self = this;
		const err = this.page.main.find("#vpos-li-err");
		if (!usr || !pwd) { err.text("Enter user ID and password."); return; }
		err.text("Signing in...");
		frappe.call({
			method: "login",
			args: { usr: usr, pwd: pwd },
			callback: (r) => {
				// frappe.call with method 'login' returns the login response
				if (r.message === "Logged In" || (r.message && !r.message.exc)) {
					self.cashier_user = usr;
					window.__vposPwd = pwd;
					self.after_login();
				} else {
					err.text((r.message && r.message.message) ? r.message.message : "Login failed.");
				}
			},
			error: () => { err.text("Login failed."); }
		});
	}

	after_login() {
		const self = this;
		frappe.call({
			method: "vehicle_management.vehicle_management.pos_api.get_cashier",
			callback: (r) => {
				const c = r.message || {};
				self.cashier = c.user || self.cashier_user;
				self.company = c.company || null;
				self.logged_in = true;
				self.render();
			},
			error: () => {
				// get_cashier unavailable — still allow login with no company
				self.cashier = self.cashier_user;
				self.logged_in = true;
				self.render();
			}
		});
	}

	open_scanner() {
		const self = this;
		const v = this.page.main.find("#vpos-video")[0];
		const err = this.page.main.find("#vpos-li-err");
		if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
			err.text("Camera not available. Upload a QR image instead.");
			return;
		}
		err.text("Point camera at the cashier QR badge...");
		navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then((stream) => {
			v.srcObject = stream; v.style.display = "block"; v.play();
			const canvas = document.createElement("canvas");
			const ctx = canvas.getContext("2d");
			const tick = () => {
				if (!self.logged_in && v.readyState === 4) {
					canvas.width = v.videoWidth; canvas.height = v.videoHeight;
					ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
					try {
						const d = ctx.getImageData(0, 0, canvas.width, canvas.height);
						let res = null;
						try { res = window.jsQR(d.data, d.width, d.height, { inversionAttempts: "attemptBoth" }); } catch (e) {}
						if (res && res.data) {
							stream.getTracks().forEach(t => t.stop());
							v.style.display = "none";
							self.apply_qr(res.data);
							return;
						}
					} catch (e) {}
				}
				setTimeout(tick, 300);
			};
			tick();
		}).catch(() => err.text("Camera access denied. Upload a QR image instead."));
	}

	decode_image(file) {
		const self = this;
		const err = this.page.main.find("#vpos-li-err");
		if (!file) return;
		err.text("Reading QR from image...");
		const img = new Image();
		const reader = new FileReader();
		reader.onload = () => {
			img.onload = () => {
				const canvas = document.createElement("canvas");
				canvas.width = img.width; canvas.height = img.height;
				const ctx = canvas.getContext("2d");
				ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
				const d = ctx.getImageData(0, 0, canvas.width, canvas.height);
				let res = null;
				try { res = window.jsQR(d.data, d.width, d.height, { inversionAttempts: "attemptBoth" }); } catch (e) {}
				if (res && res.data) { err.text("QR decoded."); self.apply_qr(res.data); }
				else { err.text("No QR found in that image."); }
			};
			img.onerror = () => err.text("Could not read image.");
			img.src = reader.result;
		};
		reader.readAsDataURL(file);
	}

	build_layout() {
		const html = `
		<div class="vpos-app">
			<!-- TOP NAV BAR -->
			<header class="vpos-topnav">
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
				<div class="vpos-topnav-cats">
					<div class="vpos-cats" id="vpos-cats"></div>
				</div>
				<div class="vpos-side-foot">v1.0 · VMS</div>
			</header>

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

				<div class="vpos-vehicle-details" id="vpos-vehicle-details"></div>

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
			this.$("#vpos-vehicle-details").empty();
			return;
		}
		frappe.db.get_value("Customer Vehicle", vehicle, ["customer","customer_name","contact_no","email","plate_no","make","model","year_model","color","vin","transmission","fuel_type","status"]).then((r) => {
			if (r && r.customer) {
				self.customer = r.customer;
				const label = r.customer_name ? `${r.customer} — ${r.customer_name}` : r.customer;
				self.$(".vpos-customer").val(r.customer);
				self.$(".vpos-customer-display").text(label);
				self.render_vehicle_details(r, true);
			} else {
				self.customer = null;
				self.$(".vpos-customer").val("");
				self.$(".vpos-customer-display").text("");
				self.render_vehicle_details(r, false);
				frappe.msgprint(__("Selected Customer Vehicle has no linked Customer."));
			}
		});
	}

	render_vehicle_details(r, linked) {
		const self = this;
		const box = this.$("#vpos-vehicle-details").empty();
		if (!r) return;
		const esc = (v) => (v == null ? "" : String(v).replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c])));
		const row = (label, val) => { const e = esc(val); return e ? `<div class="vpos-vd-row"><span class="vpos-vd-label">${label}</span><span class="vpos-vd-val">${e}</span></div>` : ""; };
		const vehicleLine = [r.make, r.model, r.year_model].filter(Boolean).map(esc).join(" ");
		let html = "";
		html += `<div class="vpos-vd-head"><span class="vpos-vd-plate">${esc(r.plate_no)}</span>`;
		if (r.status) html += `<span class="vpos-vd-badge${r.status === "Active" ? " vpos-vd-badge-active" : ""}">${esc(r.status)}</span>`;
		html += `</div>`;
		html += row("Vehicle", vehicleLine);
		html += row("Color", r.color);
		html += row("VIN", r.vin);
		html += row("Transmission", r.transmission);
		html += row("Fuel", r.fuel_type);
		const cust = r.customer_name || r.customer;
		html += row("Customer", cust);
		html += row("Contact", r.contact_no);
		html += row("Email", r.email);
		if (linked && r.customer) {
			html += `<div class="vpos-vd-link">Linked to customer: ${esc(r.customer)}</div>`;
		} else {
			html += `<div class="vpos-vd-warn">No linked customer — invoice cannot be created</div>`;
		}
		box.append(html);
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
		/* CASHIER LOGIN */
		.vpos-login { position: fixed; inset: 0; background: linear-gradient(160deg, #0c1a18, #123b33); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 16px; }
		.vpos-login-card { background: #fff; border-radius: 24px; padding: 32px 24px; width: 360px; max-width: 100%; box-shadow: 0 24px 60px rgba(0,0,0,.45); text-align: center; }
		.vpos-login-logo { width: 56px; height: 56px; border-radius: 16px; background: linear-gradient(135deg,#16c784,#0fa76d); color: #04201a; font-weight: 800; font-size: 28px; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; }
		.vpos-login-title { font-weight: 800; font-size: 22px; color: #12332e; }
		.vpos-login-sub { color: #6b9080; font-size: 13px; margin-bottom: 20px; font-weight: 500; }
		.vpos-li { width: 100%; height: 46px; border: 1.5px solid #d7ecea; border-radius: 12px; padding: 0 14px; margin-bottom: 10px; font-size: 14px; background: #fbfdfc; }
		.vpos-li:focus { outline: none; border-color: #16a34a; }
		.vpos-li-btn { width: 100%; height: 48px; background: #16a34a; color: #fff; border: none; border-radius: 12px; font-weight: 800; font-size: 15px; cursor: pointer; margin-bottom: 14px; }
		.vpos-li-btn:hover { background: #15803d; }
		.vpos-li-or { color: #9bbdb4; font-size: 11px; margin: 10px 0; text-transform: uppercase; letter-spacing: .04em; }
		.vpos-li-qr { width: 100%; height: 46px; background: #eef7f3; color: #0f766e; border: 1.5px solid #d7ecea; border-radius: 12px; font-weight: 700; cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 6px; }
		.vpos-li-qr:hover { background: #e0f2ed; }
		.vpos-li-up { display: flex; width: 100%; height: 46px; background: #eef7f3; color: #0f766e; border: 1.5px dashed #bfe3dd; border-radius: 12px; font-weight: 700; cursor: pointer; font-size: 13px; align-items: center; justify-content: center; gap: 6px; margin-bottom: 10px; }
		.vpos-li-err { color: #dc2626; font-size: 12px; min-height: 16px; margin-top: 8px; font-weight: 600; }
		.vpos-li-ok { color: #16a34a; font-size: 12px; margin-bottom: 10px; font-weight: 600; }
		.vehicle-pos-page .page-head, .vehicle-pos-page .page-head .title { display: none !important; }
		.vehicle-pos-page .layout-main-section { padding: 0 !important; margin: 0 !important; }
		.vehicle-pos-page .page-content { padding: 0 !important; }
		.vpos-app { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto 1fr; grid-template-areas: "topnav topnav" "main order"; height: calc(100vh - 46px); min-height: 520px; }

		/* TOP NAV */
		.vpos-topnav { grid-area: topnav; display: flex; align-items: center; gap: 14px; width: 100%; background: #ffffff; border-bottom: 1px solid #d7ecea; padding: 10px 14px; flex-wrap: wrap; }
		.vpos-brand { display: flex; align-items: center; gap: 10px; padding: 4px 6px; }
		.vpos-brand-logo { width: 38px; height: 38px; border-radius: 10px; background: #16a34a; color: #fff; font-weight: 800; font-size: 20px; display: flex; align-items: center; justify-content: center; }
		.vpos-brand-name { font-weight: 800; font-size: 15px; color: #0f2e2a; line-height: 1.1; }
		.vpos-brand-sub { font-size: 11px; color: #6b9080; }
		.vpos-nav { display: flex; flex-direction: row; gap: 4px; margin-top: 0; flex-wrap: nowrap; overflow-x: auto; }
		.vpos-nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: #3d5a54; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; white-space: nowrap; }
		.vpos-nav-item:hover { background: #f0faf8; }
		.vpos-nav-item.active { background: #16a34a; color: #fff; }
		.vpos-nav-ic { font-size: 14px; }
		.vpos-topnav-cats { display: flex; align-items: center; flex: 1 1 auto; min-width: 0; overflow: hidden; }
		.vpos-side-foot { margin-left: auto; margin-top: 0; font-size: 11px; color: #9bbdb4; padding: 0 6px; white-space: nowrap; }

		/* MAIN */
		.vpos-main { flex: 1 1 auto; grid-area: main; overflow: hidden; display: flex; flex-direction: column; min-width: 0; padding: 14px 16px; gap: 12px; }
		.vpos-topbar { display: flex; gap: 12px; align-items: flex-end; }
		.vpos-search-wrap { flex: 1; position: relative; }
		.vpos-search-ic { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); font-size: 14px; opacity: .6; }
		.vpos-search { padding-left: 34px !important; height: 42px; border-radius: 10px; border: 1px solid #cfeee9; background: #fff; }
		.vpos-company-wrap { display: flex; flex-direction: column; gap: 3px; }
		.vpos-company-wrap label { font-size: 10px; color: #6b9080; font-weight: 700; text-transform: uppercase; }
		.vpos-company { height: 42px; border-radius: 10px; border: 1px solid #cfeee9; background: #fff; min-width: 150px; }

		.vpos-cats { display: flex; gap: 8px; flex-wrap: nowrap; overflow-x: auto; white-space: nowrap; }
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
		.vpos-order { flex: none; grid-area: order; min-width: 0; overflow-y: auto; background: #ffffff; border-left: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 14px; gap: 12px; }
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
		.vpos-print { flex: 0 0 120px; background: #f5a623; border: none; color: #1a1a1a; font-weight: 800; font-size: 13px; border-radius: 10px; padding: 12px; cursor: pointer; transition: .12s; display: flex; align-items: center; justify-content: center; gap: 6px; }
		.vpos-print:hover { background: #e0961a; }
		.vpos-print:disabled { opacity: .4; cursor: not-allowed; }
		/* RESPONSIVE: tablet + mobile (fix overlap + 50/50 on all sizes) */
		@media (max-width: 1024px) {
			.vpos-app { grid-template-columns: 1fr 1fr; }
			.vpos-products { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
		}
		@media (max-width: 768px) {
			.vpos-app { display: grid; grid-template-columns: 1fr; grid-template-rows: auto auto auto; grid-template-areas: "topnav" "main" "order"; height: auto; min-height: 0; }
			.vpos-topnav { flex-wrap: wrap; }
			.vpos-nav { flex-wrap: nowrap; }
			.vpos-topnav-cats { flex-basis: 100%; overflow-x: auto; }
			.vpos-main { overflow: visible; }
			.vpos-order { width: 100%; border-left: none; border-top: 1px solid #d7ecea; max-height: 65vh; }
			.vpos-products { grid-template-columns: repeat(2, 1fr); }
		}
	
		/* VEHICLE DETAILS PANEL */
		.vpos-vehicle-details { background: #f1faf8; border: 1px solid #d7ecea; border-radius: 10px; padding: 10px 12px; margin-top: 10px; font-size: 12px; overflow: hidden; }
		.vpos-vd-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
		.vpos-vd-plate { font-weight: 800; font-size: 14px; color: #0f2e2a; }
		.vpos-vd-badge { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 999px; background: #e2e8f0; color: #475569; text-transform: uppercase; letter-spacing: .03em; }
		.vpos-vd-badge-active { background: #dcfce7; color: #15803d; }
		.vpos-vd-row { display: flex; justify-content: space-between; gap: 10px; padding: 2px 0; border-bottom: 1px dashed #e6f2ef; }
		.vpos-vd-row:last-of-type { border-bottom: none; }
		.vpos-vd-label { color: #9bbdb4; font-size: 11px; text-transform: uppercase; letter-spacing: .02em; white-space: nowrap; }
		.vpos-vd-val { color: #12332e; font-weight: 600; text-align: right; word-break: break-word; }
		.vpos-vd-link { margin-top: 8px; padding: 6px 10px; background: #dcfce7; border: 1px solid #86efac; border-radius: 8px; color: #16a34a; font-weight: 700; font-size: 12px; }
		.vpos-vd-warn { margin-top: 8px; padding: 6px 10px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; color: #dc2626; font-weight: 700; font-size: 12px; }
</style>`).appendTo("head");
}
