"""
Install Web Pages for Vehicle Management Company Dashboard
"""
import sys, os
sys.path.insert(0, 'apps/frappe')
os.chdir('sites')
import frappe
frappe.init(site='erp.localhost')
frappe.connect()

from frappe.utils import now_datetime
now = now_datetime()

# ─── HUB PAGE HTML (Company Selector) ────────────────────────────────────────
HUB_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Vehicle Management — Company Hub</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#080808;--bg2:#111;--bg3:#1a1a1a;
  --card:#141414;--card-h:#1e1e1e;
  --border:#222;--border-h:#333;
  --text:#f0f0f0;--muted:#888;--accent:#fff;
  --green:#22c55e;--red:#ef4444;--amber:#f59e0b;--blue:#3b82f6;
}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',sans-serif}
/* NAV */
.nav{display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;background:rgba(8,8,8,.9);backdrop-filter:blur(16px)}
.nav-brand{display:flex;align-items:center;gap:.75rem;font-weight:800;font-size:1.1rem;letter-spacing:-.02em}
.nav-brand img{height:32px;border-radius:6px}
.nav-links{display:flex;gap:1.5rem}
.nav-links a{color:var(--muted);text-decoration:none;font-size:.875rem;font-weight:500;transition:color .2s}
.nav-links a:hover,.nav-links a.active{color:var(--text)}
.nav-badge{background:var(--border);color:var(--text);font-size:.7rem;padding:.2rem .5rem;border-radius:20px;font-weight:600}
/* HERO */
.hero{padding:4rem 2rem 2rem;text-align:center;max-width:800px;margin:0 auto}
.hero-label{font-size:.75rem;text-transform:uppercase;letter-spacing:.15em;color:var(--muted);margin-bottom:1rem}
.hero h1{font-size:clamp(2rem,5vw,3.5rem);font-weight:900;line-height:1.1;letter-spacing:-.04em;margin-bottom:1rem}
.hero h1 span{color:var(--muted)}
.hero p{color:var(--muted);font-size:1rem;max-width:500px;margin:0 auto 2rem}
.period-bar{display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap;margin-bottom:3rem}
.period-btn{background:var(--card);border:1px solid var(--border);color:var(--muted);padding:.45rem 1rem;border-radius:8px;cursor:pointer;font-size:.8rem;font-weight:500;font-family:inherit;transition:all .2s}
.period-btn:hover,.period-btn.active{background:var(--text);color:var(--bg);border-color:var(--text)}
/* SUMMARY STRIP */
.summary-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;max-width:1400px;margin:0 auto 3rem;padding:0 2rem}
.strip-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1.25rem;text-align:center;transition:all .3s}
.strip-card:hover{border-color:var(--border-h);background:var(--card-h);transform:translateY(-2px)}
.strip-v{font-size:1.5rem;font-weight:800;letter-spacing:-.03em}
.strip-l{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-top:.25rem}
/* GRID */
.companies-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1.5rem;max-width:1400px;margin:0 auto;padding:0 2rem 4rem}
/* COMPANY CARD */
.co-card{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;cursor:pointer;transition:all .35s cubic-bezier(.16,1,.3,1);position:relative}
.co-card:hover{border-color:var(--border-h);background:var(--card-h);transform:translateY(-4px);box-shadow:0 20px 60px rgba(0,0,0,.5)}
.co-card:hover .co-details{opacity:1;max-height:200px}
.co-header{display:flex;align-items:center;gap:1rem;padding:1.25rem}
.co-logo{width:48px;height:48px;border-radius:10px;object-fit:contain;background:var(--bg3);display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0}
.co-logo img{width:100%;height:100%;object-fit:contain}
.co-logo-text{width:48px;height:48px;border-radius:10px;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.9rem;color:var(--muted);flex-shrink:0}
.co-name{font-weight:700;font-size:.95rem;letter-spacing:-.01em}
.co-abbr{font-size:.7rem;color:var(--muted);margin-top:.1rem;text-transform:uppercase;letter-spacing:.08em}
.co-arrow{margin-left:auto;color:var(--muted);font-size:1.25rem;transition:transform .3s}
.co-card:hover .co-arrow{transform:translateX(4px);color:var(--text)}
.co-kpis{display:grid;grid-template-columns:1fr 1fr 1fr;border-top:1px solid var(--border)}
.kpi-cell{padding:1rem;text-align:center;border-right:1px solid var(--border)}
.kpi-cell:last-child{border-right:none}
.kpi-v{font-size:1.1rem;font-weight:700;letter-spacing:-.02em}
.kpi-l{font-size:.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:.2rem}
.co-details{overflow:hidden;max-height:0;opacity:0;transition:all .35s ease;border-top:1px solid var(--border)}
.detail-row{display:flex;align-items:center;justify-content:space-between;padding:.5rem 1.25rem;font-size:.8rem}
.detail-row span{color:var(--muted)}
.detail-row strong{color:var(--text);font-weight:600}
.co-cta{display:flex;padding:1rem 1.25rem;gap:.5rem}
.btn-dash{flex:1;padding:.6rem;border-radius:8px;border:1px solid var(--border-h);background:transparent;color:var(--text);font-size:.8rem;font-weight:600;font-family:inherit;cursor:pointer;transition:all .2s}
.btn-dash:hover,.btn-dash.primary{background:var(--text);color:var(--bg)}
/* LOADING */
.skeleton{background:linear-gradient(90deg,var(--card) 25%,var(--card-h) 50%,var(--card) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.loading-overlay{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;z-index:999;transition:opacity .5s}
.loading-overlay.hidden{opacity:0;pointer-events:none}
.spinner{width:40px;height:40px;border:2px solid var(--border);border-top-color:var(--text);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
/* TOAST */
.toast{position:fixed;bottom:2rem;right:2rem;background:var(--card-h);border:1px solid var(--border-h);color:var(--text);padding:.75rem 1.25rem;border-radius:10px;font-size:.8rem;font-weight:500;transform:translateY(100px);transition:transform .3s;z-index:999}
.toast.show{transform:translateY(0)}
/* RESPONSIVE */
@media(max-width:768px){.companies-grid{grid-template-columns:1fr}.hero{padding:2rem 1rem 1rem}.summary-strip{padding:0 1rem}}
</style>
</head>
<body>
<div class="loading-overlay" id="loader"><div class="spinner"></div></div>

<nav class="nav">
  <div class="nav-brand">
    <img src="/files/ultra_mrf_logo.png" alt="Logo" onerror="this.style.display='none'"/>
    <span>VM Analytics</span>
  </div>
  <div class="nav-links">
    <a href="/vm-dashboard" class="active">Hub</a>
    <a href="/desk#vehicle-management">ERPNext</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-label">Vehicle Management System</div>
  <h1>Company <span>Performance</span> Hub</h1>
  <p>Real-time analytics across all branches and companies. Hover over cards to see details.</p>
  <div class="period-bar">
    <button class="period-btn" data-period="this_month">This Month</button>
    <button class="period-btn active" data-period="this_year">This Year</button>
    <button class="period-btn" data-period="last_year">Last Year</button>
    <button class="period-btn" data-period="all_time">All Time</button>
  </div>
</div>

<div class="summary-strip" id="summaryStrip">
  <div class="strip-card"><div class="kpi-v skeleton" style="height:28px;width:80%;margin:0 auto"></div><div class="strip-l skeleton" style="height:12px;width:60%;margin:.5rem auto 0"></div></div>
  <div class="strip-card"><div class="kpi-v skeleton" style="height:28px;width:80%;margin:0 auto"></div><div class="strip-l skeleton" style="height:12px;width:60%;margin:.5rem auto 0"></div></div>
  <div class="strip-card"><div class="kpi-v skeleton" style="height:28px;width:80%;margin:0 auto"></div><div class="strip-l skeleton" style="height:12px;width:60%;margin:.5rem auto 0"></div></div>
  <div class="strip-card"><div class="kpi-v skeleton" style="height:28px;width:80%;margin:0 auto"></div><div class="strip-l skeleton" style="height:12px;width:60%;margin:.5rem auto 0"></div></div>
</div>

<div class="companies-grid" id="companiesGrid">
</div>

<div class="toast" id="toast"></div>

<script>
const API = '/api/method/vehicle_management.vehicle_management.dashboard_api';
let currentPeriod = 'this_year';
let companiesData = [];

const fmt = (n, dec=0) => {
  if(n === null || n === undefined) return '—';
  if(n >= 1_000_000) return '₱' + (n/1_000_000).toFixed(1) + 'M';
  if(n >= 1_000) return '₱' + (n/1_000).toFixed(0) + 'K';
  return '₱' + Number(n).toLocaleString('en-PH', {minimumFractionDigits:dec, maximumFractionDigits:dec});
};
const fmtN = n => Number(n||0).toLocaleString();

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

async function loadHub(period) {
  try {
    const res = await fetch(`${API}.get_all_companies_summary`, {
      method:'POST', headers:{'Content-Type':'application/json','X-Frappe-CSRF-Token':''},
      body: JSON.stringify({})
    });
    const json = await res.json();
    companiesData = json.message || [];
    renderGrid(companiesData);
    renderSummary(companiesData);
  } catch(e) {
    console.error(e);
    showToast('Failed to load data');
  } finally {
    document.getElementById('loader').classList.add('hidden');
  }
}

function renderSummary(data) {
  const totalRev = data.reduce((s,c) => s + (c.ytd_revenue||0), 0);
  const totalJO = data.reduce((s,c) => s + (c.ytd_jo_count||0), 0);
  const totalInv = data.reduce((s,c) => s + (c.ytd_invoices||0), 0);
  document.getElementById('summaryStrip').innerHTML = `
    <div class="strip-card"><div class="strip-v">${data.length}</div><div class="strip-l">Active Companies</div></div>
    <div class="strip-card"><div class="strip-v">${fmt(totalRev)}</div><div class="strip-l">YTD Total Revenue</div></div>
    <div class="strip-card"><div class="strip-v">${fmtN(totalJO)}</div><div class="strip-l">YTD Job Orders</div></div>
    <div class="strip-card"><div class="strip-v">${fmtN(totalInv)}</div><div class="strip-l">YTD Invoices</div></div>
  `;
}

function renderGrid(data) {
  const grid = document.getElementById('companiesGrid');
  grid.innerHTML = '';
  data.forEach(co => {
    const card = document.createElement('div');
    card.className = 'co-card';
    const logoHTML = co.logo
      ? `<div class="co-logo"><img src="${co.logo}" alt="${co.name}" onerror="this.parentElement.innerHTML='<span style=\\"font-weight:700;color:#888\\">${co.abbr}</span>'"/></div>`
      : `<div class="co-logo-text">${co.abbr}</div>`;
    card.innerHTML = `
      <div class="co-header">
        ${logoHTML}
        <div>
          <div class="co-name">${co.name}</div>
          <div class="co-abbr">${co.abbr}</div>
        </div>
        <div class="co-arrow">→</div>
      </div>
      <div class="co-kpis">
        <div class="kpi-cell"><div class="kpi-v">${fmt(co.ytd_revenue)}</div><div class="kpi-l">Revenue</div></div>
        <div class="kpi-cell"><div class="kpi-v">${fmtN(co.ytd_jo_count)}</div><div class="kpi-l">Job Orders</div></div>
        <div class="kpi-cell"><div class="kpi-v">${fmtN(co.ytd_invoices)}</div><div class="kpi-l">Invoices</div></div>
      </div>
      <div class="co-details">
        <div class="detail-row"><span>YTD Revenue</span><strong>${fmt(co.ytd_revenue, 2)}</strong></div>
        <div class="detail-row"><span>Job Orders</span><strong>${fmtN(co.ytd_jo_count)}</strong></div>
        <div class="detail-row"><span>Invoices</span><strong>${fmtN(co.ytd_invoices)}</strong></div>
        <div class="co-cta">
          <button class="btn-dash primary" onclick="window.location='/vm-company-dashboard?company=${encodeURIComponent(co.name)}'">View Dashboard →</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

document.querySelectorAll('.period-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentPeriod = btn.dataset.period;
    document.getElementById('loader').classList.remove('hidden');
    loadHub(currentPeriod);
  });
});

loadHub(currentPeriod);
</script>
</body>
</html>
"""

# ─── COMPANY DASHBOARD PAGE HTML ─────────────────────────────────────────────
DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title id="pageTitle">VM Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#080808;--bg2:#0e0e0e;--bg3:#161616;
  --card:#111;--card-h:#181818;
  --border:#1e1e1e;--border-h:#2a2a2a;
  --text:#f0f0f0;--muted:#666;--muted2:#888;
  --accent:#fff;
  --green:#22c55e;--red:#ef4444;--amber:#f59e0b;--blue:#60a5fa;
  --grad:linear-gradient(135deg,#1a1a1a 0%,#0d0d0d 100%);
}
html,body{min-height:100%;background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}
/* LOADER */
.loading-overlay{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;z-index:9999;transition:opacity .6s}
.loading-overlay.hidden{opacity:0;pointer-events:none}
.loader-content{text-align:center}
.spinner{width:44px;height:44px;border:2px solid var(--border-h);border-top-color:var(--text);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 1rem}
.loader-text{color:var(--muted2);font-size:.875rem}
@keyframes spin{to{transform:rotate(360deg)}}
/* NAV */
.nav{display:flex;align-items:center;justify-content:space-between;padding:.875rem 1.75rem;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;background:rgba(8,8,8,.92);backdrop-filter:blur(20px)}
.nav-brand{display:flex;align-items:center;gap:.75rem}
.co-logo-nav{height:32px;width:32px;border-radius:8px;object-fit:contain;background:var(--bg3)}
.co-name-nav{font-weight:700;font-size:.9rem;letter-spacing:-.01em}
.co-abbr-nav{font-size:.65rem;color:var(--muted);margin-left:.5rem;text-transform:uppercase;letter-spacing:.1em}
.nav-right{display:flex;align-items:center;gap:1rem}
.nav-links{display:flex;gap:1rem}
.nav-links a{color:var(--muted);text-decoration:none;font-size:.8rem;font-weight:500;transition:color .2s}
.nav-links a:hover{color:var(--text)}
.company-select{background:var(--card);border:1px solid var(--border-h);color:var(--text);padding:.4rem .75rem;border-radius:8px;font-size:.8rem;font-family:inherit;cursor:pointer;outline:none}
/* PERIOD TABS */
.period-bar{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.75rem;border-bottom:1px solid var(--border)}
.period-tabs{display:flex;gap:.375rem;background:var(--bg2);padding:.25rem;border-radius:10px;border:1px solid var(--border)}
.period-tab{padding:.375rem .875rem;border-radius:7px;border:none;background:transparent;color:var(--muted);font-size:.78rem;font-weight:500;font-family:inherit;cursor:pointer;transition:all .2s}
.period-tab.active{background:var(--text);color:var(--bg)}
.last-update{font-size:.7rem;color:var(--muted);display:flex;align-items:center;gap:.375rem}
.dot{width:6px;height:6px;background:var(--green);border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
/* MAIN */
.main{padding:1.5rem 1.75rem;max-width:1600px;margin:0 auto}
/* SECTION HEADER */
.section-hd{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem}
.section-title{font-size:.7rem;text-transform:uppercase;letter-spacing:.15em;color:var(--muted);font-weight:600}
/* KPI ROW */
.kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.875rem;margin-bottom:1.5rem}
.kpi-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.25rem;position:relative;overflow:hidden;cursor:default;transition:all .35s cubic-bezier(.16,1,.3,1)}
.kpi-card::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.015) 0%,transparent 100%);pointer-events:none}
.kpi-card:hover{border-color:var(--border-h);background:var(--card-h);transform:translateY(-3px);box-shadow:0 16px 48px rgba(0,0,0,.4)}
.kpi-card:hover .kpi-tooltip{opacity:1;transform:translateY(0)}
.kpi-icon{font-size:1.25rem;margin-bottom:.75rem}
.kpi-label{font-size:.65rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:.35rem}
.kpi-value{font-size:1.6rem;font-weight:800;letter-spacing:-.04em;line-height:1}
.kpi-sub{font-size:.72rem;color:var(--muted2);margin-top:.4rem}
.kpi-tooltip{position:absolute;bottom:0;left:0;right:0;background:var(--card-h);border-top:1px solid var(--border-h);padding:.625rem 1rem;font-size:.72rem;color:var(--muted2);opacity:0;transform:translateY(8px);transition:all .25s;pointer-events:none}
/* CHARTS GRID */
.charts-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem}
.chart-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.25rem}
.chart-card.wide{grid-column:1/-1}
.chart-title{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:1rem}
.chart-wrap{position:relative;height:200px}
/* TABLES GRID */
.tables-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem}
.table-card{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden}
.table-card.wide{grid-column:1/-1}
.table-hd{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;border-bottom:1px solid var(--border)}
.table-hd-title{font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}
.tbl{width:100%;border-collapse:collapse}
.tbl th{padding:.6rem 1rem;font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);text-align:left;border-bottom:1px solid var(--border);font-weight:500}
.tbl td{padding:.65rem 1rem;font-size:.8rem;border-bottom:1px solid var(--border);transition:background .2s;vertical-align:middle}
.tbl tr:last-child td{border-bottom:none}
.tbl tbody tr:hover td{background:var(--card-h)}
.rank-badge{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:6px;font-size:.65rem;font-weight:700;background:var(--bg3);color:var(--muted)}
.rank-badge.gold{background:rgba(245,158,11,.12);color:#f59e0b}
.rank-badge.silver{background:rgba(148,163,184,.12);color:#94a3b8}
.rank-badge.bronze{background:rgba(180,83,9,.12);color:#b45309}
.bar-inline{display:inline-block;height:4px;background:var(--border-h);border-radius:2px;vertical-align:middle;position:relative;overflow:hidden;margin-left:.5rem}
.bar-fill{height:100%;background:var(--text);border-radius:2px;transition:width .8s ease}
.badge-status{padding:.2rem .55rem;border-radius:6px;font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.badge-completed{background:rgba(34,197,94,.12);color:var(--green)}
.badge-progress{background:rgba(96,165,250,.12);color:var(--blue)}
.badge-released{background:rgba(245,158,11,.12);color:var(--amber)}
/* AUDIT TRAIL */
.audit-card{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;margin-bottom:1.5rem}
.audit-row{display:grid;grid-template-columns:auto 1fr auto auto;gap:1rem;align-items:center;padding:.75rem 1.25rem;border-bottom:1px solid var(--border);transition:background .2s;font-size:.8rem}
.audit-row:last-child{border-bottom:none}
.audit-row:hover{background:var(--card-h)}
.audit-type{padding:.2rem .55rem;border-radius:6px;font-size:.65rem;font-weight:600;white-space:nowrap}
.audit-si{background:rgba(96,165,250,.1);color:var(--blue)}
.audit-jo{background:rgba(34,197,94,.1);color:var(--green)}
.audit-pay{background:rgba(245,158,11,.1);color:var(--amber)}
.audit-ref{font-weight:600;color:var(--text)}
.audit-party{color:var(--muted2);font-size:.75rem}
.audit-amt{font-weight:700;text-align:right}
.audit-date{color:var(--muted);font-size:.7rem;text-align:right;white-space:nowrap}
/* DUE SERVICE */
.due-card{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;margin-bottom:1.5rem}
.due-row{display:grid;grid-template-columns:1fr auto auto;gap:1rem;align-items:center;padding:.75rem 1.25rem;border-bottom:1px solid var(--border);transition:background .2s;font-size:.8rem}
.due-row:last-child{border-bottom:none}
.due-row:hover{background:var(--card-h)}
.due-days{padding:.2rem .6rem;border-radius:6px;font-size:.7rem;font-weight:700}
.due-urgent{background:rgba(239,68,68,.12);color:var(--red)}
.due-soon{background:rgba(245,158,11,.12);color:var(--amber)}
.due-ok{background:rgba(34,197,94,.12);color:var(--green)}
/* RESPONSIVE */
@media(max-width:900px){.charts-grid,.tables-grid{grid-template-columns:1fr}.chart-card.wide,.table-card.wide{grid-column:1}}
@media(max-width:600px){.kpi-row{grid-template-columns:1fr 1fr}.main{padding:1rem}.period-bar{flex-direction:column;gap:.75rem;align-items:flex-start}}
</style>
</head>
<body>
<div class="loading-overlay" id="loader">
  <div class="loader-content">
    <div class="spinner"></div>
    <div class="loader-text">Loading dashboard…</div>
  </div>
</div>

<nav class="nav">
  <div class="nav-brand">
    <img id="coLogoNav" class="co-logo-nav" src="/files/ultra_mrf_logo.png" alt="Logo" onerror="this.style.display='none'"/>
    <span class="co-name-nav" id="coNameNav">Loading…</span>
    <span class="co-abbr-nav" id="coAbbrNav"></span>
  </div>
  <div class="nav-right">
    <select class="company-select" id="companySelect" onchange="switchCompany(this.value)">
      <option value="">All Companies</option>
    </select>
    <div class="nav-links">
      <a href="/vm-dashboard">← Hub</a>
      <a href="/desk#vehicle-management">ERPNext</a>
    </div>
  </div>
</nav>

<div class="period-bar">
  <div class="period-tabs">
    <button class="period-tab" data-p="this_month">Month</button>
    <button class="period-tab active" data-p="this_year">Year</button>
    <button class="period-tab" data-p="last_year">Last Year</button>
    <button class="period-tab" data-p="all_time">All Time</button>
  </div>
  <div class="last-update"><div class="dot"></div><span id="lastUpdate">—</span></div>
</div>

<div class="main" id="mainContent">
  <!-- content injected by JS -->
</div>

<script>
const API_BASE = '/api/method/vehicle_management.vehicle_management.dashboard_api';
const params = new URLSearchParams(window.location.search);
let currentCompany = params.get('company') || '';
let currentPeriod = 'this_year';
let chartRevenue, chartJO, chartPL;

// ─── Format helpers ───────────────────────────────────────────────────────────
const phpFmt = new Intl.NumberFormat('en-PH',{style:'currency',currency:'PHP',minimumFractionDigits:0,maximumFractionDigits:0});
const numFmt = new Intl.NumberFormat('en-PH');
const fmt = n => { n=Number(n||0); if(n>=1e6) return '₱'+(n/1e6).toFixed(1)+'M'; if(n>=1e3) return '₱'+(n/1e3).toFixed(0)+'K'; return '₱'+n.toFixed(0); };
const fmtFull = n => phpFmt.format(Number(n||0));
const fmtN = n => numFmt.format(Number(n||0));
const fmtDate = s => s ? new Date(s).toLocaleDateString('en-PH',{month:'short',day:'numeric',year:'numeric'}) : '—';
const rankBadge = (i) => {
  if(i===0) return '<span class="rank-badge gold">1</span>';
  if(i===1) return '<span class="rank-badge silver">2</span>';
  if(i===2) return '<span class="rank-badge bronze">3</span>';
  return `<span class="rank-badge">${i+1}</span>`;
};
const bar = (val,max) => {
  const pct = max > 0 ? Math.round(val/max*100) : 0;
  return `<span class="bar-inline" style="width:60px"><span class="bar-fill" style="width:${pct}%"></span></span>`;
};

// ─── Chart default options ────────────────────────────────────────────────────
Chart.defaults.color = '#666';
Chart.defaults.font.family = 'Inter';
Chart.defaults.font.size = 11;
const gridColor = '#1e1e1e';
const textColor = '#888';

function destroyChart(ref) { if(ref && ref.chart) { ref.chart.destroy(); ref.chart = null; } }

// ─── Load Data ────────────────────────────────────────────────────────────────
async function loadDashboard() {
  document.getElementById('loader').classList.remove('hidden');
  try {
    const res = await fetch(`${API_BASE}.get_company_dashboard`, {
      method:'POST',
      headers:{'Content-Type':'application/json','X-Frappe-CSRF-Token':''},
      body: JSON.stringify({ company: currentCompany || null, period: currentPeriod })
    });
    const json = await res.json();
    const data = json.message;
    if(!data) throw new Error('No data');
    renderAll(data);
    populateCompanySelect(data.all_companies);
  } catch(e) {
    console.error(e);
    document.getElementById('mainContent').innerHTML = `<div style="text-align:center;padding:4rem;color:#666">Failed to load dashboard. <a href="javascript:loadDashboard()" style="color:#f0f0f0">Retry</a></div>`;
  } finally {
    document.getElementById('loader').classList.add('hidden');
    document.getElementById('lastUpdate').textContent = 'Updated ' + new Date().toLocaleTimeString('en-PH',{hour:'2-digit',minute:'2-digit'});
  }
}

function populateCompanySelect(companies) {
  const sel = document.getElementById('companySelect');
  sel.innerHTML = '<option value="">All Companies</option>';
  (companies||[]).forEach(co => {
    const opt = document.createElement('option');
    opt.value = co.name; opt.textContent = co.name;
    if(co.name === currentCompany) opt.selected = true;
    sel.appendChild(opt);
  });
}

function switchCompany(company) {
  currentCompany = company;
  const url = new URL(window.location);
  if(company) url.searchParams.set('company', company);
  else url.searchParams.delete('company');
  window.history.pushState({}, '', url);
  loadDashboard();
}

// ─── Render All ───────────────────────────────────────────────────────────────
function renderAll(data) {
  const co = data.company_info;
  const kpi = data.kpis;

  // Nav
  document.getElementById('coNameNav').textContent = data.company;
  document.getElementById('coAbbrNav').textContent = co?.abbr || '';
  document.getElementById('pageTitle').textContent = `${data.company} — VM Dashboard`;
  if(co?.company_logo) document.getElementById('coLogoNav').src = co.company_logo;

  // Build main content
  document.getElementById('mainContent').innerHTML = `
    <!-- KPI CARDS -->
    <div class="section-hd"><div class="section-title">Key Performance Indicators</div><div style="font-size:.7rem;color:var(--muted)">${data.from_date} → ${data.to_date}</div></div>
    <div class="kpi-row" id="kpiRow"></div>

    <!-- CHARTS -->
    <div class="charts-grid" id="chartsGrid">
      <div class="chart-card"><div class="chart-title">Monthly Revenue Trend</div><div class="chart-wrap"><canvas id="chartRevenue"></canvas></div></div>
      <div class="chart-card"><div class="chart-title">Monthly Job Orders</div><div class="chart-wrap"><canvas id="chartJO"></canvas></div></div>
      <div class="chart-card"><div class="chart-title">Labor vs Parts Revenue</div><div class="chart-wrap"><canvas id="chartPL"></canvas></div></div>
      <div class="chart-card"><div class="chart-title">Job Order Status</div><div class="chart-wrap"><canvas id="chartStatus"></canvas></div></div>
    </div>

    <!-- TOP TABLES -->
    <div class="tables-grid">
      <!-- Top Customers -->
      <div class="table-card">
        <div class="table-hd"><div class="table-hd-title">Top Customers</div></div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Customer</th><th>Visits</th><th>Revenue</th></tr></thead>
          <tbody id="tblCustomers"></tbody>
        </table>
      </div>
      <!-- Top Vehicles -->
      <div class="table-card">
        <div class="table-hd"><div class="table-hd-title">Top Vehicles Served</div></div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Vehicle</th><th>Visits</th><th>Revenue</th></tr></thead>
          <tbody id="tblVehicles"></tbody>
        </table>
      </div>
      <!-- Top Services -->
      <div class="table-card">
        <div class="table-hd"><div class="table-hd-title">Top Selling Services</div></div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Service</th><th>Count</th><th>Revenue</th></tr></thead>
          <tbody id="tblServices"></tbody>
        </table>
      </div>
      <!-- Top Products -->
      <div class="table-card">
        <div class="table-hd"><div class="table-hd-title">Top Selling Products</div></div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Product</th><th>Qty</th><th>Revenue</th></tr></thead>
          <tbody id="tblProducts"></tbody>
        </table>
      </div>
    </div>

    <!-- DUE FOR SERVICE -->
    <div class="section-hd"><div class="section-title">Due for Service (Next 90 Days)</div></div>
    <div class="due-card" id="dueCard"></div>

    <!-- AUDIT TRAIL -->
    <div class="section-hd"><div class="section-title">Audit Trail — Recent Transactions</div></div>
    <div class="audit-card" id="auditCard"></div>
  `;

  renderKPIs(kpi);
  renderCharts(data);
  renderTopTables(data);
  renderDueService(data.due_for_service);
  renderAuditTrail(data.audit_trail);
}

// ─── KPI Cards ────────────────────────────────────────────────────────────────
function renderKPIs(k) {
  const cards = [
    { icon:'💰', label:'Total Revenue', value: fmt(k.total_revenue), sub: `${fmtN(k.invoice_count)} invoices`, tip: `Full amount: ${fmtFull(k.total_revenue)}` },
    { icon:'🔧', label:'Job Orders', value: fmtN(k.total_jo), sub: `${fmtN(k.completed_jo)} completed`, tip: `In Progress: ${k.in_progress_jo} | Released: ${k.released_jo}` },
    { icon:'⚙️', label:'Labor Revenue', value: fmt(k.labor_revenue), sub: 'Service income', tip: `Exact: ${fmtFull(k.labor_revenue)}` },
    { icon:'📦', label:'Parts Revenue', value: fmt(k.parts_revenue), sub: 'Parts & tires', tip: `Exact: ${fmtFull(k.parts_revenue)}` },
    { icon:'🛒', label:'Purchases', value: fmt(k.total_purchases), sub: `${fmtN(k.po_count)} POs`, tip: `Total purchasing spend: ${fmtFull(k.total_purchases)}` },
    { icon:'💳', label:'Collected', value: fmt(k.total_collected), sub: `${fmtN(k.payment_count)} payments`, tip: `Cash received from customers` },
    { icon:'👥', label:'Customers', value: fmtN(k.unique_customers), sub: 'Unique served', tip: `Unique vehicles: ${fmtN(k.unique_vehicles)}` },
    { icon:'🏆', label:'Commissions', value: fmt(k.total_commissions), sub: '50% per transaction', tip: `Sales team commissions paid: ${fmtFull(k.total_commissions)}` },
  ];
  document.getElementById('kpiRow').innerHTML = cards.map(c => `
    <div class="kpi-card">
      <div class="kpi-icon">${c.icon}</div>
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value">${c.value}</div>
      <div class="kpi-sub">${c.sub}</div>
      <div class="kpi-tooltip">${c.tip}</div>
    </div>
  `).join('');
}

// ─── Charts ───────────────────────────────────────────────────────────────────
function renderCharts(data) {
  const revTrend = data.revenue_trend || [];
  const joTrend = data.jo_trend || [];
  const kpi = data.kpis;

  // Revenue Trend
  if(window._chartRev) window._chartRev.destroy();
  window._chartRev = new Chart(document.getElementById('chartRevenue').getContext('2d'), {
    type:'line',
    data:{
      labels: revTrend.map(r=>r.label),
      datasets:[{
        label:'Revenue (PHP)',
        data: revTrend.map(r=>r.revenue),
        borderColor:'#fff',
        backgroundColor:'rgba(255,255,255,.05)',
        borderWidth:2,
        tension:.4,
        fill:true,
        pointRadius:3,
        pointBackgroundColor:'#fff',
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>' '+fmtFull(ctx.raw)}}},
      scales:{
        x:{grid:{color:gridColor},ticks:{color:textColor}},
        y:{grid:{color:gridColor},ticks:{color:textColor,callback:v=>fmt(v)}}
      }
    }
  });

  // JO Trend
  if(window._chartJO) window._chartJO.destroy();
  window._chartJO = new Chart(document.getElementById('chartJO').getContext('2d'), {
    type:'bar',
    data:{
      labels: joTrend.map(r=>r.label),
      datasets:[{
        label:'Job Orders',
        data: joTrend.map(r=>r.jo_count),
        backgroundColor:'rgba(255,255,255,.15)',
        borderColor:'rgba(255,255,255,.3)',
        borderWidth:1,
        borderRadius:4,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${ctx.raw} job orders`}}},
      scales:{
        x:{grid:{color:gridColor},ticks:{color:textColor}},
        y:{grid:{color:gridColor},ticks:{color:textColor},beginAtZero:true}
      }
    }
  });

  // Labor vs Parts Donut
  if(window._chartPL) window._chartPL.destroy();
  window._chartPL = new Chart(document.getElementById('chartPL').getContext('2d'), {
    type:'doughnut',
    data:{
      labels:['Labor / Services','Parts & Tires'],
      datasets:[{
        data:[kpi.labor_revenue, kpi.parts_revenue],
        backgroundColor:['rgba(255,255,255,.85)','rgba(255,255,255,.2)'],
        borderColor:['#fff','#333'],
        borderWidth:1,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      cutout:'68%',
      plugins:{
        legend:{position:'bottom',labels:{color:textColor,padding:16,font:{size:11}}},
        tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${fmtFull(ctx.raw)}`}}
      }
    }
  });

  // JO Status Donut
  if(window._chartStatus) window._chartStatus.destroy();
  window._chartStatus = new Chart(document.getElementById('chartStatus').getContext('2d'), {
    type:'doughnut',
    data:{
      labels:['Completed','In Progress','Released'],
      datasets:[{
        data:[kpi.completed_jo, kpi.in_progress_jo, kpi.released_jo],
        backgroundColor:['rgba(34,197,94,.7)','rgba(96,165,250,.7)','rgba(245,158,11,.7)'],
        borderColor:['#22c55e','#60a5fa','#f59e0b'],
        borderWidth:1,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      cutout:'68%',
      plugins:{
        legend:{position:'bottom',labels:{color:textColor,padding:16,font:{size:11}}},
        tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${ctx.raw}`}}
      }
    }
  });
}

// ─── Top Tables ───────────────────────────────────────────────────────────────
function renderTopTables(data) {
  const maxCust = data.top_customers?.[0]?.total_spent || 1;
  document.getElementById('tblCustomers').innerHTML = (data.top_customers||[]).map((r,i)=>`
    <tr><td>${rankBadge(i)}</td>
    <td>${r.customer||'—'}</td>
    <td>${fmtN(r.visits)}</td>
    <td>${fmt(r.total_spent)}${bar(r.total_spent,maxCust)}</td></tr>
  `).join('') || '<tr><td colspan="4" style="color:#666;text-align:center;padding:1.5rem">No data</td></tr>';

  const maxVeh = data.top_vehicles?.[0]?.visits || 1;
  document.getElementById('tblVehicles').innerHTML = (data.top_vehicles||[]).map((r,i)=>`
    <tr><td>${rankBadge(i)}</td>
    <td>${r.vehicle||'—'}</td>
    <td>${fmtN(r.visits)}${bar(r.visits,maxVeh)}</td>
    <td>${fmt(r.revenue)}</td></tr>
  `).join('') || '<tr><td colspan="4" style="color:#666;text-align:center;padding:1.5rem">No data</td></tr>';

  const maxSvc = data.top_services?.[0]?.revenue || 1;
  document.getElementById('tblServices').innerHTML = (data.top_services||[]).map((r,i)=>`
    <tr><td>${rankBadge(i)}</td>
    <td>${r.name||'—'}</td>
    <td>${fmtN(r.count)}</td>
    <td>${fmt(r.revenue)}${bar(r.revenue,maxSvc)}</td></tr>
  `).join('') || '<tr><td colspan="4" style="color:#666;text-align:center;padding:1.5rem">No data</td></tr>';

  const maxProd = data.top_products?.[0]?.revenue || 1;
  document.getElementById('tblProducts').innerHTML = (data.top_products||[]).map((r,i)=>`
    <tr><td>${rankBadge(i)}</td>
    <td>${r.name||'—'}</td>
    <td>${fmtN(r.qty)}</td>
    <td>${fmt(r.revenue)}${bar(r.revenue,maxProd)}</td></tr>
  `).join('') || '<tr><td colspan="4" style="color:#666;text-align:center;padding:1.5rem">No data</td></tr>';
}

// ─── Due for Service ──────────────────────────────────────────────────────────
function renderDueService(rows) {
  if(!rows || !rows.length) {
    document.getElementById('dueCard').innerHTML = '<div style="padding:1.5rem;color:#666;text-align:center">No vehicles due in the next 90 days</div>';
    return;
  }
  document.getElementById('dueCard').innerHTML = rows.map(r => {
    const days = parseInt(r.days_left||0);
    const cls = days <= 7 ? 'due-urgent' : days <= 30 ? 'due-soon' : 'due-ok';
    return `
      <div class="due-row">
        <div>
          <div style="font-weight:600">${r.customer||'—'}</div>
          <div style="color:var(--muted);font-size:.72rem">${r.vehicle||'—'} · ${r.plate_no||'—'}</div>
          <div style="color:var(--muted);font-size:.68rem;margin-top:.2rem">Last visit: ${fmtDate(r.last_visit)}</div>
        </div>
        <div style="text-align:right">
          <div style="font-size:.72rem;color:var(--muted)">Due</div>
          <div style="font-size:.82rem;font-weight:600">${fmtDate(r.next_due)}</div>
        </div>
        <div><span class="due-days ${cls}">${days > 0 ? days + 'd' : 'OVERDUE'}</span></div>
      </div>
    `;
  }).join('');
}

// ─── Audit Trail ──────────────────────────────────────────────────────────────
function renderAuditTrail(rows) {
  if(!rows || !rows.length) {
    document.getElementById('auditCard').innerHTML = '<div style="padding:1.5rem;color:#666;text-align:center">No recent transactions</div>';
    return;
  }
  const typeMap = {
    'Sales Invoice': {cls:'audit-si', label:'Invoice'},
    'Job Order': {cls:'audit-jo', label:'Job Order'},
    'Payment': {cls:'audit-pay', label:'Payment'},
  };
  document.getElementById('auditCard').innerHTML = rows.map(r => {
    const t = typeMap[r.doc_type] || {cls:'audit-si', label: r.doc_type};
    return `
      <div class="audit-row">
        <span class="audit-type ${t.cls}">${t.label}</span>
        <div>
          <div class="audit-ref">${r.ref||'—'}</div>
          <div class="audit-party">${r.party||'—'} · by ${r.modified_by||r.created_by||'—'}</div>
        </div>
        <div class="audit-amt">${fmt(r.amount)}</div>
        <div class="audit-date">${fmtDate(r.date)}</div>
      </div>
    `;
  }).join('');
}

// ─── Period Tabs ──────────────────────────────────────────────────────────────
document.querySelectorAll('.period-tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.period-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentPeriod = btn.dataset.p;
    loadDashboard();
  });
});

// ─── Auto-refresh every 5 minutes ─────────────────────────────────────────────
setInterval(loadDashboard, 5 * 60 * 1000);

// ─── Init ──────────────────────────────────────────────────────────────────────
loadDashboard();
</script>
</body>
</html>
"""

# ─── Install Web Pages ────────────────────────────────────────────────────────
# NOTE: The raw HTML must live in `main_section_html` with `content_type = "HTML"`.
# Frappe's Web Page renderer (get_html_content_based_on_type) only reads
# `main_section_html` when content_type == "HTML" (Page Builder reads page_blocks).
# Using the ORM (get_doc/save) rebuilds route + website generator caches too.
pages = [
    {
        "name": "vm-dashboard",
        "title": "VM Company Hub",
        "route": "vm-dashboard",
        "content": HUB_HTML,
        "published": 1,
    },
    {
        "name": "vm-company-dashboard",
        "title": "VM Company Dashboard",
        "route": "vm-company-dashboard",
        "content": DASHBOARD_HTML,
        "published": 1,
    },
]

created = 0
updated = 0

for page in pages:
    if frappe.db.exists("Web Page", page["name"]):
        doc = frappe.get_doc("Web Page", page["name"])
    else:
        doc = frappe.new_doc("Web Page")
        doc.name = page["name"]
        created += 1
    doc.title = page["title"]
    doc.route = page["route"]
    doc.content_type = "HTML"
    doc.main_section_html = page["content"]
    doc.main_section = ""        # clear the Page-Builder field so it isn't double-rendered
    doc.published = page["published"]
    doc.save(ignore_permissions=True)
    updated += 1 if not doc.is_new() else 0
    print(f"{'CREATED' if doc.is_new() else 'UPDATED'}: {page['name']}")

frappe.db.commit()
frappe.clear_cache()
print(f"\nDone! Created: {created}, Updated: {updated}")
print("\nPages available at:")
print("  http://erp.localhost/vm-dashboard")
print("  http://erp.localhost/vm-company-dashboard?company=Ultra+MRF+Dau+Main")
