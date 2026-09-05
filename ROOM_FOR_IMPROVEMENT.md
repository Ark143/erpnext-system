# erpnext-system — Room for Improvement

> Comprehensive audit: codebase, Docker/VPS deployment, vehicle_management app, web page status, and repo hygiene.
> Generated: 2026-09-06 by autonomous agent sweep.

---

## EXECUTIVE SUMMARY

| Area | Status | Issues | Critical |
|------|--------|--------|----------|
| VPS Live (web pages) | **DOWN** | ALL routes 404 | YES |
| Docker Deployment | Poor | 37 issues | 7 CRITICAL |
| vehicle_management Code | Fair | ~15 issues | 0 CRITICAL, some HIGH |
| Repo Hygiene | Poor | ~600 temp files, SQL dumps committed | HIGH (data exposure) |
| Backups | Weak | 25 identical SQL dumps, no offsite | HIGH |

**Top 3 priorities:**
1. **VPS is down** — all routes 404. Frappe/Caddy not responding to HTTP on the public IP.
2. **Secrets baked into Docker image** — `site_config.json` with passwords and `developer_mode: 1` copied at build time.
3. **600+ dead scripts + SQL dumps in repo** — 280 in pos-static, 121 in frappe-bench, 48MB+ SQL committed to VCS.

---

## 1. VPS LIVE STATUS — ALL PAGES 404

Every URL tested returns **404 page not found** from the Go-level fallback, meaning Caddy isn't routing to Frappe (which would return Frappe's own 404 page, not a Go 404).

### Test Results (VPS: 38.247.138.224)

| URL | Status | Notes |
|-----|--------|-------|
| `/` | 404 | Go default, not Frappe |
| `/executive` | 404 | |
| `/executive-automan-car-care-center` | 404 | |
| `/executive-san-fernando-warehouse` | 404 | |
| `/executive-the-wheelhub` | 404 | |
| `/executive-ultra-mrf` | 404 | |
| `/executive-ultra-mrf-dau-annex` | 404 | |
| `/executive-ultra-mrf-dau-main` | 404 | |
| `/executive-ultra-mrf-mexico-warehouse` | 404 | |
| `/executive-ultra-mrf-san-fernando` | 404 | |
| `/executive-ultra-mrf-telebastagan` | 404 | |
| `/executive-ultra-mrf-telebastagan-2` | 404 | |
| `/executive-ultra-mrf-warehouse-dau` | 404 | |
| `/executive-wheel-core` | 404 | |
| `/pos` | 404 | |
| `/pos-terminal` | 404 | |
| `/login` | 404 | |
| `/desk` | 404 | |
| `/app` | 404 | |

### Root Cause Analysis

- Port 80 is **OPEN** but serving a Go 404 — the container/ERPNext is not running, OR Caddy is not proxying correctly.
- Port 443 is **OPEN** but also returns 404.
- SSH (port 10016) times out — cannot log in to diagnose (sshpass/paramiko not installed on this host).
- Likely causes: (a) ERPNext container crashed/stopped, (b) Caddy container running but upstream `erpnext:8000` unreachable, (c) container recreation lost network bindings.

### Fix
1. SSH in: `ssh -p 10016 administrator@38.247.138.224` (need password or key setup).
2. Run `docker ps -a` to check container states.
3. If stopped: `docker start <erpnext-container>` or `docker-compose -f /workspace/vps_migration/docker-compose.yml up -d`.
4. Check Caddy logs: `docker logs <caddy-container>`.
5. Check Frappe logs: `docker exec <erpnext> cat /workspace/frappe-bench/sites/site1.local/logs/frappe.log`.

---

## 2. DOCKER DEPLOYMENT — 37 ISSUES

### CRITICAL (7)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `docker-compose.yml:6` | Postgres password `postgres` hardcoded | Use Docker Secrets or `.env` excluded from VCS |
| 2 | `docker-compose.yml:37` | ERPNext connects as `postgres` superuser | Create least-privilege DB user |
| 3 | `site_config.json:6` | DB password `postgres` baked into image via COPY | Mount at runtime, don't COPY |
| 4 | `site_config.json:8` | Admin password `admin` hardcoded | Override via env at container start |
| 5 | `site_config.json:12` | `allow_cors: ["*"]` — CSRF bypass risk | Restrict to specific origins |
| 6 | `Dockerfile:32` | `COPY sites/` bakes secrets into image layer | Mount as runtime volume |
| 7 | `restore.sh:15` | `ALTER ROLE site1_local WITH SUPERUSER` | Grant only needed privileges |

### HIGH (10)

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `docker-compose.yml:18` | Redis `--appendonly no`, no volume | Add `redis_data:/data` + enable AOF |
| 2 | `entrypoint.sh:15` | `exec` orphans SocketIO process | Use dumb-init/tinit + trap signals |
| 3 | `entrypoint.sh:19-26` | No init reaper, zombie risk | Same as above |
| 4 | `restore.sh:17` | `DROP DATABASE IF EXISTS` — no guard | Add sentinel file / RESTORE_ONCE=1 guard |
| 5 | `Caddyfile:1` | No TLS/HTTPS — credentials in cleartext | Add domain + automatic HTTPS |
| 6 | `Caddyfile:3` | Hardcoded container IP `10.88.0.50` | Use service name `erpnext:8000` |
| 7 | `Caddyfile:2-7` | Socket.IO missing websocket upgrade headers | Add `header_up Connection "upgrade"` + `Upgrade "websocket"` |
| 8 | `Dockerfile:4` | Base `python:3.14-slim-bookworm` (RC in production) | Pin to `python:3.11-slim-bookworm` |
| 9 | `Containerfile:1` | Base `python:3.14-rc-slim-bookworm` | Pin to stable `3.11` or `3.12` |
| 10 | `site_config.json:11` | `developer_mode: 1` in production | Set to `0` for production |

### MEDIUM (15) + LOW (5)

See `docker-config-audit.json` in repo root for full details with line numbers.

Key themes:
- No security headers in Caddy (X-Frame-Options, CSP, HSTS)
- No backup cron/sidecar container
- `latest` image tag — non-reproducible deploys
- No explicit Docker network isolation
- Redis state lost on restart
- `server_script_enabled: true` + weak admin = code execution path
- SocketIO logs to file with no rotation (disk fill risk)
- `git apply --reject || true` silently ignores patch failures
- `psql -v ON_ERROR_STOP=0` continues through SQL errors
- `PGPASSWORD` exported in env (visible in /proc)
- No `--require-hashes` on pip install
- No integrity check on backup gzip files

---

## 3. VEHICLE_MANAGEMENT APP — CODE QUALITY

### Findings

| Severity | File | Issue | Fix |
|----------|------|-------|-----|
| **HIGH** | `analytics.py:8` | `@frappe.whitelist(allow_guest=True)` exposes customer financial data (revenue, job orders, vehicles) to unauthenticated users | Remove `allow_guest=True`; add `frappe.has_permission()` checks |
| **HIGH** | `detailed_sales_report.py` | Raw psycopg2 connection with hardcoded `user='postgres'` — bypasses Frappe ORM and permissions | Replace with `frappe.db.sql()` |
| **MEDIUM** | `hooks.py` | Missing `after_install` hook for seeding custom fields/default data | Add `after_install` pointing to `vehicle_management.install.after_install` |
| **MEDIUM** | `hooks.py` | `doc_events` on_change fires on every Sales Invoice save | Replace with `on_update` + guard condition |
| **MEDIUM** | `seed_report.py:31` | Debug `print()` statement left in production code | Remove or guard with `if frappe.conf.developer_mode` |
| **MEDIUM** | `seed_probe.py` | Debug script accessible via web context | Move to scheduled job or restrict to developer mode |
| **MEDIUM** | Multiple reports | N+1 query pattern in report `execute()` functions | Use single SQL with JOINs or batch fetches |
| **LOW** | `_vmprobe2.py` | Debug/probe script in app directory | Move out of production app or remove |
| **LOW** | Various | No `after_uninstall` hook for cleanup | Add to remove custom fields/data on uninstall |

---

## 4. REPO HYGIENE — DEAD CODE & BLOAT

### File Counts

| Directory | .py files | Total size | Verdict |
|-----------|-----------|------------|---------|
| `pos-static/` | 280 | 140 MB | **ALL dead code** — temp debug/check scripts |
| `vps_migration/` | 324 | 98 MB | **90% dead** — deploy iterations |
| `frappe-bench/` (root) | 121 | ~50 MB | **95% dead** — scratchpads and test scripts |
| `acct_fix/` | 12 | 285 KB | Keep (real financial fixes) |

### Critical Issues

| Issue | Severity | Fix |
|-------|----------|-----|
| `full_restored.sql` (48 MB) committed to repo root | HIGH (data exposure) | Delete, add `*.sql` to .gitignore |
| `backup_site1_local.sql` (8.8 MB) in repo | HIGH | Delete, add to .gitignore |
| `temp_backup.dump` (6.3 MB) in repo | HIGH | Delete |
| 25 identical SQL backups in `backups/` (~140 MB total) | HIGH (disk waste) | Keep only 1-2 most recent, delete rest |
| `.git` directory is 199 MB | MEDIUM | Run `git gc --aggressive --prune=today`; consider BFG to purge large files from history |
| `*.out`, `*.txt`, `*.md` debug artifacts in `pos-static/` | LOW | Delete all non-code files |
| 93 numbered-variant scripts in `pos-static/` (e.g., `check_cur.py` through `check_cur8.py`) | LOW | Delete all — no production value |

### Cleanup Command

```bash
# Remove dead debug scripts
rm pos-static/*.py pos-static/*.out pos-static/*.txt pos-static/*.md
rm pos-static/csv/* pos-static/doctype_defs/* pos-static/export/*

# Remove duplicate deploy iterations (keep only final versions)
# In vps_migration/: keep only the non-numeric variants
rm vps_migration/*2.py vps_migration/*3.py vps_migration/*4.py vps_migration/*5.py

# Remove SQL dumps from repo
rm backup_site1_local.sql full_restored.sql temp_backup.dump

# Remove frappe-bench scratchpads
rm frappe-bench/_*.py frappe-bench/*.log
```

### Disk Savings

| Action | Est. Savings |
|--------|--------------|
| Delete `pos-static/*.py` + artifacts | ~130 MB |
| Delete `vps_migration` numeric variants + debug files | ~60 MB |
| Delete `frappe-bench` root scratchpads | ~40 MB |
| Delete root SQL dumps | ~63 MB |
| Prune duplicate backups | ~120 MB |
| `.git` repack | ~50-100 MB |
| **Total** | **~400-500 MB** |

---

## 5. SECURITY AUDIT

### Immediate Risks

| Risk | Severity | Evidence |
|------|----------|----------|
| Admin password `admin` | CRITICAL | `site_config.json` — default, unchanged |
| DB password `postgres` | CRITICAL | Multiple files, weak default |
| `developer_mode: 1` | HIGH | Enables debug stack traces |
| `server_script_enabled: true` | HIGH | Arbitrary Python execution from desk |
| `allow_cors: ["*"]` | HIGH | Cross-origin data access |
| DB user has SUPERUSER | CRITICAL | `restore.sh:15` |
| No TLS on public endpoint | HIGH | Plain HTTP on port 80 |
| SQL dumps in repo with customer data | HIGH | `full_restored.sql` 48MB |

### Recommended Actions

1. **Change admin password immediately**: `bench --site site1.local set-admin-password <strong-password>`
2. **Rotate DB password**: Create new role, update `site_config.json`, remount volume
3. **Disable developer_mode**: Set to `0` in site_config
4. **Disable server_scripts** unless actively developing: `bench set-config server_script_enabled false`
5. **Enable HTTPS**: Get a domain, point DNS, let Caddy auto-issue Let's Encrypt
6. **Restrict CORS**: `bench set-config allow_cors '["https://your-domain.com"]'`
7. **Purge SQL dumps from git history**: Use BFG Repo-Cleaner

---

## 6. MISSING / BROKEN FUNCTIONALITY

| Item | Status | Notes |
|------|--------|-------|
| `after_install` hook | MISSING | No custom field seeding on app install |
| `after_uninstall` hook | MISSING | Leaves orphaned custom fields |
| Backup automation | MISSING | No cron/scheduled DB dump on VPS |
| Log rotation | MISSING | `realtime.log` fills disk |
| Health checks on erpnext | MISSING | Docker can't detect app readiness |
| Process supervisor | MISSING | SocketIO orphan risk on restart |
| HTTPS redirect | MISSING | Plain HTTP only |
| Security headers | MISSING | No CSP, HSTS, X-Frame-Options |

---

## 7. RECOMMENDED IMPROVEMENT ROADMAP

### Week 1 — Critical Fixes
- [ ] Fix VPS: SSH in, restart containers, verify Frappe is running
- [ ] Change admin password from `admin` to strong random
- [ ] Change DB password from `postgres` to strong random
- [ ] Set `developer_mode: 0` in production
- [ ] Remove SQL dumps from git history (BFG)
- [ ] Add `*.sql`, `*.sql.gz`, `*.dump` to `.gitignore`

### Week 2 — Deployment Hardening
- [ ] Externalize secrets: don't COPY `site_config.json` at build time
- [ ] Add `dumb-init` as PID 1 in entrypoint
- [ ] Add healthcheck to erpnext service in docker-compose
- [ ] Add websocket upgrade headers to Caddyfile
- [ ] Pin base images to stable Python (3.11/3.12)
- [ ] Add security headers to Caddy

### Week 3 — Repo Cleanup
- [ ] Delete all `pos-static/*.py` (280 debug scripts)
- [ ] Delete duplicate deploy scripts in `vps_migration/`
- [ ] Delete scratchpads in `frappe-bench/` root
- [ ] Prune duplicate backups (keep 2 most recent)
- [ ] Run `git gc --aggressive --prune=today`

### Week 4 — Monitoring & Reliability
- [ ] Add backup cron container (daily pg_dump to offsite)
- [ ] Enable Redis persistence (appendonly yes)
- [ ] Add log rotation for all container logs
- [ ] Set up HTTPS with real domain + Let's Encrypt
- [ ] Add Caddy healthcheck
- [ ] Document runbook for VPS recovery

---

## APPENDIX: KEY FILES REFERENCED

| File | Purpose |
|------|---------|
| `vps_migration/docker-compose.yml` | VPS container orchestration |
| `vps_migration/Dockerfile` | VPS ERPNext image build |
| `vps_migration/Caddyfile` | VPS reverse proxy config |
| `vps_migration/entrypoint.sh` | VPS container startup |
| `vps_migration/restore.sh` | VPS database restore |
| `vps_migration/sites/site1.local/site_config.json` | VPS site config (secrets) |
| `Caddyfile` | Local reverse proxy config |
| `Containerfile` | Local build |
| `entrypoint.sh` | Local container startup |
| `docker-config-audit.json` | Full Docker audit results |
| `frappe-bench/apps/vehicle_management/` | Custom app source |
| `pos-static/` | 280 debug scripts (DELETE) |
| `backups/` | 25 duplicate SQL dumps |

---

*This file is a living document. Update as issues are resolved.*
