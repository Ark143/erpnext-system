import subprocess, time, re, os

print("Starting Cloudflare Public Live Internet Tunnel...")
proc = subprocess.Popen(
    ["tools/cloudflared.exe", "tunnel", "--url", "http://localhost:80", "--http-host-header", "site1.local"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

url = None
t0 = time.time()
while time.time() - t0 < 30:
    line = proc.stdout.readline()
    if line:
        print(line, end="")
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url = match.group(0)
            break

if url:
    print("\n" + "=" * 65)
    print("  LIVE PUBLIC HTTPS URL READY FOR TESTING:")
    print("  " + url)
    print("=" * 65)
    with open("tools/live_public_url.txt", "w") as f:
        f.write(url)
    
    # Keep tunnel alive
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
else:
    print("Could not find public URL in 30 seconds.")
