import requests
import json
import urllib.parse

VPS_BASE = "http://38.247.138.224:10017"
s = requests.Session()
s.post(f"{VPS_BASE}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})

comps = s.get(f"{VPS_BASE}/api/resource/Company?fields=[\"name\",\"sales_monthly_history\",\"total_monthly_sales\"]&limit_page_length=100").json().get("data", [])

# Let's compute actual sales history for each company from Sales Invoices on VPS
for c in comps:
    c_name = c.get("name")
    
    # Query invoices for this company
    sinvs = s.get(f"{VPS_BASE}/api/resource/Sales Invoice?filters=[[\"company\",\"=\",\"{c_name}\"],[\"docstatus\",\"=\",1]]&fields=[\"name\",\"posting_date\",\"base_grand_total\"]&limit_page_length=5000").json().get("data", [])
    
    history_dict = {}
    current_month_total = 0.0
    for inv in sinvs:
        p_date = inv.get("posting_date", "")
        if p_date and len(p_date) >= 7:
            # Format: MM-YYYY
            parts = p_date.split("-")
            m_y = f"{parts[1]}-{parts[0]}"
            amt = float(inv.get("base_grand_total") or 0.0)
            history_dict[m_y] = history_dict.get(m_y, 0.0) + amt
            if m_y == "09-2026":
                current_month_total += amt
                
    if not history_dict:
        history_dict = {"09-2026": 0.0}
        
    print(f"Company '{c_name}': {len(sinvs)} invoices, total: {current_month_total}, history: {history_dict}")
    
    # Update Company record
    try:
        s.put(f"{VPS_BASE}/api/resource/Company/{urllib.parse.quote(c_name)}", json={
            "sales_monthly_history": json.dumps(history_dict),
            "total_monthly_sales": current_month_total
        })
    except Exception as e:
        print(f"Failed to update company {c_name}: {e}")

print("\nTesting get_monthly_goal_graph_data for Automan Car Care Center...")
res_goal = s.get(f"{VPS_BASE}/api/method/frappe.utils.goal.get_monthly_goal_graph_data", params={
    "doctype": "Company",
    "docname": "Automan Car Care Center",
    "title": "Sales",
    "goal_value_field": "monthly_sales_target",
    "goal_total_field": "total_monthly_sales",
    "goal_history_field": "sales_monthly_history",
    "goal_doctype": "Sales Invoice",
    "goal_doctype_link": "company",
    "goal_field": "base_grand_total",
    "date_field": "posting_date",
    "filters": json.dumps({"docstatus": 1, "is_opening": ["!=", "Yes"]}),
    "aggregation": "sum"
})
print("Goal Graph API Status:", res_goal.status_code)
print("Goal Graph API Response:", json.dumps(res_goal.json(), indent=2))
