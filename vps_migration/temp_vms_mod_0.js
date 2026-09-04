
window.VMS = {
  theme: 'dark',

  init: function() {
    this.initTheme();
    this.initUserInfo();
    this.initBranch();
  },

  initTheme: function() {
    var saved = localStorage.getItem('vms_theme') || 'dark';
    this.setTheme(saved);
  },

  setTheme: function(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('vms_theme', theme);
    var btn = document.getElementById('vms-theme-toggle-btn');
    if (btn) {
      btn.innerHTML = theme === 'dark' ? '🌙' : '☀️';
    }
  },

  toggleTheme: function() {
    var next = this.theme === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  },

  initUserInfo: function() {
    var user = (window.frappe && frappe.session && frappe.session.user) ? frappe.session.user : 'Administrator';
    var userFullName = (window.frappe && frappe.session && frappe.session.user_fullname) ? frappe.session.user_fullname : (user.split('@')[0]);

    var uName = document.getElementById('vms-sidebar-username');
    var uRole = document.getElementById('vms-sidebar-userrole');
    var uAvatar = document.getElementById('vms-avatar-letter');
    var uGreeting = document.getElementById('vms-greeting');

    if (uName) uName.textContent = userFullName;
    if (uRole) uRole.textContent = user.includes('admin') ? 'System Manager' : 'Staff User';
    if (uAvatar) uAvatar.textContent = userFullName.charAt(0).toUpperCase();
    if (uGreeting) uGreeting.textContent = 'Welcome back, ' + userFullName;
  },

  initBranch: function() {
    var saved = localStorage.getItem('vms_selected_branch') || 'Ultra MRF Dau Main';
    var sel = document.getElementById('vms-company-select');
    if (sel) sel.value = saved;
  },

  onBranchChange: function(val) {
    localStorage.setItem('vms_selected_branch', val);
  },

  setOpsFilter: function(status, btn) {
    document.querySelectorAll('.filter-tab').forEach(function(t) { t.classList.remove('active'); });
    btn.classList.add('active');

    var rows = document.querySelectorAll('#vms-ops-tbody tr');
    rows.forEach(function(row) {
      var s = row.getAttribute('data-status');
      if (status === 'all' || s === status) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  },

  filterAll: function(q) {
    var query = (q || '').toLowerCase().trim();
    
    var cards = document.querySelectorAll('.module-card');
    cards.forEach(function(c) {
      var search = c.getAttribute('data-search') || '';
      var text = c.textContent.toLowerCase();
      if (!query || search.includes(query) || text.includes(query)) {
        c.style.display = 'flex';
      } else {
        c.style.display = 'none';
      }
    });

    var rows = document.querySelectorAll('#vms-ops-tbody tr');
    rows.forEach(function(row) {
      var text = row.textContent.toLowerCase();
      if (!query || text.includes(query)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() { VMS.init(); });
} else {
  VMS.init();
}
