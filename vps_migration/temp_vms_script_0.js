
window.VMS = {
  theme: 'dark',

  init: function() {
    this.initTheme();
    this.initUser();
    this.initBranch();
    this.fetchLiveStats();
  },

  initTheme: function() {
    const saved = localStorage.getItem('vms_theme') || 'dark';
    this.setTheme(saved);
  },

  setTheme: function(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('vms_theme', theme);
    const btn = document.getElementById('vms-theme-btn');
    if (btn) {
      btn.innerHTML = theme === 'dark' ? '🌙' : '☀️';
    }
  },

  toggleTheme: function() {
    const next = this.theme === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  },

  initUser: function() {
    // Check if logged in in frappe
    const user = (window.frappe && frappe.session && frappe.session.user) ? frappe.session.user : 'Administrator';
    const userFullName = (window.frappe && frappe.session && frappe.session.user_fullname) ? frappe.session.user_fullname : (user.split('@')[0]);
    
    const nameEl = document.getElementById('vms-user-fullname');
    const initEl = document.getElementById('vms-user-initial');
    const titleEl = document.getElementById('vms-welcome-title');
    
    if (nameEl) nameEl.textContent = userFullName;
    if (initEl) initEl.textContent = userFullName.charAt(0).toUpperCase();
    if (titleEl) titleEl.textContent = 'Welcome, ' + userFullName;
  },

  initBranch: function() {
    const savedBranch = localStorage.getItem('vms_selected_branch') || 'Ultra MRF Dau Main';
    const sel = document.getElementById('vms-branch-dropdown');
    if (sel) {
      sel.value = savedBranch;
    }
  },

  onBranchChange: function(val) {
    localStorage.setItem('vms_selected_branch', val);
    // Refresh stats filtered by company if available
    this.fetchLiveStats();
  },

  fetchLiveStats: function() {
    // Optionally fetch dynamic numbers from backend
    fetch('/api/method/vm_pos_meta', { credentials: 'include' })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        // Meta connected
      })
      .catch(function(e) {
        // fallback to defaults
      });
  },

  filterCards: function(query) {
    const q = (query || '').toLowerCase().trim();
    const cards = document.querySelectorAll('.vms-card');
    cards.forEach(function(card) {
      const kw = card.getAttribute('data-keywords') || '';
      const text = card.textContent.toLowerCase();
      if (!q || kw.includes(q) || text.includes(q)) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  },

  searchPlate: function(e) {
    e.preventDefault();
    const input = document.getElementById('vms-plate-query');
    const plate = (input ? input.value : '').trim();
    if (!plate) {
      window.location.href = '/desk#List/Customer%20Vehicle';
      return;
    }
    window.location.href = '/desk#List/Customer%20Vehicle?name=' + encodeURIComponent(plate);
  }
};

// Bootstrap on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() { VMS.init(); });
} else {
  VMS.init();
}
