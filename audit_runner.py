"""Compatibility entry point for the corrected, read-only scoped audit."""
from tools.audit_verified import main

if __name__ == "__main__":
    raise SystemExit(main())
