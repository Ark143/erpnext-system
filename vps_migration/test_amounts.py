#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar
URL = "http://127.0.0.1:8000"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)

def call(method, params=None):
    qs = ("?"+urllib.parse.urlencode(params)) if params else ""
    r = op.open(urllib.request.Request(URL+f"/api/method/vehicle_management.vehicle_management.pos_api.{method}{qs}", headers=H), timeout=60)
    return r.status, r.read().decode()

# current shift state
st, body = call("get_cashier_shift")
print("shift before:", body[:300])

# close with a closing amount (if open)
import re
m = re.search(r'"open":\s*(true|false)', body)
if m and m.group(1) == "true":
    st, body = call("close_cashier", {"closing_amount": 1500})
    print("close with 1500:", body[:300])
    # verify closing entry recorded the amount
    import subprocess
else:
    print("(no open shift to close)")

# open with opening amount
st, body = call("open_cashier", {"company": "Ultra MRF Dau Annex", "opening_amount": 500})
print("open with 500:", body[:300])

# shift now shows opening amount
st, body = call("get_cashier_shift")
print("shift after open:", body[:300])
