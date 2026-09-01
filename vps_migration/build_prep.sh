#!/bin/bash
# Build the ERPNext v16 image on the VPS: clone frappe/erpnext at the exact
# refs the source bench used, apply the Postgres patches, copy in the
# vehicle_management app, install everything editable, then commit as an image.
set -euo pipefail

BENCH=/workspace/frappe-bench
FRA="5cba016e86b54b57f34a3864282b92300ef20fb0"   # frappe HEAD on source bench
ERP="b24c9eba551905e256e336ff170a91a92d197a2f"   # erpnext HEAD on source bench

# Rewrite GitHub SSH URLs to HTTPS so yarn can fetch git deps without a key
git config --global url."https://github.com/".insteadOf "ssh://git@github.com/"
git config --global url."https://github.com/".insteadOf "git@github.com:"

mkdir -p "$BENCH/apps"
cd "$BENCH"

# ---- frappe + erpnext at exact refs ----
if [ ! -d apps/frappe/.git ]; then
  git clone --filter=blob:none --no-checkout https://github.com/frappe/frappe.git apps/frappe
  (cd apps/frappe && git checkout "$FRA")
fi
if [ ! -d apps/erpnext/.git ]; then
  git clone --filter=blob:none --no-checkout https://github.com/frappe/erpnext.git apps/erpnext
  (cd apps/erpnext && git checkout "$ERP")
fi

# ---- apply the user's Postgres patches (extracted from the source bench) ----
echo ">> applying frappe.patch"
(cd apps/frappe && git apply --reject /tmp/artifacts/frappe.patch || true)
echo ">> applying erpnext.patch"
(cd apps/erpnext && git apply --reject /tmp/artifacts/erpnext.patch || true)

# ---- vehicle_management app ----
rm -rf apps/vehicle_management
mkdir -p apps/vehicle_management
tar xzf /tmp/artifacts/vm_app.tgz -C apps/vehicle_management

# ---- install editable ----
pip install --no-deps -e apps/frappe -e apps/erpnext -e apps/vehicle_management

# ---- node deps for frappe + erpnext (yarn) ----
cd apps/frappe && yarn install --frozen-lockfile || yarn install
cd ../erpnext && yarn install --frozen-lockfile || yarn install

echo "BUILD_PREP_DONE"
