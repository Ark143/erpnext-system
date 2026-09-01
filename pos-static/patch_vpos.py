# -*- coding: utf-8 -*-
import io, sys

path = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/page/vehicle_pos/vehicle_pos.js"

with io.open(path, "r", encoding="utf-8") as f:
    s = f.read()

repls = []

# ---- HTML: sidebar <aside> -> top nav <header> ----
repls.append((
    '\t\t\t<!-- LEFT SIDEBAR -->\n\t\t\t<aside class="vpos-side">',
    '\t\t\t<!-- TOP NAV BAR -->\n\t\t\t<header class="vpos-topnav">'
))

# insert cats strip before the foot inside topnav
repls.append((
    '\t\t\t\t<div class="vpos-side-foot">v1.0 \u00b7 VMS</div>\n\t\t\t</aside>',
    '\t\t\t\t<div class="vpos-topnav-cats">\n\t\t\t\t\t<div class="vpos-cats" id="vpos-cats"></div>\n\t\t\t\t</div>\n\t\t\t\t<div class="vpos-side-foot">v1.0 \u00b7 VMS</div>\n\t\t\t</header>'
))

# remove vpos-cats from the items column (keep id so load_categories still works)
repls.append((
    '\t\t\t\t<div class="vpos-cats" id="vpos-cats"></div>\n\n\t\t\t\t<div class="vpos-products" id="vpos-products"></div>',
    '\t\t\t\t<div class="vpos-products" id="vpos-products"></div>'
))

# ---- CSS: app grid becomes topnav + 50/50 body ----
repls.append((
    '.vpos-app { display: grid; grid-template-columns: 220px 1fr 1fr; height: calc(100vh - 46px); min-height: 520px; }',
    '.vpos-app { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto 1fr; grid-template-areas: "topnav topnav" "main order"; height: calc(100vh - 46px); min-height: 520px; }'
))

# SIDEBAR block -> TOP NAV block
old_sidebar = (
    '\t\t/* SIDEBAR */\n'
    '\t\t.vpos-side { flex: 0 0 220px; grid-column: 1; min-height: 0; overflow-y: auto; background: #ffffff; border-right: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 16px 12px; }\n'
    '\t\t.vpos-brand { display: flex; align-items: center; gap: 10px; padding: 6px 6px 16px; }\n'
    '\t\t.vpos-brand-logo { width: 38px; height: 38px; border-radius: 10px; background: #16a34a; color: #fff; font-weight: 800; font-size: 20px; display: flex; align-items: center; justify-content: center; }\n'
    '\t\t.vpos-brand-name { font-weight: 800; font-size: 15px; color: #0f2e2a; line-height: 1.1; }\n'
    '\t\t.vpos-brand-sub { font-size: 11px; color: #6b9080; }\n'
    '\t\t.vpos-nav { display: flex; flex-direction: column; gap: 4px; margin-top: 8px; }\n'
    '\t\t.vpos-nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: #3d5a54; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; }\n'
    '\t\t.vpos-nav-item:hover { background: #f0faf8; }\n'
    '\t\t.vpos-nav-item.active { background: #16a34a; color: #fff; }\n'
    '\t\t.vpos-nav-ic { font-size: 14px; }\n'
    '\t\t.vpos-side-foot { margin-top: auto; font-size: 11px; color: #9bbdb4; padding: 8px 6px 0; }'
)
new_sidebar = (
    '\t\t/* TOP NAV */\n'
    '\t\t.vpos-topnav { grid-area: topnav; display: flex; align-items: center; gap: 14px; width: 100%; background: #ffffff; border-bottom: 1px solid #d7ecea; padding: 10px 14px; flex-wrap: wrap; }\n'
    '\t\t.vpos-brand { display: flex; align-items: center; gap: 10px; padding: 4px 6px; }\n'
    '\t\t.vpos-brand-logo { width: 38px; height: 38px; border-radius: 10px; background: #16a34a; color: #fff; font-weight: 800; font-size: 20px; display: flex; align-items: center; justify-content: center; }\n'
    '\t\t.vpos-brand-name { font-weight: 800; font-size: 15px; color: #0f2e2a; line-height: 1.1; }\n'
    '\t\t.vpos-brand-sub { font-size: 11px; color: #6b9080; }\n'
    '\t\t.vpos-nav { display: flex; flex-direction: row; gap: 4px; margin-top: 0; flex-wrap: nowrap; overflow-x: auto; }\n'
    '\t\t.vpos-nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: #3d5a54; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; white-space: nowrap; }\n'
    '\t\t.vpos-nav-item:hover { background: #f0faf8; }\n'
    '\t\t.vpos-nav-item.active { background: #16a34a; color: #fff; }\n'
    '\t\t.vpos-nav-ic { font-size: 14px; }\n'
    '\t\t.vpos-topnav-cats { display: flex; align-items: center; flex: 1 1 auto; min-width: 0; overflow: hidden; }\n'
    '\t\t.vpos-side-foot { margin-left: auto; margin-top: 0; font-size: 11px; color: #9bbdb4; padding: 0 6px; white-space: nowrap; }'
)
repls.append((old_sidebar, new_sidebar))

# main + order grid-area
repls.append((
    '.vpos-main { flex: 1 1 auto; grid-column: 2; overflow: hidden; display: flex; flex-direction: column; min-width: 0; padding: 14px 16px; gap: 12px; }',
    '.vpos-main { flex: 1 1 auto; grid-area: main; overflow: hidden; display: flex; flex-direction: column; min-width: 0; padding: 14px 16px; gap: 12px; }'
))
repls.append((
    '.vpos-order { flex: none; grid-column: 3; min-width: 0; overflow-y: auto; background: #ffffff; border-left: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 14px; gap: 12px; }',
    '.vpos-order { flex: none; grid-area: order; min-width: 0; overflow-y: auto; background: #ffffff; border-left: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 14px; gap: 12px; }'
))

# cats: horizontal scroll
repls.append((
    '.vpos-cats { display: flex; gap: 8px; flex-wrap: wrap; }',
    '.vpos-cats { display: flex; gap: 8px; flex-wrap: nowrap; overflow-x: auto; white-space: nowrap; }'
))

# responsive 1024 (2-tab base)
repls.append((
    '\t\t@media (max-width: 1024px) {\n'
    '\t\t\t.vpos-app { grid-template-columns: 200px 1fr 1fr; }\n'
    '\t\t\t.vpos-products { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }\n'
    '\t\t}',
    '\t\t@media (max-width: 1024px) {\n'
    '\t\t\t.vpos-app { grid-template-columns: 1fr 1fr; }\n'
    '\t\t\t.vpos-products { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }\n'
    '\t\t}'
))

# responsive 768 (2-tab base)
old768 = (
    '\t\t@media (max-width: 768px) {\n'
    '\t\t\t.vpos-app { display: flex; flex-direction: column; height: auto; min-height: 0; }\n'
    '\t\t\t.vpos-side { flex: 0 0 auto; width: 100%; flex-direction: row; flex-wrap: wrap; align-items: center; border-right: none; border-bottom: 1px solid #d7ecea; padding: 10px 12px; }\n'
    '\t\t\t.vpos-main { overflow: visible; }\n'
    '\t\t\t.vpos-order { width: 100%; border-left: none; border-top: 1px solid #d7ecea; max-height: 65vh; }\n'
    '\t\t\t.vpos-products { grid-template-columns: repeat(2, 1fr); }\n'
    '\t\t}'
)
new768 = (
    '\t\t@media (max-width: 768px) {\n'
    '\t\t\t.vpos-app { display: grid; grid-template-columns: 1fr; grid-template-rows: auto auto auto; grid-template-areas: "topnav" "main" "order"; height: auto; min-height: 0; }\n'
    '\t\t\t.vpos-topnav { flex-wrap: wrap; }\n'
    '\t\t\t.vpos-nav { flex-wrap: nowrap; }\n'
    '\t\t\t.vpos-topnav-cats { flex-basis: 100%; overflow-x: auto; }\n'
    '\t\t\t.vpos-main { overflow: visible; }\n'
    '\t\t\t.vpos-order { width: 100%; border-left: none; border-top: 1px solid #d7ecea; max-height: 65vh; }\n'
    '\t\t\t.vpos-products { grid-template-columns: repeat(2, 1fr); }\n'
    '\t\t}'
)
repls.append((old768, new768))

# apply + verify each replaced exactly once
for i, (old, new) in enumerate(repls):
    cnt = s.count(old)
    if cnt != 1:
        sys.stderr.write("REPL %d matched %d times (expected 1)\n" % (i, cnt))
        sys.exit(1)
    s = s.replace(old, new)

with io.open(path, "w", encoding="utf-8") as f:
    f.write(s)

sys.stdout.write("OK: all %d replacements applied exactly once\n" % len(repls))
