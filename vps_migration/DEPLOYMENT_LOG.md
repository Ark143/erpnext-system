# ERPNext → VPS Docker Deployment — Status & Issue Log

## Goal
Deploy the local erpnext-system (Frappe v16 / ERPNext v16 / Postgres) to a new VPS
via Docker, public-facing, so the user can show a client the ERP is working.
Full data migration: web pages, POS, vehicle_management, master data, Postgres patches.

## VPS
- IP: 38.247.138.224 (public, NAT gateway)
- SSH: port 10016, user `administrator`, host key SHA256:6oUCxFvQWMVXSGtz/JycJgEt7X2xn5DIQOaVfmHRFpM
- Guest NIC: 192.168.122.27 (libvirt/KVM private subnet, gateway 192.168.122.1)
- OS: Ubuntu 24.04 LTS, 2 vCPU / 3.8 GB RAM / 63 GB disk
- Docker 29.7.2, Compose v5.5.0

## What's DONE (verified)
1. Docker + compose installed.
2. Local data extracted from the Podman bench:
   - site1_local (Postgres 18) full dump → plain-SQL `site1_local.sql` (54.6 MB, version-independent)
   - Postgres source patches: `erpnext.patch` (39 files) + `frappe.patch` (4 files)
   - vehicle_management app tarball (with app_icon fix)
   - site public files (logo/favicon)
3. Image built on VPS: `erpnext-v16:latest` (6.13 GB) — clone frappe/erpnext at exact refs
   (frappe 5cba016e, erpnext b24c9eba), apply patches, install vehicle_management, yarn install.
4. DB restored on VPS — counts verified MATCH local:
   Customer 39466, Item 10531, Customer Vehicle 38654, Web Page 18, Server Script 10,
   Workspace 20, Vehicle Make 71, Vehicle POS Invoice 5.
5. migrate + assets build (BUNDLE DONE) + public files restored.
6. Full stack running: postgres + redis + erpnext + caddy.
7. INTERNAL serving verified (all 200):
   /login, /desk (301), /api/method/ping (pong), /api/method/login (Logged In),
   /pos-terminal, /vehicle-pos, /files/ultra_mrf_logo.png.

## BLOCKER (external reachability) — provider port-forward missing
- Public 80/443 return a bare `404 page not found` (Go http.NotFound style, NO `Server: Caddy`
  and NO `Via` header). Confirmed from BOTH my machine AND from inside the VPS
  (`curl http://38.247.138.224/api/method/ping` → 404), while `curl http://localhost/...`
  → 200 `Via: 1.1 Caddy`. So public 80/443 do NOT reach the caddy container.
- SSH works on public 10016 → internal 22, proving the provider NATs specific ports only.
- FIX (provider-side, cannot be done from guest): add port-forwards in the provider panel:
    TCP 80  → 192.168.122.27:80   (HTTP)
    TCP 443 → 192.168.122.27:443  (HTTPS, later)
  OR tell us the public port already mapped to the guest's :80 and we bind caddy there.

## Build/restore pitfalls fixed during this deploy (for future reuse)
1. air-datepicker yarn SSH dep → set `git config --global url."https://github.com/".insteadOf "ssh://git@github.com/"` AND regenerate patches WITHOUT yarn.lock noise (the source bench's `git diff` included a yarn.lock change that forced `git+ssh://` on air-datepicker).
2. **LOGIN UI BROKEN = missing asset bundles.** Symptom: login page HTML references `.bundle.<HASH>.css/js` but all return 404; `assets.json` lists hashes but the `sites/assets/*/dist/` files don't exist. Root cause: `frappe.build.bundle(mode="production")` (and `bench build`, which silently no-ops as root) only run the erpnext **banking** Vite sub-build — they do NOT emit the core frappe/erpnext bundles. FIX: run the real esbuild directly in each app: `cd apps/frappe && yarn run production` (emits frappe/dist/css|js/*) and `cd apps/erpnext && yarn run production`. Then the login page picks up new hashes and all assets serve 200. VERIFY with a per-asset curl loop over the login page's href/src refs.
3. Postgres 18 (local) vs 16 (VPS) dump incompatibility → `pg_restore: unsupported version (1.15)`.
   Fix: re-dump local with plain SQL (`pg_dump --no-owner --no-privileges --no-comments`), restore with `psql -f`. Custom `-Fc` format is NOT cross-version.
3. psql/restore needs `export PGPASSWORD=postgres` (postgres:16 image has no trust auth).
4. `bench install-app` / `bench migrate` crash as root (drop_privileges / getpwnam) → run via direct python (`frappe.init` + `SiteMigration().run` / `install_app`).
5. frappe serve crashes if `/workspace/frappe-bench/logs` missing (cssutils.log FileNotFound) → entrypoint must `mkdir -p /workspace/frappe-bench/logs`.

## Post-deploy fixes (2026-09-01)
6. **`/desk/vehicle_pos` renders BLANK.** Root cause: `page_js` commented out in hooks.py AND no
   `public/js/vehicle_pos.js` copy — Frappe serves a custom-app Page ONLY as a built/static asset,
   so the page loaded with NO JS. FIX (apply in BOTH the VPS container and the local repo):
   (a) `cp page/vehicle_pos/vehicle_pos.js public/js/vehicle_pos.js`;
   (b) `page_js = {"vehicle_pos": "public/js/vehicle_pos.js"}` in hooks.py;
   (c) add `app_icon = "fa fa-car"` (fixes sidebar "Icon not configured"). Then restart container +
   `redis-cli FLUSHALL`. VERIFY `curl -s -o /dev/null -w '%{http_code}' .../assets/vehicle_management/js/vehicle_pos.js` → 200.
7. **POS transaction blocked: "POS Opening Entry ... is outdated"** (VMS blocker #6). The stale open
   `POS-OPE-2026-00002` (period_start_date yesterday) blocks new POS Invoices. FIX (after a DB backup):
   `UPDATE "tabPOS Opening Entry" SET docstatus=2, status='Closed' WHERE name='POS-OPE-2026-00002' AND status='Open';`
   Then `create_from_pos` works → Vehicle POS Invoice VMSPOS-2026-00006 + linked POS Invoice ACC-PSINV-2026-00004.
   Note: dump with `erpdeploy-postgres-1` (PG16 pg_dump), NOT erpnext-1 (its pg_dump is v15 → version mismatch).
8. **Master data is GLOBAL (no company field on Item/Customer/Supplier)** — confirmed no `company`
   column exists, so all masters visible to all companies. User Permissions (6 rows) are all `allow`,
   none deny. No cross-company restriction. Verified counts: Item 10531, Customer 39466, Supplier 832,
   Customer Vehicle 38654, all P2P/O2C/VMS doctypes readable.
9. **socket.io 502** — entrypoint.sh referenced `/usr/local/bin/node` (wrong; node is at `/usr/bin/node`
   in this image). Fixed to `/usr/bin/node`; socketio serves 200.
10. **"VehiclePOS already declared"** — `page_js` static-serve caused a double-load with the desk's
    developer-mode page serving. FIX: keep `page_js` COMMENTED OUT; developer_mode=1 serves
    `page/vehicle_pos/vehicle_pos.js` directly. (Earlier fix #6 was WRONG and was reverted in commit 19921c7.)
11. **`/desk/vehicle_pos` customer↔vehicle linking bug** — replaced the desk page's own POS impl with the
    full web POS terminal (Web Page vehicle-pos-terminal, route /pos-terminal) in an iframe. Desk route now
    reuses the proven SPA. Commit 541b3bb.
12. **Cashier ID tab fixes (Web Page main_section_html)** — (a) company logo `/files/ultra_mrf_logo.png`
    replaces the "V" placeholder in the profile card, the HTML ID card, AND the download SVG (embedded as a
    base64 data URL). (b) responsive rules so the ID card fits mobile/tablet/pc without scroll
    (`@media (max-width:768px)` sets `.vpos-idcard{width:100%;aspect-ratio:85.6/54}`). (c) print + download
    already existed. PITFALL: inserting a base64 data URL into the SPA's JS string via Python `repr()` broke
    the single-quoted string literal (`href='data:...` → bare identifier). Use DOUBLE quotes around the data
    URL inside the JS string, and ALWAYS validate the served page's <script> blocks with
    `node -e 'new Function(s)'` after any string patch.

13. **Desk crash: `TypeError: Cannot read properties of undefined (reading 'toLowerCase')`**
    at `slug` / `generate_route`.** Root cause: the "Vehicle Management" workspace `content` JSONB
    had a card `{"type":"card","data":{"card_name":"POS"}}` but no Workspace Card/Shortcut named "POS"
    existed, so `frappe.utils.generate_route()` got an item with no `type` and crashed on
    `item.type.toLowerCase()`. FIX: create a real "POS" Workspace Shortcut (type Page → vehicle_pos)
    and rewrite the content JSON to reference it as `shortcut_name`. VERIFY with
    `frappe.get_all("Workspace Shortcut")` that every `shortcut_name` in the content resolves.

14. **Second contributor to the same desk crash: orphaned "Welcome Workspace" sidebar link.**
    `auto_generate_sidebar_from_module()` builds a sidebar Link item for EVERY Workspace in a module,
    INCLUDING "Welcome Workspace" (module Core). But `get_desktop_page()` EXCLUDES "Welcome Workspace"
    from `frappe.workspaces` (desktop.py:402 `page.title != "Welcome Workspace"`). So the sidebar has a
    "Welcome Workspace" Workspace link whose route target is absent from `frappe.workspaces` →
    `frappe.workspaces[slug]` undefined → `slug(undefined)` crash in `get_route`/`DesktopIconGrid`.
    FIX: skip "Welcome Workspace" in `create_sidebar_items()` (workspace_sidebar.py):
    `if entity_lower == "workspace" and item == "Welcome Workspace": continue`.
    VERIFY: boot `workspace_sidebar_item` no longer contains it (`NO (clean)`).
    NOTE: `frappe.workspaces` global at runtime is a SLUG-KEYED map (not `{pages:...}`) — confirmed via
    browser `Object.keys(frappe.workspaces)` = build,home,vehicle-management,... (19 entries, all titled).

15. **`route_history.deferred_insert` returns 400** — harmless best-effort route-history log quirk;
    `tabRoute History` table exists; not a functional bug. Ignore.

## Files (local)
- C:/Users/josem/erpnext-system/vps_migration/  (Dockerfile, docker-compose.yml, Caddyfile,
  entrypoint.sh, restore.sh, build_prep.sh, requirements.txt, artifacts/, sites/)
- On VPS: ~/erpdeploy/  (same set)
