#!/bin/bash
# Full ERPNext System Audit
BASE="http://38.247.138.224:10017"
CK="./audit_ck.txt"
rm -f "$CK"

# Login
curl -s -c "$CK" -X POST "$BASE/api/method/login" -H "Content-Type: application/json" -d '{"usr":"administrator","pwd":"admin"}' >/dev/null

N=0
add() { N=$((N+1)); echo "ISS-$N|$1|$2|$3|$4"; }

echo "=== AUDIT $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

echo "--- MASTER DATA ---"
curl -s -b "$CK" "$BASE/api/resource/Company?limit_page_length=20&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Companies: {len(d)}')"
curl -s -b "$CK" "$BASE/api/resource/Customer?limit_page_length=5&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Customers: {len(d)}')"
curl -s -b "$CK" "$BASE/api/resource/Supplier?limit_page_length=5&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Suppliers: {len(d)}')"
curl -s -b "$CK" "$BASE/api/resource/Item?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Items: {len(d)}')"
curl -s -b "$CK" "$BASE/api/resource/Warehouse?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Warehouses: {len(d)}')"
curl -s -b "$CK" "$BASE/api/resource/Employee?limit_page_length=10&fields=%5B%22name%22%5D" | python -c "import sys,json;d=json.load(sys.stdin).get('data',[]);print(f'Employees: {len(d)}')"

echo "--- DATA COLLECTION ---"
CUST=$(curl -s -b "$CK" "$BASE/api/resource/Customer?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])")
ITEM=$(curl -s -b "$CK" "$BASE/api/resource/Item?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])")
WH=$(curl -s -b "$CK" "$BASE/api/resource/Warehouse?limit_page_length=10&fields=%5B%22name%22%2C%22company%22%5D" | python -c "import sys,json;d=json.load(sys.stdin)['data'];r=[x['name'] for x in d if x.get('company')=='ULTRA MRF'];print(r[0] if r else 'Stores - UM')")
ACCT=$(curl -s -b "$CK" "$BASE/api/resource/Account?limit_page_length=20&fields=%5B%22name%22%2C%22account_type%22%5D" | python -c "import sys,json;d=json.load(sys.stdin)['data'];r=[x['name'] for x in d if x.get('account_type')=='Receivable'];print(r[0] if r else 'Debtors - ULTRA MRF')")
SUPP=$(curl -s -b "$CK" "$BASE/api/resource/Supplier?limit_page_length=1&fields=%5B%22name%22%5D" | python -c "import sys,json;print(json.load(sys.stdin)['data'][0]['name'])")

echo "Using: CUST=$CUST ITEM=$ITEM WH=$WH ACCT=$ACCT SUPP=$SUPP"

echo "--- SELLING MODULE ---"
RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Quotation" -H "Content-Type: application/json" -d "{\"quotation_to\":\"Customer\",\"customer\":\"$CUST\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100}]}")
echo "Quotation: $(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null || echo "FAIL - $(echo "$RESP" | head -c 100)")"

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales%20Order" -H "Content-Type: application/json" -d "{\"customer\":\"$CUST\",\"delivery_date\":\"2026-09-10\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100,\"warehouse\":\"$WH\"}]}")
SO=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Sales Order: $SO"
if [ -n "$SO" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Sales%20Order/$SO")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales%20Order/$SO" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add CRITICAL "Selling" "SO submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales%20Invoice" -H "Content-Type: application/json" -d "{\"customer\":\"$CUST\",\"due_date\":\"2026-09-10\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100,\"warehouse\":\"$WH\"}]}")
SI=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Sales Invoice: $SI"
if [ -n "$SI" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Sales%20Invoice/$SI")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Sales%20Invoice/$SI" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add HIGH "Selling" "SI submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Delivery%20Note" -H "Content-Type: application/json" -d "{\"customer\":\"$CUST\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100,\"warehouse\":\"$WH\"}]}")
DN=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Delivery Note: $DN"

echo "--- BUYING MODULE ---"
RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase%20Order" -H "Content-Type: application/json" -d "{\"supplier\":\"$SUPP\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100,\"schedule_date\":\"2026-09-10\"}]}")
PO=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Purchase Order: $PO"
if [ -n "$PO" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Purchase%20Order/$PO")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase%20Order/$PO" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add HIGH "Buying" "PO submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase%20Invoice" -H "Content-Type: application/json" -d "{\"supplier\":\"$SUPP\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"rate\":100,\"warehouse\":\"$WH\"}]}")
PI=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Purchase Invoice: $PI"
if [ -n "$PI" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Purchase%20Invoice/$PI")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Purchase%20Invoice/$PI" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add HIGH "Buying" "PI submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

echo "--- STOCK MODULE ---"
RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock%20Entry" -H "Content-Type: application/json" -d "{\"stock_entry_type\":\"Material Receipt\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":10,\"t_warehouse\":\"$WH\",\"rate\":100}]}")
SE=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Stock Entry (Receipt): $SE"
if [ -n "$SE" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Stock%20Entry/$SE")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock%20Entry/$SE" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add CRITICAL "Stock" "SE Receipt submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock%20Entry" -H "Content-Type: application/json" -d "{\"stock_entry_type\":\"Material Issue\",\"items\":[{\"item_code\":\"$ITEM\",\"qty\":1,\"s_warehouse\":\"$WH\"}]}")
SEI=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Stock Entry (Issue): $SEI"
if [ -n "$SEI" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Stock%20Entry/$SEI")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Stock%20Entry/$SEI" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add CRITICAL "Stock" "Material Issue submit blocked" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

echo "--- ACCOUNTS MODULE ---"
RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Payment%20Entry" -H "Content-Type: application/json" -d "{\"payment_type\":\"Receive\",\"party_type\":\"Customer\",\"party\":\"$CUST\",\"paid_amount\":100,\"received_amount\":100}")
PE=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Payment Entry: $PE"
if [ -n "$PE" ]; then
  RESP2=$(curl -s -b "$CK" "$BASE/api/resource/Payment%20Entry/$PE")
  TS=$(echo "$RESP2" | python -c "import sys,json;print(json.load(sys.stdin)['data']['modified'])" 2>/dev/null)
  SUBMIT=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Payment%20Entry/$PE" -H "Content-Type: application/json" -d "{\"docstatus\":1,\"modified\":\"$TS\"}")
  if echo "$SUBMIT" | grep -q '"docstatus":1'; then echo "  Submit: OK"; else echo "  Submit: FAIL"; add HIGH "Accounts" "PE submit failed" "$(echo "$SUBMIT" | head -c 150)"; fi
fi

RESP=$(curl -s -b "$CK" -X POST "$BASE/api/resource/Journal%20Entry" -H "Content-Type: application/json" -d "{\"voucher_type\":\"Journal Entry\",\"accounts\":[{\"account\":\"$ACCT\",\"party_type\":\"Customer\",\"party\":\"$CUST\",\"credit_in_account_currency\":100},{\"account\":\"Sales - ULTRA MRF\",\"debit_in_account_currency\":100}]}")
JE=$(echo "$RESP" | python -c "import sys,json;print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
echo "Journal Entry: $JE"

echo "--- HR MODULE ---"
for DT in "Salary Structure" "Salary Slip" "Expense Claim" "Leave Application" "Attendance"; do
  RESP=$(curl -s -b "$CK" "$BASE/api/resource/$DT?limit_page_length=1")
  if echo "$RESP" | grep -q '"data"'; then
    echo "$DT: $(echo "$RESP" | python -c "import sys,json;d=json.load(sys.stdin)['data'];print(len(d))" 2>/dev/null || echo '?') records"
  else
    echo "$DT: NOT FOUND"; add HIGH "HR" "$DT missing" "Payroll module not installed"
  fi
done

echo "--- MANUFACTURING MODULE ---"
for DT in "BOM" "Work Order" "Job Card" "Operation"; do
  RESP=$(curl -s -b "$CK" "$BASE/api/resource/$DT?limit_page_length=5&fields=%5B%22name%22%5D")
  if echo "$RESP" | grep -q '"data"'; then
    CNT=$(echo "$RESP" | python -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
    echo "$DT: $CNT records"
    if [ "$CNT" = "0" ] && [ "$DT" = "BOM" -o "$DT" = "Work Order" ]; then add MEDIUM "Mfg" "No ${DT}s" "Mfg non-functional"; fi
  else
    echo "$DT: FAIL"; add HIGH "Mfg" "$DT list failed" "$(echo "$RESP" | head -c 80)"
  fi
done

echo "--- VEHICLE MANAGEMENT MODULE ---"
for DT in "Vehicle Job Order" "Customer Vehicle"; do
  RESP=$(curl -s -b "$CK" "$BASE/api/resource/$DT?limit_page_length=5&fields=%5B%22name%22%5D")
  if echo "$RESP" | grep -q '"data"'; then
    CNT=$(echo "$RESP" | python -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
    echo "$DT: $CNT records"
  else
    echo "$DT: FAIL - $(echo "$RESP" | head -c 100)"
  fi
done

echo "--- WEB PAGES ---"
for P in "/" "/desk" "/login" "/pos" "/pos-terminal" "/executive"; do
  S=$(curl -s -o /dev/null -w "%{http_code}" -b "$CK" "$BASE$P")
  echo "$P -> $S"
  if [ "$S" = "404" ]; then add HIGH "Web" "$P 404" "Page missing"; fi
done

echo "--- SYSTEM ---"
RESP=$(curl -s -b "$CK" "$BASE/api/resource/Error%20Log?limit_page_length=10&fields=%5B%22name%22%2C%22method%22%2C%22error%22%5D")
if echo "$RESP" | grep -q '"data"'; then
  echo "$RESP" | python -c "
import sys,json
d=json.load(sys.stdin).get('data',[])
print(f'Errors: {len(d)}')
for e in d[:5]: print(f'  {e.get(\"method\",\"?\")}: {str(e.get(\"error\",\"\"))[:80]}')
"
else
  echo "Error Log: FAIL"
fi

RESP=$(curl -s -b "$CK" "$BASE/api/resource/Server%20Script?limit_page_length=50&fields=%5B%22name%22%2C%22disabled%22%5D")
if echo "$RESP" | grep -q '"data"'; then
  echo "$RESP" | python -c "
import sys,json
d=json.load(sys.stdin).get('data',[])
print(f'Server Scripts: {len(d)}')
for s in d: print(f'  {s[\"name\"]} (disabled={s.get(\"disabled\",0)})')
"
fi

echo "=== AUDIT COMPLETE: $N issues ==="
rm -f "$CK"
