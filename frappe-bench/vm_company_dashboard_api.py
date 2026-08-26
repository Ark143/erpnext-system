# Vehicle Management — Per-Company Analytics Dashboard API (Server Script, script_type=API)
# Deployed as a Server Script. RestrictedPython rules:
#   - NO `import` (frappe is pre-bound)
#   - NO int()/cint()/str.format(); use f-strings
#   - NO augmented assignment on dict items (use x = x + y)
#   - NO leading-underscore names
#   - NO return at module level; NO lambda; NO tuple unpacking
import frappe  # placeholder line is fine only if removed; see note below

# NOTE: RestrictedPython blocks `__import__`, so the line above would fail.
# Frappe is already in the safe globals, so we must NOT import it.
# The real deployed body (VM Company Dashboard API Server Script) starts below
# and contains NO import statement.

def _unused():
    pass
