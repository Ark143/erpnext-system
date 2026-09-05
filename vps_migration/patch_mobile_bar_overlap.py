import requests, json

URL = 'http://38.247.138.224:10017'
s = requests.Session()
s.post(f'{URL}/api/method/login', data={'usr': 'Administrator', 'pwd': 'admin'})

wp = s.get(f'{URL}/api/resource/Web Page/vehicle-pos-terminal').json()
html = wp['data']['main_section_html']

# 1. Update CSS to hide mobile cart bar when ticket is open and fix z-index
old_css_rule = """  .vpos-ticket.mobile-active { display: flex; }
  .vpos-mobile-back { display: inline-flex; align-items: center; }

  /* Floating Bottom Cart Bar */
  .vpos-mobile-cart-bar { display: flex; }"""

new_css_rule = """  .vpos-ticket.mobile-active { display: flex; z-index: 999 !important; }
  .vpos-mobile-back { display: inline-flex; align-items: center; }

  /* Floating Bottom Cart Bar */
  .vpos-mobile-cart-bar { display: flex; z-index: 90; }
  .vpos-ticket.mobile-active ~ .vpos-mobile-cart-bar,
  #vpos-ticket-panel.mobile-active ~ #vpos-mobile-cart-bar { display: none !important; }"""

if old_css_rule in html:
    html = html.replace(old_css_rule, new_css_rule)
    print("Replaced mobile ticket CSS rule")

# 2. Update toggleMobileTicket in JS
old_toggle = """  toggleMobileTicket(show) {
    const p = document.getElementById("vpos-ticket-panel");
    const bar = document.getElementById("vpos-mobile-cart-bar");
    if (p) {
      if (show) p.classList.add("mobile-active");
      else p.classList.remove("mobile-active");
    }
    if (bar) bar.style.display = show ? "none" : (this.cart.length ? "flex" : "none");
  },"""

new_toggle = """  toggleMobileTicket(show) {
    const p = document.getElementById("vpos-ticket-panel");
    const bar = document.getElementById("vpos-mobile-cart-bar");
    if (p) {
      if (show) {
        p.classList.add("mobile-active");
        p.style.display = "flex";
      } else {
        p.classList.remove("mobile-active");
        if (window.innerWidth <= 900) p.style.display = "none";
      }
    }
    if (bar) {
      bar.style.display = (show || !this.cart.length) ? "none" : "flex";
    }
  },"""

if old_toggle in html:
    html = html.replace(old_toggle, new_toggle)
    print("Replaced toggleMobileTicket JS function")

# Save updated HTML to Web Page
res = s.put(f'{URL}/api/resource/Web Page/vehicle-pos-terminal', json={'main_section_html': html})
print("Web Page update HTTP status:", res.status_code)
