# Deploy ERPNext stack to Podman Pod
$ErrorActionPreference = "Continue"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  DEPLOYING ERPNEXT STACK TO PODMAN" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Cleanup existing pods and containers
Write-Host "`n[1/5] Cleaning up existing pods and containers..." -ForegroundColor Yellow
wsl -d podman-machine-default sudo podman pod rm -f erpnext-pod 2>$null
wsl -d podman-machine-default sudo podman rm -f erp-postgres erp-redis erp-frappe erp-caddy 2>$null

# 2. Create shared Podman Pod with host port-forwarding
Write-Host "`n[2/5] Creating Podman Pod (erpnext-pod)..." -ForegroundColor Yellow
wsl -d podman-machine-default sudo podman pod create --name erpnext-pod -p 80:80 -p 8000:8000 -p 9000:9000 -p 55433:5432 -p 6379:6379

# 3. Start Redis 7 & PostgreSQL 16
Write-Host "`n[3/5] Starting Redis 7 Alpine container..." -ForegroundColor Yellow
wsl -d podman-machine-default sudo podman run -d --name erp-redis --pod erpnext-pod --restart=always docker.io/library/redis:7-alpine

Write-Host "`n[4/5] Starting PostgreSQL 16 container..." -ForegroundColor Yellow
wsl -d podman-machine-default sudo podman run -d --name erp-postgres --pod erpnext-pod --restart=always -e POSTGRES_DB=site1_local -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=admin -v erp_pgdata:/var/lib/postgresql/data docker.io/library/postgres:16-alpine

# 4. Start Frappe Container with live workspace mount
Write-Host "`n[5/5] Starting Frappe server and Realtime Socket.IO..." -ForegroundColor Yellow
wsl -d podman-machine-default sudo podman run -d --name erp-frappe --pod erpnext-pod --restart=always -v /mnt/c/Users/josem/erpnext-system/frappe-bench:/workspace/frappe-bench -v /mnt/c/Users/josem/erpnext-system/entrypoint.sh:/entrypoint.sh:ro localhost/erp-frappe:base

# 5. Start Caddy Reverse Proxy
Write-Host "`nStarting Caddy Reverse Proxy (port 80)..." -ForegroundColor Yellow
wsl -d podman-machine-default sudo podman run -d --name erp-caddy --pod erpnext-pod --restart=always -v /mnt/c/Users/josem/erpnext-system/Caddyfile:/etc/caddy/Caddyfile:ro docker.io/library/caddy:alpine

Write-Host "`n=================================================" -ForegroundColor Green
Write-Host "  PODMAN DEPLOYMENT COMPLETE & RUNNING!" -ForegroundColor Green
Write-Host "  Web Desk:    http://erp.localhost/desk" -ForegroundColor Green
Write-Host "  Login Page:  http://erp.localhost/login" -ForegroundColor Green
Write-Host "  Socket.IO:   http://erp.localhost/socket.io" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
wsl -d podman-machine-default sudo podman ps
