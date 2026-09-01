#!/usr/bin/env python3
import urllib.request, urllib.parse, json, http.cookiejar
URL = "http://localhost"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
data = urllib.parse.urlencode({"cmd":"login","usr":"administrator","pwd":"admin"}).encode()
op.open(urllib.request.Request(URL+"/api/method/login", data=data, headers=H), timeout=30)
# fetch the page via getpage
req = urllib.request.Request(URL+"/api/method/frappe.desk.desk_page.getpage?name=vehicle_pos", headers=H)
r = op.open(req, timeout=30)
body = r.read().decode()
print("status:", r.status)
print("has VehiclePOS:", "class VehiclePOS" in body)
print("has build_login:", "build_login" in body)
print("has on_page_load:", "on_page_load" in body)
print("len:", len(body))
# also check: does it contain the page dir js or just the page_js?
print("first 200 chars:", body[:200])
