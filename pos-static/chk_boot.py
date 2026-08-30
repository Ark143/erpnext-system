import urllib.request, json, urllib.parse
# login and fetch bootinfo, check if vehicle_management app has an icon
URL="http://127.0.0.1:8000"
import http.cookiejar
jar=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def post(path, data):
    req=urllib.request.Request(URL+path, data=urllib.parse.urlencode(data).encode(), headers={"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest"})
    return urllib.request.urlopen(req, timeout=15).read()
# login as admin
post("/api/method/login", {"usr":"Administrator","pwd":open("/workspace/frappe-bench/sites/site1.local/pwd.txt").read().strip() if __import__("os").path.exists("/workspace/frappe-bench/sites/site1.local/pwd.txt") else "admin"})
# get boot
boot=json.loads(urllib.request.urlopen(URL+"/api/method/frappe.boot", timeout=15).read())
apps = boot.get("bootinfo",{}).get("apps",[]) or boot.get("apps",[])
print("apps in boot:", [a.get("app_name") or a.get("name") for a in apps][:10])
for a in apps:
    name=a.get("app_name") or a.get("name")
    if name and "vehicle" in str(name).lower():
        print("VEHICLE APP:", a)
