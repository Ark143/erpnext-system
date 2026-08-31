# VPS backup manifest — 2026-09-01 (after desk-crash fix batch)

## Files
- backup_site1_local.dump    (7,845,572 bytes)  PostgreSQL custom-format dump (site1_local) — taken from erpdeploy-postgres-1 via pg_dump -Fc
- bench_sites_backup.tgz      (531,612 bytes)    tar.gz of erpdeploy-erpnext-1 /workspace/frappe-bench/{apps/vehicle_management, sites} (patched app source + site configs)

## How taken
- DB:  docker exec -e PGPASSWORD=... erpdeploy-postgres-1 pg_dump -h 127.0.0.1 -U postgres -d site1_local --no-owner --no-privileges -Fc -f /tmp/backup_site1_local.dump
- App: docker exec erpdeploy-erpnext-1 tar czf /tmp/bench_sites_backup.tgz -C /workspace/frappe-bench apps/vehicle_management sites
- Then docker cp to host /tmp, then pscp to this dir.

## Restore
- DB:  docker exec -i erpdeploy-postgres-1 pg_restore -h 127.0.0.1 -U postgres -d site1_local --no-owner < backup_site1_local.dump
- App: docker cp bench_sites_backup.tgz erpdeploy-erpnext-1:/tmp/ && docker exec erpdeploy-erpnext-1 tar xzf /tmp/bench_sites_backup.tgz -C /workspace/frappe-bench
