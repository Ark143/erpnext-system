"""
Comprehensive Code Review and Syntax Validation for vehicle_management and customizations.
"""

import os
import sys
import json
import ast
import subprocess

bench_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(bench_dir, "apps", "vehicle_management")

errors = []
warnings = []
passed = []

print("=" * 60)
print("  COMPREHENSIVE CODE REVIEW & SYNTAX VALIDATION")
print("=" * 60)

# 1. Check all JavaScript files
print("\n[1/4] Checking JavaScript files...")
for root, _, files in os.walk(app_dir):
    for f in files:
        if f.endswith(".js"):
            js_path = os.path.join(root, f)
            rel_path = os.path.relpath(js_path, bench_dir)
            try:
                res = subprocess.run(["node", "--check", js_path], capture_output=True, text=True)
                if res.returncode != 0:
                    errors.append(f"JS Syntax Error in {rel_path}:\n{res.stderr.strip()}")
                    print(f"  [FAIL] {rel_path}")
                else:
                    passed.append(rel_path)
                    print(f"  [PASS] {rel_path}")
            except Exception as e:
                errors.append(f"Could not run node check on {rel_path}: {e}")

# 2. Check all Python files
print("\n[2/4] Checking Python files...")
for root, _, files in os.walk(app_dir):
    for f in files:
        if f.endswith(".py"):
            py_path = os.path.join(root, f)
            rel_path = os.path.relpath(py_path, bench_dir)
            try:
                with open(py_path, "r", encoding="utf-8") as f_obj:
                    ast.parse(f_obj.read(), filename=py_path)
                passed.append(rel_path)
                print(f"  [PASS] {rel_path}")
            except SyntaxError as e:
                errors.append(f"Python Syntax Error in {rel_path} (Line {e.lineno}): {e.msg}")
                print(f"  [FAIL] {rel_path}")

# 3. Check all JSON files
print("\n[3/4] Checking JSON files...")
for root, _, files in os.walk(app_dir):
    for f in files:
        if f.endswith(".json"):
            json_path = os.path.join(root, f)
            rel_path = os.path.relpath(json_path, bench_dir)
            try:
                with open(json_path, "r", encoding="utf-8") as f_obj:
                    data = json.load(f_obj)
                # Check for doctype json structure if applicable
                if "doctype" in data and "fields" in data:
                    fieldnames = [f.get("fieldname") for f in data.get("fields", []) if f.get("fieldname")]
                    if len(fieldnames) != len(set(fieldnames)):
                        dups = [x for x in fieldnames if fieldnames.count(x) > 1]
                        warnings.append(f"Duplicate fieldname(s) in DocType {data.get('name')}: {set(dups)}")
                passed.append(rel_path)
                print(f"  [PASS] {rel_path}")
            except json.JSONDecodeError as e:
                errors.append(f"JSON Syntax Error in {rel_path} (Line {e.lineno}): {e.msg}")
                print(f"  [FAIL] {rel_path}")

# 4. Check Frappe connection & DocType database sanity
print("\n[4/4] Checking Frappe Database & DocType Sanity...")
try:
    sys.path.insert(0, os.path.join(bench_dir, "apps", "frappe"))
    sys.path.insert(0, os.path.join(bench_dir, "apps", "erpnext"))
    sys.path.insert(0, os.path.join(bench_dir, "apps", "vehicle_management"))
    import frappe
    os.chdir(os.path.join(bench_dir, "sites"))
    frappe.init("site1.local")
    frappe.connect()

    for dt in ["Vehicle Job Order", "Customer Vehicle", "Vehicle Make", "Vehicle Model", "Vehicle Inspection", "Job Order Service Item", "Job Order Part Item"]:
        if not frappe.db.exists("DocType", dt):
            errors.append(f"DocType '{dt}' is missing from the database!")
        else:
            meta = frappe.get_meta(dt)
            print(f"  [PASS] DocType '{dt}' is valid (Fields: {len(meta.fields)})")
except Exception as e:
    errors.append(f"Frappe connection/meta check failed: {e}")

print("\n" + "=" * 60)
print(f"SUMMARY: {len(passed)} passed, {len(errors)} error(s), {len(warnings)} warning(s)")
print("=" * 60)

if errors:
    print("\nERRORS FOUND:")
    for err in errors:
        print(f" - {err}")

if warnings:
    print("\nWARNINGS:")
    for warn in warnings:
        print(f" - {warn}")
