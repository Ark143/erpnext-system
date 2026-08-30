import os, re, collections

app = "/workspace/frappe-bench/apps/erpnext/erpnext"
pats = {
    "limit_a_b (MySQL comma LIMIT)": re.compile(r'limit\s+%\(start\)s\s*,\s*%\(page_len\)s', re.I),
    "limit {start}, {page_len}": re.compile(r'limit\s*\{start\}\s*,\s*\{page_len\}', re.I),
    "ifnull(": re.compile(r'ifnull\s*\('),
    "zero-date 0000-00-00": re.compile(r"'0000-00-00'"),
    "backtick tablename": re.compile(r'`tab'),
    "if( in sql (MySQL ternary)": re.compile(r'\bif\s*\(\s*[a-z_%.\(\)\s]+\s*,\s*[^,]+,\s*[^)]+\)'),
    "group_concat": re.compile(r'group_concat'),
    "regexp ": re.compile(r'regexp\s'),
    "unquoted tabX. colref": re.compile(r'(?<![\"\w])tab[A-Z][A-Za-z]+\.'),
}
counts = collections.Counter()
per_module = collections.defaultdict(collections.Counter)
files_hit = collections.defaultdict(list)

for root, _, files in os.walk(app):
    for fn in files:
        if not fn.endswith(".py"):
            continue
        p = os.path.join(root, fn)
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        mod = os.path.relpath(root, app).split(os.sep)[0]
        for name, rx in pats.items():
            n = len(rx.findall(txt))
            if n:
                counts[name] += n
                per_module[mod][name] += n
                if len(files_hit[name]) < 200:
                    files_hit[name].append(os.path.relpath(p, app))

print("=== TOTAL occurrences per pattern (across erpnext app) ===")
for k, v in counts.most_common():
    print(f"{v:6d}  {k}")
print("\n=== per-module (top patterns) ===")
for mod in sorted(per_module):
    tot = sum(per_module[mod].values())
    print(f"\n[{mod}] total={tot}")
    for k, v in per_module[mod].most_common(6):
        print(f"    {v:5d}  {k}")
