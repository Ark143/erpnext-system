import socket
req = ("GET /socket.io/?EIO=4&transport=websocket HTTP/1.1\r\n"
       "Host: localhost\r\n"
       "Origin: http://localhost\r\n"
       "Connection: Upgrade\r\n"
       "Upgrade: websocket\r\n"
       "Sec-WebSocket-Version: 13\r\n"
       "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n")
s = socket.create_connection(("localhost", 80), timeout=8)
s.sendall(req.encode())
s.settimeout(5)
try:
    data = s.recv(4096)
    first = data.split(b"\r\n")[0].decode(errors="replace")
    print("WS upgrade response:", first)
    print("RESULT:", "101 Switching Protocols -> origin ACCEPTED (socket.io fixed)" if "101" in first else "NOT 101 -> still failing")
except Exception as e:
    print("recv err:", e)
s.close()
