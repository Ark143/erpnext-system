#!/bin/bash
BASE="http://38.247.138.224:10017"
CK="/tmp/ck_audit.txt"
rm -f "$CK"
curl -s -c "$CK" -X POST "$BASE/api/method/login" -H "Content-Type: application/json" -d '{"usr":"administrator","pwd":"admin"}' >/dev/null

N=0
add() { N=$((N+1)); echo "ISS-$N|$1|$2|$3|$4"; }

echo "=== START AUDIT $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

echo "--- MASTER DATA ---"
curl -s -b "$CK" "$BASE/api/resource/Company?limit_page_length=20&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Companies: {len(d)}')" 2>/dev/null
curl -s -b "$CK" "$BASE/api/resource/Customer?limit_page_length=5&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Customers: {len(d)}')" 2>/dev/null
curl -s -b "$CK" "$BASE/api/resource/Supplier?limit_page_length=5&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Suppliers: {len(d)}')" 2>/dev/null
curl -s -b "$CK" "$BASE/api/resource/Item?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Items: {len(d)}')" 2>/dev/null
curl -s -b "$CK" "$BASE/api/resource/Warehouse?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Warehouses: {len(d)}')" 2>/dev/null
curl -s -b "$CK" "$BASE/api/resource/Employee?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Employees: {len(d)}')" 2>/dev/null
curl -s -b "$CK" "$BASE/api/resource/Account?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Accounts: {len(d)}')" 2>/dev/null

echo "--- SELLING ---"
CUST=$(curl -s -b "$CK" "$BASE/api/resource/Customer?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])" 2>/dev/null)
ITEM=$(curl -s -b "$CK" "$BASE/api/resource/Item?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])" 2>/dev/null)
WH=$(curl -s -b "$CK" "$BASE/api/resource/Warehouse?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])" 2>/dev/null)
ACCT=$(curl -s -b "$CK" "$BASE/api/resource/Account?limit_page_length=10&fields=%5B%22name%22%2C%22account_type%22%5D" | python -c "import sys,json;d=json.load(sys.stdin)['data'];r=[x['name'] for x in d if x.get('account_type')=='Receivable'];print(r[0] if r else 'Debtors - ULTRA MRF')" 2>/dev/null)

echo "Using: CUST=$CUST ITEM=$ITEM WH=$WH ACCT=$ACCT"

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Quotation" -H "Content-Type: application/json" -d "{\"quotation_to\":\"Customer\",\"customer\":\"$CUST\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100}]}")
echo "Quotation: $(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null || echo "$RESP" | head -c 150)"

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales Order" -H "Content-Type: application/json" -d "{\"customer\":\"$CUST\",\"delivery_date\":\"2026-09-10\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100}]}")
SO=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Sales Order: $SO"
if [ -n "$SO" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales Order/$SO" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL - $(echo "$SUBMIT" | head -c 200)"; add CRITICAL "Selling" "SO submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales Invoice" -H "Content-Type: application/json" -d "{\"customer\":\"$CUST\",\"due_date\":\"2026-09-10\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100}]}")
SI=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Sales Invoice: $SI"
if [ -n "$SI" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales Invoice/$SI" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL - $(echo "$SUBMIT" | head -c 200)"; add HIGH "Selling" "SI submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Delivery Note" -H "Content-Type: application/json" -d "{\"customer\":\"$CUST\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100}]}")
DN=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Delivery Note: $DN"

echo "--- BUYING ---"
SUPP=$(curl -s -b "$CK" "$BASE/api/resource/Supplier?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])" 2>/dev/null)

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase Order" -H "Content-Type: application/json" -d "{\"supplier\":\"$SUPP\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100,\"schedule_date\":\"2026-09-10\"}]}")
PO=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Purchase Order: $PO"
if [ -n "$PO" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase Order/$PO" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL - $(echo "$SUBMIT" | head -c 200)"; add HIGH "Buying" "PO submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase Invoice" -H "Content-Type: application/json" -d "{\"supplier\":\"$SUPP\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100}]}")
PI=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Purchase Invoice: $PI"
if [ -n "$PI" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase Invoice/$PI" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add HIGH "Buying" "PI submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

echo "--- STOCK ---"
RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock Entry" -H "Content-Type: application/json" -d "{\"stock_entry_type\":\"Material Receipt\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":10,\"t_warehouse\":\"$WH\",\"rate\":100}]}")
SE=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Stock Entry (Receipt): $SE"
if [ -n "$SE" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock Entry/$SE" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL - $(echo "$SUBMIT" | head -c 200)"; add CRITICAL "Stock" "SE Receipt submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock Entry" -H "Content-Type: application/json" -d "{\"stock_entry_type\":\"Material Issue\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"s_warehouse\":\"$WH\"}]}")
SEI=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Stock Entry (Issue): $SEI"
if [ -n "$SEI" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock Entry/$SEI" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL - $(echo "$SUBMIT" | head -c 200)"; add CRITICAL "Stock" "Material Issue submit blocked" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

echo "--- ACCOUNTS ---"
RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Payment Entry" -H "Content-Type: application/json" -d "{\"payment_type\":\"Receive\",\"party_type\":\"Customer\",\"party\":\"$CUST\",\"paid_amount\":100,\"received_amount\":100}")
PE=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Payment Entry (Receive): $PE"
if [ -n "$PE" ]; then
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Payment Entry/$PE" -H "Content-Type: application/json" -d '{"docstatus":1}')
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add HIGH "Accounts" "PE submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Journal Entry" -H "Content-Type: application/json" -d "{\"voucher_type\":\"Journal Entry\",\"accounts\":[{\"account\":\"$ACCT\",\"party_type\":\"Customer\",\"party\":\"$CUST\",\"credit_in_account_currency\":100},{\"account\":\"Sales - ULTRA MRF\",\"debit_in_account_currency\":100}]}")
JE=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Journal Entry: $JE"

echo "--- HR ---"
for DT in "Salary Structure" "Salary Slip" "Expense Claim" "Leave Application" "Attendance"; do
  RESP=$(curl -s -b "$CK" "$BASE/api/resource/$DT?limit_page_length=1")
  if echo "$RESP" | grep -q '"data"'; then
    echo "$DT: $(echo "$RESP" | python -c "import sys,json;d=json.load(sys.stdin)['data'];print(len(d))" 2>/dev/null || echo '?') records"
  else
    echo "$DT: NOT FOUND - $(echo "$RESP" | head -c 100)"; add HIGH "HR" "$DT missing" "Payroll module not installed"
  fi
done

echo "--- MANUFACTURING ---"
for DT in "BOM" "Work Order" "Job Card" "Operation"; do
  RESP=$(curl -s -b "$CK" "$BASE/api/resource/$DT?limit_page_length=5&fields=%5B%22name%22%5D")
  if echo "$RESP" | grep -q '"data"'; then
    CNT=$(echo "$RESP" | python -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
    echo "$DT: $CNT records"
    if [ "$CNT" = "0" ] && [ "$DT" = "BOM" -o "$DT" = "Work Order" ]; then add MEDIUM "Mfg" "No ${DT}s" "Mfg non-functional"; fi
  else
    echo "$DT: FAIL - $(echo "$RESP" | head -c 100)"; add HIGH "Mfg" "$DT list failed" "$(echo "$RESP" | head -c 80)"
  fi
done

echo "--- VEHICLE MANAGEMENT ---"
for DT in "Vehicle Job Order" "Customer Vehicle"; do
  RESP=$(curl -s -b "$CK" "$BASE/api/resource/$DT?limit_page_length=5&fields=%5B%22name%22%5D")
  if echo "$RESP" | grep -q '"data"'; then
    CNT=$(echo "$RESP" | python -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
    echo "$DT: $CNT records"
  else
    echo "$DT: FAIL - $(echo "$RESP" | head -c 120)"
  fi
done

echo "--- WEB PAGES ---"
for P in "/" "/desk" "/login" "/pos" "/pos-terminal" "/executive"; do
  S=$(curl -s -o /dev/null -w "%{http_code}" -b "$CK" "$BASE$P")
  echo "$P -> $S"
  if [ "$S" = "404" ]; then add HIGH "Web" "$P 404" "Page missing"; fi
done

echo "--- SYSTEM ---"
RESP=$(curl -s -b "$CK" "$BASE/api/resource/Error Log?limit_page_length=10&fields=%5B%22name%22%2C%22method%22%2C%22error%22%5D")
if echo "$RESP" | grep -q '"data"'; then
  echo "$RESP" | python -c "
import sys,json
d=json.load(sys.stdin).get('data',[])
print(f'Errors: {len(d)}')
for e in d[:5]: print(f'  {e.get(\"method\",\"?\")}: {str(e.get(\"error\",\"\"))[:80]}')
" 2>/dev/null
else
  echo "Error Log: FAIL - $(echo "$RESP" | head -c 100)"
fi

RESP=$(curl -s -b "$CK" "$BASE/api/resource/Server Script?limit_page_length=50&fields=%5B%22name%22%2C%22disabled%22%5D")
if echo "$RESP" | grep -q '"data"'; then
  echo "$RESP" | python -c "
import sys,json
d=json.load(sys.stdin).get('data',[])
print(f'Server Scripts: {len(d)}')
for s in d: print(f'  {s[\"name\"]} (disabled={s.get(\"disabled\",0)})')
" 2>/dev/null
fi

echo "=== AUDIT COMPLETE ==="
echo "Total issues: $N"
