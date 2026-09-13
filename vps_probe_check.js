const http = require("http");
const base = "http://38.247.138.224:10017";
const jar = { cookie: "" };

function get(url, cb) {
  const opts = { headers: jar.cookie ? { Cookie: jar.cookie } : {} };
  http.get(base + url, opts, res => {
    let body = "";
    res.on("data", c => body += c);
    res.on("end", () => { if (cb) cb(res.statusCode, body); });
  }).on("error", e => { if (cb) cb(0, e.message); });
}

function post(url, data, cb) {
  const postData = typeof data === "string" ? data : new URLSearchParams(data).toString();
  const opts = {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", ...(jar.cookie ? { Cookie: jar.cookie } : {}) }
  };
  const req = http.request(base + url, opts, res => {
    let body = "";
    res.on("data", c => body += c);
    res.on("end", () => {
      jar.cookie = res.headers["set-cookie"] ? res.headers["set-cookie"].map(c => c.split(";")[0]).join("; ") : "";
      if (cb) cb(res.statusCode, body);
    });
  });
  req.write(postData);
  req.end();
}

post("/api/method/login", { usr: "Administrator", pwd: "admin" }, (code, body) => {
  console.log("LOGIN:", code);
  get("/", (code, html) => {
    const re = /\/assets\/[^"']+\.(js|css)/g;
    const assetUrls = [];
    let m;
    while ((m = re.exec(html)) !== null) assetUrls.push(m[0]);
    const unique = [...new Set(assetUrls)];
    console.log("Found", unique.length, "asset URLs in HTML");
    let checked = 0;
    let failures = [];
    unique.forEach((url) => {
      get(url, (code) => {
        checked++;
        if (code !== 200) failures.push({ url, code });
        if (checked === unique.length) {
          console.log("=== ASSET FAILURES (first 25) ===");
          failures.slice(0, 25).forEach(f => console.log(f.code + " " + f.url));
          console.log("Total failures:", failures.length, "of", unique.length);
          probeAPIs();
        }
      });
    });
  });
});

function probeAPIs() {
  const endpoints = [
    "/api/method/ping",
    "/api/method/frappe.boot",
    "/api/method/frappe.client.get_list?doctype=Customer&limit_page_length=1",
    "/api/resource/DESK",
    "/api/method/vehicle_management.api.portal.system_health",
  ];
  let epLeft = endpoints.length;
  endpoints.forEach((path) => {
    get(path, (code, body) => {
      epLeft--;
      const ok = code === 200;
      console.log((ok ? "OK " : "FAIL " + code) + " " + path);
      if (!ok && body.length > 0) {
        try {
          const j = JSON.parse(body);
          console.log("  ->", j.exc_type || j.message || JSON.stringify(j).substring(0, 100));
        } catch(e) {}
      }
      if (epLeft === 0) {
        console.log("=== END ===");
        probeWS();
      }
    });
  });
}

function probeWS() {
  const opts = {
    method: "GET",
    headers: {
      "Connection": "Upgrade",
      "Upgrade": "websocket",
      "Sec-WebSocket-Version": "13",
      "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
      ...(jar.cookie ? { Cookie: jar.cookie } : {})
    }
  };
  http.get(base + "/socket.io/?EIO=4&transport=websocket", opts, res => {
    console.log("WEBSOCKET_UPGRADE:", res.statusCode);
  }).on("error", e => console.log("WS_ERR:", e.message));
}
