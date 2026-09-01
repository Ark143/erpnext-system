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

# close the currently-open shift (POS-OPE-2026-00007, opened with 500) with closing amount 700
st, body = call("close_cashier", {"closing_amount": 700})
print("close:", body[:200])

# verify the closing entry recorded the amount
import re
name = re.search(r'"name":"(POS-CLO-\d+)"', body).group(1)
print("closing name:", name)
