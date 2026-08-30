import urllib.request
def chk(url):
    try:
        r=urllib.request.urlopen(url, timeout=8)
        return r.status
    except Exception as e:
        return "ERR:"+type(e).__name__+":"+str(e)[:60]
print("logo /files/  :", chk("http://127.0.0.1:80/files/ultra_mrf_logo.png"))
print("socket.io     :", chk("http://127.0.0.1:80/socket.io/?EIO=4&transport=polling"))
print("direct :8000  :", chk("http://10.88.0.50:8000/login"))
print("direct :9000  :", chk("http://10.88.0.50:9000/socket.io/?EIO=4&transport=polling"))
