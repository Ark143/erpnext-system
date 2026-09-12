#!/usr/bin/env bash
# Scoped read-only audit. Credentials must come from ERPNEXT_PASSWORD.
set -euo pipefail
cd "$(dirname "$0")"
exec "${PYTHON:-python}" audit_comprehensive.py "$@"
