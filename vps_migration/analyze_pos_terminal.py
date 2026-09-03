import re

with open(r'c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\pos_terminal.html', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find all API calls
api_calls = re.findall(r'api\(["\'](.*?)["\']', content)
print('All API calls (unique):')
for a in sorted(set(api_calls)):
    print(' ', a)

# Find keywords related to opening/shift
print()
print('Lines with shift/company/opening/cashier/pos_profile keywords:')
keywords = ['get_cashier', 'shift', 'company', 'pos_profile', 'opening', 'cashier']
for i, line in enumerate(lines, 1):
    lower = line.lower()
    if any(kw in lower for kw in keywords):
        print(f'  L{i}: {line.strip()[:120]}')
