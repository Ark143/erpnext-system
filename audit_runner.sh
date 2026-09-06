#!/bin/bash
# ERPNext System Audit Script
# Tests all modules end-to-end on VPS http://38.247.138.224:10017

BASE_URL="http://38.247.138.224:10017"
COOKIE_JAR="/tmp/erp_audit_cookies_$$.txt"
AUDIT_LOG="/c/Users/josem/erpnext-system/audit_run_$(date +%Y%m%d_%H%M%S).json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0
ISSUE_NUM=0

echo "============================================================"
echo "ERPNext System Audit"
echo "Target: $BASE_URL"
echo "Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"

# Cleanup on exit
cleanup() {
    rm -f "$COOKIE_JAR"
}
trap cleanup EXIT

# Login
echo -e "\n[1/10] Authenticating..."
LOGIN_RESP=$(curl -s -c "$COOKIE_JAR" -X POST "$BASE_URL/api/method/login" \
    -H "Content-Type: application/json" \
    -d '{"usr":"administrator","pwd":"admin"}')

if echo "$LOGIN_RESP" | grep -q '"Logged In"'; then
    echo -e "  ${GREEN}✓ Logged in successfully${NC}"
else
    echo -e "  ${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESP"
    exit 1
fi

# Helper functions
api_get() {
    local endpoint="$1"
    local params="${2:-}"
    if [ -n "$params" ]; then
        curl -s -b "$COOKIE_JAR" "${BASE_URL}/api/resource/${endpoint}?${params}"
    else
        curl -s -b "$COOKIE_JAR" "${BASE_URL}/api/resource/${endpoint}"
    fi
}

api_post() {
    local endpoint="$1"
    local data="$2"
    curl -s -b "$COOKIE_JAR" -X POST "$BASE_URL/api/resource/$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data"
}

submit_doc() {
    local doctype="$1"
    local name="$2"
    curl -s -b "$COOKIE_Jar" -X POST "$BASE_URL/api/resource/$doctype/$name" \
        -H "Content-Type: application/json" \
        -d '{"docstatus":1}'
}

web_get() {
    local path="$1"
    curl -s -o /dev/null -w "%{http_code}" -b "$COOKIE_JAR" "${BASE_URL}${path}"
}

check_ok() {
    local label="$1"
    local response="$2"
    if echo "$response" | grep -q '"data"'; then
        echo -e "  ${GREEN}✓ $label${NC}"
        ((PASS++))
        return 0
    elif echo "$response" | grep -q '"name"'; then
        echo -e "  ${GREEN}✓ $label${NC}"
        ((PASS++))
        return 0
    else
        echo -e "  ${RED}✗ $label${NC}"
        echo "    Response: $(echo "$response" | head -c 300)"
        ((FAIL++))
        return 1
    fi
}

add_issue() {
    local severity="$1"
    local module="$2"
    local issue="$3"
    local detail="${4:-}"
    ((ISSUE_NUM++))
    echo "ISS-${ISSUE_NUM}|${severity}|${module}|${issue}|${detail}"
}

# Test Selling Module
echo -e "\n[2/10] Testing Selling Module..."
SELLING_ISSUES=""

echo "  Creating Quotation..."
QTN_RESP=$(api_post "Quotation" '{"quotation_to":"Customer","customer":"Test Customer","items":[{"item_code":"Test Item","qty":1,"rate":100}]}')
if check_ok "Quotation created" "$QTN_RESP"; then
    QTN_NAME=$(echo "$QTN_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    echo "    Name: $QTN_NAME"
fi

echo "  Creating Sales Order..."
SO_RESP=$(api_post "Sales Order" '{"customer":"Test Customer","delivery_date":"2026-09-10","items":[{"item_code":"Test Item","qty":1,"rate":100}]}')
if check_ok "Sales Order created" "$SO_RESP"; then
    SO_NAME=$(echo "$SO_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    echo "    Name: $SO_NAME"
    
    echo "  Submitting Sales Order..."
    SO_SUBMIT=$(submit_doc "Sales Order" "$SO_NAME")
    if echo "$SO_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Sales Order submitted${NC}"
    else
        echo -e "    ${RED}✗ Sales Order submit FAILED${NC}"
        echo "      $(echo "$SO_SUBMIT" | head -c 300)"
        SELLING_ISSUES="${SELLING_ISSUES}$(add_issue "CRITICAL" "Selling" "Sales Order submit failed" "$(echo "$SO_SUBMIT" | head -c 200)")\n"
    fi
fi

echo "  Creating Sales Invoice..."
SINV_RESP=$(api_post "Sales Invoice" '{"customer":"Test Customer","due_date":"2026-09-10","items":[{"item_code":"Test Item","qty":1,"rate":100}]}')
if check_ok "Sales Invoice created" "$SINV_RESP"; then
    SINV_NAME=$(echo "$SINV_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    echo "    Name: $SINV_NAME"
    
    SINV_SUBMIT=$(submit_doc "Sales Invoice" "$SINV_NAME")
    if echo "$SINV_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Sales Invoice submitted${NC}"
    else
        echo -e "    ${RED}✗ Sales Invoice submit FAILED${NC}"
        SELLING_ISSUES="${SELLING_ISSUES}$(add_issue "HIGH" "Selling" "Sales Invoice submit failed" "$(echo "$SINV_SUBMIT" | head -c 200)")\n"
    fi
fi

echo "  Creating Delivery Note..."
DN_RESP=$(api_post "Delivery Note" '{"customer":"Test Customer","items":[{"item_code":"Test Item","qty":1,"rate":100}]}')
if check_ok "Delivery Note created" "$DN_RESP"; then
    DN_NAME=$(echo "$DN_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    echo "    Name: $DN_NAME"
fi

# Test Buying Module
echo -e "\n[3/10] Testing Buying Module..."
BUYING_ISSUES=""

echo "  Creating Supplier Quotation..."
SQ_RESP=$(api_post "Supplier Quotation" '{"supplier":"Test Supplier","items":[{"item_code":"Test Item","qty":1,"rate":100}]}')
check_ok "Supplier Quotation created" "$SQ_RESP"

echo "  Creating Purchase Order..."
PO_RESP=$(api_post "Purchase Order" '{"supplier":"Test Supplier","items":[{"item_code":"Test Item","qty":1,"rate":100,"schedule_date":"2026-09-10"}]}')
if check_ok "Purchase Order created" "$PO_RESP"; then
    PO_NAME=$(echo "$PO_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    PO_SUBMIT=$(submit_doc "Purchase Order" "$PO_NAME")
    if echo "$PO_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Purchase Order submitted${NC}"
    else
        echo -e "    ${RED}✗ Purchase Order submit FAILED${NC}"
        BUYING_ISSUES="${BUYING_ISSUES}$(add_issue "HIGH" "Buying" "Purchase Order submit failed" "$(echo "$PO_SUBMIT" | head -c 200)")\n"
    fi
fi

echo "  Creating Purchase Invoice..."
PINV_RESP=$(api_post "Purchase Invoice" '{"supplier":"Test Supplier","items":[{"item_code":"Test Item","qty":1,"rate":100}]}')
if check_ok "Purchase Invoice created" "$PINV_RESP"; then
    PINV_NAME=$(echo "$PINV_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    PINV_SUBMIT=$(submit_doc "Purchase Invoice" "$PINV_NAME")
    if echo "$PINV_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Purchase Invoice submitted${NC}"
    else
        BUYING_ISSUES="${BUYING_ISSUES}$(add_issue "HIGH" "Buying" "Purchase Invoice submit failed" "$(echo "$PINV_SUBMIT" | head -c 200)")\n"
    fi
fi

# Test Stock Module
echo -e "\n[4/10] Testing Stock Module..."
STOCK_ISSUES=""

echo "  Creating Stock Entry (Material Receipt)..."
SE_RESP=$(api_post "Stock Entry" '{"stock_entry_type":"Material Receipt","items":[{"item_code":"Test Item","qty":10,"t_warehouse":"Stores - ULTRA MRF","rate":100}]}')
if check_ok "Stock Entry (Receipt) created" "$SE_RESP"; then
    SE_NAME=$(echo "$SE_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    SE_SUBMIT=$(submit_doc "Stock Entry" "$SE_NAME")
    if echo "$SE_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Stock Entry (Receipt) submitted${NC}"
    else
        echo -e "    ${RED}✗ Stock Entry submit FAILED${NC}"
        echo "      $(echo "$SE_SUBMIT" | head -c 300)"
        STOCK_ISSUES="${STOCK_ISSUES}$(add_issue "CRITICAL" "Stock" "Stock Entry submit failed" "$(echo "$SE_SUBMIT" | head -c 200)")\n"
    fi
fi

echo "  Creating Stock Entry (Material Issue)..."
SE_ISSUE_RESP=$(api_post "Stock Entry" '{"stock_entry_type":"Material Issue","items":[{"item_code":"Test Item","qty":1,"s_warehouse":"Stores - ULTRA MRF"}]}')
if check_ok "Stock Entry (Issue) created" "$SE_ISSUE_RESP"; then
    SE_ISSUE_NAME=$(echo "$SE_ISSUE_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    SE_ISSUE_SUBMIT=$(submit_doc "Stock Entry" "$SE_ISSUE_NAME")
    if echo "$SE_ISSUE_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Stock Entry (Issue) submitted${NC}"
    else
        echo -e "    ${RED}✗ Stock Entry (Issue) submit FAILED${NC}"
        echo "      $(echo "$SE_ISSUE_SUBMIT" | head -c 300)"
        STOCK_ISSUES="${STOCK_ISSUES}$(add_issue "CRITICAL" "Stock" "Material Issue submit blocked" "$(echo "$SE_ISSUE_SUBMIT" | head -c 200)")\n"
    fi
fi

# Test Accounts Module
echo -e "\n[5/10] Testing Accounts Module..."
ACCT_ISSUES=""

echo "  Creating Payment Entry (Receive)..."
PE_RESP=$(api_post "Payment Entry" '{"payment_type":"Receive","party_type":"Customer","party":"Test Customer","paid_amount":100,"received_amount":100}')
if check_ok "Payment Entry (Receive) created" "$PE_RESP"; then
    PE_NAME=$(echo "$PE_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    PE_SUBMIT=$(submit_doc "Payment Entry" "$PE_NAME")
    if echo "$PE_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Payment Entry submitted${NC}"
    else
        ACCT_ISSUES="${ACCT_ISSUES}$(add_issue "HIGH" "Accounts" "Payment Entry submit failed" "$(echo "$PE_SUBMIT" | head -c 200)")\n"
    fi
fi

echo "  Creating Payment Entry (Pay)..."
PE_PAY_RESP=$(api_post "Payment Entry" '{"payment_type":"Pay","party_type":"Supplier","party":"Test Supplier","paid_amount":100,"received_amount":100}')
if check_ok "Payment Entry (Pay) created" "$PE_PAY_RESP"; then
    PE_PAY_NAME=$(echo "$PE_PAY_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    PE_PAY_SUBMIT=$(submit_doc "Payment Entry" "$PE_PAY_NAME")
    if echo "$PE_PAY_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Payment Entry (Pay) submitted${NC}"
    fi
fi

echo "  Creating Journal Entry..."
JE_RESP=$(api_post "Journal Entry" '{"voucher_type":"Journal Entry","accounts":[{"account":"Debtors - ULTRA MRF","party_type":"Customer","party":"Test Customer","credit_in_account_currency":100},{"account":"Sales - ULTRA MRF","debit_in_account_currency":100}]}')
if check_ok "Journal Entry created" "$JE_RESP"; then
    JE_NAME=$(echo "$JE_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['name'])" 2>/dev/null)
    JE_SUBMIT=$(submit_doc "Journal Entry" "$JE_NAME")
    if echo "$JE_SUBMIT" | grep -q '"docstatus":1'; then
        echo -e "    ${GREEN}✓ Journal Entry submitted${NC}"
    else
        ACCT_ISSUES="${ACCT_ISSUES}$(add_issue "MEDIUM" "Accounts" "Journal Entry submit failed" "$(echo "$JE_SUBMIT" | head -c 200)")\n"
    fi
fi

# Test HR Module
echo -e "\n[6/10] Testing HR Module..."
HR_ISSUES=""

EMP_RESP=$(api_get "Employee" "limit_page_length=5")
if check_ok "Employee list retrieved" "$EMP_RESP"; then
    EMP_COUNT=$(echo "$EMP_RESP" | python -c "import sys,json; print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
    echo "    Employees: $EMP_COUNT"
fi

for DT in "Salary Structure" "Salary Slip" "Expense Claim" "Leave Application" "Attendance"; do
    RESP=$(api_get "$DT" "limit_page_length=1")
    if check_ok "$DT accessible" "$RESP"; then
        :
    else
        if echo "$RESP" | grep -q "DoesNotExistError\|not found"; then
            HR_ISSUES="${HR_ISSUES}$(add_issue "HIGH" "HR" "$DT DocType not installed" "Payroll module may not be installed")\n"
        fi
    fi
done

# Test Manufacturing Module
echo -e "\n[7/10] Testing Manufacturing Module..."
MFG_ISSUES=""

for DT in "BOM" "Work Order" "Job Card" "Operation"; do
    RESP=$(api_get "$DT" "limit_page_length=5")
    if check_ok "$DT list retrieved" "$RESP"; then
        COUNT=$(echo "$RESP" | python -c "import sys,json; print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
        echo "    $DT count: $COUNT"
        if [ "$COUNT" = "0" ] && [ "$DT" = "BOM" -o "$DT" = "Work Order" ]; then
            MFG_ISSUES="${MFG_ISSUES}$(add_issue "MEDIUM" "Manufacturing" "No ${DT}s exist" "Manufacturing requires BOMs to function")\n"
        fi
    else
        MFG_ISSUES="${MFG_ISSUES}$(add_issue "HIGH" "Manufacturing" "$DT list failed" "$(echo "$RESP" | head -c 200)")\n"
    fi
done

# Test Vehicle Management Module
echo -e "\n[8/10] Testing Vehicle Management Module..."
VM_ISSUES=""

for DT in "Vehicle Job Order" "Customer Vehicle" "Vehicle Service Item"; do
    RESP=$(api_get "$DT" "limit_page_length=5")
    if check_ok "$DT list retrieved" "$RESP"; then
        COUNT=$(echo "$RESP" | python -c "import sys,json; print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
        echo "    $DT count: $COUNT"
    else
        if echo "$RESP" | grep -q "DoesNotExistError\|not found"; then
            VM_ISSUES="${VM_ISSUES}$(add_issue "MEDIUM" "Vehicle Mgmt" "$DT not found" "$(echo "$RESP" | head -c 200)")\n"
        elif echo "$RESP" | grep -q "DataError\|not permitted"; then
            VM_ISSUES="${VM_ISSUES}$(add_issue "MEDIUM" "Vehicle Mgmt" "$DT query error" "$(echo "$RESP" | head -c 200)")\n"
        fi
    fi
done

# Test Web Pages
echo -e "\n[9/10] Testing Web Pages..."
WEB_ISSUES=""

for PAGE in "/" "/desk" "/login" "/pos" "/pos-terminal" "/executive"; do
    STATUS=$(web_get "$PAGE")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "301" ] || [ "$STATUS" = "302" ]; then
        echo -e "  ${GREEN}✓ $PAGE → $STATUS${NC}"
        ((PASS++))
    elif [ "$STATUS" = "404" ]; then
        echo -e "  ${RED}✗ $PAGE → 404${NC}"
        WEB_ISSUES="${WEB_ISSUES}$(add_issue "HIGH" "Web Pages" "$PAGE returns 404" "Page not found")\n"
        ((FAIL++))
    else
        echo -e "  ${YELLOW}⚠ $PAGE → $STATUS${NC}"
        ((WARN++))
    fi
done

# Test System Health
echo -e "\n[10/10] Testing System Health..."
SYS_ISSUES=""

ERR_RESP=$(api_get "Error Log" "limit_page_length=5")
if check_ok "Error Log accessible" "$ERR_RESP"; then
    ERR_COUNT=$(echo "$ERR_RESP" | python -c "import sys,json; print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
    echo "    Recent errors: $ERR_COUNT"
    # Parse errors
    if [ "$ERR_COUNT" -gt 0 ] 2>/dev/null; then
        echo "$ERR_RESP" | python -c "
import sys,json
data = json.load(sys.stdin).get('data',[])
for e in data[:5]:
    print(f'    - {e.get(\"method\",\"?\")}: {e.get(\"error\",\"\")[:80]}')
" 2>/dev/null
    fi
fi

# Check Server Scripts
echo "  Checking Server Scripts..."
SS_RESP=$(api_get "Server Script" "limit_page_length=50&fields=%5B%22name%22%5C%2C%22script_type%22%5C%2C%22disabled%22%5D")
if echo "$SS_RESP" | grep -q '"data"'; then
    SS_COUNT=$(echo "$SS_RESP" | python -c "import sys,json; print(len(json.load(sys.stdin).get('data',[])))" 2>/dev/null)
    echo -e "    ${GREEN}✓ Server Scripts: $SS_COUNT active${NC}"
fi

# Summary
echo ""
echo "============================================================"
echo "AUDIT SUMMARY"
echo "============================================================"
echo -e "Passed:  $PASS"
echo -e "Failed:  $FAIL"
echo -e "Warning: $WARN"
echo "---------------------------"
echo "TOTAL:   $((PASS + FAIL + WARN))"
echo "============================================================"

# Combine all issues
ALL_ISSUES="${SELLING_ISSUES}${BUYING_ISSUES}${STOCK_ISSUES}${ACCT_ISSUES}${HR_ISSUES}${MFG_ISSUES}${VM_ISSUES}${WEB_ISSUES}${SYS_ISSUES}"

echo ""
echo "=== ISSUE LOG ==="
echo -e "$ALL_ISSUES" | grep -v "^$"
echo "================="

# Save to file
echo -e "$ALL_ISSUES" > "/tmp/issues_$$.txt"

exit 0
