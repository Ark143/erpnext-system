#!/usr/bin/env python3
"""Precise patch of the minified openScanner in the DB: add a mediaDevices guard + graceful fallback."""
import frappe, subprocess

frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites")
frappe.connect()
frappe.set_user("Administrator")
html = frappe.db.get_value("Web Page", "vehicle-pos-terminal", "main_section_html")

# exact minified substrings from the DB dump
old = '''    err.textContent="Point camera at the cashier QR badge...";
    navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"}}).then(stream=>{'''
new = '''    err.textContent="Point camera at the cashier QR badge...";
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){err.textContent="Camera is blocked over HTTP (needs HTTPS). Upload the QR image or paste the badge code instead.";const f=document.getElementById("vpos-li-file");if(f)f.click();return;}
    navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"}}).then(stream=>{'''

assert old in html, "scanner target not found"
html = html.replace(old, new, 1)
print("patched; len", len(html))

open("/tmp/new_terminal5.html", "w", encoding="utf-8").write(html)
node = subprocess.run(
    ["node", "-e",
     "const fs=require('fs');const h=fs.readFileSync('/tmp/new_terminal5.html','utf8');"
     "const s=[...h.matchAll(/<script[^>]*>([\\s\\S]*?)<\\/script>/g)].map(m=>m[1]);"
     "let bad=0;s.forEach((b,i)=>{try{new Function(b)}catch(e){console.log('block',i,'ERR',e.message.slice(0,120));bad++}});"
     "console.log('blocks',s.length,'bad',bad);process.exit(bad?1:0)"],
    capture_output=True, text=True,
)
print("NODE:", node.stdout.strip(), node.stderr.strip())
if node.returncode != 0:
    raise SystemExit(2)

frappe.db.set_value("Web Page", "vehicle-pos-terminal", "main_section_html", html)
frappe.db.commit()
print("COMMITTED")
