
window.VMS = {
  theme: 'dark',

  init: function() {
    this.initTheme();
    this.initUserInfo();
    this.initBranch();
  },

  initTheme: function() {
    const saved = localStorage.getItem('vms_theme') || 'dark';
    this.setTheme(saved);
  },

  setTheme: function(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('vms_theme', theme);
    const btn = document.getElementById('vms-theme-toggle-btn');
    if (btn) {
      btn.innerHTML = theme === 'dark' ? '🌙' : '☀️';
    }
  },

  toggleTheme: function() {
    const next = this.theme === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  },

  initUserInfo: function() {
    const user = (window.frappe && frappe.session && frappe.session.user) ? frappe.session.user : 'Administrator';
    const userFullName = (window.frappe && frappe.session && frappe.session.user_fullname) ? frappe.session.user_fullname : (user.split('@')[0]);

    const uName = document.getElementById('vms-sidebar-username');
    const uRole = document.getElementById('vms-sidebar-userrole');
    const uAvatar = document.getElementById('vms-avatar-letter');
    const uGreeting = document.getElementById('vms-greeting');

    if (uName) uName.textContent = userFullName;
    if (uRole) uRole.textContent = user.includes('admin') ? 'System Manager' : 'Staff User';
    if (uAvatar) uAvatar.textContent = userFullName.charAt(0).toUpperCase();
    if (uGreeting) uGreeting.textContent = 'Welcome back, ' + userFullName;
  },

  initBranch: function() {
    const saved = localStorage.getItem('vms_selected_branch') || 'Ultra MRF Dau Main';
    const sel = document.getElementById('vms-company-select');
    if (sel) sel.value = saved;
  },

  onBranchChange: function(val) {
    localStorage.setItem('vms_selected_branch', val);
  },

  setOpsFilter: function(status, btn) {
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(function(t) { t.classList.remove('active'); });
    btn.classList.add('active');

    // Filter table rows
    const rows = document.querySelectorAll('#vms-ops-tbody tr');
    rows.forEach(function(row) {
      const s = row.getAttribute('data-status');
      if (status === 'all' || s === status) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  },

  filterAll: function(q) {
    const query = (q || '').toLowerCase().trim();
    
    // Filter module cards
    const cards = document.querySelectorAll('.module-card');
    cards.forEach(function(c) {
      const search = c.getAttribute('data-search') || '';
      const text = c.textContent.toLowerCase();
      if (!query || search.includes(query) || text.includes(query)) {
        c.style.display = 'flex';
      } else {
        c.style.display = 'none';
      }
    });

    // Filter operations table
    const rows = document.querySelectorAll('#vms-ops-tbody tr');
    rows.forEach(function(row) {
      const text = row.textContent.toLowerCase();
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
