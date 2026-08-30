import urllib.request
def chk(url):
    try:
        r=urllib.request.urlopen(url, timeout=8)
        return r.status
    except Exception as e:
        return "ERR:"+type(e).__name__+":"+str(e)[:70]
# from frappe container: hit caddy on its container IP
caddy = "10.88.0.4"  # guess; use 127.0.0.1 won't reach caddy. Find caddy IP.
import subprocess
out = subprocess.run("getent hosts erp-caddy || true", shell=True, capture_output=True, text=True).stdout
print("erp-caddy hosts:", out.strip())
# Use the docker/podman network: try common alias
for ip in ["10.88.0.4","10.88.0.5","10.88.0.6","10.88.0.7"]:
    s = chk(f"http://{ip}:80/files/ultra_mrf_logo.png")
    print(f"caddy {ip}:80 logo ->", s)
print("direct socketio :9000 ->", chk("http://10.88.0.50:9000/socket.io/?EIO=4&transport=polling"))
