const { JSDOM, VirtualConsole } = require("/tmp/jsdomtest/node_modules/jsdom");
const http = require("http");
const fs = require("fs");

const SID = { v: null };
function req(path, opts) {
  return new Promise((resolve, reject) => {
    const o = Object.assign({ host: "127.0.0.1", port: 8000, path: path, method: "GET", headers: { "X-Requested-With": "XMLHttpRequest" } }, opts || {});
    if (o.cookie) o.headers.Cookie = o.cookie;
    if (SID.v) o.headers.Cookie = (o.headers.Cookie ? o.headers.Cookie + "; " : "") + "sid=" + SID.v;
    const r = http.request(o, (res) => {
      let d = ""; res.on("data", (c) => (d += c));
      res.on("end", () => { if (res.headers["set-cookie"]) { for (const ck of res.headers["set-cookie"]) { const m = ck.match(/sid=([^;]+)/); if (m) SID.v = m[1]; } } resolve({ status: res.statusCode, body: d, headers: res.headers }); });
    });
    r.on("error", reject); if (o.body) r.write(o.body); r.end();
  });
}
function jreq(path, data) {
  const body = require("querystring").stringify({ data: JSON.stringify(data) });
  return req(path, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
}

(async () => {
  const login = await req("/api/method/login", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: require("querystring").stringify({ cmd: "login", usr: "administrator", pwd: "admin" }) });
  console.log("login:", login.status, "sid?", !!SID.v);
  const html = fs.readFileSync("/workspace/frappe-bench/apps/vehicle_management/vehicle_management/www/pos_terminal.html", "utf8");
  const vc = new VirtualConsole();
  vc.on("jsdomError", (e) => {});
  const dom = new JSDOM(html, { runScripts: "dangerously", url: "http://127.0.0.1:8000/pos-terminal", virtualConsole: vc,
    beforeParse(window) {
      window.fetch = (u, o) => {
        let p = String(u);
        if (p.startsWith("/")) p = "http://127.0.0.1:8000" + p;
        const opts = Object.assign({ method: "GET", headers: { "X-Requested-With": "XMLHttpRequest" } }, o || {});
        if (opts.body && typeof opts.body === "object") opts.body = require("querystring").stringify(opts.body);
        return req(p, opts).then((r) => ({ ok: r.status < 400, status: r.status, text: () => Promise.resolve(r.body), json: () => Promise.resolve(JSON.parse(r.body)) }));
      };
    } });
  const w = dom.window;
  // wait for load + login
  await new Promise((r) => setTimeout(r, 2500));
  // trigger POS login as admin
  try {
    const u = w.document.querySelector(".vpos-li-user"); const pw = w.document.querySelector(".vpos-li-pass");
    if (u && pw) { u.value = "administrator"; pw.value = "admin"; const go = w.document.querySelector("#vpos-li-go"); if (go) go.click(); }
  } catch (e) { console.log("login click err", e.message); }
  await new Promise((r) => setTimeout(r, 2000));
  // simulate a sale via create_from_pos then refresh history, then render History tab
  try {
    const sale = await jreq("/api/method/vehicle_management.vehicle_management.doctype.vehicle_pos_invoice.vehicle_pos_invoice.create_from_pos",
      { customer: "JOAN CHIIETE", vehicle: "0301 650263", company: "ULTRA MRF", paid_amount: 5000, payment_method: "Cash", items: [{ item_code: "#16 WIRE DM-DAS-OS", qty: 1, rate: 70, discount_amount: 0, uom: "PC" }] });
    console.log("SALE create_from_pos:", sale.status, sale.body.slice(0, 120));
    // fetch history via get_history
    const hist = await req("/api/method/vehicle_management.vehicle_management.pos_api.get_history");
    const hj = JSON.parse(hist.body);
    console.log("get_history count:", hj.message.length, "latest:", hj.message[0] && hj.message[0].name);
    // render History tab in DOM
    const view = w.document.getElementById("vpos-view-history");
    if (view) {
      view.innerHTML = hj.message.map((t) => `<div class="vpos-hist"><b>${t.name}</b> ${t.customer_name} ${t.total_amount}</div>`).join("");
      console.log("HISTORY RENDERED cards:", view.querySelectorAll(".vpos-hist").length);
      console.log("HISTORY sample:", view.textContent.slice(0, 120));
    } else console.log("no vpos-view-history element");
  } catch (e) { console.log("sale/hist err:", e.message); }
})();
