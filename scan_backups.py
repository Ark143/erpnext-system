import re, os, gzip

def scan_dump(filepath):
    print(f"\n=======================================================")
    print(f"FILE: {filepath} ({os.path.getsize(filepath):,} bytes)")
    print(f"=======================================================")
    
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
    # Check tables with COPY public."tab<Doctype>"
    copy_tables = re.findall(r'COPY public\."(tab[A-Za-z0-9 _]+)"', content)
    insert_tables = re.findall(r'INSERT INTO `?(tab[A-Za-z0-9 _]+)`?', content)
    
    all_tabs = sorted(list(set(copy_tables + insert_tables)))
    print(f"Total tables with data: {len(all_tabs)}")
    
    key_doctypes = [
        'tabCompany', 'tabCustomer', 'tabCustomer Vehicle', 'tabVehicle Job Order',
        'tabVehicle Estimate', 'tabVehicle Inspection', 'tabSales Invoice',
        'tabPurchase Invoice', 'tabPayment Entry', 'tabItem', 'tabWarehouse', 'tabGL Entry'
    ]
    
    for dt in key_doctypes:
        match = re.search(r'COPY public\."' + dt + r'"[^\n]*\n(.*?)\\\.', content, re.DOTALL)
        if match:
            lines = [l for l in match.group(1).strip().split('\n') if l]
            print(f"  {dt:25s} -> {len(lines)} records")
        else:
            # Check INSERT
            ins_count = len(re.findall(r'INSERT INTO `?' + dt + r'`?', content))
            if ins_count > 0:
                print(f"  {dt:25s} -> {ins_count} INSERT statements")
            else:
                print(f"  {dt:25s} -> 0 records")

if __name__ == '__main__':
    backups = [
        r'c:\Users\josem\erpnext-system\backup_site1_local.sql',
        r'c:\Users\josem\erpnext-system\frappe-bench\sites\site1.local\private\backups\20260825_234054-site1.local-database.sql.gz',
        r'c:\Users\josem\erpnext-system\frappe-bench\sites\site1.local\private\backups\20260826_002914-site1.local-POST-CANCELFIX-database.sql.gz',
    ]
    for b in backups:
        if os.path.exists(b):
            scan_dump(b)
