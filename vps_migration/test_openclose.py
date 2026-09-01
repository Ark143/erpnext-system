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

# close current shift
st, body = call("close_cashier")
print("close_cashier:", st, body[:300])
# check shift now closed
st, body = call("get_cashier_shift")
print("after close shift:", body[:200])
# reopen
st, body = call("open_cashier", {"company":"Ultra MRF Dau Annex","opening_amount":0})
print("open_cashier:", st, body[:200])
