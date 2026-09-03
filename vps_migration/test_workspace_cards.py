import urllib.request, urllib.parse, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')

# 1. Get Workspace
r = opener.open('http://38.247.138.224:10017/api/resource/Workspace/Vehicle%20Management')
ws = json.loads(r.read().decode())['data']

print("--- TESTING NUMBER CARDS ---")
for c in ws.get('number_cards', []):
    card_name = c['number_card_name']
    card_doc_r = opener.open('http://38.247.138.224:10017/api/resource/Number%20Card/' + urllib.parse.quote(card_name))
    card_doc = json.loads(card_doc_r.read().decode())['data']
    
    # Frappe desk calls number_card.get_result with {doc: JSON.stringify(card_doc), filters: ...}
    payload = urllib.parse.urlencode({
        'doc': json.dumps(card_doc),
        'filters': json.dumps([])
    }).encode()
    try:
        req = urllib.request.Request('http://38.247.138.224:10017/api/method/frappe.desk.doctype.number_card.number_card.get_result', data=payload)
        res = opener.open(req)
        print(f"  CARD: {card_name} -> OK: {res.read().decode()[:80]}")
    except urllib.error.HTTPError as e:
        print(f"  CARD: {card_name} -> FAILED {e.code}: {e.read().decode()[:200]}")

print("\n--- TESTING DASHBOARD CHARTS ---")
for ch in ws.get('charts', []):
    chart_name = ch['chart_name']
    payload = urllib.parse.urlencode({
        'chart_name': chart_name,
        'refresh': 1
    }).encode()
    try:
        req = urllib.request.Request('http://38.247.138.224:10017/api/method/frappe.desk.doctype.dashboard_chart.dashboard_chart.get', data=payload)
        res = opener.open(req)
        print(f"  CHART: {chart_name} -> OK: {res.read().decode()[:80]}")
    except urllib.error.HTTPError as e:
        print(f"  CHART: {chart_name} -> FAILED {e.code}: {e.read().decode()[:200]}")
