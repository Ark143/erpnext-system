import requests, json

BASE_URL = "http://38.247.138.224:10017"
session = requests.Session()
session.post(f"{BASE_URL}/api/method/login", data={'usr': 'Administrator', 'pwd': 'admin'}, timeout=30)

res = session.get(f"{BASE_URL}/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button")
cs_doc = res.json().get("data", {})

script = cs_doc.get("script", "")
if "Consolidated Multi-Company Financials" not in script:
    # Add to sidebar items
    insert_str = '{ label: "📊 Consolidated Financials & Audit", link_to: "/consolidated-financials", link_type: "URL", type: "Link", icon: "pie-chart", child: 0, collapsible: 1, indent: 0, keep_closed: 0, show_arrow: 0 },\n    '
    script = script.replace('const VM_SIDEBAR_ITEMS = [\n    ', 'const VM_SIDEBAR_ITEMS = [\n    ' + insert_str)
    
    # Also inject a global navbar button if navbar exists
    navbar_snippet = '''
  function addConsolidatedNavButton() {
    if ($("#btn-consolidated-financials").length === 0 && $(".navbar-nav").length > 0) {
      const btn = $(`
        <li class="nav-item" id="btn-consolidated-financials" style="margin-right: 8px;">
          <a class="nav-link btn btn-xs btn-default" href="/consolidated-financials" target="_blank" style="padding: 4px 10px; font-weight: 600; font-size: 12px; background: #000; color: #fff; border: 1px solid #333; border-radius: 6px;">
            📊 Consolidated Financials
          </a>
        </li>
      `);
      $(".navbar-nav.navbar-right").prepend(btn);
    }
  }
  $(document).ready(addConsolidatedNavButton);
  $(document).on("page-change toolbar_setup", addConsolidatedNavButton);
'''
    script = script + "\n" + navbar_snippet

    put_res = session.put(f"{BASE_URL}/api/resource/Client%20Script/VM%20Header%20Shortcut%20Button", json={"script": script})
    print("Updated VM Header Shortcut Button:", put_res.status_code)
else:
    print("Already added to VM Header Shortcut Button")
