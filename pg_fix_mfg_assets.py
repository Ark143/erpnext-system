#!/usr/bin/env python
"""
Convert MySQL SQL dialect -> PostgreSQL in ERPNext manufacturing/assets/
projects/setup/utilities/startup files.

Scope (SQL-string-only conversions):
  1. ifnull( / IFNULL(  -> coalesce(      (NOT pypika's CamelCase IfNull()
  2. '0000-00-00'       -> '0001-01-01'
  3. MySQL if(a,b,c) in SQL -> CASE WHEN a THEN b ELSE c END
  4. locate(x, y)       -> strpos(y, x)
  5. bare "" empty-string literal inside SQL -> ''  (Postgres treats "" as a
     zero-length delimited identifier and errors out)
"""

import difflib
import py_compile
import re

BASE = "/workspace/frappe-bench/apps/erpnext/erpnext"

FILES = [
    "manufacturing/doctype/job_card/job_card.py",
    "manufacturing/doctype/work_order/work_order.py",
    "assets/doctype/asset/asset.py",
    "assets/doctype/asset_depreciation_schedule/deppreciation_schedule_controller.py",
    "assets/doctype/location/location.py",
    "projects/doctype/activity_cost/activity_cost.py",
    "setup/doctype/company/company.py",
    "utilities/naming.py",
    "startup/boot.py",
]

# lowercase/UPPERCASE ifnull only -- never pypika's `IfNull(`
RE_IFNULL = re.compile(r"\b(?:ifnull|IFNULL)\s*\(")
RE_ZERODATE = re.compile(r"0000-00-00(?:\s+00:00:00)?")
RE_LOCATE = re.compile(r"\b(?:locate|LOCATE)\s*\(")
RE_MYSQL_IF = re.compile(r"(?<![A-Za-z0-9_.])(?:if|IF)\s*\(")
# coalesce(col, "") / = "" style empty double-quoted SQL literal
RE_EMPTY_DQ = re.compile(r'(coalesce\s*\([^()]*?,\s*)""(\s*\))')

results = []

for rel in FILES:
    path = f"{BASE}/{rel}"
    with open(path, encoding="utf-8") as fh:
        orig = fh.read()

    text = orig
    counts = {}

    text, n = RE_IFNULL.subn("coalesce(", text)
    counts["ifnull->coalesce"] = n

    text, n = RE_ZERODATE.subn("0001-01-01", text)
    counts["0000-00-00->0001-01-01"] = n

    # report-only detectors (converted manually if found)
    counts["locate( found"] = len(RE_LOCATE.findall(text))
    counts["mysql if( found"] = len(RE_MYSQL_IF.findall(text))

    text, n = RE_EMPTY_DQ.subn(r"\1''\2", text)
    counts['empty "" -> \'\''] = n

    changed = text != orig
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    # verify
    try:
        py_compile.compile(path, doraise=True)
        compiled = "OK"
    except Exception as exc:  # noqa: BLE001
        compiled = f"FAIL: {exc}"

    diff = ""
    if changed:
        diff = "".join(
            difflib.unified_diff(
                orig.splitlines(keepends=True),
                text.splitlines(keepends=True),
                fromfile=rel,
                tofile=rel + " (patched)",
                n=1,
            )
        )

    results.append((rel, counts, changed, compiled, diff))

print("=" * 78)
for rel, counts, changed, compiled, diff in results:
    total = counts["ifnull->coalesce"] + counts["0000-00-00->0001-01-01"] + counts['empty "" -> \'\'']
    if not changed:
        print(f"{rel}\n    no SQL ifnull / zero-date / locate / if() -- SKIPPED   py_compile={compiled}")
    else:
        summary = ", ".join(f"{k}={v}" for k, v in counts.items() if v)
        print(f"{rel}\n    CHANGED ({total} edits): {summary}\n    py_compile={compiled}")
    if diff:
        for line in diff.splitlines():
            print("      " + line)
    print("-" * 78)
