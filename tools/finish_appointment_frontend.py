"""One-time transformation of Gemini's portal; the HTML is the source of truth."""
from pathlib import Path
import re

path = Path('frappe-bench/apps/vehicle_management/vehicle_management/www/appointment.html')
html = path.read_text(encoding='utf-8')
html = html.replace('vehicle_management.api.portal.', 'vehicle_management.secure_portal.')
html = re.sub(r'<div class="demo-users">.*?</div>', '<p class="form-label">Existing customer? Ask your branch to link your email account to your Customer profile.</p>', html, flags=re.S)
html = html.replace('Customer Name, Mobile Phone, Email, or Plate #', 'Email Address')
html = re.sub(r'<input type="text" id="loginIdentifier"[^>]+>', '<input type="email" id="loginIdentifier" class="form-input" autocomplete="username" placeholder="Your account email" required autofocus>\n<label class="form-label" for="loginPassword">Password</label>\n<input type="password" id="loginPassword" class="form-input" autocomplete="current-password" required>', html)
html = html.replace('id="regEmail" class=', 'id="regEmail" required autocomplete="username" class=')
html = html.replace('<!-- Mode B:', '<!-- Mode B:')
html = html.replace('<input type="email" id="regEmail"', '<label class="form-label" for="regPassword">Password (at least 12 characters)</label><input type="password" id="regPassword" class="form-input" autocomplete="new-password" minlength="12" maxlength="128" required>\n<input type="email" id="regEmail"')
start = html.index('  function checkSavedSession()')
end = html.index('  // ── AUTHENTICATION', start)
html = html[:start] + '''  let portalCsrf = '';
  async function portalRequest(method, data, verb = 'POST') {
    const options = {method: verb, credentials: 'same-origin', headers: {}};
    if (portalCsrf) options.headers['X-Frappe-CSRF-Token'] = portalCsrf;
    if (verb !== 'GET') {
      options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
      options.body = new URLSearchParams(data || {});
    }
    const res = await fetch('/api/method/' + method, options);
    const json = await res.json();
    if (!res.ok) {
      let error = res.status === 401 ? 'Email or password is incorrect.' : 'Unable to complete this request.';
      try { error = JSON.parse(JSON.parse(json._server_messages)[0]).message; } catch (_) {}
      throw new Error(String(error).replace(/<[^>]*>/g, ''));
    }
    const msg = json.message || {};
    if (msg.csrf_token) portalCsrf = msg.csrf_token;
    return msg;
  }
  async function checkSavedSession() {
    localStorage.removeItem('ultra_portal_customer_ident');
    await quickLogin(null, true);
  }
  async function signIn(email, password) {
    await portalRequest('login', {usr: email, pwd: password});
    portalCsrf = '';
    const msg = await portalRequest('vehicle_management.secure_portal.get_customer_data', null, 'GET');
    if (!msg.success) throw new Error('Ask your branch to link your Customer profile.');
    document.getElementById('loginPassword').value = '';
    document.getElementById('regPassword').value = '';
    setCustomerSession(msg);
  }

''' + html[end:]
start = html.index('  async function handleLoginSubmit(')
end = html.index('  async function handleRegisterSubmit(', start)
html = html[:start] + '''  async function handleLoginSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('btnLoginSubmit');
    btn.disabled = true;
    try {
      await signIn(document.getElementById('loginIdentifier').value.trim(), document.getElementById('loginPassword').value);
      showToast('Welcome to your customer portal.', 'success');
    } catch (err) { showToast(err.message, 'error'); }
    finally { btn.disabled = false; }
  }
  async function quickLogin(identifier, silent = false) {
    try {
      const msg = await portalRequest('vehicle_management.secure_portal.get_customer_data', null, 'GET');
      if (msg.success) setCustomerSession(msg);
    } catch (err) { if (!silent) showToast(err.message, 'error'); }
  }

''' + html[end:]
html = html.replace("customer_email: document.getElementById('regEmail').value.trim(),", "customer_email: document.getElementById('regEmail').value.trim(),\n      password: document.getElementById('regPassword').value,")
# Replace the three mutation fetch blocks with CSRF-aware, status-aware requests.
html = re.sub(r"const res = await fetch\('/api/method/(vehicle_management.secure_portal.\w+)', \{.*?const msg = json.message \|\| \{\};", lambda m: "const msg = await portalRequest('" + m[1] + "', payload);", html, flags=re.S)
html = html.replace("setCustomerSession(msg);\n        showToast(`Profile", "await signIn(payload.customer_email, payload.password);\n        showToast(`Profile")
html = html.replace("localStorage.setItem('ultra_portal_customer_ident', currentCustomer.name || currentCustomer.phone);", "// Authentication is held by the server session, never a public identifier.")
html = html.replace('  function logoutCustomer() {', "  async function logoutCustomer() {\n    try { await portalRequest('logout'); } catch (err) { showToast(err.message, 'error'); return; }\n    portalCsrf = '';")
html = html.replace("showToast('Registration failed. Please check your connection.', 'error');", "showToast(err.message, 'error');")
html = html.replace("showToast('Error adding vehicle.', 'error');", "showToast(err.message, 'error');")
html = html.replace("showToast('Network error while scheduling appointment.', 'error');", "showToast(err.message, 'error');")
html = html.replace('confirmed successfully!', 'requested. Your branch will confirm availability.')
html = html.replace('Confirming Appointment...', 'Sending Appointment Request...').replace('Confirm & Schedule Appointment', 'Request Appointment')
html = html.replace('quickLogin(currentCustomer.name, true);', 'await quickLogin(null, true);')
html = html.replace("const tomorrow = d.toISOString().split('T')[0];", "const tomorrow = [d.getFullYear(), String(d.getMonth()+1).padStart(2,'0'), String(d.getDate()).padStart(2,'0')].join('-');")
html = html.replace("${b.bays || 8} Service Bays", 'Availability confirmed by branch').replace("${b.bays || 8} Bays", 'Ask branch')
html = html.replace("${b.phone || '0917-555-0101'}", "${b.phone || 'Not configured'}").replace("${b.address || 'Pampanga'}", "${b.address || 'Contact branch'}")
html = html.replace("(${s.duration})", "${s.duration || ''}")
html = html.replace("${v.year || '2024'}", "${v.year || 'Year not provided'}")
html = html.replace("${v.transmission || 'Automatic'}", "${v.transmission || 'Not specified'}")
html = html.replace("`${(currentCustomer.loyalty_points || 0)} loyalty pts`", "'Registered profile'")
# Encode data in HTML templates; use indices for onclick arguments so HTML decoding cannot inject JS.
html = html.replace('currentVehicles.map(v =>', 'currentVehicles.map((v, index) =>')
html = html.replace("scheduleForVehicle('${v.plate_no}')", "scheduleForVehicle(currentVehicles[${index}].plate_no)")
html = html.replace('referenceBranches.map(b =>', 'referenceBranches.map((b, index) =>')
html = html.replace("toggleBranchTile('${b.key}')", "toggleBranchTile(referenceBranches[${index}].key)")
html = html.replace("selectBranchAndSchedule('${b.key}')", "selectBranchAndSchedule(referenceBranches[${index}].key)")
html = html.replace("selectServicePill(this, '${s.name}')", "selectServicePill(this, referenceServices[${idx}].name)")
html = html.replace("  let portalCsrf = '';", "  const esc = value => String(value ?? '').replace(/[&<>\"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[ch]));\n  let portalCsrf = '';")
# Wrap interpolated record expressions (not nested table markup or numeric formatted values).
html = re.sub(r'\$\{((?:a|v|inv|item|b|s|m|currentCustomer)\.[^{}]+)\}', lambda m: '${esc(' + m[1] + ')}' if '.toLocaleString' not in m[1] else m[0], html)
html = html.replace('PHP ${(inv.', '${esc(inv.currency || "PHP")} ${(inv.')
html = html.replace('Rate (PHP)', 'Rate (${esc(inv.currency || "PHP")})').replace('Amount (PHP)', 'Amount (${esc(inv.currency || "PHP")})')
html = html.replace("total += (inv.grand_total || 0);", "if (inv.currency === 'PHP') total += (inv.grand_total || 0);")
html = html.replace('PHP ${total.toLocaleString', 'PHP ${total.toLocaleString')
path.write_text(html, encoding='utf-8')
