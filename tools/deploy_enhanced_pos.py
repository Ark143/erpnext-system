import urllib.request, urllib.parse, json, http.cookiejar
import re
import os

print("="*70)
print("  DEPLOYING ENHANCED SEARCH PREVIEW & COMPACT CATEGORY NAV")
print("="*70)

# ── 1. LOGIN TO VPS ──────────────────────────────────────────────────────────
BASE = "http://38.247.138.224:10017"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f"{BASE}/api/method/login", data=data, headers=H))
print("[+] Authenticated with VPS as Administrator")

# ── 2. READ & PATCH pos_terminal.html ─────────────────────────────────────────
pos_path = r"frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html"
with open(pos_path, "r", encoding="utf-8") as f:
    html = f.read()

# 2A. CSS ENHANCEMENTS
css_styles = r'''
/* ── ENHANCED SEARCH PREVIEW & CATEGORY BAR STYLES ── */
.vpos-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
}

.vpos-scan-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 320px;
  position: relative;
}

.vpos-burger-cat-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #0c1a18;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 12px;
  padding: 0 14px;
  height: 46px;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all .15s ease;
  font-family: var(--font-base);
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.vpos-burger-cat-btn:hover {
  background: var(--mint);
  color: #04201a;
  border-color: var(--mint);
}
.vpos-burger-icon {
  font-size: 15px;
  line-height: 1;
}

.vpos-scan-wrap {
  position: relative;
  flex: 1;
  min-width: 180px;
}

.vpos-scan {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--card);
  border: 1.5px solid var(--line);
  border-radius: 14px;
  padding: 0 14px;
  height: 46px;
  box-shadow: 0 2px 6px rgba(0,0,0,.02);
  transition: all .15s;
}
.vpos-scan:focus-within {
  border-color: var(--mint);
  box-shadow: 0 0 0 3px rgba(22,199,132,0.15);
}

.vpos-search-clear {
  background: none;
  border: none;
  color: var(--muted);
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.vpos-search-clear:hover {
  color: var(--danger);
}

/* Search Live Preview Dropdown */
.vpos-search-preview {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1.5px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(0,0,0,0.16);
  z-index: 1200;
  max-height: 380px;
  overflow-y: auto;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.vpos-prev-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all .12s ease;
  border-bottom: 1px solid #f2f7f5;
  gap: 10px;
}
.vpos-prev-item:last-child {
  border-bottom: none;
}
.vpos-prev-item:hover, .vpos-prev-item.active {
  background: #eef8f4;
  border-color: transparent;
}
.vpos-prev-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}
.vpos-prev-thumb {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #e7f3ef;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  overflow: hidden;
}
.vpos-prev-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.vpos-prev-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.vpos-prev-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--txt);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.vpos-prev-sub {
  font-size: 11px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
.vpos-prev-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.vpos-prev-stock {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
}
.vpos-prev-stock.in-stock {
  background: rgba(22,199,132,0.15);
  color: #0fa76d;
}
.vpos-prev-stock.out-stock {
  background: rgba(239,68,68,0.12);
  color: #ef4444;
}
.vpos-prev-rate {
  font-size: 13.5px;
  font-weight: 800;
  color: var(--txt);
  font-family: var(--font-head);
  min-width: 70px;
  text-align: right;
}
.vpos-prev-add-btn {
  background: var(--mint);
  color: #04201a;
  border: none;
  border-radius: 8px;
  padding: 5px 10px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  transition: transform .1s;
}
.vpos-prev-add-btn:hover {
  background: var(--mint-d);
}

/* Category Bar: Small Buttons, Min 10 on Screen + More Dropdown */
.vpos-cats-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  position: relative;
}

.vpos-cats {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 2px 0 6px;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  flex: 1;
  align-items: center;
}
.vpos-cats::-webkit-scrollbar { display: none; }

.vpos-cat {
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--slate);
  padding: 5px 12px;
  height: 29px;
  line-height: 17px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all .12s ease;
  touch-action: manipulation;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.vpos-cat:hover {
  border-color: var(--mint);
  color: var(--txt);
  background: #f4faf7;
}
.vpos-cat.active {
  background: var(--mint) !important;
  color: #04201a !important;
  border-color: var(--mint) !important;
  font-weight: 800 !important;
}

/* '+ More' Dropdown */
.vpos-cat-more-wrap {
  position: relative;
  flex-shrink: 0;
}
.vpos-cat-more-btn {
  border: 1.5px solid var(--line);
  background: #eef7f3;
  color: var(--mint-d);
  padding: 5px 12px;
  height: 29px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all .12s;
}
.vpos-cat-more-btn:hover, .vpos-cat-more-btn.open {
  background: var(--mint);
  color: #04201a;
  border-color: var(--mint);
}

.vpos-cat-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: #ffffff;
  border: 1.5px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 16px 36px rgba(0,0,0,0.15);
  z-index: 1100;
  min-width: 230px;
  max-height: 320px;
  overflow-y: auto;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.vpos-cat-drop-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--txt);
  cursor: pointer;
  transition: background .12s;
}
.vpos-cat-drop-item:hover {
  background: #eef8f4;
  color: var(--mint-d);
}
.vpos-cat-drop-item.active {
  background: var(--mint);
  color: #04201a;
  font-weight: 800;
}

/* Full Burger Category Drawer / Modal */
.vpos-cat-drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(3px);
  z-index: 2000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 16px;
  animation: vposFadeIn .15s ease-out;
}
@keyframes vposFadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.vpos-cat-drawer {
  background: #ffffff;
  width: 720px;
  max-width: 100%;
  border-radius: 20px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 85vh;
}
.vpos-cat-drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid var(--line);
  background: #f9fcfb;
}
.vpos-cat-drawer-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 800;
  font-family: var(--font-head);
  color: var(--ink);
}
.vpos-cat-total-badge {
  background: #e7f6f0;
  color: var(--mint-d);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}
.vpos-cat-drawer-close {
  background: #eef2f0;
  border: none;
  font-size: 20px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--slate);
  transition: all .12s;
}
.vpos-cat-drawer-close:hover {
  background: var(--danger);
  color: #fff;
}

.vpos-cat-drawer-search {
  padding: 12px 22px;
  background: #ffffff;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  gap: 8px;
}
.vpos-cat-drawer-search input {
  width: 100%;
  height: 38px;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0 12px;
  font-size: 13px;
  outline: none;
  font-family: var(--font-base);
}
.vpos-cat-drawer-search input:focus {
  border-color: var(--mint);
}

.vpos-cat-drawer-grid {
  padding: 18px 22px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 10px;
}
.vpos-drawer-cat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 1.5px solid var(--line);
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all .15s ease;
}
.vpos-drawer-cat-card:hover {
  border-color: var(--mint);
  background: #f4faf7;
  transform: translateY(-1px);
}
.vpos-drawer-cat-card.active {
  background: var(--mint);
  border-color: var(--mint);
  color: #04201a;
  font-weight: 800;
}
.vpos-drawer-cat-card .cat-icon {
  font-size: 18px;
}
.vpos-drawer-cat-card .cat-name {
  font-size: 12.5px;
  font-weight: 700;
}
'''

if "/* ── ENHANCED SEARCH PREVIEW & CATEGORY BAR STYLES ── */" not in html:
    html = html.replace("</style>", f"{css_styles}\n</style>", 1)

# 2B. REPLACE THE TOP SEARCH AND CATEGORY BAR HTML IN POS TEMPLATE
old_bar_pattern = r'''<div class="vpos-bar">[\s\S]*?<div class="vpos-cats" id="vpos-cats"></div>'''
new_bar_html = r'''<div class="vpos-bar">
            <div class="vpos-scan-group">
              <button type="button" class="vpos-burger-cat-btn" id="vpos-burger-cat-btn" title="Open Categories Navigation">
                <span class="vpos-burger-icon">&#9776;</span>
                <span class="vpos-burger-label">Categories</span>
              </button>
              <div class="vpos-scan-wrap">
                <div class="vpos-scan">
                  <span class="ic">&#128269;</span>
                  <input class="vpos-search" placeholder="Scan barcode or type item name / code..." autocomplete="off">
                  <button type="button" class="vpos-search-clear" id="vpos-search-clear" style="display:none;" title="Clear Search">&times;</button>
                </div>
                <div class="vpos-search-preview" id="vpos-search-preview" style="display:none;"></div>
              </div>
            </div>
            <div class="vpos-branch-row">
              <div class="vpos-branch-badge" title="Assigned Cashier Branch">
                <span class="vpos-branch-lbl">&#127970; BRANCH:</span>
                <span class="vpos-branch-val" id="vpos-branch-name">${this.company || "ULTRA MRF"}</span>
              </div>
              <div class="vpos-shift-badge" id="vpos-shift-badge" title="Active Shift & Opening Cash" style="display:flex;align-items:center;gap:6px;background:rgba(22,199,132,0.12);border:1px solid rgba(22,199,132,0.3);border-radius:10px;padding:4px 10px;font-size:11.5px;color:#16c784;font-weight:700;">
                <span>&#128994; SHIFT: <span id="vpos-shift-name-top">${this.openingEntry || 'Active'}</span></span>
                <span style="opacity:0.4">|</span>
                <span>Drawer: <span id="vpos-shift-drawer-top">₱${(this.openingAmount || 0).toLocaleString('en-US', {minimumFractionDigits:2})}</span></span>
                <button type="button" id="vpos-btn-top-close-shift" style="margin-left:4px;background:#f85149;color:#fff;border:none;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;cursor:pointer;">Close Shift</button>
              </div>
              <button class="vpos-stock-toggle" id="vpos-stock-toggle" title="Toggle in-stock filter">In Stock: OFF</button>
            </div>
          </div>
          <div class="vpos-cats-wrapper" id="vpos-cats-wrapper">
            <div class="vpos-cats" id="vpos-cats"></div>
            <div class="vpos-cat-more-wrap" id="vpos-cat-more-wrap" style="display:none;">
              <button type="button" class="vpos-cat-more-btn" id="vpos-cat-more-btn">
                <span>+ More</span> <span class="vpos-cat-more-count" id="vpos-cat-more-count"></span> &#9662;
              </button>
              <div class="vpos-cat-dropdown-menu" id="vpos-cat-dropdown-menu" style="display:none;"></div>
            </div>
          </div>

          <!-- Category Burger Modal Drawer -->
          <div class="vpos-cat-drawer-overlay" id="vpos-cat-drawer-overlay" style="display:none;">
            <div class="vpos-cat-drawer" id="vpos-cat-drawer">
              <div class="vpos-cat-drawer-head">
                <div class="vpos-cat-drawer-title">
                  <span>&#128450;&#65039; All Item Categories</span>
                  <span class="vpos-cat-total-badge" id="vpos-cat-total-badge">0 categories</span>
                </div>
                <button type="button" class="vpos-cat-drawer-close" id="vpos-cat-drawer-close">&times;</button>
              </div>
              <div class="vpos-cat-drawer-search">
                <span class="ic">&#128269;</span>
                <input type="text" id="vpos-cat-drawer-input" placeholder="Search categories..." autocomplete="off">
              </div>
              <div class="vpos-cat-drawer-grid" id="vpos-cat-drawer-grid"></div>
            </div>
          </div>'''

html = re.sub(old_bar_pattern, new_bar_html, html, count=1)

# 2C. REPLACE JAVASCRIPT FOR CATEGORY BAR & SEARCH LIVE PREVIEW
old_load_cat_pattern = r'''async load\(\) \{[\s\S]*?cat\(box, val, label, active\) \{[\s\S]*?box\.appendChild\(b\);\s*\},'''

new_load_cat_js = r'''async load() {
    const meta = await api("vehicle_management.vehicle_management.pos_api.get_meta");
    this.categories = (meta && meta.categories) ? meta.categories : [];
    this.renderCategoryBar();

    // Ensure company is set from cashier employee record or default to ULTRA MRF
    if (!this.company) {
      this.company = "ULTRA MRF";
    }
    const bName = document.getElementById("vpos-branch-name");
    if (bName) bName.textContent = this.company || "All Branches";
    const coFoot = document.getElementById("vpos-co");
    if (coFoot) coFoot.innerHTML = (this.company || "") + "<br>" + (this.cashier || "");
    this.totals();
    this.search();
    this.history = await api("vm_pos_history") || [];
  },

  renderCategoryBar() {
    const box = document.getElementById("vpos-cats");
    const moreWrap = document.getElementById("vpos-cat-more-wrap");
    const moreCount = document.getElementById("vpos-cat-more-count");
    const dropMenu = document.getElementById("vpos-cat-dropdown-menu");
    const drawerGrid = document.getElementById("vpos-cat-drawer-grid");
    const drawerBadge = document.getElementById("vpos-cat-total-badge");

    if (!box) return;
    box.innerHTML = "";
    if (dropMenu) dropMenu.innerHTML = "";
    if (drawerGrid) drawerGrid.innerHTML = "";

    const cats = this.categories || [];
    if (drawerBadge) drawerBadge.textContent = `${cats.length + 1} categories`;

    // 'All Categories' pill
    this.cat(box, "", "All Categories", !this.category);

    // Burger drawer "All Categories" card
    if (drawerGrid) {
      this.createDrawerCatCard(drawerGrid, "", "All Categories", !this.category, "🏠");
    }

    // Minimum 10 categories visible on screen
    const minOnScreen = 10;
    const onScreenCats = cats.slice(0, minOnScreen);
    const overflowCats = cats.slice(minOnScreen);

    onScreenCats.forEach(c => {
      const isActive = (this.category === c);
      this.cat(box, c, c, isActive);
    });

    cats.forEach(c => {
      if (drawerGrid) {
        const icon = this.getCategoryIcon(c, "");
        this.createDrawerCatCard(drawerGrid, c, c, (this.category === c), icon);
      }
    });

    if (overflowCats.length > 0 && moreWrap && dropMenu) {
      moreWrap.style.display = "inline-flex";
      if (moreCount) moreCount.textContent = `(${overflowCats.length})`;

      const activeInOverflow = overflowCats.find(c => c === this.category);
      const moreBtn = document.getElementById("vpos-cat-more-btn");
      if (moreBtn) {
        if (activeInOverflow) {
          moreBtn.classList.add("open");
          moreBtn.innerHTML = `<span>📁 ${activeInOverflow}</span> <span class="vpos-cat-more-count">(${overflowCats.length})</span> &#9662;`;
        } else {
          moreBtn.classList.remove("open");
          moreBtn.innerHTML = `<span>+ More</span> <span class="vpos-cat-more-count">(${overflowCats.length})</span> &#9662;`;
        }
      }

      overflowCats.forEach(c => {
        const d = document.createElement("div");
        d.className = "vpos-cat-drop-item" + (this.category === c ? " active" : "");
        const icon = this.getCategoryIcon(c, "");
        d.innerHTML = `<span>${icon}</span> <span>${c}</span>`;
        d.onclick = (e) => {
          e.stopPropagation();
          this.setCategory(c);
          dropMenu.style.display = "none";
        };
        dropMenu.appendChild(d);
      });
    } else if (moreWrap) {
      moreWrap.style.display = "none";
    }

    // Bind More button dropdown toggle
    const moreBtn = document.getElementById("vpos-cat-more-btn");
    if (moreBtn && dropMenu) {
      moreBtn.onclick = (e) => {
        e.stopPropagation();
        const isOpen = dropMenu.style.display === "flex";
        dropMenu.style.display = isOpen ? "none" : "flex";
      };
    }

    // Bind Burger Category button
    const burgerBtn = document.getElementById("vpos-burger-cat-btn");
    if (burgerBtn) {
      burgerBtn.onclick = (e) => {
        e.stopPropagation();
        this.toggleCategoryDrawer(true);
      };
    }

    // Bind Drawer Close & Search
    const drawerClose = document.getElementById("vpos-cat-drawer-close");
    const drawerOverlay = document.getElementById("vpos-cat-drawer-overlay");
    if (drawerClose) drawerClose.onclick = () => this.toggleCategoryDrawer(false);
    if (drawerOverlay) {
      drawerOverlay.onclick = (e) => {
        if (e.target === drawerOverlay) this.toggleCategoryDrawer(false);
      };
    }

    const drawerInput = document.getElementById("vpos-cat-drawer-input");
    if (drawerInput) {
      drawerInput.oninput = () => {
        this.filterDrawerCategories(drawerInput.value);
      };
    }
  },

  createDrawerCatCard(parent, val, label, active, icon) {
    const card = document.createElement("div");
    card.className = "vpos-drawer-cat-card" + (active ? " active" : "");
    card.innerHTML = `<span class="cat-icon">${icon}</span> <span class="cat-name">${label}</span>`;
    card.onclick = () => {
      this.setCategory(val);
      this.toggleCategoryDrawer(false);
    };
    parent.appendChild(card);
  },

  setCategory(val) {
    this.category = val || null;
    this.renderCategoryBar();
    this.search();
  },

  toggleCategoryDrawer(show) {
    const overlay = document.getElementById("vpos-cat-drawer-overlay");
    if (!overlay) return;
    overlay.style.display = show ? "flex" : "none";
    if (show) {
      const inp = document.getElementById("vpos-cat-drawer-input");
      if (inp) {
        inp.value = "";
        inp.focus();
        this.filterDrawerCategories("");
      }
    }
  },

  filterDrawerCategories(query) {
    const q = (query || "").toLowerCase();
    const cards = document.querySelectorAll("#vpos-cat-drawer-grid .vpos-drawer-cat-card");
    cards.forEach(c => {
      const text = c.textContent.toLowerCase();
      c.style.display = text.includes(q) ? "flex" : "none";
    });
  },

  cat(box, val, label, active) {
    const b = document.createElement("button");
    b.className = "vpos-cat" + (active ? " active" : "");
    b.textContent = label;
    b.setAttribute("data-cat", val);
    b.onclick = () => {
      this.setCategory(val);
    };
    box.appendChild(b);
  },

  handleSearchInput(val) {
    const txt = (val || "").trim();
    const clearBtn = document.getElementById("vpos-search-clear");
    if (clearBtn) clearBtn.style.display = txt ? "flex" : "none";

    clearTimeout(this._searchT);
    clearTimeout(this._previewT);

    if (!txt) {
      this.hideSearchPreview();
      this.search();
      return;
    }

    this._previewT = setTimeout(() => {
      this.showSearchPreview(txt);
    }, 120);

    this._searchT = setTimeout(() => {
      this.search();
    }, 220);
  },

  async showSearchPreview(txt) {
    const previewEl = document.getElementById("vpos-search-preview");
    if (!previewEl) return;

    const items = await api("vm_pos_get_items", {
      txt: txt,
      category: this.category || "",
      company: this.company || "",
      only_stock: this.onlyStock ? 1 : 0,
      limit: 10
    }) || [];

    if (!items.length) {
      previewEl.innerHTML = `<div style="padding:14px;text-align:center;font-size:12.5px;color:var(--muted);">No matching items found for "<b>${esc(txt)}</b>"</div>`;
      previewEl.style.display = "flex";
      this._previewItems = [];
      this._previewIdx = -1;
      return;
    }

    this._previewItems = items;
    this._previewIdx = -1;

    const escapeRegex = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const rx = new RegExp(`(${escapeRegex(txt)})`, "gi");

    previewEl.innerHTML = items.slice(0, 8).map((it, idx) => {
      const highlightedName = (it.name || it.code).replace(rx, '<mark style="background:#bbf7d0;color:#04201a;border-radius:2px;padding:0 2px;">$1</mark>');
      const icon = this.getCategoryIcon(it.group, it.name);
      const st = flt(it.stock != null ? it.stock : (this.STOCK[it.code] || {}).stock);
      const stockHtml = st > 0
        ? `<span class="vpos-prev-stock in-stock">&#10003; ${st} in stock</span>`
        : `<span class="vpos-prev-stock out-stock">Out of stock</span>`;
      const thumb = it.image
        ? `<img src="${it.image}" onerror="this.parentElement.innerHTML='${icon}'">`
        : icon;

      return `
      <div class="vpos-prev-item" data-idx="${idx}" data-code="${esc(it.code)}">
        <div class="vpos-prev-left">
          <div class="vpos-prev-thumb">${thumb}</div>
          <div class="vpos-prev-info">
            <div class="vpos-prev-name">${highlightedName}</div>
            <div class="vpos-prev-sub">
              <span>Code: <b>${it.code}</b></span>
              ${it.group ? `<span>\xb7 ${it.group}</span>` : ''}
            </div>
          </div>
        </div>
        <div class="vpos-prev-right">
          ${stockHtml}
          <div class="vpos-prev-rate">₱${flt(it.rate).toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
          <button type="button" class="vpos-prev-add-btn">+ Add</button>
        </div>
      </div>`;
    }).join("") + `<div style="padding:6px 12px;font-size:11px;color:var(--muted);text-align:right;background:#f9fcfb;border-top:1px solid var(--line);border-radius:0 0 12px 12px;">↵ Press Enter to select · Esc to close</div>`;

    previewEl.style.display = "flex";

    const self = this;
    previewEl.querySelectorAll(".vpos-prev-item").forEach(el => {
      el.onclick = (e) => {
        const idx = parseInt(el.getAttribute("data-idx"), 10);
        const it = self._previewItems[idx];
        if (it) {
          self.add(it);
          self.hideSearchPreview();
        }
      };
    });
  },

  hideSearchPreview() {
    const previewEl = document.getElementById("vpos-search-preview");
    if (previewEl) previewEl.style.display = "none";
    this._previewItems = [];
    this._previewIdx = -1;
  },'''

html = re.sub(old_load_cat_pattern, lambda m: new_load_cat_js, html, count=1)

# 2D. HOOK SEARCH INPUT & EVENT LISTENERS
old_search_listener = r'''r\.querySelector\("\.vpos-search"\)\.addEventListener\("keydown",\s*e\s*=>\s*\{\s*if\s*\(e\.key\s*===\s*"Enter"\)\s*self\.search\(\);\s*\}\);[\s\S]*?self\._searchT\s*=\s*setTimeout\(\(\)\s*=>\s*self\.search\(\),\s*280\);\s*\}\);'''

new_search_listener = r'''const sInput = r.querySelector(".vpos-search");
    if (sInput) {
      sInput.addEventListener("keydown", e => {
        if (e.key === "Escape") {
          self.hideSearchPreview();
        } else if (e.key === "Enter") {
          if (self._previewItems && self._previewItems.length > 0) {
            const chosen = (self._previewIdx >= 0 && self._previewIdx < self._previewItems.length)
              ? self._previewItems[self._previewIdx]
              : self._previewItems[0];
            if (chosen) {
              self.add(chosen);
              self.hideSearchPreview();
              return;
            }
          }
          self.search();
          self.hideSearchPreview();
        } else if (e.key === "ArrowDown") {
          e.preventDefault();
          if (self._previewItems && self._previewItems.length > 0) {
            self._previewIdx = Math.min((self._previewIdx ?? -1) + 1, self._previewItems.length - 1);
            const items = document.querySelectorAll("#vpos-search-preview .vpos-prev-item");
            items.forEach((it, i) => it.classList.toggle("active", i === self._previewIdx));
          }
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          if (self._previewItems && self._previewItems.length > 0) {
            self._previewIdx = Math.max((self._previewIdx ?? 0) - 1, 0);
            const items = document.querySelectorAll("#vpos-search-preview .vpos-prev-item");
            items.forEach((it, i) => it.classList.toggle("active", i === self._previewIdx));
          }
        }
      });

      sInput.addEventListener("input", e => {
        self.handleSearchInput(e.target.value);
      });
    }

    const clearSearchBtn = r.querySelector("#vpos-search-clear");
    if (clearSearchBtn && sInput) {
      clearSearchBtn.onclick = () => {
        sInput.value = "";
        self.handleSearchInput("");
        sInput.focus();
      };
    }

    // Close preview / dropdowns when clicking outside
    document.addEventListener("click", e => {
      if (!e.target.closest(".vpos-scan-group")) {
        self.hideSearchPreview();
      }
      if (!e.target.closest(".vpos-cat-more-wrap")) {
        const drop = document.getElementById("vpos-cat-dropdown-menu");
        if (drop) drop.style.display = "none";
      }
    });'''

html = re.sub(old_search_listener, lambda m: new_search_listener, html, count=1)


# Write local file
with open(pos_path, "w", encoding="utf-8") as f:
    f.write(html)
print("[+] Updated local pos_terminal.html with live search preview & compact category navigation")

# Sync to Live VPS Web Page
req_vpos = urllib.request.Request(
    f"{BASE}/api/resource/Web%20Page/vehicle-pos-terminal",
    data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html})}).encode(),
    headers=H
)
req_vpos.get_method = lambda: 'PUT'
res_vpos = op.open(req_vpos)
print(f"[+] Synced pos_terminal.html to VPS Web Page 'vehicle-pos-terminal' (HTTP {res_vpos.status})")

# Also check Web Page vehicle-pos if separate
try:
    req_vp = urllib.request.Request(
        f"{BASE}/api/resource/Web%20Page/vehicle-pos",
        data=urllib.parse.urlencode({'data': json.dumps({'main_section_html': html})}).encode(),
        headers=H
    )
    req_vp.get_method = lambda: 'PUT'
    res_vp = op.open(req_vp)
    print(f"[+] Synced to VPS Web Page 'vehicle-pos' (HTTP {res_vp.status})")
except Exception as e:
    print(f"[-] Note on vehicle-pos: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. UPDATE ERPNEXT POINT OF SALE (pos_item_selector.js)
# ─────────────────────────────────────────────────────────────────────────────
pos_selector_path = r"frappe-bench\apps\erpnext\erpnext\selling\page\point_of_sale\pos_item_selector.js"
with open(pos_selector_path, "r", encoding="utf-8") as f:
    sel_code = f.read()

# Enhance prepare_dom to include category pills bar
old_dom = r'''prepare_dom\(\) \{
\s*this\.wrapper\.append\(
\s*`<section class="items-selector">
\s*<div class="filter-section">
\s*<div class="label">\$\{__\("All Items"\)\}</div>
\s*<div class="search-field"></div>
\s*<div class="item-group-field"></div>
\s*</div>
\s*<div class="items-container"></div>
\s*</section>`
\s*\);'''

new_dom = r'''prepare_dom() {
		this.wrapper.append(
			`<section class="items-selector">
				<div class="filter-section">
					<div class="label">${__("All Items")}</div>
					<div class="search-field"></div>
					<div class="item-group-field"></div>
				</div>
				<div class="pos-category-pills-bar" style="display:flex;align-items:center;gap:6px;padding:4px 0 8px;overflow-x:auto;scrollbar-width:none;">
					<button class="btn btn-xs btn-default pos-burger-cat-btn" type="button" style="font-size:11.5px;font-weight:700;border-radius:6px;white-space:nowrap;padding:3px 8px;background:#0c1a18;color:#fff;border:none;" title="View all categories">☰ Categories</button>
					<div class="pos-category-pills-list" style="display:flex;gap:5px;align-items:center;"></div>
					<div class="pos-category-more-wrap" style="display:none;position:relative;">
						<button class="btn btn-xs btn-default pos-category-more-btn" type="button" style="font-size:11.5px;font-weight:700;border-radius:6px;white-space:nowrap;padding:3px 8px;background:#eef7f3;color:#0fa76d;">+ More ▾</button>
						<div class="pos-category-more-dropdown" style="display:none;position:absolute;top:100%;right:0;background:#fff;border:1px solid #d1d8dd;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.12);z-index:100;min-width:180px;max-height:240px;overflow-y:auto;padding:4px;"></div>
					</div>
				</div>
				<div class="items-container"></div>
			</section>`
		);'''

sel_code = re.sub(old_dom, new_dom, sel_code, count=1)

with open(pos_selector_path, "w", encoding="utf-8") as f:
    f.write(sel_code)

print("[+] Updated ERPNext Point of Sale pos_item_selector.js")
print("\nSUCCESS: All changes applied & deployed to Vehicle POS and POS Terminal!")
