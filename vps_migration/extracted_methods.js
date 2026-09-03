async submit(tot, paid) {
    const items = this.cart.map(c => ({ item_code: c.item_code, qty: c.qty, rate: c.rate, discount_amount: c.discount_amount, uom: c.uom }));
    const remEl = document.getElementById("vpos-remarks");
    const remarks = remEl ? remEl.value.trim() : "";
    const payload = {
      customer: this.customer,
      vehicle: this.vehicle || null,
      company: this.company,
      paid_amount: paid,
      payment_method: this.payment_method || "Cash",
      remarks: remarks,
      items: items
    };
    const r = await api("vm_pos_create_invoice", { data: JSON.stringify(payload) });
    if (r && r.name) {
      alert("✅ POS Invoice " + r.name + " (" + (r.payment_method || payload.payment_method) + ") created successfully!");
      this._recentSale = {
        company: this.company || "",
        cashier: this.cashier || this.user || "Cashier",
        date: new Date().toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" }),
        time: new Date().toLocaleTimeString("en-PH", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        invoice_no: r.name,
        vehicle: this.vehicle || "",
        customer: this.customer || "",
        customer_name: this._customerLabel() || "",
        payment_method: this.payment_method || "Cash",
        paid_amount: paid,
        change_amount: paid - tot,
        total_amount: tot,
        discount_amount: 0,
        items_html: this.cart.map(c => `<div class="vpos-receipt-item"><span class="vpos-receipt-item-q">${c.qty} × ${c.item_name}</span><span class="vpos-receipt-item-a">${peso(c.qty * c.rate - c.discount_amount)}</span></div>`).join(""),
        remarks: remarks
      };
      this.clear();
      await this.fetchHistory();
      window.open("/desk#Form/POS Invoice/" + encodeURIComponent(r.name), "_blank");
      // Auto-print the receipt after a short delay so the alert dialog is dismissed first
      setTimeout(() => { this.printReceipt(this._recentSale); }, 800);
    } else {
      const err = api.lastError || "Unknown server response. Please verify in console.";
      alert("⚠️ Failed to create invoice:\n" + err);
    }
  },

  initTip() {
    const tip = document.createElement("div");
    tip.className = "vpos-tip";
    document.body.appendChild(tip);
    this._tip = tip;
    const grid = document.getElementById("vpos-products");
    if (!grid) return;
    grid.addEventListener("mouseover", e => {
      const c = e.target.closest("[data-tip]");
      if (c && c.getAttribute("data-tip")) {
        tip.innerHTML = c.getAttribute("data-tip").replace(/&/g, "&amp;").replace(/\n/g, "<br>").replace(/(bin [^\n<]+)/g, "<b>$1</b>");
        tip.style.display = "block";
        tip.style.opacity = "1";
      }
    });
    grid.addEventListener("mousemove", e => {
      let x = e.clientX + 14, y = e.clientY + 14;
      if (x + tip.offsetWidth > window.innerWidth) x = window.innerWidth - tip.offsetWidth - 8;
      if (y + tip.offsetHeight > window.innerHeight) y = window.innerHeight - tip.offsetHeight - 8;
      tip.style.left = x + "px";
      tip.style.top = y + "px";
    });
    grid.addEventListener("mouseout", e => {
      if (e.target.closest("[data-tip]")) {
        tip.style.opacity = "0";
        tip.style.display = "none";
      }
    });
  }
};

window.addEventListener("DOMContentLoaded", () => {
  try { POS.init(); } catch (err) {
    console.error(err);
    document.getElementById("vpos-root").innerHTML = '<div style="padding:24px;color:#b91c1c">POS failed: ' + (err && err.message ? err.message : err) + '</div>';
  }
});
</script>

	</article>
	
</div></div>

		<div class="page-footer"></div>
	</main>
	
</div>

</div>


<footer class="web-footer">
<div class="container">
<div class="footer-logo-extension">
<div class="row">
<div class="text-left col-md-6"></div>
<div class="text-right col-md-6">
</div>
</div>
</div>
<div class="footer-links">
<div class="row">
<div class="footer-col-left col-sm-6"></div>
<d