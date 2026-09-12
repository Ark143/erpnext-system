import requests
import json
import re

BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{BASE}/api/method/login", json={"usr": "Administrator", "pwd": "admin"})

print("="*70)
print("  UPDATING VEHICLE POS & ERPNEXT POS TERMINAL")
print("="*70)

# ─────────────────────────────────────────────────────────────────────────────
# 1. UPDATE VEHICLE POS TERMINAL (Web Page `vehicle-pos-terminal`)
# ─────────────────────────────────────────────────────────────────────────────
pos_file = r"frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html"
with open(pos_file, "r", encoding="utf-8") as f:
    html = f.read()

# A. Add CSS styles for Search Preview, Small Category Buttons, + More Dropdown & Burger Drawer
custom_css = r'''
/* ── ENHANCED SEARCH & CATEGORY BAR STYLES ── */
.vpos-scan-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 340px;
  position: relative;
}

.vpos-burger-cat-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #0c1a18;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.1);
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
  min-width: 200px;
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
  transition: border-color .15s;
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

/* Category Pills Bar (Small Buttons, Min 10 on Screen + More Dropdown) */
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

# Insert custom CSS before </style>
if "/* ── ENHANCED SEARCH & CATEGORY BAR STYLES ── */" not in html:
    html = html.replace("</style>", f"{custom_css}\n</style>", 1)

print("[+] Integrated Enhanced CSS into pos_terminal.html")

# Write updated pos_terminal.html locally
with open(pos_file, "w", encoding="utf-8") as f:
    f.write(html)

print("[+] Saved local pos_terminal.html")
