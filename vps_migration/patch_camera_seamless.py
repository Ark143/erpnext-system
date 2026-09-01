import urllib.request, urllib.parse, json, http.cookiejar, subprocess

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

r = op.open(urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal', headers=H))
wp = json.loads(r.read().decode())
html = wp['data']['main_section_html']

start_idx = html.find('buildLogin(){')
end_idx = html.find('build(){', start_idx)

if start_idx == -1 or end_idx == -1:
    print("ERROR: could not locate block")
    exit(1)

new_login_block = """buildLogin(){
    const r=document.getElementById("vpos-root");
    r.innerHTML=`<div class="vpos-login" id="vpos-login">
      <div class="vpos-login-card">
        <div class="vpos-login-logo" style="background:linear-gradient(135deg,#16c784,#0fa76d);font-size:22px;font-weight:900;letter-spacing:-1px">V</div>
        <div class="vpos-login-title">Vehicle POS Terminal</div>
        <div class="vpos-login-sub">Cashier Sign-In</div>
        ${this.loggedOutMsg?('<div class="vpos-li-ok">'+this.loggedOutMsg+'</div>'):''}
        <input class="vpos-li vpos-li-user" placeholder="User ID / Email" autocomplete="username">
        <input class="vpos-li vpos-li-pass" type="password" placeholder="Password" autocomplete="current-password">
        <button class="vpos-li-btn" id="vpos-li-go">Sign In</button>
        <div class="vpos-li-or">— or scan your QR badge —</div>
        <button class="vpos-li-qr" id="vpos-li-scan">&#128247; Scan QR Code / Camera</button>
        <input type="file" accept="image/*" capture="environment" id="vpos-li-file" style="display:none">
        <button class="vpos-li-qr" id="vpos-li-upbtn" style="margin-top:6px;background:#f0fdf4;border-color:#bbf7d0;color:#166534;">&#128193; Upload QR Image File</button>
        <div class="vpos-li-or">— or paste badge code —</div>
        <input class="vpos-li vpos-li-code" id="vpos-li-code" placeholder="user|password" autocomplete="off">
        <button class="vpos-li-qr" id="vpos-li-codego">Use code</button>
        <div class="vpos-li-err" id="vpos-li-err"></div>
        <div id="vpos-scanner-box" style="display:none;position:relative;margin-top:12px;border-radius:12px;overflow:hidden;background:#000;">
          <video id="vpos-video" playsinline style="width:100%;display:block;border-radius:12px;"></video>
          <div style="position:absolute;inset:15%;border:2px dashed #16c784;border-radius:10px;pointer-events:none;box-shadow:0 0 0 9999px rgba(0,0,0,0.45);"></div>
          <button id="vpos-scan-stop" type="button" style="position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(239,68,68,0.9);color:#fff;border:none;padding:6px 14px;border-radius:8px;font-size:12px;cursor:pointer;font-weight:700;">✕ Stop Camera</button>
        </div>
      </div>
    </div>`;
    const self=this;
    const userInput = r.querySelector(".vpos-li-user");
    const passInput = r.querySelector(".vpos-li-pass");
    const codeInput = r.querySelector("#vpos-li-code");
    const fileInput = r.querySelector("#vpos-li-file");
    const err = r.querySelector("#vpos-li-err");

    r.querySelector("#vpos-li-go").onclick=()=>self.doLogin(userInput.value, passInput.value);
    r.querySelector("#vpos-li-scan").onclick=()=>self.openScanner();
    r.querySelector("#vpos-li-upbtn").onclick=()=>{ if (fileInput) fileInput.click(); };
    fileInput.onchange=e=>{ if(e.target.files && e.target.files[0]) self.decodeImage(e.target.files[0]); };
    r.querySelector("#vpos-li-codego").onclick=()=>{ const c=codeInput.value; self.applyQr(c); };

    // Support Enter key across all inputs
    passInput.onkeydown = e => { if (e.key === "Enter") self.doLogin(userInput.value, passInput.value); };
    codeInput.onkeydown = e => { if (e.key === "Enter") self.applyQr(codeInput.value); };
    
    // Auto-detect QR badge pasted or scanned into User field (e.g. user|pass)
    userInput.oninput = () => {
      const val = userInput.value;
      if (val.includes("|") || val.includes("\\t")) {
        self.applyQr(val);
      }
    };
    userInput.onkeydown = e => {
      if (e.key === "Enter") {
        const val = userInput.value;
        if (val.includes("|") || val.includes("\\t")) {
          self.applyQr(val);
        } else {
          passInput.focus();
        }
      }
    };

    // Global barcode scanner listener on login screen (keyboard wedge support)
    this._scanBuf = "";
    this._scanTimer = null;
    this._keyHandler = e => {
      if (self.loggedIn) return;
      if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) {
        if (e.key === "Enter" && e.target.value && e.target.value.includes("|")) {
          self.applyQr(e.target.value);
        }
        return;
      }
      if (e.key === "Enter") {
        if (self._scanBuf.includes("|") || self._scanBuf.length > 5) {
          self.applyQr(self._scanBuf);
          self._scanBuf = "";
        }
      } else if (e.key && e.key.length === 1) {
        self._scanBuf += e.key;
        clearTimeout(self._scanTimer);
        self._scanTimer = setTimeout(() => { self._scanBuf = ""; }, 500);
      }
    };
    document.addEventListener("keydown", this._keyHandler);
  },
  applyQr(data){
    if(!data)return;
    let raw = String(data).trim();
    raw = raw.replace(/[\\r\\n]+$/, "").trim();
    let usr = "", pwd = "";
    if (raw.startsWith("{") && raw.endsWith("}")) {
      try {
        const parsed = JSON.parse(raw);
        usr = parsed.usr || parsed.user || parsed.username || parsed.email || "";
        pwd = parsed.pwd || parsed.password || "";
      } catch(e){}
    }
    if (!usr && !pwd) {
      let parts = raw.split("|");
      if (parts.length < 2 && raw.includes("\\t")) parts = raw.split("\\t");
      if (parts.length < 2 && raw.includes(":")) parts = raw.split(":");
      usr = (parts[0] || "").trim();
      pwd = (parts.slice(1).join("|") || "").trim();
    }
    const u=document.querySelector(".vpos-li-user");
    const p=document.querySelector(".vpos-li-pass");
    const c=document.querySelector("#vpos-li-code");
    if(u) u.value = usr;
    if(p) p.value = pwd;
    if(c) c.value = raw;
    if (usr && pwd) {
      this.doLogin(usr, pwd);
    } else if (usr) {
      const err = document.getElementById("vpos-li-err");
      if (err) err.textContent = "Please enter password for " + usr;
      if (p) p.focus();
    }
  },
  async decodeImage(file){
    const err=document.getElementById("vpos-li-err");
    if(!file)return;
    err.textContent="Scanning QR code...";
    try {
      // 1. Try native BarcodeDetector if supported
      if ("BarcodeDetector" in window) {
        try {
          const detector = new BarcodeDetector({ formats: ["qr_code"] });
          const bmp = await createImageBitmap(file);
          const barcodes = await detector.detect(bmp);
          if (barcodes && barcodes.length > 0 && barcodes[0].rawValue) {
            err.textContent = "QR decoded!";
            this.applyQr(barcodes[0].rawValue);
            return;
          }
        } catch(be){}
      }
      // 2. Try jsQR multi-scale canvas scanning
      const reader = new FileReader();
      reader.onload = () => {
        const img = new Image();
        img.onload = () => {
          const tryScales = [1.0, 800 / Math.max(img.width, img.height), 1200 / Math.max(img.width, img.height), 400 / Math.max(img.width, img.height)];
          for (let scale of tryScales) {
            if (scale > 1.0) continue;
            const w = Math.round(img.width * scale);
            const h = Math.round(img.height * scale);
            const canvas = document.createElement("canvas");
            canvas.width = w; canvas.height = h;
            const ctx = canvas.getContext("2d", { willReadFrequently: true });
            ctx.drawImage(img, 0, 0, w, h);
            try {
              const d = ctx.getImageData(0, 0, w, h);
              if (window.jsQR) {
                const res = window.jsQR(d.data, d.width, d.height, { inversionAttempts: "attemptBoth" });
                if (res && res.data) {
                  err.textContent = "QR decoded!";
                  this.applyQr(res.data);
                  return;
                }
              }
            } catch(e){}
          }
          err.textContent = "No QR found in image. Please take a clearer photo or paste badge code.";
        };
        img.onerror = () => { err.textContent = "Could not read image file."; };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    } catch(e) {
      err.textContent = "Error scanning image: " + e.message;
    }
  },
  openScanner(){
    const self=this;
    const sBox=document.getElementById("vpos-scanner-box");
    const v=document.getElementById("vpos-video");
    const err=document.getElementById("vpos-li-err");
    const stopBtn=document.getElementById("vpos-scan-stop");
    const f=document.getElementById("vpos-li-file");
    
    // Check if live camera stream is available (HTTPS or localhost)
    if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
      err.textContent = "Opening camera...";
      if(f) f.click();
      return;
    }
    
    if (sBox) sBox.style.display = "block";
    err.textContent="Point camera at cashier QR badge...";
    
    let activeStream = null;
    const stopCamera = () => {
      if (activeStream) {
        activeStream.getTracks().forEach(t => t.stop());
        activeStream = null;
      }
      if (sBox) sBox.style.display = "none";
      if (v) v.srcObject = null;
    };
    if (stopBtn) stopBtn.onclick = () => { stopCamera(); err.textContent = ""; };

    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
      activeStream = stream;
      v.srcObject = stream;
      v.play();
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      let stopped = false;

      const scanFrame = async () => {
        if (self.loggedIn || stopped || !activeStream) return;
        if (v.readyState === 4 && v.videoWidth > 0) {
          canvas.width = v.videoWidth;
          canvas.height = v.videoHeight;
          ctx.drawImage(v, 0, 0, canvas.width, canvas.height);
          
          let qrFound = null;
          // 1. Try BarcodeDetector
          if ("BarcodeDetector" in window) {
            try {
              const detector = new BarcodeDetector({ formats: ["qr_code"] });
              const barcodes = await detector.detect(canvas);
              if (barcodes && barcodes.length > 0 && barcodes[0].rawValue) {
                qrFound = barcodes[0].rawValue;
              }
            } catch(be){}
          }
          // 2. Try jsQR
          if (!qrFound && window.jsQR) {
            try {
              const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
              const res = window.jsQR(imgData.data, imgData.width, imgData.height, { inversionAttempts: "attemptBoth" });
              if (res && res.data) qrFound = res.data;
            } catch(qe){}
          }

          if (qrFound) {
            stopped = true;
            stopCamera();
            err.textContent = "QR scanned!";
            self.applyQr(qrFound);
            return;
          }
        }
        requestAnimationFrame(scanFrame);
      };
      requestAnimationFrame(scanFrame);
    }).catch(e => {
      if (sBox) sBox.style.display = "none";
      err.textContent = "Opening camera...";
      if(f) f.click();
    });
  },
  async doLogin(usr,pwd){
    const err=document.getElementById("vpos-li-err");
    if(!usr||!pwd){err.textContent="Enter user ID and password.";return;}
    err.textContent="Signing in...";
    try{
      const j=await frappeLogin(usr,pwd);
      if(j&&(j.message==="Logged In"||j.full_name||j.home_route||(j&&!j.exc))){
        this.user=usr;window.__vposPwd=pwd;
        if (this._keyHandler) {
          document.removeEventListener("keydown", this._keyHandler);
          this._keyHandler = null;
        }
        await this.afterLogin();
      } else {
        err.textContent=(j&&j.message)?j.message:"Login failed.";
      }
    }catch(e){err.textContent="Login error: "+e.message;}
  },
  async afterLogin(){
    const c=await api("vehicle_management.vehicle_management.pos_api.get_cashier");
    if(c&&c.company){this.company=c.company;this.cashier=c.user;this.email=c.email||c.user;this.employee=c.employee||"";this.empName=c.employee_name||"";this.empNo=c.employee_number||"";this.designation=c.designation||"";this.branch=c.branch||"";this.department=c.department||"";this.reportsTo=c.reports_to_name||c.reports_to||"";}
    else{this.company=null;this.cashier=this.user;this.email=this.user;this.employee="";this.empName="";this.empNo="";this.designation="";this.branch="";this.department="";this.reportsTo="";}
    this.loggedIn=true;
    this.build();
    this.load();
  },
  """

patched_html = html[:start_idx] + new_login_block + html[end_idx:]

with open("c:/Users/josem/erpnext-system/vps_migration/temp_patched2.html", "w", encoding="utf-8") as f:
    f.write(patched_html)

node_cmd = ["node", "-e",
    "const fs=require('fs');const h=fs.readFileSync('c:/Users/josem/erpnext-system/vps_migration/temp_patched2.html','utf8');"
    "const s=[...h.matchAll(/<script[^>]*>([\\s\\S]*?)<\\/script>/g)].map(m=>m[1]);"
    "let bad=0;s.forEach((b,i)=>{try{new Function(b)}catch(e){console.log('block',i,'ERR',e.message.slice(0,120));bad++}});"
    "console.log('blocks',s.length,'bad',bad);process.exit(bad?1:0)"
]
node_res = subprocess.run(node_cmd, capture_output=True, text=True)
print("NODE VALIDATION:", node_res.stdout.strip(), node_res.stderr.strip())
if node_res.returncode != 0:
    print("JS validation failed!")
    exit(2)

save_data = urllib.parse.urlencode({"data": json.dumps({"main_section_html": patched_html})}).encode()
req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Web%20Page/vehicle-pos-terminal', data=save_data, headers=H)
req.get_method = lambda: 'PUT'
r_put = op.open(req)
print("PUT STATUS:", r_put.status)
print("SUCCESSFULLY APPLIED CAMERA CAPTURE FALLBACK")
