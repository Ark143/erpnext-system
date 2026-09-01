#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar
URL = "http://127.0.0.1:8000"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)
for m in ["get_cashier_shift","get_history","get_receipt"]:
    args = {"name":"VMSPOS-2026-00006"} if m=="get_receipt" else None
    qs = ("?"+urllib.parse.urlencode(args)) if args else ""
    r = op.open(urllib.request.Request(URL+f"/api/method/vehicle_management.vehicle_management.pos_api.{m}{qs}", headers=H), timeout=30)
    body = r.read().decode()
    print(m, "->", r.status, body[:200])
