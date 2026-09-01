#!/usr/bin/env python3
"""Fix QR camera scan: guard navigator.mediaDevices (undefined over plain HTTP).
When camera is unavailable (non-HTTPS), show a clear message and fall back to the
file-upload / paste-code path, which work over HTTP."""
import frappe, subprocess

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

old = '''  openScanner() {
    const v = document.getElementById("vpos-video");
    const err = document.getElementById("vpos-li-err");
    err.textContent = "Point camera at the cashier QR badge...";
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
      v.srcObject = stream; v.style.display = "block"; v.play();
      const canvas = document.createElement("canvas");
      const tick = () => {
        if (v.videoWidth === 0) { requestAnimationFrame(tick); return; }
        canvas.width = v.videoWidth; canvas.height = v.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
        const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
        let res = null;
        try { res = window.jsQR(img.data, img.width, img.height, { inversionAttempts: "attemptBoth" }); } catch (e) {}
        if (res && res.data) {
          stream.getTracks().forEach(t => t.stop());
          v.style.display = "none";
          this.applyQr(res.data);
        } else { requestAnimationFrame(tick); }
      };
      tick();
    }).catch(e => { err.textContent = "Camera unavailable: " + e.message; });
  },'''

new = '''  openScanner() {
    const v = document.getElementById("vpos-video");
    const err = document.getElementById("vpos-li-err");
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      err.textContent = "Camera is blocked over HTTP (needs HTTPS). Upload the QR image or paste the badge code instead.";
      const f = document.getElementById("vpos-li-file");
      if (f) f.click();
      return;
    }
    err.textContent = "Point camera at the cashier QR badge...";
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
      v.srcObject = stream; v.style.display = "block"; v.play();
      const canvas = document.createElement("canvas");
      const tick = () => {
        if (v.videoWidth === 0) { requestAnimationFrame(tick); return; }
        canvas.width = v.videoWidth; canvas.height = v.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
        const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
        let res = null;
        try { res = window.jsQR(img.data, img.width, img.height, { inversionAttempts: "attemptBoth" }); } catch (e) {}
        if (res && res.data) {
          stream.getTracks().forEach(t => t.stop());
          v.style.display = "none";
          this.applyQr(res.data);
        } else { requestAnimationFrame(tick); }
      };
      tick();
    }).catch(e => { err.textContent = "Camera unavailable: " + e.message + " — upload the QR image or paste the badge code instead."; });
  },'''

assert old in html, "openScanner block not found"
html = html.replace(old, new, 1)
print("patched openScanner; len", len(html))

open("/tmp/new_terminal4.html", "w", encoding="utf-8").write(html)
node = subprocess.run(
    ["node", "-e",
     "const fs=require('fs');const h=fs.readFileSync('/tmp/new_terminal4.html','utf8');"
     "const s=[...h.matchAll(/<script[^>]*>([\\s\\S]*?)<\\/script>/g)].map(m=>m[1]);"
     "let bad=0;s.forEach((b,i)=>{try{new Function(b)}catch(e){console.log('block',i,'ERR',e.message.slice(0,120));bad++}});"
     "console.log('blocks',s.length,'bad',bad);process.exit(bad?1:0)"],
    capture_output=True, text=True,
)
print("NODE:", node.stdout.strip(), node.stderr.strip())
if node.returncode != 0:
    print("!! JS INVALID — NOT committing")
    raise SystemExit(2)

frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
frappe.db.commit()
print("COMMITTED")
