import socket, urllib.request
# Simulate socket.io websocket upgrade with Origin header through caddy (Windows host path)
import http.client
conn = http.client.HTTPConnection("localhost", 80, timeout=10)
req = ("GET /socket.io/?EIO=4&transport=websocket HTTP/1.1\r\n"
       "Host: localhost\r\n"
       "Origin: http://localhost\r\n"
       "Connection: Upgrade\r\n"
       "Upgrade: websocket\r\n"
       "Sec-WebSocket-Version: 13\r\n"
       "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
       "Sec-WebSocket-Protocol: chat\r\n\r\n")
conn.send(req.encode())
try:
    conn.sock.settimeout(5)
    data = conn.recv(4096)
    print("WS upgrade response (first line):", data.split(b"\r\n")[0].decode(errors="replace"))
    print("GOT WEBSOCKET UPGRADE -> origin accepted" if b"101" in data.split(b"\r\n")[0] else "no 101; check")
except Exception as e:
    print("recv err:", e)
conn.close()
