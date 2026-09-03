"""Fix 'Identifier PESO already declared' double-execution error.

Inline <script> blocks in Web Page main_section_html declare top-level
`const`/`let` (PESO, peso, SERIES, COMPANY, etc.). When the desk's HTML/Markdown
editor re-renders the preview (or the script is re-evaluated), the second
top-level `const`/`let` throws a SyntaxError. `var` redeclaration is a silent
no-op, so converting top-level const/let -> var makes re-execution safe without
changing single-execution semantics.

Backup-first, then fix each published Web Page's inline scripts, then verify.
"""
import requests, json, re, urllib.parse, time

BASE = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{BASE}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

r = s.get(f'{BASE}/api/resource/Web%20Page?limit_page_length=200&fields=[%22name%22,%22published%22]', timeout=30)
pages = r.json()['data']
print(f'Total Web Pages: {len(pages)}')

TOPLEVEL_DECL = re.compile(r'^(const|let)\s+[A-Za-z_$]')


def fix_script_toplevel(html):
    """Convert top-level (column 0) const/let -> var inside <script> blocks."""
    def repl(m):
        script = m.group(0)
        open_tag = re.match(r'<script[^>]*>', script).group(0)
        body = script[len(open_tag):-len('</script>')]
        lines = body.split('\n')
        out = []
        for ln in lines:
            if TOPLEVEL_DECL.match(ln):
                ln = re.sub(r'^(const|let)\s+', 'var ', ln, count=1)
            out.append(ln)
        return open_tag + '\n'.join(out) + '</script>'
    return re.sub(r'<script[^>]*>.*?</script>', repl, html, flags=re.DOTALL)


# 1. backup
backup = {}
for p in pages:
    try:
        doc = s.get(f"{BASE}/api/resource/Web%20Page/{urllib.parse.quote(p['name'])}", timeout=30).json()['data']
        backup[p['name']] = doc.get('main_section_html') or ''
    except Exception:
        pass
bk_file = rf'c:\Users\josem\erpnext-system\vps_migration\backups\webpages_main_section_html_backup_{int(time.time())}.json'
with open(bk_file, 'w', encoding='utf-8') as f:
    json.dump(backup, f, indent=2, ensure_ascii=False)
print(f'Backed up {len(backup)} Web Pages -> {bk_file}')

# 2. fix changed pages
changed = 0
for p in pages:
    try:
        doc = s.get(f"{BASE}/api/resource/Web%20Page/{urllib.parse.quote(p['name'])}", timeout=30).json()['data']
    except Exception:
        continue
    html = doc.get('main_section_html') or ''
    new_html = fix_script_toplevel(html)
    if new_html == html:
        continue
    # PUT back
    payload = {'main_section_html': new_html}
    try:
        pr = s.put(f"{BASE}/api/resource/Web%20Page/{urllib.parse.quote(p['name'])}", json=payload, timeout=60)
        if pr.status_code in (200, 201):
            changed += 1
            # count conversions
            n = len(re.findall(r'^(const|let)\s+', html, flags=re.MULTILINE)) - \
                len(re.findall(r'^(const|let)\s+', new_html, flags=re.MULTILINE))
            print(f'  FIXED {p["name"]}: {n} top-level const/let -> var (HTTP {pr.status_code})')
        else:
            print(f'  FAIL {p["name"]}: HTTP {pr.status_code} {pr.text[:200]}')
    except Exception as e:
        print(f'  ERROR {p["name"]}: {e}')

print(f'\nChanged {changed} Web Pages.')

# 3. verify: no page should still have top-level const PESO
print('\n=== VERIFY (remaining top-level const/let PESO) ===')
for p in pages:
    try:
        doc = s.get(f"{BASE}/api/resource/Web%20Page/{urllib.parse.quote(p['name'])}", timeout=30).json()['data']
    except Exception:
        continue
    html = doc.get('main_section_html') or ''
    if re.search(r'^(const|let)\s+PESO\b', html, flags=re.MULTILINE):
        print(f'  STILL BROKEN: {p["name"]}')
print('  (no output above = all clear)')
