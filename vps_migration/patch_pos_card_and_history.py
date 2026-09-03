import urllib.request, json, re

with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'r', encoding='utf-8') as f:
    html = f.read()

# =========================================================================
# 1. CSS ENHANCEMENTS: Card Thumbnail, Standard Price & +ADD Button, History UI
# =========================================================================
css_additions = """
/* Product Card Image & Standardized Footer */
.vpos-thumb {
  width: 100%;
  height: 110px;
  border-radius: 14px;
  background: #f1f7f4;
  color: var(--mint-d);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
  overflow: hidden;
  border: 1px solid #e2ebe6;
  position: relative;
}
.vpos-thumb img {
  width: 100%;
  height: 110px;
  object-fit: cover;
  border-radius: 14px;
  display: block;
}
.vpos-thumb-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
}
.vpos-thumb-placeholder span.ico {
  font-size: 36px;
  line-height: 1;
}

.vpos-card-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 8px;
  gap: 6px;
  border-top: 1px solid #f0f4f2;
}
.vpos-card-rate {
  color: var(--mint-d);
  font-weight: 800;
  font-size: 13.5px;
  font-family: var(--font-head);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.3px;
  flex: 1;
  min-width: 0;
  line-height: 1.2;
}
.vpos-card-add {
  border: none;
  background: var(--mint);
  color: #04201a;
  font-weight: 800;
  font-size: 11.5px;
  height: 34px;
  min-width: 72px;
  padding: 0 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: all .12s;
  touch-action: manipulation;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.vpos-card-add:hover {
  background: var(--mint-d);
  color: #fff;
}

/* History Toolbar & Interactive List */
.vpos-hist-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px 0 24px;
}
.vpos-hist-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 12px 18px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
.vpos-hist-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.vpos-hist-title h3 {
  margin: 0;
  font-family: var(--font-head);
  font-size: 18px;
  font-weight: 800;
  color: var(--ink);
}
.vpos-hist-badge {
  background: #eef7f3;
  color: var(--mint-d);
  font-size: 12px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 999px;
}
.vpos-hist-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.vpos-hist-pills {
  display: flex;
  gap: 4px;
  background: #f1f5f3;
  padding: 3px;
  border-radius: 12px;
}
.vpos-hist-pill {
  border: none;
  background: transparent;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 700;
  color: var(--slate);
  border-radius: 9px;
  cursor: pointer;
  transition: all .15s;
}
.vpos-hist-pill.active {
  background: #fff;
  color: var(--ink);
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}
.vpos-hist-dates {
  display: flex;
  align-items: center;
  gap: 6px;
}
.vpos-hist-dt {
  height: 34px;
  border: 1.5px solid var(--line);
  border-radius: 10px;
  padding: 0 8px;
  font-size: 12px;
  font-family: var(--font-base);
  color: var(--txt);
  background: #fff;
}
.vpos-hist-btn {
  height: 34px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1.5px solid var(--line);
  background: #fff;
  font-size: 12px;
  font-weight: 700;
  color: var(--txt);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all .12s;
}
.vpos-hist-btn:hover {
  border-color: var(--mint);
  background: #f0faf5;
}
.vpos-hist-btn.primary {
  background: var(--mint);
  border-color: var(--mint);
  color: #04201a;
  font-weight: 800;
}
.vpos-hist-search-box {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 0 14px;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.vpos-hist-search-box input {
  border: none;
  outline: none;
  width: 100%;
  font-size: 13.5px;
  font-family: var(--font-base);
}
.vpos-hist-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.vpos-hist-card {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px 18px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: transform .12s, box-shadow .12s, border-color .12s;
}
.vpos-hist-card:hover {
  border-color: var(--mint);
  box-shadow: 0 6px 18px rgba(22,199,132,0.14);
  transform: translateY(-1px);
}
.vpos-hist-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.vpos-hist-code {
  font-family: var(--font-head);
  font-weight: 800;
  font-size: 14.5px;
  color: #1e3a8a;
  cursor: pointer;
}
.vpos-hist-code:hover {
  text-decoration: underline;
}
.vpos-hist-time {
  font-size: 11.5px;
  color: var(--muted);
  font-weight: 600;
}
.vpos-hist-mid {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.vpos-hist-cust {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--ink);
}
.vpos-hist-sub {
  font-size: 12px;
  color: var(--slate);
  display: flex;
  gap: 8px;
  align-items: center;
}
.vpos-hist-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px dashed var(--line);
  padding-top: 8px;
  margin-top: 4px;
}
.vpos-hist-amt {
  font-family: var(--font-head);
  font-weight: 800;
  font-size: 16px;
  color: var(--mint-d);
}
.vpos-hist-tags {
  display: flex;
  align-items: center;
  gap: 6px;
}
.vpos-hist-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
}
.vpos-hist-tag.paid {
  background: #dcfce7;
  color: #166534;
}
.vpos-hist-tag.desk-link {
  background: #eff6ff;
  color: #1e40af;
  cursor: pointer;
}
.vpos-hist-tag.desk-link:hover {
  background: #dbeafe;
}
"""

html = html.replace('</style>', css_additions + '\n</style>', 1)

# =========================================================================
# 2. UPDATE card(it, box) TO RENDER ITEM IMAGE AND STANDARD FOOTER
# =========================================================================
old_card_code = """  card(it, box) {
    const self = this;
    const name = it.name || it.code;
    const rate = flt(it.rate) || 0;
    const card = document.createElement("div");
    card.className = "vpos-card";
    card.setAttribute("data-code", it.code);
    const stock = this.STOCK && this.STOCK[it.code] ? this.STOCK[it.code].stock : null;
    const tip = this.STOCK && this.STOCK[it.code] ? this.stockTip(this.STOCK[it.code]) : "";

    card.innerHTML = `
      <div class="vpos-thumb">${name.charAt(0).toUpperCase()}</div>
      <div class="vpos-card-name">${name}</div>
      <div class="vpos-card-code">${it.code}</div>
      <div class="vpos-card-stock">${stock == null ? "Stock: …" : "Stock: " + flt(stock)}</div>
      <div class="vpos-card-foot">
        <div class="vpos-card-rate">${peso(rate)}</div>
        <button class="vpos-card-add">+ ADD</button>
      </div>`;

    if (tip) card.setAttribute("data-tip", tip);
    const inc = this.cart.find(c => c.item_code === it.code);
    if (inc) {
      const b = document.createElement("div");
      b.className = "vpos-card-badge";
      b.textContent = inc.qty + " in cart";
      card.appendChild(b);
    }
    card.onclick = () => self.add(it.code, name, rate, it.uom);
    card.querySelector(".vpos-card-add").onclick = (e) => {
      e.stopPropagation();
      self.add(it.code, name, rate, it.uom);
    };
    box.appendChild(card);
  },"""

new_card_code = """  getCategoryIcon(group, name) {
    const s = ((group || "") + " " + (name || "")).toLowerCase();
    if (s.includes("tire") || s.includes("tyre") || s.includes("wheel") || s.includes("rim") || s.includes("mag")) return "🛞";
    if (s.includes("oil") || s.includes("lube") || s.includes("lubricant") || s.includes("fluid")) return "🛢️";
    if (s.includes("service") || s.includes("labor") || s.includes("alignment") || s.includes("pms") || s.includes("repair")) return "🔧";
    if (s.includes("battery")) return "🔋";
    if (s.includes("brake") || s.includes("pad") || s.includes("rotor")) return "🛑";
    if (s.includes("filter")) return "🌪️";
    return "📦";
  },

  card(it, box) {
    const self = this;
    const name = it.name || it.code;
    const rate = flt(it.rate) || 0;
    const card = document.createElement("div");
    card.className = "vpos-card";
    card.setAttribute("data-code", it.code);
    const stock = this.STOCK && this.STOCK[it.code] ? this.STOCK[it.code].stock : null;
    const tip = this.STOCK && this.STOCK[it.code] ? this.stockTip(this.STOCK[it.code]) : "";

    let thumbHtml = "";
    if (it.image) {
      thumbHtml = `<div class="vpos-thumb"><img src="${it.image}" alt="${name}" loading="lazy" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\\'vpos-thumb-placeholder\\'><span class=\\'ico\\'>${self.getCategoryIcon(it.group, name)}</span><span>${it.group || 'Product'}</span></div>';"></div>`;
    } else {
      thumbHtml = `<div class="vpos-thumb"><div class="vpos-thumb-placeholder"><span class="ico">${self.getCategoryIcon(it.group, name)}</span><span>${it.group || 'Item'}</span></div></div>`;
    }

    card.innerHTML = `
      ${thumbHtml}
      <div class="vpos-card-name" title="${name}">${name}</div>
      <div class="vpos-card-code">${it.code}</div>
      <div class="vpos-card-stock">${stock == null ? "Stock: …" : "Stock: " + flt(stock)}</div>
      <div class="vpos-card-foot">
        <div class="vpos-card-rate" title="${peso(rate)}">${peso(rate)}</div>
        <button class="vpos-card-add" type="button">+ ADD</button>
      </div>`;

    if (tip) card.setAttribute("data-tip", tip);
    const inc = this.cart.find(c => c.item_code === it.code);
    if (inc) {
      const b = document.createElement("div");
      b.className = "vpos-card-badge";
      b.textContent = inc.qty + " in cart";
      card.appendChild(b);
    }
    card.onclick = () => self.add(it.code, name, rate, it.uom);
    card.querySelector(".vpos-card-add").onclick = (e) => {
      e.stopPropagation();
      self.add(it.code, name, rate, it.uom);
    };
    box.appendChild(card);
  },"""

html = html.replace(old_card_code, new_card_code)

# =========================================================================
# 3. UPGRADE HISTORY TAB: Real-Time Dynamic Fetch, Filters & Refresh
# =========================================================================
old_history_funcs = """  renderHistory() {
    const view = document.getElementById("vpos-view-history");
    if (!view) return;
    const h = this.history || [];
    if (!h.length) { view.innerHTML = '<div class="vpos-empty">No transactions yet recorded.</div>'; return; }
    view.innerHTML = h.map(t => `
      <div class="vpos-hist">
        <div class="vpos-hist-top"><b>${t.name}</b><span>${t.posting_date || ""}</span></div>
        <div class="vpos-hist-sub">${t.customer_name || ""} ${t.vehicle ? "· " + t.vehicle : ""}</div>
        <div class="vpos-hist-foot"><span>${peso(t.total_amount)}</span><span>${t.payment_method || "Cash"}</span></div>
      </div>
    `).join("");
  },"""

new_history_funcs = """  async fetchHistory(params = {}) {
    const view = document.getElementById("vpos-view-history");
    const countEl = document.getElementById("vpos-hist-count");
    const listEl = document.getElementById("vpos-hist-list");
    const refBtn = document.getElementById("vpos-hist-refresh");

    if (refBtn) { refBtn.disabled = true; refBtn.textContent = "⏳ Syncing..."; }
    if (listEl) listEl.innerHTML = '<div class="vpos-empty" style="padding:24px;">🔄 Fetching real-time transactions...</div>';

    this.histPeriod = params.period !== undefined ? params.period : (this.histPeriod || "all");
    this.histFromDate = params.from_date !== undefined ? params.from_date : (this.histFromDate || "");
    this.histToDate = params.to_date !== undefined ? params.to_date : (this.histToDate || "");
    this.histSearch = params.search !== undefined ? params.search : (this.histSearch || "");

    const queryParams = {
      period: this.histPeriod,
      from_date: this.histFromDate,
      to_date: this.histToDate,
      search: this.histSearch,
      company: this.company || ""
    };

    let list = [];
    try {
      list = await api("vehicle_management.vehicle_management.pos_api.get_history", queryParams) || [];
    } catch (e) {
      console.error("fetchHistory error:", e);
    }
    this.history = list;
    if (refBtn) { refBtn.disabled = false; refBtn.textContent = "🔄 Refresh"; }
    this.renderHistoryList();
    return list;
  },

  renderHistory() {
    const view = document.getElementById("vpos-view-history");
    if (!view) return;

    // Render history container shell if not already built
    if (!view.querySelector(".vpos-hist-bar")) {
      const todayIso = new Date().toISOString().split("T")[0];
      view.innerHTML = `
      <div class="vpos-hist-box">
        <div class="vpos-hist-bar">
          <div class="vpos-hist-title">
            <h3>Transaction History</h3>
            <span class="vpos-hist-badge" id="vpos-hist-count">0 invoices</span>
          </div>
          <div class="vpos-hist-controls">
            <div class="vpos-hist-pills" id="vpos-hist-pills">
              <button class="vpos-hist-pill active" data-period="all">All</button>
              <button class="vpos-hist-pill" data-period="today">Today</button>
              <button class="vpos-hist-pill" data-period="month">This Month</button>
            </div>
            <div class="vpos-hist-dates">
              <input type="date" id="vpos-hist-from" class="vpos-hist-dt" title="From Date">
              <span style="font-size:12px;color:var(--muted)">to</span>
              <input type="date" id="vpos-hist-to" class="vpos-hist-dt" title="To Date">
              <button class="vpos-hist-btn primary" id="vpos-hist-apply" style="height:34px">Apply</button>
            </div>
            <button class="vpos-hist-btn" id="vpos-hist-refresh">🔄 Refresh</button>
          </div>
        </div>

        <div class="vpos-hist-search-box">
          <span style="font-size:16px;opacity:.6">🔍</span>
          <input type="text" id="vpos-hist-search" placeholder="Search customer name, vehicle plate, or invoice #...">
        </div>

        <div class="vpos-hist-list" id="vpos-hist-list"></div>
      </div>`;

      // Bind filter pill buttons
      const self = this;
      view.querySelectorAll(".vpos-hist-pill").forEach(p => {
        p.onclick = () => {
          view.querySelectorAll(".vpos-hist-pill").forEach(x => x.classList.remove("active"));
          p.classList.add("active");
          const per = p.getAttribute("data-period");
          self.fetchHistory({ period: per, from_date: "", to_date: "" });
        };
      });

      // Bind date range apply
      const applyBtn = view.querySelector("#vpos-hist-apply");
      if (applyBtn) {
        applyBtn.onclick = () => {
          view.querySelectorAll(".vpos-hist-pill").forEach(x => x.classList.remove("active"));
          const f = (view.querySelector("#vpos-hist-from") || {}).value || "";
          const t = (view.querySelector("#vpos-hist-to") || {}).value || "";
          self.fetchHistory({ period: "custom", from_date: f, to_date: t });
        };
      }

      // Bind refresh button
      const refBtn = view.querySelector("#vpos-hist-refresh");
      if (refBtn) refBtn.onclick = () => self.fetchHistory();

      // Bind search input with debounce
      const sInput = view.querySelector("#vpos-hist-search");
      if (sInput) {
        sInput.oninput = () => {
          clearTimeout(self._histST);
          self._histST = setTimeout(() => {
            self.fetchHistory({ search: sInput.value });
          }, 300);
        };
      }
    }

    // Always trigger a real-time fetch when opening the tab
    this.fetchHistory({ period: this.histPeriod || "all" });
  },

  renderHistoryList() {
    const listEl = document.getElementById("vpos-hist-list");
    const countEl = document.getElementById("vpos-hist-count");
    if (!listEl) return;

    const list = this.history || [];
    if (countEl) countEl.textContent = list.length + (list.length === 1 ? " invoice" : " invoices");

    if (!list.length) {
      listEl.innerHTML = '<div class="vpos-empty" style="padding:40px;background:#fff;border-radius:16px;border:1px solid var(--line);">No transactions found matching the selected filter/date range.</div>';
      return;
    }

    listEl.innerHTML = list.map(t => {
      const isPaid = (t.status === "Paid" || flt(t.paid_amount) >= flt(t.total_amount));
      const posLink = t.pos_invoice ? `<span class="vpos-hist-tag desk-link" onclick="window.open('/desk#Form/POS Invoice/${encodeURIComponent(t.pos_invoice)}', '_blank')">🔗 ${t.pos_invoice}</span>` : "";
      const vehDisplay = (t.plate_no || t.vehicle) ? `🚗 <b>${t.plate_no || t.vehicle}</b>` : "";
      const remDisplay = t.remarks ? `<div style="font-size:11px;color:var(--muted);margin-top:2px;">📝 ${t.remarks}</div>` : "";

      return `
      <div class="vpos-hist-card">
        <div class="vpos-hist-top">
          <div class="vpos-hist-code" onclick="window.open('/desk#Form/Vehicle POS Invoice/${encodeURIComponent(t.name)}', '_blank')" title="Open Vehicle POS Invoice in Desk">${t.name}</div>
          <div class="vpos-hist-time">${t.timestamp || t.posting_date || ""}</div>
        </div>
        <div class="vpos-hist-mid">
          <div class="vpos-hist-cust">${t.customer_name || "Walk-in Customer"}</div>
          <div class="vpos-hist-sub">${vehDisplay} ${t.company ? "· 🏢 " + t.company : ""}</div>
        </div>
        ${remDisplay}
        <div class="vpos-hist-foot">
          <div class="vpos-hist-amt">${peso(t.total_amount)}</div>
          <div class="vpos-hist-tags">
            <span class="vpos-hist-tag">${t.payment_method || "Cash"}</span>
            <span class="vpos-hist-tag ${isPaid ? 'paid' : ''}">${isPaid ? '✓ Paid' : 'Draft'}</span>
            ${posLink}
          </div>
        </div>
      </div>`;
    }).join("");
  },"""

html = html.replace(old_history_funcs, new_history_funcs)

# Update submit() so it immediately re-fetches history in the background upon sale completion
html = html.replace(
    'this.history = await api("vehicle_management.vehicle_management.pos_api.get_history") || this.history;',
    'this.fetchHistory();'
)

# Save to local files
with open('c:/Users/josem/erpnext-system/vps_migration/current_pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/pos_terminal.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('c:/Users/josem/erpnext-system/pos-static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated local files. Saving to Web Page vehicle-pos-terminal...")

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

save_url = 'http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal'
payload = json.dumps({'main_section_html': html}).encode('utf-8')
req = urllib.request.Request(save_url, data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
res = opener.open(req)
print("SUCCESSFULLY saved Web Page vehicle-pos-terminal! Status:", res.status)
