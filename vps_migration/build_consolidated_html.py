import os

html_code = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Consolidated Multi-Company Financials &amp; Accounting Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
  <style>
    /* ── Website Chrome Suppression ── */
    header.navbar, footer, .navbar, .web-footer, .page-header, .page-breadcrumbs, .standard-breadcrumbs, .sidebar-column, .web-page-sidebar, .page-container > .col-sm-3 {
      display: none !important;
    }
    .page-container, .container, .page-content, .main-section, .body-content, main {
      padding: 0 !important;
      margin: 0 !important;
      max-width: 100% !important;
      width: 100% !important;
      background: transparent !important;
      border: none !important;
    }
    *, *::before, *::after {
      box-sizing: border-box;
    }

    /* ── Monochrome Modern Dark / Light Theme System ── */
    :root {
      --bg-canvas: #040404;
      --bg-surface: #0c0c0c;
      --bg-surface-elevated: #141414;
      --bg-surface-hover: #1c1c1c;
      --bg-cell-zebra: #080808;
      --bg-sticky: #111111;
      --border-hairline: #1e1e1e;
      --border-subtle: #2a2a2a;
      --border-strong: #3f3f46;
      --border-highlight: #ffffff;
      --text-primary: #ffffff;
      --text-secondary: #a1a1aa;
      --text-muted: #52525b;
      --text-dimmed: #3f3f46;
      --accent-solid: #ffffff;
      --accent-contrast: #000000;
      --accent-blue: #38bdf8;
      --badge-neutral-bg: #18181b;
      --badge-neutral-border: #27272a;
      --positive-color: #22c55e;
      --negative-color: #ef4444;
      --warning-color: #f59e0b;
      --info-color: #06b6d4;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --shadow-elevation-1: 0 4px 20px rgba(0, 0, 0, 0.8);
      --shadow-elevation-2: 0 10px 40px rgba(0, 0, 0, 0.9);
      --scrollbar-thumb: #27272a;
    }

    [data-theme="light"] {
      --bg-canvas: #f8fafc;
      --bg-surface: #ffffff;
      --bg-surface-elevated: #f1f5f9;
      --bg-surface-hover: #e2e8f0;
      --bg-cell-zebra: #f8fafc;
      --bg-sticky: #ffffff;
      --border-hairline: #e2e8f0;
      --border-subtle: #cbd5e1;
      --border-strong: #94a3b8;
      --border-highlight: #0f172a;
      --text-primary: #09090b;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --text-dimmed: #94a3b8;
      --accent-solid: #09090b;
      --accent-contrast: #ffffff;
      --accent-blue: #0284c7;
      --badge-neutral-bg: #f1f5f9;
      --badge-neutral-border: #e2e8f0;
      --positive-color: #16a34a;
      --negative-color: #dc2626;
      --warning-color: #d97706;
      --info-color: #0891b2;
      --shadow-elevation-1: 0 4px 20px rgba(0, 0, 0, 0.05);
      --shadow-elevation-2: 0 10px 40px rgba(0, 0, 0, 0.1);
      --scrollbar-thumb: #cbd5e1;
    }

    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      min-height: 100vh;
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      font-family: var(--font-sans);
      font-size: 13px;
      line-height: 1.45;
      overflow-x: hidden;
    }

    /* ── Scrollbars ── */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: var(--bg-canvas);
    }
    ::-webkit-scrollbar-thumb {
      background: var(--scrollbar-thumb);
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--border-strong);
    }

    .app-shell {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      width: 100%;
    }

    /* ── Sticky Top Header Bar ── */
    .top-header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(12, 12, 12, 0.95);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-hairline);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }

    .brand-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo {
      width: 36px;
      height: 36px;
      background: var(--accent-solid);
      color: var(--accent-contrast);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 15px;
      letter-spacing: -0.5px;
    }
    .brand-title-wrap {
      display: flex;
      flex-direction: column;
    }
    .brand-title {
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.3px;
      color: var(--text-primary);
      margin: 0;
    }
    .brand-subtitle {
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 0.2px;
      text-transform: uppercase;
      font-weight: 600;
    }

    /* ── Header Controls ── */
    .header-controls {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .date-pill-group {
      display: flex;
      align-items: center;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 2px;
      gap: 2px;
    }
    .date-preset-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-family: var(--font-sans);
      font-size: 11px;
      font-weight: 600;
      padding: 5px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .date-preset-btn:hover {
      color: var(--text-primary);
      background: var(--bg-surface-hover);
    }
    .date-preset-btn.active {
      background: var(--accent-solid);
      color: var(--accent-contrast);
    }
    .date-inputs {
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 4px 8px;
    }
    .date-input {
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 11px;
      outline: none;
      cursor: pointer;
    }
    .date-input::-webkit-calendar-picker-indicator {
      filter: invert(1);
      cursor: pointer;
    }

    .btn-action {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      font-family: var(--font-sans);
      cursor: pointer;
      transition: all 0.15s ease;
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      position: relative;
    }
    .btn-action:hover {
      background: var(--bg-surface-hover);
      border-color: var(--border-strong);
    }
    .btn-action.btn-primary {
      background: var(--accent-solid);
      color: var(--accent-contrast);
      border-color: var(--accent-solid);
    }
    .btn-action.active {
      background: var(--accent-solid);
      color: var(--accent-contrast);
    }

    /* ── Company Filter Dropdown Popover ── */
    .company-dropdown-popover {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: 6px;
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      border-radius: 10px;
      box-shadow: var(--shadow-elevation-2);
      width: 320px;
      max-height: 420px;
      z-index: 200;
      display: none;
      flex-direction: column;
      overflow: hidden;
      animation: popoverFade 0.15s ease-out;
    }
    .company-dropdown-popover.open {
      display: flex;
    }
    @keyframes popoverFade {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .popover-header {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-hairline);
      background: var(--bg-surface-elevated);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 700;
      font-size: 12px;
    }
    .popover-list {
      padding: 8px 12px;
      overflow-y: auto;
      max-height: 280px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .company-check-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      cursor: pointer;
      padding: 4px 6px;
      border-radius: 6px;
      transition: background 0.1s ease;
    }
    .company-check-item:hover {
      background: var(--bg-surface-hover);
    }
    .company-check-item input[type="checkbox"] {
      cursor: pointer;
      accent-color: var(--accent-solid);
      width: 14px;
      height: 14px;
    }
    .popover-footer {
      padding: 8px 14px;
      border-top: 1px solid var(--border-hairline);
      background: var(--bg-surface-elevated);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* ── Sticky Tab Navigation Bar ── */
    .nav-tabs-bar {
      position: sticky;
      top: 61px;
      z-index: 95;
      background: rgba(12, 12, 12, 0.95);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-hairline);
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      overflow-x: auto;
    }
    .tabs-list {
      display: flex;
      align-items: center;
      gap: 4px;
      margin: 0;
      padding: 0;
      list-style: none;
      overflow-x: auto;
    }
    .tab-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary);
      border-bottom: 2px solid transparent;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      user-select: none;
    }
    .tab-item:hover {
      color: var(--text-primary);
      background: var(--bg-surface-hover);
    }
    .tab-item.active {
      color: var(--text-primary);
      border-bottom-color: var(--accent-solid);
      background: rgba(255, 255, 255, 0.05);
    }
    .tab-badge {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 10px;
      background: var(--badge-neutral-bg);
      border: 1px solid var(--badge-neutral-border);
      color: var(--text-secondary);
    }

    /* ── Dynamic KPI Ribbon ── */
    .kpi-ribbon {
      padding: 16px 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      background: var(--bg-canvas);
    }
    .kpi-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      border-radius: 10px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .kpi-card:hover {
      border-color: var(--border-strong);
      transform: translateY(-2px);
      box-shadow: var(--shadow-elevation-1);
    }
    .kpi-label {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .kpi-value {
      font-family: var(--font-mono);
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.5px;
    }
    .kpi-subtext {
      font-size: 11px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 4px;
    }

    /* ── Content Viewport ── */
    .content-viewport {
      padding: 0 24px 40px 24px;
      flex: 1;
    }
    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
      animation: fadeIn 0.2s ease-in-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* ── Tables & Multi-Column Matrix ── */
    .matrix-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-elevation-1);
    }
    .matrix-toolbar {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-hairline);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      background: var(--bg-surface-elevated);
    }
    .matrix-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .search-box-wrap {
      display: flex;
      align-items: center;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 4px 10px;
      gap: 8px;
      min-width: 240px;
    }
    .search-input {
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-size: 12px;
      font-family: var(--font-sans);
      outline: none;
      width: 100%;
    }
    .search-input::placeholder {
      color: var(--text-muted);
    }

    .table-container {
      width: 100%;
      overflow-x: auto;
      max-height: calc(100vh - 280px);
    }
    .table-matrix {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: left;
    }
    .table-matrix th, .table-matrix td {
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-hairline);
      white-space: nowrap;
    }
    .table-matrix thead th {
      position: sticky;
      top: 0;
      z-index: 10;
      background: var(--bg-surface-elevated);
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      color: var(--text-secondary);
      border-bottom: 2px solid var(--border-subtle);
    }
    
    /* Sticky First Column */
    .table-matrix th.sticky-col,
    .table-matrix td.sticky-col {
      position: sticky;
      left: 0;
      z-index: 5;
      background: var(--bg-surface);
      font-weight: 600;
      color: var(--text-primary);
      border-right: 1px solid var(--border-subtle);
      min-width: 260px;
      max-width: 320px;
    }
    .table-matrix thead th.sticky-col {
      z-index: 15;
      background: var(--bg-surface-elevated);
    }

    /* Sticky Total Column */
    .table-matrix th.sticky-total,
    .table-matrix td.sticky-total {
      position: sticky;
      right: 0;
      z-index: 5;
      background: var(--bg-surface-elevated);
      font-weight: 700;
      border-left: 2px solid var(--border-subtle);
      text-align: right;
    }
    .table-matrix thead th.sticky-total {
      z-index: 15;
    }

    /* Row Hover & Alternating */
    .table-matrix tbody tr:hover td {
      background-color: var(--bg-surface-hover) !important;
    }
    .table-matrix tbody tr:nth-child(even) td {
      background-color: var(--bg-cell-zebra);
    }

    /* Section Category Headers */
    .row-section-header td {
      background: var(--bg-surface-elevated) !important;
      font-weight: 800;
      font-size: 12px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: var(--text-primary);
      padding-top: 14px;
      padding-bottom: 8px;
      border-top: 2px solid var(--border-subtle);
      border-bottom: 1px solid var(--border-subtle);
    }
    .row-section-total td {
      background: rgba(255, 255, 255, 0.03) !important;
      font-weight: 700;
      border-top: 1px solid var(--border-strong);
      border-bottom: 1px solid var(--border-strong);
      color: var(--text-primary);
    }
    .row-grand-total td {
      background: rgba(255, 255, 255, 0.08) !important;
      font-weight: 800;
      font-size: 13px;
      border-top: 2px solid var(--border-highlight);
      border-bottom: 2px solid var(--border-highlight);
      color: var(--text-primary);
    }

    /* Number & Accounting Formatting */
    .num-cell {
      font-family: var(--font-mono);
      text-align: right;
      font-variant-numeric: tabular-nums;
      cursor: pointer;
    }
    .num-cell:hover {
      text-decoration: underline;
      color: var(--accent-solid);
    }
    .num-negative {
      color: var(--negative-color);
    }
    .num-zero {
      color: var(--text-dimmed);
    }

    /* ── Drill-down Modal ── */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      z-index: 1000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .modal-overlay.open {
      display: flex;
    }
    .modal-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-strong);
      border-radius: 12px;
      width: 100%;
      max-width: 960px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-elevation-2);
      animation: modalPop 0.2s ease-out;
    }
    @keyframes modalPop {
      from { opacity: 0; transform: scale(0.96); }
      to { opacity: 1; transform: scale(1); }
    }
    .modal-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-hairline);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .modal-title {
      font-size: 15px;
      font-weight: 700;
      margin: 0;
    }
    .modal-body {
      padding: 16px 20px;
      overflow-y: auto;
      flex: 1;
    }
    .modal-footer {
      padding: 12px 20px;
      border-top: 1px solid var(--border-hairline);
      display: flex;
      justify-content: flex-end;
      background: var(--bg-surface-elevated);
    }

    /* ── Loading Spinner ── */
    .loading-overlay {
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(3px);
      align-items: center;
      justify-content: center;
      z-index: 50;
      border-radius: 12px;
    }
    .loading-overlay.active {
      display: flex;
    }
    .spinner {
      width: 36px;
      height: 36px;
      border: 3px solid var(--border-subtle);
      border-top-color: var(--accent-solid);
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* ── Badges ── */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      font-family: var(--font-sans);
    }
    .badge-success {
      background: rgba(34, 197, 94, 0.12);
      color: #22c55e;
      border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .badge-warning {
      background: rgba(245, 158, 11, 0.12);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-danger {
      background: rgba(239, 68, 68, 0.12);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-info {
      background: rgba(6, 182, 212, 0.12);
      color: #06b6d4;
      border: 1px solid rgba(6, 182, 212, 0.3);
    }
    .badge-neutral {
      background: var(--badge-neutral-bg);
      color: var(--text-secondary);
      border: 1px solid var(--badge-neutral-border);
    }

    /* ── Print Styles ── */
    @media print {
      body {
        background: #fff !important;
        color: #000 !important;
      }
      .top-header, .nav-tabs-bar, .matrix-toolbar, .header-controls, .btn-action, .kpi-ribbon {
        display: none !important;
      }
      .tab-content {
        display: none !important;
      }
      .tab-content.active {
        display: block !important;
      }
      .table-matrix th, .table-matrix td {
        border-color: #cbd5e1 !important;
        color: #000 !important;
        background: transparent !important;
      }
      .matrix-card {
        border: none !important;
        box-shadow: none !important;
      }
      .table-matrix th.sticky-col, .table-matrix td.sticky-col,
      .table-matrix th.sticky-total, .table-matrix td.sticky-total {
        position: static !important;
      }
      .print-header {
        display: block !important;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #000;
      }
    }
    .print-header {
      display: none;
    }
  </style>
</head>
<body>
  <div class="app-shell">
    
    <!-- ── Print Only Header ── -->
    <div class="print-header">
      <h2 style="margin: 0; font-size: 20px;">ULTRA MRF Automotive &bull; Financial Statement</h2>
      <div style="font-size: 12px; color: #475569; margin-top: 4px;" id="print-meta-text">Consolidated Enterprise Group</div>
    </div>

    <!-- ── Top Header Bar ── -->
    <header class="top-header">
      <div class="brand-section">
        <div class="brand-logo">UM</div>
        <div class="brand-title-wrap">
          <h1 class="brand-title">Consolidated Multi-Company Financials &amp; Accounting Suite</h1>
          <span class="brand-subtitle">Enterprise Group Reporting &bull; Dynamic Column Filtering</span>
        </div>
      </div>

      <div class="header-controls">
        <!-- Company Filter Popover Trigger -->
        <div style="position: relative;">
          <button class="btn-action" id="btn-company-filter" onclick="toggleCompanyPopover()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            <span id="company-filter-label">🏢 Companies (13)</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>

          <!-- Company Filter Popover Dropdown -->
          <div class="company-dropdown-popover" id="company-popover">
            <div class="popover-header">
              <span>Filter Company Columns</span>
              <div style="display: flex; gap: 6px;">
                <button class="date-preset-btn" style="padding: 2px 6px; font-size: 10px;" onclick="selectAllCompanies(true)">Select All</button>
                <button class="date-preset-btn" style="padding: 2px 6px; font-size: 10px;" onclick="selectAllCompanies(false)">Clear</button>
              </div>
            </div>
            <div class="popover-list" id="company-checkboxes-container">
              <!-- Dynamically populated company checkboxes -->
            </div>
            <div class="popover-footer">
              <span style="font-size: 11px; color: var(--text-muted);" id="popover-selected-count">13 selected</span>
              <button class="btn-action btn-primary" style="padding: 4px 10px; font-size: 11px;" onclick="applyCompanyFilter()">Apply Filter</button>
            </div>
          </div>
        </div>

        <!-- Date Presets -->
        <div class="date-pill-group">
          <button class="date-preset-btn" onclick="setPreset('today')">Today</button>
          <button class="date-preset-btn" onclick="setPreset('mtd')">MTD</button>
          <button class="date-preset-btn" onclick="setPreset('qtd')">QTD</button>
          <button class="date-preset-btn active" onclick="setPreset('ytd')">YTD 2026</button>
          <button class="date-preset-btn" onclick="setPreset('all')">All Time</button>
        </div>

        <!-- Custom Date Range -->
        <div class="date-inputs">
          <input type="date" id="input-from-date" class="date-input" value="2026-01-01" onchange="reloadActiveTab()">
          <span style="color: var(--text-muted);">&rarr;</span>
          <input type="date" id="input-to-date" class="date-input" value="2026-12-31" onchange="reloadActiveTab()">
        </div>

        <!-- Action Buttons -->
        <button class="btn-action" onclick="reloadActiveTab()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh
        </button>

        <button class="btn-action btn-primary" onclick="exportCurrentTableExcel()" title="Download the active tab as an Excel worksheet (.xlsx)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Export Excel
        </button>

        <button class="btn-action" onclick="printReport()" title="Print or Save as PDF">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          Print
        </button>

        <button class="btn-action" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
          <svg id="theme-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        </button>
      </div>
    </header>

    <!-- ── Tab Navigation Bar ── -->
    <nav class="nav-tabs-bar">
      <ul class="tabs-list">
        <li class="tab-item active" id="tab-nav-pnl" onclick="switchTab('pnl')">
          <span>📊 Consolidated Profit &amp; Loss</span>
          <span class="tab-badge" id="badge-pnl-status">Live</span>
        </li>
        <li class="tab-item" id="tab-nav-balance_sheet" onclick="switchTab('balance_sheet')">
          <span>🏛️ Consolidated Balance Sheet</span>
          <span class="tab-badge" id="badge-bs-status">Balanced</span>
        </li>
        <li class="tab-item" id="tab-nav-cash_flow" onclick="switchTab('cash_flow')">
          <span>💵 Cash Flow (Daily / Monthly / Yearly)</span>
          <span class="tab-badge" id="badge-cf-status">Live</span>
        </li>
        <li class="tab-item" id="tab-nav-ar_aging" onclick="switchTab('ar_aging')">
          <span>📥 AR Aging (30, 60, 90 Days)</span>
          <span class="tab-badge" id="badge-ar-count">0 Invoices</span>
        </li>
        <li class="tab-item" id="tab-nav-ap_aging" onclick="switchTab('ap_aging')">
          <span>📤 AP Aging (30, 60, 90 Days)</span>
          <span class="tab-badge" id="badge-ap-count">0 Bills</span>
        </li>
        <li class="tab-item" id="tab-nav-general_ledger" onclick="switchTab('general_ledger')">
          <span>📜 General Ledger Explorer</span>
          <span class="tab-badge" id="badge-gl-count">0 Entries</span>
        </li>
        <li class="tab-item" id="tab-nav-inventory_audit" onclick="switchTab('inventory_audit')">
          <span>📦 Inventory Audit &amp; On Hand</span>
          <span class="tab-badge" id="badge-inv-count">0 Items</span>
        </li>
      </ul>
      <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); white-space: nowrap;">
        Currency: <strong style="color: var(--text-primary);">PHP (₱)</strong>
      </div>
    </nav>

    <!-- ── Dynamic KPI Ribbon ── -->
    <section class="kpi-ribbon" id="kpi-ribbon-container">
      <!-- Dynamically updated per active tab -->
    </section>

    <!-- ── Main Viewport Content ── -->
    <main class="content-viewport">
      
      <!-- ── TAB 1: Consolidated P&L ── -->
      <section id="tab-pnl" class="tab-content active">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-pnl"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📊 Consolidated Profit &amp; Loss Matrix</span>
              <span class="badge badge-neutral" id="pnl-date-badge">2026-01-01 to 2026-12-31</span>
            </div>
            <div class="search-box-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="search-pnl" class="search-input" placeholder="Filter P&amp;L accounts..." oninput="filterTableRows('table-pnl', this.value)">
            </div>
          </div>

          <div class="table-container">
            <table class="table-matrix" id="table-pnl">
              <thead id="thead-pnl"></thead>
              <tbody id="tbody-pnl"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ── TAB 2: Consolidated Balance Sheet ── -->
      <section id="tab-balance_sheet" class="tab-content">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-bs"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>🏛️ Consolidated Balance Sheet Matrix</span>
              <span class="badge badge-neutral" id="bs-date-badge">As of 2026-12-31</span>
            </div>
            <div class="search-box-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="search-bs" class="search-input" placeholder="Filter balance sheet accounts..." oninput="filterTableRows('table-bs', this.value)">
            </div>
          </div>

          <div class="table-container">
            <table class="table-matrix" id="table-bs">
              <thead id="thead-bs"></thead>
              <tbody id="tbody-bs"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ── TAB 3: Consolidated Cash Flow Statement (Daily / Monthly / Yearly) ── -->
      <section id="tab-cash_flow" class="tab-content">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-cf"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
              <div class="matrix-title">
                <span>💵 Consolidated Cash Flow Statement</span>
                <span class="badge badge-neutral" id="cf-date-badge">2026-01-01 to 2026-12-31</span>
              </div>
              
              <!-- Period Granularity Toggle (Daily, Monthly, Yearly) -->
              <div class="date-pill-group">
                <button class="date-preset-btn" id="cf-period-daily" onclick="setCashFlowPeriod('daily')">📅 Daily</button>
                <button class="date-preset-btn active" id="cf-period-monthly" onclick="setCashFlowPeriod('monthly')">📆 Monthly</button>
                <button class="date-preset-btn" id="cf-period-yearly" onclick="setCashFlowPeriod('yearly')">🏛️ Yearly</button>
              </div>

              <!-- Sub-View Switcher -->
              <div class="date-pill-group">
                <button class="date-preset-btn active" id="cf-view-matrix" onclick="setCashFlowView('matrix')">🏢 Multi-Company Matrix</button>
                <button class="date-preset-btn" id="cf-view-periods" onclick="setCashFlowView('periods')">📆 Periodic Trend</button>
              </div>
            </div>

            <div class="search-box-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="search-cf" class="search-input" placeholder="Filter cash flow items..." oninput="filterCashFlowRows(this.value)">
            </div>
          </div>

          <!-- View 1: Multi-Company Matrix Table -->
          <div class="table-container" id="cf-matrix-container">
            <table class="table-matrix" id="table-cf-matrix">
              <thead id="thead-cf-matrix"></thead>
              <tbody id="tbody-cf-matrix"></tbody>
            </table>
          </div>

          <!-- View 2: Periodic Trend Table -->
          <div class="table-container" id="cf-periods-container" style="display: none;">
            <table class="table-matrix" id="table-cf-periods">
              <thead id="thead-cf-periods">
                <tr>
                  <th>Period</th>
                  <th style="text-align: right;">Opening Balance (₱)</th>
                  <th style="text-align: right;">Total Inflows (₱)</th>
                  <th style="text-align: right;">Total Outflows (₱)</th>
                  <th style="text-align: right;">Net Cash Flow (₱)</th>
                  <th style="text-align: right;">Ending Balance (₱)</th>
                  <th style="text-align: center;">Transactions</th>
                </tr>
              </thead>
              <tbody id="tbody-cf-periods"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ── TAB 4: AR Aging Analysis (30, 60, 90 Days) ── -->
      <section id="tab-ar_aging" class="tab-content">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-ar"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
              <div class="matrix-title">
                <span>📥 Accounts Receivable (AR) Aging Analysis</span>
                <span class="badge badge-neutral" id="ar-asof-badge">As of Today</span>
              </div>

              <!-- View Switcher -->
              <div class="date-pill-group">
                <button class="date-preset-btn active" id="ar-view-summary" onclick="setARView('summary')">👥 Customer Summary</button>
                <button class="date-preset-btn" id="ar-view-companies" onclick="setARView('companies')">🏢 Company Matrix</button>
                <button class="date-preset-btn" id="ar-view-details" onclick="setARView('details')">📄 Invoices Detail</button>
              </div>
            </div>

            <div class="search-box-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="search-ar" class="search-input" placeholder="Search customer, invoice #, terms..." oninput="filterARRows(this.value)">
            </div>
          </div>

          <!-- AR Customer Summary Table -->
          <div class="table-container" id="ar-summary-container">
            <table class="table-matrix" id="table-ar-summary">
              <thead>
                <tr>
                  <th class="sticky-col">Customer Name</th>
                  <th>Primary Branch</th>
                  <th style="text-align: right;">Current / Not Due</th>
                  <th style="text-align: right;">1 - 30 Days</th>
                  <th style="text-align: right;">31 - 60 Days</th>
                  <th style="text-align: right;">61 - 90 Days</th>
                  <th style="text-align: right;">90+ Days</th>
                  <th class="sticky-total">Total Outstanding</th>
                  <th style="text-align: center;">Invoices</th>
                </tr>
              </thead>
              <tbody id="tbody-ar-summary"></tbody>
            </table>
          </div>

          <!-- AR Company Matrix Table -->
          <div class="table-container" id="ar-companies-container" style="display: none;">
            <table class="table-matrix" id="table-ar-companies">
              <thead>
                <tr>
                  <th class="sticky-col">Operating Company</th>
                  <th>Abbr</th>
                  <th style="text-align: right;">Current / Not Due</th>
                  <th style="text-align: right;">1 - 30 Days</th>
                  <th style="text-align: right;">31 - 60 Days</th>
                  <th style="text-align: right;">61 - 90 Days</th>
                  <th style="text-align: right;">90+ Days</th>
                  <th class="sticky-total">Total Receivables</th>
                  <th style="text-align: center;">Invoices</th>
                </tr>
              </thead>
              <tbody id="tbody-ar-companies"></tbody>
            </table>
          </div>

          <!-- AR Detailed Invoices Table -->
          <div class="table-container" id="ar-details-container" style="display: none;">
            <table class="table-matrix" id="table-ar-details">
              <thead>
                <tr>
                  <th>Invoice No</th>
                  <th>Customer</th>
                  <th>Company</th>
                  <th>Posting Date</th>
                  <th>Due Date (Terms)</th>
                  <th style="text-align: center;">Days Overdue</th>
                  <th style="text-align: center;">Aging Bucket</th>
                  <th style="text-align: right;">Invoice Total</th>
                  <th style="text-align: right;">Outstanding</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="tbody-ar-details"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ── TAB 5: AP Aging Analysis (30, 60, 90 Days) ── -->
      <section id="tab-ap_aging" class="tab-content">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-ap"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
              <div class="matrix-title">
                <span>📤 Accounts Payable (AP) Aging Analysis</span>
                <span class="badge badge-neutral" id="ap-asof-badge">As of Today</span>
              </div>

              <!-- View Switcher -->
              <div class="date-pill-group">
                <button class="date-preset-btn active" id="ap-view-summary" onclick="setAPView('summary')">🏢 Supplier Summary</button>
                <button class="date-preset-btn" id="ap-view-companies" onclick="setAPView('companies')">🏢 Company Matrix</button>
                <button class="date-preset-btn" id="ap-view-details" onclick="setAPView('details')">📄 Bills Detail</button>
              </div>
            </div>

            <div class="search-box-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="search-ap" class="search-input" placeholder="Search supplier, bill #, terms..." oninput="filterAPRows(this.value)">
            </div>
          </div>

          <!-- AP Supplier Summary Table -->
          <div class="table-container" id="ap-summary-container">
            <table class="table-matrix" id="table-ap-summary">
              <thead>
                <tr>
                  <th class="sticky-col">Supplier Name</th>
                  <th>Primary Branch</th>
                  <th style="text-align: right;">Current / Not Due</th>
                  <th style="text-align: right;">1 - 30 Days</th>
                  <th style="text-align: right;">31 - 60 Days</th>
                  <th style="text-align: right;">61 - 90 Days</th>
                  <th style="text-align: right;">90+ Days</th>
                  <th class="sticky-total">Total Outstanding</th>
                  <th style="text-align: center;">Bills</th>
                </tr>
              </thead>
              <tbody id="tbody-ap-summary"></tbody>
            </table>
          </div>

          <!-- AP Company Matrix Table -->
          <div class="table-container" id="ap-companies-container" style="display: none;">
            <table class="table-matrix" id="table-ap-companies">
              <thead>
                <tr>
                  <th class="sticky-col">Operating Company</th>
                  <th>Abbr</th>
                  <th style="text-align: right;">Current / Not Due</th>
                  <th style="text-align: right;">1 - 30 Days</th>
                  <th style="text-align: right;">31 - 60 Days</th>
                  <th style="text-align: right;">61 - 90 Days</th>
                  <th style="text-align: right;">90+ Days</th>
                  <th class="sticky-total">Total Payables</th>
                  <th style="text-align: center;">Bills</th>
                </tr>
              </thead>
              <tbody id="tbody-ap-companies"></tbody>
            </table>
          </div>

          <!-- AP Detailed Bills Table -->
          <div class="table-container" id="ap-details-container" style="display: none;">
            <table class="table-matrix" id="table-ap-details">
              <thead>
                <tr>
                  <th>Bill / Invoice No</th>
                  <th>Supplier</th>
                  <th>Company</th>
                  <th>Bill Date</th>
                  <th>Due Date (Terms)</th>
                  <th style="text-align: center;">Days Overdue</th>
                  <th style="text-align: center;">Aging Bucket</th>
                  <th style="text-align: right;">Bill Total</th>
                  <th style="text-align: right;">Outstanding</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="tbody-ap-details"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ── TAB 6: Multi-Company General Ledger ── -->
      <section id="tab-general_ledger" class="tab-content">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-gl"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📜 General Ledger Journal Explorer</span>
              <span class="badge badge-neutral" id="gl-records-badge">0 Entries</span>
            </div>
            
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <select id="gl-voucher-type-filter" class="btn-action" onchange="loadGLData()">
                <option value="">All Voucher Types</option>
                <option value="Sales Invoice">Sales Invoice</option>
                <option value="Purchase Invoice">Purchase Invoice</option>
                <option value="Payment Entry">Payment Entry</option>
                <option value="Journal Entry">Journal Entry</option>
                <option value="Stock Entry">Stock Entry</option>
                <option value="POS Invoice">POS Invoice</option>
              </select>

              <div class="search-box-wrap">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" id="search-gl" class="search-input" placeholder="Search voucher #, account, remarks..." onkeydown="if(event.key==='Enter') loadGLData()">
              </div>
            </div>
          </div>

          <div class="table-container">
            <table class="table-matrix" id="table-gl">
              <thead>
                <tr>
                  <th>Posting Date</th>
                  <th>Company</th>
                  <th>Account</th>
                  <th>Voucher Type</th>
                  <th>Voucher No</th>
                  <th>Against</th>
                  <th style="text-align: right;">Debit (₱)</th>
                  <th style="text-align: right;">Credit (₱)</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody id="tbody-gl"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ── TAB 7: Multi-Company Inventory Audit ── -->
      <section id="tab-inventory_audit" class="tab-content">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-inv"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📦 Multi-Company Inventory Audit &bull; Running Balance &amp; On Hand</span>
              <span class="badge badge-neutral" id="inv-sku-badge">0 SKUs</span>
            </div>
            
            <div class="search-box-wrap">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <input type="text" id="search-inv" class="search-input" placeholder="Search all items code, name, group..." oninput="inventoryRefreshFilter()">
            </div>
          </div>

          <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;padding:12px 20px">
            <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
              <input id="inv-stock-only" type="checkbox" onchange="inventoryRefreshFilter()" style="accent-color: var(--accent-solid);">
              <span>Only items with stock on hand</span>
            </label>
            <details><summary id="inv-selection-label" style="cursor:pointer; font-weight: 600;">All Items Selection</summary>
              <div style="padding:10px;display:grid;gap:8px">
                <div>
                  <button class="btn-action" onclick="inventorySelectAll(true)">Select All Items</button>
                  <button class="btn-action" onclick="inventorySelectAll(false)">Clear Selection</button>
                </div>
                <label for="inv-item-select">Choose items (Ctrl / Cmd to select multiple)</label>
                <select id="inv-item-select" multiple size="10" onchange="inventorySelectChanged()" style="max-width:80vw;width:440px;background:var(--bg-surface-elevated);color:var(--text-primary);border:1px solid var(--border-subtle);border-radius:6px;padding:6px;"></select>
              </div>
            </details>
          </div>
          <div class="table-container">
            <table class="table-matrix" id="table-inv">
              <thead id="thead-inv"></thead>
              <tbody id="tbody-inv"></tbody>
            </table>
          </div>
        </div>
      </section>

    </main>

    <!-- ── Drill-Down Modal ── -->
    <div class="modal-overlay" id="drilldown-modal">
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h3 class="modal-title" id="drilldown-title">GL Breakdown</h3>
            <span style="font-size: 11px; color: var(--text-muted);" id="drilldown-subtitle">Detailed transaction ledger</span>
          </div>
          <button class="btn-action" onclick="closeDrilldown()">✕</button>
        </div>
        <div class="modal-body">
          <table class="table-matrix" style="width: 100%;">
            <thead>
              <tr>
                <th>Date</th>
                <th>Voucher Type</th>
                <th>Voucher No</th>
                <th style="text-align: right;">Debit (₱)</th>
                <th style="text-align: right;">Credit (₱)</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody id="drilldown-tbody"></tbody>
          </table>
        </div>
        <div class="modal-footer">
          <button class="btn-action btn-primary" onclick="closeDrilldown()">Close</button>
        </div>
      </div>
    </div>

    <!-- ── Stock Ledger Modal ── -->
    <div class="modal-overlay" id="stock-modal">
      <div class="modal-card" style="max-width: 1050px;">
        <div class="modal-header">
          <div>
            <h3 class="modal-title" id="stock-modal-title">Running Stock Ledger Audit</h3>
            <span style="font-size: 11px; color: var(--text-muted);" id="stock-modal-subtitle">Chronological running transactions &amp; balance on hand</span>
          </div>
          <button class="btn-action" onclick="closeStockDrilldown()">✕</button>
        </div>
        <div class="modal-body">
          <div id="stock-modal-summary" style="display:flex;gap:20px;padding:8px 0 16px 0;font-size:12px;font-family:var(--font-mono);border-bottom:1px solid var(--border-hairline);margin-bottom:12px"></div>
          <table class="table-matrix" style="width: 100%;">
            <thead>
              <tr>
                <th>Date / Time</th>
                <th>Branch</th>
                <th>Warehouse</th>
                <th>Voucher Type</th>
                <th>Voucher No</th>
                <th style="text-align: right;">Actual Qty</th>
                <th style="text-align: right;">Running Qty</th>
                <th style="text-align: right;">Rate (₱)</th>
                <th style="text-align: right;">Stock Value (₱)</th>
              </tr>
            </thead>
            <tbody id="stock-modal-tbody"></tbody>
          </table>
        </div>
        <div class="modal-footer">
          <button class="btn-action btn-primary" onclick="closeStockDrilldown()">Close</button>
        </div>
      </div>
    </div>

  </div>

  <script>
    let activeTab = 'pnl';
    let allAvailableCompanies = [];
    let selectedCompanies = [];
    let cfPeriod = 'monthly';
    let cfView = 'matrix';
    let arView = 'summary';
    let apView = 'summary';

    let currentData = {
      pnl: null,
      balance_sheet: null,
      cash_flow: null,
      ar_aging: null,
      ap_aging: null,
      general_ledger: null,
      inventory_audit: null
    };

    const API_BASE = '/api/method/vehicle_management.vehicle_management.consolidated_financials_api.get_consolidated_financials';
    const FALLBACK_API = '/api/method/vm_consolidated_financials';

    function fmt(num) {
      if (num === null || num === undefined || isNaN(num)) return '₱0.00';
      const val = parseFloat(num);
      if (val === 0) return '<span class="num-zero">₱0.00</span>';
      const formatted = '₱' + Math.abs(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (val < 0) {
        return `<span class="num-negative">(${formatted})</span>`;
      }
      return formatted;
    }

    function fmtPlain(num) {
      if (num === null || num === undefined || isNaN(num)) return '₱0.00';
      const val = parseFloat(num);
      if (val === 0) return '₱0.00';
      const formatted = '₱' + Math.abs(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      return val < 0 ? `(${formatted})` : formatted;
    }

    function fmtQty(num, uom = '') {
      if (num === null || num === undefined || isNaN(num)) return '<span class="num-zero">0</span>';
      const val = parseFloat(num);
      if (val === 0) return '<span class="num-zero">0</span>';
      return val.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) + (uom ? ' ' + uom : '');
    }

    // ── Tab Navigation ──
    function switchTab(tabId) {
      activeTab = tabId;
      window.location.hash = tabId;
      
      document.querySelectorAll('.tab-item').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));

      const navEl = document.getElementById(`tab-nav-${tabId}`);
      if (navEl) navEl.classList.add('active');

      const contentEl = document.getElementById(`tab-${tabId}`);
      if (contentEl) contentEl.classList.add('active');

      loadDataForTab(tabId);
    }

    // ── Company Filter Management ──
    function toggleCompanyPopover() {
      const p = document.getElementById('company-popover');
      p.classList.toggle('open');
    }

    document.addEventListener('click', (e) => {
      const popover = document.getElementById('company-popover');
      const btn = document.getElementById('btn-company-filter');
      if (popover && btn && !popover.contains(e.target) && !btn.contains(e.target)) {
        popover.classList.remove('open');
      }
    });

    function renderCompanyCheckboxes(companies) {
      allAvailableCompanies = companies;
      if (selectedCompanies.length === 0) {
        selectedCompanies = [...companies];
      }

      const container = document.getElementById('company-checkboxes-container');
      let html = '';
      companies.forEach(co => {
        const isChecked = selectedCompanies.includes(co);
        html += `<label class="company-check-item">
          <input type="checkbox" value="${co}" ${isChecked ? 'checked' : ''} onchange="updateSelectedCompaniesState()">
          <span>${co}</span>
        </label>`;
      });
      container.innerHTML = html;
      updatePopoverSelectedCount();
    }

    function updateSelectedCompaniesState() {
      const checkboxes = document.querySelectorAll('#company-checkboxes-container input[type="checkbox"]');
      selectedCompanies = [];
      checkboxes.forEach(cb => {
        if (cb.checked) selectedCompanies.push(cb.value);
      });
      updatePopoverSelectedCount();
    }

    function updatePopoverSelectedCount() {
      const label = selectedCompanies.length === allAvailableCompanies.length
        ? `🏢 Companies (${allAvailableCompanies.length})`
        : `🏢 Companies (${selectedCompanies.length}/${allAvailableCompanies.length})`;
      document.getElementById('company-filter-label').innerText = label;
      document.getElementById('popover-selected-count').innerText = `${selectedCompanies.length} selected`;
    }

    function selectAllCompanies(selectAll) {
      const checkboxes = document.querySelectorAll('#company-checkboxes-container input[type="checkbox"]');
      checkboxes.forEach(cb => { cb.checked = selectAll; });
      updateSelectedCompaniesState();
    }

    function applyCompanyFilter() {
      document.getElementById('company-popover').classList.remove('open');
      reloadActiveTab();
    }

    // ── Date Presets ──
    function setPreset(preset) {
      document.querySelectorAll('.date-preset-btn').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');

      const now = new Date();
      const currYear = now.getFullYear();
      let fromDate = `${currYear}-01-01`;
      let toDate = `${currYear}-12-31`;

      if (preset === 'today') {
        const todayStr = now.toISOString().split('T')[0];
        fromDate = todayStr;
        toDate = todayStr;
      } else if (preset === 'mtd') {
        const m = String(now.getMonth() + 1).padStart(2, '0');
        fromDate = `${currYear}-${m}-01`;
        toDate = now.toISOString().split('T')[0];
      } else if (preset === 'qtd') {
        const qMonth = Math.floor(now.getMonth() / 3) * 3 + 1;
        fromDate = `${currYear}-${String(qMonth).padStart(2, '0')}-01`;
        toDate = now.toISOString().split('T')[0];
      } else if (preset === 'ytd') {
        fromDate = `${currYear}-01-01`;
        toDate = `${currYear}-12-31`;
      } else if (preset === 'all') {
        fromDate = '2020-01-01';
        toDate = '2030-12-31';
      }

      document.getElementById('input-from-date').value = fromDate;
      document.getElementById('input-to-date').value = toDate;
      reloadActiveTab();
    }

    function reloadActiveTab() {
      loadDataForTab(activeTab, true);
    }

    // ── API Fetcher ──
    async function fetchFinancialAPI(params) {
      if (selectedCompanies.length > 0 && selectedCompanies.length < allAvailableCompanies.length) {
        params.selected_companies = selectedCompanies.join(',');
      }
      const urlParams = new URLSearchParams(params);
      let response = await fetch(`${FALLBACK_API}?${urlParams.toString()}`);
      if (!response.ok) {
        response = await fetch(`${API_BASE}?${urlParams.toString()}`);
      }
      const json = await response.json();
      return json.message || json;
    }

    // ── Data Loader Dispatcher ──
    async function loadDataForTab(tabId, force = false) {
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;

      if (tabId === 'pnl') {
        document.getElementById('loading-pnl').classList.add('active');
        document.getElementById('pnl-date-badge').innerText = `${fromDate} to ${toDate}`;
        try {
          const data = await fetchFinancialAPI({ report_type: 'pnl', from_date: fromDate, to_date: toDate });
          currentData.pnl = data;
          if (data.all_companies && allAvailableCompanies.length === 0) {
            renderCompanyCheckboxes(data.all_companies);
          }
          renderPNLTable(data);
          updateKPIs();
        } catch (e) {
          console.error(e);
        } finally {
          document.getElementById('loading-pnl').classList.remove('active');
        }
      } else if (tabId === 'balance_sheet') {
        document.getElementById('loading-bs').classList.add('active');
        document.getElementById('bs-date-badge').innerText = `As of ${toDate}`;
        try {
          const data = await fetchFinancialAPI({ report_type: 'balance_sheet', to_date: toDate });
          currentData.balance_sheet = data;
          if (data.all_companies && allAvailableCompanies.length === 0) {
            renderCompanyCheckboxes(data.all_companies);
          }
          renderBalanceSheetTable(data);
          updateKPIs();
        } catch (e) {
          console.error(e);
        } finally {
          document.getElementById('loading-bs').classList.remove('active');
        }
      } else if (tabId === 'cash_flow') {
        document.getElementById('loading-cf').classList.add('active');
        document.getElementById('cf-date-badge').innerText = `${fromDate} to ${toDate} (${cfPeriod.toUpperCase()})`;
        try {
          const data = await fetchFinancialAPI({ report_type: 'cash_flow', from_date: fromDate, to_date: toDate, period: cfPeriod });
          currentData.cash_flow = data;
          if (data.all_companies && allAvailableCompanies.length === 0) {
            renderCompanyCheckboxes(data.all_companies);
          }
          renderCashFlowTable(data);
          updateKPIs();
        } catch (e) {
          console.error(e);
        } finally {
          document.getElementById('loading-cf').classList.remove('active');
        }
      } else if (tabId === 'ar_aging') {
        document.getElementById('loading-ar').classList.add('active');
        document.getElementById('ar-asof-badge').innerText = `As of ${toDate}`;
        try {
          const data = await fetchFinancialAPI({ report_type: 'ar_aging', as_of_date: toDate });
          currentData.ar_aging = data;
          if (data.all_companies && allAvailableCompanies.length === 0) {
            renderCompanyCheckboxes(data.all_companies);
          }
          document.getElementById('badge-ar-count').innerText = `${data.invoice_count || 0} Invoices`;
          renderARTable(data);
          updateKPIs();
        } catch (e) {
          console.error(e);
        } finally {
          document.getElementById('loading-ar').classList.remove('active');
        }
      } else if (tabId === 'ap_aging') {
        document.getElementById('loading-ap').classList.add('active');
        document.getElementById('ap-asof-badge').innerText = `As of ${toDate}`;
        try {
          const data = await fetchFinancialAPI({ report_type: 'ap_aging', as_of_date: toDate });
          currentData.ap_aging = data;
          if (data.all_companies && allAvailableCompanies.length === 0) {
            renderCompanyCheckboxes(data.all_companies);
          }
          document.getElementById('badge-ap-count').innerText = `${data.bill_count || 0} Bills`;
          renderAPTable(data);
          updateKPIs();
        } catch (e) {
          console.error(e);
        } finally {
          document.getElementById('loading-ap').classList.remove('active');
        }
      } else if (tabId === 'general_ledger') {
        loadGLData();
      } else if (tabId === 'inventory_audit') {
        loadInventoryData();
      }
    }

    // ── Dynamic KPI Ribbon Renderer ──
    function updateKPIs() {
      const container = document.getElementById('kpi-ribbon-container');
      const coCount = selectedCompanies.length || 13;

      if (activeTab === 'pnl' && currentData.pnl) {
        const d = currentData.pnl;
        const kpis = d.kpis || {};
        container.innerHTML = `
          <div class="kpi-card" onclick="switchTab('pnl')">
            <div class="kpi-label"><span>Consolidated Revenue</span><span class="badge badge-success">Topline</span></div>
            <div class="kpi-value">${fmtPlain(kpis.consolidated_revenue)}</div>
            <div class="kpi-subtext">Across ${coCount} operating companies</div>
          </div>
          <div class="kpi-card" onclick="switchTab('pnl')">
            <div class="kpi-label"><span>Gross Profit</span><span class="badge badge-neutral">${kpis.consolidated_gross_profit && kpis.consolidated_revenue ? ((kpis.consolidated_gross_profit/kpis.consolidated_revenue)*100).toFixed(1) : 0}% Margin</span></div>
            <div class="kpi-value">${fmtPlain(kpis.consolidated_gross_profit)}</div>
            <div class="kpi-subtext">COGS: ${fmtPlain(kpis.consolidated_cogs)}</div>
          </div>
          <div class="kpi-card" onclick="switchTab('pnl')">
            <div class="kpi-label"><span>Net Operating Income</span><span class="badge ${kpis.consolidated_net_profit >= 0 ? 'badge-success' : 'badge-danger'}">${kpis.consolidated_net_margin || 0}% Net</span></div>
            <div class="kpi-value" style="color: ${kpis.consolidated_net_profit >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmtPlain(kpis.consolidated_net_profit)}</div>
            <div class="kpi-subtext">Expenses: ${fmtPlain(kpis.consolidated_expenses)}</div>
          </div>
        `;
      } else if (activeTab === 'balance_sheet' && currentData.balance_sheet) {
        const d = currentData.balance_sheet;
        const kpis = d.kpis || {};
        container.innerHTML = `
          <div class="kpi-card" onclick="switchTab('balance_sheet')">
            <div class="kpi-label"><span>Total Assets</span><span class="badge badge-info">Assets</span></div>
            <div class="kpi-value">${fmtPlain(kpis.consolidated_assets)}</div>
            <div class="kpi-subtext">Operating assets across group</div>
          </div>
          <div class="kpi-card" onclick="switchTab('balance_sheet')">
            <div class="kpi-label"><span>Total Liabilities</span><span class="badge badge-warning">Payables & Debt</span></div>
            <div class="kpi-value">${fmtPlain(kpis.consolidated_liabilities)}</div>
            <div class="kpi-subtext">External obligations</div>
          </div>
          <div class="kpi-card" onclick="switchTab('balance_sheet')">
            <div class="kpi-label"><span>Total Equity</span><span class="badge badge-success">Capital</span></div>
            <div class="kpi-value">${fmtPlain(kpis.consolidated_equity)}</div>
            <div class="kpi-subtext">Liab + Equity: ${fmtPlain((kpis.consolidated_liabilities || 0) + (kpis.consolidated_equity || 0))}</div>
          </div>
        `;
      } else if (activeTab === 'cash_flow' && currentData.cash_flow) {
        const d = currentData.cash_flow;
        const s = d.summary || {};
        container.innerHTML = `
          <div class="kpi-card">
            <div class="kpi-label"><span>Beginning Cash Balance</span><span class="badge badge-neutral">Opening</span></div>
            <div class="kpi-value">${fmtPlain(s.opening_consolidated)}</div>
            <div class="kpi-subtext">Prior to period start</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>Total Cash Inflows</span><span class="badge badge-success">Collections</span></div>
            <div class="kpi-value" style="color: var(--positive-color);">${fmtPlain(s.inflows_consolidated)}</div>
            <div class="kpi-subtext">Customer & POS receipts</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>Total Cash Outflows</span><span class="badge badge-warning">Disbursements</span></div>
            <div class="kpi-value" style="color: var(--warning-color);">${fmtPlain(s.outflows_consolidated)}</div>
            <div class="kpi-subtext">Supplier & operating expenses</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>Net Cash Flow</span><span class="badge ${s.net_consolidated >= 0 ? 'badge-success' : 'badge-danger'}">${s.net_consolidated >= 0 ? '+ Positive' : '- Deficit'}</span></div>
            <div class="kpi-value" style="color: ${s.net_consolidated >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmtPlain(s.net_consolidated)}</div>
            <div class="kpi-subtext">Period net movement</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>Ending Cash Balance</span><span class="badge badge-info">Closing</span></div>
            <div class="kpi-value" style="color: var(--accent-blue);">${fmtPlain(s.ending_consolidated)}</div>
            <div class="kpi-subtext">Live running cash on hand</div>
          </div>
        `;
      } else if (activeTab === 'ar_aging' && currentData.ar_aging) {
        const d = currentData.ar_aging;
        const t = d.totals || {};
        container.innerHTML = `
          <div class="kpi-card">
            <div class="kpi-label"><span>Total Accounts Receivable</span><span class="badge badge-info">${d.invoice_count || 0} Invoices</span></div>
            <div class="kpi-value">${fmtPlain(t.total_outstanding)}</div>
            <div class="kpi-subtext">Across ${d.customer_summary ? d.customer_summary.length : 0} customers</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>Current / Not Due</span><span class="badge badge-success">On Term</span></div>
            <div class="kpi-value" style="color: var(--positive-color);">${fmtPlain(t.current)}</div>
            <div class="kpi-subtext">Within credit terms</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>1 - 30 Days Overdue</span><span class="badge badge-warning">Grace Period</span></div>
            <div class="kpi-value" style="color: var(--warning-color);">${fmtPlain(t.range_1_30)}</div>
            <div class="kpi-subtext">Follow-up required</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>31 - 60 Days Overdue</span><span class="badge badge-danger">Moderate</span></div>
            <div class="kpi-value" style="color: #f97316;">${fmtPlain(t.range_31_60)}</div>
            <div class="kpi-subtext">Second notice</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>61 - 90+ Days Overdue</span><span class="badge badge-danger">Critical</span></div>
            <div class="kpi-value" style="color: var(--negative-color);">${fmtPlain((t.range_61_90 || 0) + (t.range_90_plus || 0))}</div>
            <div class="kpi-subtext">61-90d: ${fmtPlain(t.range_61_90)} | 90+d: ${fmtPlain(t.range_90_plus)}</div>
          </div>
        `;
      } else if (activeTab === 'ap_aging' && currentData.ap_aging) {
        const d = currentData.ap_aging;
        const t = d.totals || {};
        container.innerHTML = `
          <div class="kpi-card">
            <div class="kpi-label"><span>Total Accounts Payable</span><span class="badge badge-info">${d.bill_count || 0} Bills</span></div>
            <div class="kpi-value">${fmtPlain(t.total_outstanding)}</div>
            <div class="kpi-subtext">Across ${d.supplier_summary ? d.supplier_summary.length : 0} suppliers</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>Current / Not Due</span><span class="badge badge-success">On Term</span></div>
            <div class="kpi-value" style="color: var(--positive-color);">${fmtPlain(t.current)}</div>
            <div class="kpi-subtext">Payable on schedule</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>1 - 30 Days Overdue</span><span class="badge badge-warning">Due Soon</span></div>
            <div class="kpi-value" style="color: var(--warning-color);">${fmtPlain(t.range_1_30)}</div>
            <div class="kpi-subtext">Immediate disbursement</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>31 - 60 Days Overdue</span><span class="badge badge-danger">Past Due</span></div>
            <div class="kpi-value" style="color: #f97316;">${fmtPlain(t.range_31_60)}</div>
            <div class="kpi-subtext">Vendor reminder</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label"><span>61 - 90+ Days Overdue</span><span class="badge badge-danger">Overdue</span></div>
            <div class="kpi-value" style="color: var(--negative-color);">${fmtPlain((t.range_61_90 || 0) + (t.range_90_plus || 0))}</div>
            <div class="kpi-subtext">61-90d: ${fmtPlain(t.range_61_90)} | 90+d: ${fmtPlain(t.range_90_plus)}</div>
          </div>
        `;
      }
    }

    // ── P&L Table Renderer ──
    function renderPNLTable(data) {
      const companies = data.companies || [];
      const meta = data.company_meta || {};
      const sections = data.sections || {};

      let thead = '<tr><th class="sticky-col">Account Title</th>';
      companies.forEach(c => {
        const abbr = meta[c]?.abbr || c.substring(0, 4);
        thead += `<th style="text-align: right;" title="${c}">${abbr}</th>`;
      });
      thead += '<th class="sticky-total">Consolidated (PHP)</th></tr>';
      document.getElementById('thead-pnl').innerHTML = thead;

      let tbody = '';
      const order = ['income', 'cogs', 'gross_profit', 'operating_expenses', 'net_profit'];
      order.forEach(secKey => {
        const sec = sections[secKey];
        if (!sec) return;

        if (secKey === 'gross_profit' || secKey === 'net_profit') {
          tbody += `<tr class="${secKey === 'net_profit' ? 'row-grand-total' : 'row-section-total'}">
            <td class="sticky-col"><strong>${sec.title}</strong></td>`;
          companies.forEach(c => {
            const val = sec.totals[c] || 0;
            tbody += `<td class="num-cell">${fmt(val)}</td>`;
          });
          tbody += `<td class="sticky-total">${fmt(sec.consolidated)}</td></tr>`;
        } else {
          tbody += `<tr class="row-section-header"><td colspan="${companies.length + 2}">${sec.title}</td></tr>`;
          (sec.rows || []).forEach(row => {
            tbody += `<tr>
              <td class="sticky-col">${row.account_name}</td>`;
            companies.forEach(c => {
              const val = row.companies[c] || 0;
              tbody += `<td class="num-cell" onclick="openDrilldown('${c}', '${row.account_name}')">${fmt(val)}</td>`;
            });
            tbody += `<td class="sticky-total" onclick="openDrilldown('', '${row.account_name}')">${fmt(row.total)}</td></tr>`;
          });
          tbody += `<tr class="row-section-total"><td class="sticky-col">Total ${sec.title}</td>`;
          companies.forEach(c => {
            const val = sec.totals[c] || 0;
            tbody += `<td class="num-cell">${fmt(val)}</td>`;
          });
          tbody += `<td class="sticky-total">${fmt(sec.consolidated)}</td></tr>`;
        }
      });
      document.getElementById('tbody-pnl').innerHTML = tbody;
    }

    // ── Balance Sheet Table Renderer ──
    function renderBalanceSheetTable(data) {
      const companies = data.companies || [];
      const meta = data.company_meta || {};
      const sections = data.sections || {};

      let thead = '<tr><th class="sticky-col">Balance Sheet Classification</th>';
      companies.forEach(c => {
        const abbr = meta[c]?.abbr || c.substring(0, 4);
        thead += `<th style="text-align: right;" title="${c}">${abbr}</th>`;
      });
      thead += '<th class="sticky-total">Consolidated (PHP)</th></tr>';
      document.getElementById('thead-bs').innerHTML = thead;

      let tbody = '';
      ['assets', 'liabilities', 'equity', 'total_liab_equity'].forEach(secKey => {
        const sec = sections[secKey];
        if (!sec) return;

        if (secKey === 'total_liab_equity') {
          tbody += `<tr class="row-grand-total"><td class="sticky-col"><strong>${sec.title}</strong></td>`;
          companies.forEach(c => {
            const val = sec.totals[c] || 0;
            tbody += `<td class="num-cell">${fmt(val)}</td>`;
          });
          tbody += `<td class="sticky-total">${fmt(sec.consolidated)}</td></tr>`;
        } else {
          tbody += `<tr class="row-section-header"><td colspan="${companies.length + 2}">${sec.title}</td></tr>`;
          (sec.rows || []).forEach(row => {
            tbody += `<tr><td class="sticky-col">${row.account_name}</td>`;
            companies.forEach(c => {
              const val = row.companies[c] || 0;
              tbody += `<td class="num-cell" onclick="openDrilldown('${c}', '${row.account_name}')">${fmt(val)}</td>`;
            });
            tbody += `<td class="sticky-total" onclick="openDrilldown('', '${row.account_name}')">${fmt(row.total)}</td></tr>`;
          });
          tbody += `<tr class="row-section-total"><td class="sticky-col">Total ${sec.title}</td>`;
          companies.forEach(c => {
            const val = sec.totals[c] || 0;
            tbody += `<td class="num-cell">${fmt(val)}</td>`;
          });
          tbody += `<td class="sticky-total">${fmt(sec.consolidated)}</td></tr>`;
        }
      });
      document.getElementById('tbody-bs').innerHTML = tbody;
    }

    // ── Cash Flow Statement Controls & Renderer ──
    function setCashFlowPeriod(period) {
      cfPeriod = period;
      document.querySelectorAll('#tab-cash_flow .date-pill-group button[id^="cf-period-"]').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(`cf-period-${period}`);
      if (activeBtn) activeBtn.classList.add('active');
      loadDataForTab('cash_flow', true);
    }

    function setCashFlowView(view) {
      cfView = view;
      document.querySelectorAll('#tab-cash_flow .date-pill-group button[id^="cf-view-"]').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(`cf-view-${view}`);
      if (activeBtn) activeBtn.classList.add('active');

      if (view === 'matrix') {
        document.getElementById('cf-matrix-container').style.display = 'block';
        document.getElementById('cf-periods-container').style.display = 'none';
      } else {
        document.getElementById('cf-matrix-container').style.display = 'none';
        document.getElementById('cf-periods-container').style.display = 'block';
      }
    }

    function renderCashFlowTable(data) {
      const companies = data.companies || [];
      const meta = data.company_meta || {};
      const summary = data.summary || {};
      const inflows = data.inflow_categories || {};
      const outflows = data.outflow_categories || {};
      const periods = data.periods || [];

      // 1. Matrix Header
      let thead = '<tr><th class="sticky-col">Cash Flow Activities</th>';
      companies.forEach(c => {
        const abbr = meta[c]?.abbr || c.substring(0, 4);
        thead += `<th style="text-align: right;" title="${c}">${abbr}</th>`;
      });
      thead += '<th class="sticky-total">Consolidated (PHP)</th></tr>';
      document.getElementById('thead-cf-matrix').innerHTML = thead;

      // 2. Matrix Body
      let tbody = '';
      
      // Beginning Cash Balance Row
      tbody += `<tr class="row-section-total">
        <td class="sticky-col"><strong>Beginning Cash &amp; Bank Balance</strong></td>`;
      companies.forEach(c => {
        const val = (summary.opening_balance && summary.opening_balance[c]) || 0;
        tbody += `<td class="num-cell">${fmt(val)}</td>`;
      });
      tbody += `<td class="sticky-total">${fmt(summary.opening_consolidated || 0)}</td></tr>`;

      // Cash Inflows Section
      tbody += `<tr class="row-section-header"><td colspan="${companies.length + 2}">Operating Cash Inflows &amp; Receipts</td></tr>`;
      Object.keys(inflows).forEach(k => {
        const cat = inflows[k];
        tbody += `<tr><td class="sticky-col">&bull; ${cat.label}</td>`;
        companies.forEach(c => {
          const val = (cat.companies && cat.companies[c]) || 0;
          tbody += `<td class="num-cell">${fmt(val)}</td>`;
        });
        tbody += `<td class="sticky-total">${fmt(cat.total || 0)}</td></tr>`;
      });
      tbody += `<tr class="row-section-total"><td class="sticky-col"><strong>Total Cash Inflows</strong></td>`;
      companies.forEach(c => {
        const val = (summary.inflows_total && summary.inflows_total[c]) || 0;
        tbody += `<td class="num-cell" style="color: var(--positive-color);">${fmt(val)}</td>`;
      });
      tbody += `<td class="sticky-total" style="color: var(--positive-color);">${fmt(summary.inflows_consolidated || 0)}</td></tr>`;

      // Cash Outflows Section
      tbody += `<tr class="row-section-header"><td colspan="${companies.length + 2}">Operating Cash Outflows &amp; Disbursements</td></tr>`;
      Object.keys(outflows).forEach(k => {
        const cat = outflows[k];
        tbody += `<tr><td class="sticky-col">&bull; ${cat.label}</td>`;
        companies.forEach(c => {
          const val = (cat.companies && cat.companies[c]) || 0;
          tbody += `<td class="num-cell">${fmt(val)}</td>`;
        });
        tbody += `<td class="sticky-total">${fmt(cat.total || 0)}</td></tr>`;
      });
      tbody += `<tr class="row-section-total"><td class="sticky-col"><strong>Total Cash Outflows</strong></td>`;
      companies.forEach(c => {
        const val = (summary.outflows_total && summary.outflows_total[c]) || 0;
        tbody += `<td class="num-cell" style="color: var(--warning-color);">${fmt(val)}</td>`;
      });
      tbody += `<td class="sticky-total" style="color: var(--warning-color);">${fmt(summary.outflows_consolidated || 0)}</td></tr>`;

      // Net Cash Flow Row
      tbody += `<tr class="row-section-total" style="border-top: 2px solid var(--border-highlight);">
        <td class="sticky-col"><strong>Net Cash Flow for Period</strong></td>`;
      companies.forEach(c => {
        const val = (summary.net_cash_flow && summary.net_cash_flow[c]) || 0;
        tbody += `<td class="num-cell" style="font-weight: 700;">${fmt(val)}</td>`;
      });
      tbody += `<td class="sticky-total" style="font-weight: 800;">${fmt(summary.net_consolidated || 0)}</td></tr>`;

      // Ending Cash Balance Row
      tbody += `<tr class="row-grand-total">
        <td class="sticky-col"><strong>Ending Cash &amp; Bank Balance</strong></td>`;
      companies.forEach(c => {
        const val = (summary.ending_balance && summary.ending_balance[c]) || 0;
        tbody += `<td class="num-cell" style="color: var(--accent-blue);">${fmt(val)}</td>`;
      });
      tbody += `<td class="sticky-total" style="color: var(--accent-blue);">${fmt(summary.ending_consolidated || 0)}</td></tr>`;

      document.getElementById('tbody-cf-matrix').innerHTML = tbody;

      // 3. Periodic Trend Table
      let pbody = '';
      if (periods.length === 0) {
        pbody = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--text-muted);">No cash transactions recorded in this date range.</td></tr>`;
      } else {
        periods.forEach(p => {
          pbody += `<tr>
            <td style="font-weight: 700; color: var(--text-primary);">${p.period_label}</td>
            <td class="num-cell">${fmt(p.opening_total || 0)}</td>
            <td class="num-cell" style="color: var(--positive-color);">${fmt(p.inflow_total || 0)}</td>
            <td class="num-cell" style="color: var(--warning-color);">${fmt(p.outflow_total || 0)}</td>
            <td class="num-cell" style="font-weight: 700; color: ${p.net_total >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmt(p.net_total || 0)}</td>
            <td class="num-cell" style="font-weight: 800; color: var(--accent-blue);">${fmt(p.ending_total || 0)}</td>
            <td style="text-align: center;"><span class="badge badge-neutral">${p.entries_count} tx</span></td>
          </tr>`;
        });
      }
      document.getElementById('tbody-cf-periods').innerHTML = pbody;
    }

    function filterCashFlowRows(query) {
      filterTableRows('table-cf-matrix', query);
    }

    // ── AR Aging Renderer & Controls ──
    function setARView(view) {
      arView = view;
      document.querySelectorAll('#tab-ar_aging .date-pill-group button[id^="ar-view-"]').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(`ar-view-${view}`);
      if (activeBtn) activeBtn.classList.add('active');

      document.getElementById('ar-summary-container').style.display = view === 'summary' ? 'block' : 'none';
      document.getElementById('ar-companies-container').style.display = view === 'companies' ? 'block' : 'none';
      document.getElementById('ar-details-container').style.display = view === 'details' ? 'block' : 'none';
    }

    function renderARTable(data) {
      const customers = data.customer_summary || [];
      const companies = data.company_summary || [];
      const invoices = data.invoices || [];
      const totals = data.totals || {};

      // 1. Customer Summary
      let sbody = '';
      customers.forEach(c => {
        sbody += `<tr>
          <td class="sticky-col">${c.customer_name}</td>
          <td><span class="badge badge-neutral">${c.company}</span></td>
          <td class="num-cell">${fmt(c.current)}</td>
          <td class="num-cell" style="color: var(--warning-color);">${fmt(c.range_1_30)}</td>
          <td class="num-cell" style="color: #f97316;">${fmt(c.range_31_60)}</td>
          <td class="num-cell" style="color: var(--negative-color);">${fmt(c.range_61_90)}</td>
          <td class="num-cell" style="color: var(--negative-color); font-weight: 700;">${fmt(c.range_90_plus)}</td>
          <td class="sticky-total">${fmt(c.total_outstanding)}</td>
          <td style="text-align: center;"><span class="badge badge-neutral">${c.invoice_count}</span></td>
        </tr>`;
      });
      sbody += `<tr class="row-grand-total">
        <td class="sticky-col">Grand Total AR (${customers.length} Customers)</td>
        <td>Consolidated</td>
        <td class="num-cell">${fmt(totals.current)}</td>
        <td class="num-cell">${fmt(totals.range_1_30)}</td>
        <td class="num-cell">${fmt(totals.range_31_60)}</td>
        <td class="num-cell">${fmt(totals.range_61_90)}</td>
        <td class="num-cell">${fmt(totals.range_90_plus)}</td>
        <td class="sticky-total">${fmt(totals.total_outstanding)}</td>
        <td style="text-align: center;"><span class="badge badge-neutral">${totals.invoice_count || 0}</span></td>
      </tr>`;
      document.getElementById('tbody-ar-summary').innerHTML = sbody;

      // 2. Company Matrix
      let cbody = '';
      companies.forEach(co => {
        cbody += `<tr>
          <td class="sticky-col">${co.company}</td>
          <td><span class="badge badge-neutral">${co.abbr}</span></td>
          <td class="num-cell">${fmt(co.current)}</td>
          <td class="num-cell">${fmt(co.range_1_30)}</td>
          <td class="num-cell">${fmt(co.range_31_60)}</td>
          <td class="num-cell">${fmt(co.range_61_90)}</td>
          <td class="num-cell">${fmt(co.range_90_plus)}</td>
          <td class="sticky-total">${fmt(co.total_outstanding)}</td>
          <td style="text-align: center;"><span class="badge badge-neutral">${co.invoice_count}</span></td>
        </tr>`;
      });
      cbody += `<tr class="row-grand-total">
        <td class="sticky-col">Grand Total AR (All Branches)</td>
        <td>ALL</td>
        <td class="num-cell">${fmt(totals.current)}</td>
        <td class="num-cell">${fmt(totals.range_1_30)}</td>
        <td class="num-cell">${fmt(totals.range_31_60)}</td>
        <td class="num-cell">${fmt(totals.range_61_90)}</td>
        <td class="num-cell">${fmt(totals.range_90_plus)}</td>
        <td class="sticky-total">${fmt(totals.total_outstanding)}</td>
        <td style="text-align: center;"><span class="badge badge-neutral">${totals.invoice_count || 0}</span></td>
      </tr>`;
      document.getElementById('tbody-ar-companies').innerHTML = cbody;

      // 3. Detailed Invoices Table
      let dbody = '';
      invoices.forEach(inv => {
        let bBadge = '<span class="badge badge-success">Current</span>';
        if (inv.bucket === 'range_1_30') bBadge = '<span class="badge badge-warning">1-30d</span>';
        else if (inv.bucket === 'range_31_60') bBadge = '<span class="badge badge-warning" style="background:rgba(249,115,22,0.15);color:#f97316;">31-60d</span>';
        else if (inv.bucket === 'range_61_90') bBadge = '<span class="badge badge-danger">61-90d</span>';
        else if (inv.bucket === 'range_90_plus') bBadge = '<span class="badge badge-danger" style="font-weight:800;">90+d</span>';

        dbody += `<tr>
          <td style="font-family:var(--font-mono);font-weight:600;">${inv.name}</td>
          <td>${inv.customer_name}</td>
          <td><span class="badge badge-neutral">${inv.company_abbr}</span></td>
          <td style="font-family:var(--font-mono);">${inv.posting_date}</td>
          <td style="font-family:var(--font-mono);">${inv.due_date} <small style="color:var(--text-muted)">(${inv.terms})</small></td>
          <td style="text-align: center; font-family:var(--font-mono); font-weight:700; color:${inv.days_overdue > 0 ? 'var(--negative-color)' : 'var(--positive-color)'};">${inv.days_overdue} d</td>
          <td style="text-align: center;">${bBadge}</td>
          <td class="num-cell">${fmt(inv.grand_total)}</td>
          <td class="num-cell" style="font-weight:700;">${fmt(inv.amount_aged)}</td>
          <td><span class="badge ${inv.status === 'Paid' ? 'badge-success' : 'badge-neutral'}">${inv.status}</span></td>
        </tr>`;
      });
      document.getElementById('tbody-ar-details').innerHTML = dbody;
    }

    function filterARRows(query) {
      filterTableRows('table-ar-summary', query);
      filterTableRows('table-ar-companies', query);
      filterTableRows('table-ar-details', query);
    }

    // ── AP Aging Renderer & Controls ──
    function setAPView(view) {
      apView = view;
      document.querySelectorAll('#tab-ap_aging .date-pill-group button[id^="ap-view-"]').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(`ap-view-${view}`);
      if (activeBtn) activeBtn.classList.add('active');

      document.getElementById('ap-summary-container').style.display = view === 'summary' ? 'block' : 'none';
      document.getElementById('ap-companies-container').style.display = view === 'companies' ? 'block' : 'none';
      document.getElementById('ap-details-container').style.display = view === 'details' ? 'block' : 'none';
    }

    function renderAPTable(data) {
      const suppliers = data.supplier_summary || [];
      const companies = data.company_summary || [];
      const bills = data.bills || [];
      const totals = data.totals || {};

      // 1. Supplier Summary
      let sbody = '';
      suppliers.forEach(s => {
        sbody += `<tr>
          <td class="sticky-col">${s.supplier_name}</td>
          <td><span class="badge badge-neutral">${s.company}</span></td>
          <td class="num-cell">${fmt(s.current)}</td>
          <td class="num-cell" style="color: var(--warning-color);">${fmt(s.range_1_30)}</td>
          <td class="num-cell" style="color: #f97316;">${fmt(s.range_31_60)}</td>
          <td class="num-cell" style="color: var(--negative-color);">${fmt(s.range_61_90)}</td>
          <td class="num-cell" style="color: var(--negative-color); font-weight: 700;">${fmt(s.range_90_plus)}</td>
          <td class="sticky-total">${fmt(s.total_outstanding)}</td>
          <td style="text-align: center;"><span class="badge badge-neutral">${s.bill_count}</span></td>
        </tr>`;
      });
      sbody += `<tr class="row-grand-total">
        <td class="sticky-col">Grand Total AP (${suppliers.length} Suppliers)</td>
        <td>Consolidated</td>
        <td class="num-cell">${fmt(totals.current)}</td>
        <td class="num-cell">${fmt(totals.range_1_30)}</td>
        <td class="num-cell">${fmt(totals.range_31_60)}</td>
        <td class="num-cell">${fmt(totals.range_61_90)}</td>
        <td class="num-cell">${fmt(totals.range_90_plus)}</td>
        <td class="sticky-total">${fmt(totals.total_outstanding)}</td>
        <td style="text-align: center;"><span class="badge badge-neutral">${totals.bill_count || 0}</span></td>
      </tr>`;
      document.getElementById('tbody-ap-summary').innerHTML = sbody;

      // 2. Company Matrix
      let cbody = '';
      companies.forEach(co => {
        cbody += `<tr>
          <td class="sticky-col">${co.company}</td>
          <td><span class="badge badge-neutral">${co.abbr}</span></td>
          <td class="num-cell">${fmt(co.current)}</td>
          <td class="num-cell">${fmt(co.range_1_30)}</td>
          <td class="num-cell">${fmt(co.range_31_60)}</td>
          <td class="num-cell">${fmt(co.range_61_90)}</td>
          <td class="num-cell">${fmt(co.range_90_plus)}</td>
          <td class="sticky-total">${fmt(co.total_outstanding)}</td>
          <td style="text-align: center;"><span class="badge badge-neutral">${co.bill_count}</span></td>
        </tr>`;
      });
      cbody += `<tr class="row-grand-total">
        <td class="sticky-col">Grand Total AP (All Branches)</td>
        <td>ALL</td>
        <td class="num-cell">${fmt(totals.current)}</td>
        <td class="num-cell">${fmt(totals.range_1_30)}</td>
        <td class="num-cell">${fmt(totals.range_31_60)}</td>
        <td class="num-cell">${fmt(totals.range_61_90)}</td>
        <td class="num-cell">${fmt(totals.range_90_plus)}</td>
        <td class="sticky-total">${fmt(totals.total_outstanding)}</td>
        <td style="text-align: center;"><span class="badge badge-neutral">${totals.bill_count || 0}</span></td>
      </tr>`;
      document.getElementById('tbody-ap-companies').innerHTML = cbody;

      // 3. Detailed Bills Table
      let dbody = '';
      bills.forEach(bill => {
        let bBadge = '<span class="badge badge-success">Current</span>';
        if (bill.bucket === 'range_1_30') bBadge = '<span class="badge badge-warning">1-30d</span>';
        else if (bill.bucket === 'range_31_60') bBadge = '<span class="badge badge-warning" style="background:rgba(249,115,22,0.15);color:#f97316;">31-60d</span>';
        else if (bill.bucket === 'range_61_90') bBadge = '<span class="badge badge-danger">61-90d</span>';
        else if (bill.bucket === 'range_90_plus') bBadge = '<span class="badge badge-danger" style="font-weight:800;">90+d</span>';

        dbody += `<tr>
          <td style="font-family:var(--font-mono);font-weight:600;">${bill.bill_no || bill.name}</td>
          <td>${bill.supplier_name}</td>
          <td><span class="badge badge-neutral">${bill.company_abbr}</span></td>
          <td style="font-family:var(--font-mono);">${bill.bill_date}</td>
          <td style="font-family:var(--font-mono);">${bill.due_date} <small style="color:var(--text-muted)">(${bill.terms})</small></td>
          <td style="text-align: center; font-family:var(--font-mono); font-weight:700; color:${bill.days_overdue > 0 ? 'var(--negative-color)' : 'var(--positive-color)'};">${bill.days_overdue} d</td>
          <td style="text-align: center;">${bBadge}</td>
          <td class="num-cell">${fmt(bill.grand_total)}</td>
          <td class="num-cell" style="font-weight:700;">${fmt(bill.amount_aged)}</td>
          <td><span class="badge ${bill.status === 'Paid' ? 'badge-success' : 'badge-neutral'}">${bill.status}</span></td>
        </tr>`;
      });
      document.getElementById('tbody-ap-details').innerHTML = dbody;
    }

    function filterAPRows(query) {
      filterTableRows('table-ap-summary', query);
      filterTableRows('table-ap-companies', query);
      filterTableRows('table-ap-details', query);
    }

    // ── General Ledger & Inventory Loaders ──
    async function loadGLData() {
      document.getElementById('loading-gl').classList.add('active');
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      const voucherType = document.getElementById('gl-voucher-type-filter').value;
      const search = document.getElementById('search-gl').value;

      try {
        const data = await fetchFinancialAPI({
          report_type: 'general_ledger',
          from_date: fromDate,
          to_date: toDate,
          voucher_type: voucherType,
          search_text: search,
          page: 1,
          page_length: 150
        });
        currentData.general_ledger = data;
        document.getElementById('gl-records-badge').innerText = `${data.total_records || 0} Entries`;

        let tbody = '';
        (data.entries || []).forEach(e => {
          tbody += `<tr>
            <td style="font-family:var(--font-mono);">${e.posting_date}</td>
            <td><span class="badge badge-neutral">${e.company}</span></td>
            <td>${e.account}</td>
            <td><span class="badge badge-neutral">${e.voucher_type}</span></td>
            <td style="font-family:var(--font-mono);font-weight:600;">${e.voucher_no}</td>
            <td style="color:var(--text-muted);">${e.against || '-'}</td>
            <td class="num-cell">${fmt(e.debit)}</td>
            <td class="num-cell">${fmt(e.credit)}</td>
            <td style="max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-muted);">${e.remarks || ''}</td>
          </tr>`;
        });
        document.getElementById('tbody-gl').innerHTML = tbody || '<tr><td colspan="9" style="text-align:center;padding:24px;">No GL entries found.</td></tr>';
      } catch (e) {
        console.error(e);
      } finally {
        document.getElementById('loading-gl').classList.remove('active');
      }
    }

    let allInvItems = [];
    async function loadInventoryData() {
      document.getElementById('loading-inv').classList.add('active');
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;

      try {
        const data = await fetchFinancialAPI({ report_type: 'inventory_audit', from_date: fromDate, to_date: toDate });
        currentData.inventory_audit = data;
        allInvItems = data.rows || [];
        document.getElementById('inv-sku-badge').innerText = `${data.total_sku_count || 0} SKUs`;

        const sel = document.getElementById('inv-item-select');
        sel.innerHTML = allInvItems.map(it => `<option value="${it.item_code}" selected>${it.item_code} - ${it.item_name}</option>`).join('');

        renderInventoryTable(data);
      } catch (e) {
        console.error(e);
      } finally {
        document.getElementById('loading-inv').classList.remove('active');
      }
    }

    function renderInventoryTable(data) {
      const companies = data.companies || [];
      const meta = data.company_meta || {};
      const rows = data.rows || [];

      let thead = '<tr><th class="sticky-col">Item Description</th><th>UOM</th>';
      companies.forEach(c => {
        const abbr = meta[c]?.abbr || c.substring(0, 4);
        thead += `<th style="text-align: right;" title="${c} Inflow">${abbr} IN</th>
                  <th style="text-align: right;" title="${c} Outflow">${abbr} OUT</th>
                  <th style="text-align: right; border-right:1px solid var(--border-subtle);" title="${c} On Hand">${abbr} BAL</th>`;
      });
      thead += '<th class="sticky-total">Total On Hand</th><th style="text-align: right;">Valuation (₱)</th></tr>';
      document.getElementById('thead-inv').innerHTML = thead;

      let tbody = '';
      rows.forEach(it => {
        tbody += `<tr>
          <td class="sticky-col" onclick="openStockDrilldown('${it.item_code}')" style="cursor:pointer;">
            <span style="font-weight:700; color:var(--text-primary);">${it.item_code}</span><br>
            <small style="color:var(--text-muted);">${it.item_name}</small>
          </td>
          <td><span class="badge badge-neutral">${it.stock_uom}</span></td>`;
        companies.forEach(c => {
          const inQ = it.companies_in[c] || 0;
          const outQ = it.companies_out[c] || 0;
          const endQ = it.companies_qty[c] || 0;
          tbody += `<td class="num-cell" style="color:var(--positive-color);">${fmtQty(inQ)}</td>
                    <td class="num-cell" style="color:var(--warning-color);">${fmtQty(outQ)}</td>
                    <td class="num-cell" style="font-weight:700;border-right:1px solid var(--border-subtle);">${fmtQty(endQ)}</td>`;
        });
        tbody += `<td class="sticky-total">${fmtQty(it.total_qty)}</td>
                  <td class="num-cell" style="font-weight:700;">${fmt(it.total_val)}</td></tr>`;
      });
      document.getElementById('tbody-inv').innerHTML = tbody;
    }

    function inventoryRefreshFilter() {
      const q = document.getElementById('search-inv').value.toLowerCase();
      const stockOnly = document.getElementById('inv-stock-only').checked;
      const rows = document.querySelectorAll('#tbody-inv tr');
      rows.forEach(tr => {
        const text = tr.innerText.toLowerCase();
        const match = (!q || text.includes(q));
        tr.style.display = match ? '' : 'none';
      });
    }

    function inventorySelectAll(sel) {
      const opts = document.querySelectorAll('#inv-item-select option');
      opts.forEach(o => o.selected = sel);
    }
    function inventorySelectChanged() {}

    // ── Table Row Filter Utility ──
    function filterTableRows(tableId, query) {
      const q = (query || '').toLowerCase().trim();
      const tbody = document.querySelector(`#${tableId} tbody`);
      if (!tbody) return;
      const rows = tbody.querySelectorAll('tr');
      rows.forEach(tr => {
        if (tr.classList.contains('row-grand-total') || tr.classList.contains('row-section-total')) {
          tr.style.display = '';
          return;
        }
        const text = tr.innerText.toLowerCase();
        tr.style.display = (!q || text.includes(q)) ? '' : 'none';
      });
    }

    // ── Professional Excel Export (.xlsx) Engine ──
    function exportCurrentTableExcel() {
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      let filename = `Financial_Report_${activeTab}_${toDate}.xlsx`;
      let sheetName = activeTab.toUpperCase();

      if (activeTab === 'pnl') {
        filename = `Consolidated_Profit_and_Loss_${fromDate}_to_${toDate}.xlsx`;
        sheetName = "Profit & Loss";
        exportTableToExcel('table-pnl', filename, sheetName);
      } else if (activeTab === 'balance_sheet') {
        filename = `Consolidated_Balance_Sheet_${toDate}.xlsx`;
        sheetName = "Balance Sheet";
        exportTableToExcel('table-bs', filename, sheetName);
      } else if (activeTab === 'cash_flow') {
        filename = `Consolidated_Cash_Flow_${cfPeriod.toUpperCase()}_${fromDate}_to_${toDate}.xlsx`;
        sheetName = `Cash Flow (${cfPeriod.toUpperCase()})`;
        const tableId = cfView === 'matrix' ? 'table-cf-matrix' : 'table-cf-periods';
        exportTableToExcel(tableId, filename, sheetName);
      } else if (activeTab === 'ar_aging') {
        filename = `AR_Aging_Analysis_30_60_90_${toDate}.xlsx`;
        sheetName = "AR Aging";
        const tableId = arView === 'summary' ? 'table-ar-summary' : (arView === 'companies' ? 'table-ar-companies' : 'table-ar-details');
        exportTableToExcel(tableId, filename, sheetName);
      } else if (activeTab === 'ap_aging') {
        filename = `AP_Aging_Analysis_30_60_90_${toDate}.xlsx`;
        sheetName = "AP Aging";
        const tableId = apView === 'summary' ? 'table-ap-summary' : (apView === 'companies' ? 'table-ap-companies' : 'table-ap-details');
        exportTableToExcel(tableId, filename, sheetName);
      } else if (activeTab === 'general_ledger') {
        filename = `General_Ledger_${fromDate}_to_${toDate}.xlsx`;
        sheetName = "General Ledger";
        exportTableToExcel('table-gl', filename, sheetName);
      } else if (activeTab === 'inventory_audit') {
        filename = `Inventory_Audit_Running_Balances_${toDate}.xlsx`;
        sheetName = "Inventory Audit";
        exportTableToExcel('table-inv', filename, sheetName);
      }
    }

    function exportTableToExcel(tableId, filename, sheetName) {
      const table = document.getElementById(tableId);
      if (!table) {
        alert("No active table data found to export.");
        return;
      }

      if (typeof XLSX !== 'undefined') {
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.table_to_sheet(table, { raw: false });
        XLSX.utils.book_append_sheet(wb, ws, sheetName.substring(0, 31));
        XLSX.writeFile(wb, filename);
      } else {
        // Fallback HTML-Excel download
        const html = table.outerHTML;
        const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename.replace('.xlsx', '.xls');
        a.click();
      }
    }

    // ── Print Functionality ──
    function printReport() {
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      const activeTabLabel = document.querySelector('.tab-item.active')?.innerText || 'Financial Statement';
      document.getElementById('print-meta-text').innerText = `${activeTabLabel} &bull; Period: ${fromDate} to ${toDate} &bull; Generated: ${new Date().toLocaleDateString()}`;
      window.print();
    }

    // ── Drilldown Modals ──
    async function openDrilldown(company, account) {
      document.getElementById('drilldown-modal').classList.add('open');
      document.getElementById('drilldown-title').innerText = `${account} &bull; ${company || 'Consolidated Group'}`;
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;

      try {
        const data = await fetchFinancialAPI({ report_type: 'drilldown', company: company, account: account, from_date: fromDate, to_date: toDate });
        let tbody = '';
        (data.entries || []).forEach(e => {
          tbody += `<tr>
            <td style="font-family:var(--font-mono);">${e.posting_date}</td>
            <td><span class="badge badge-neutral">${e.voucher_type}</span></td>
            <td style="font-family:var(--font-mono);">${e.voucher_no}</td>
            <td class="num-cell">${fmt(e.debit)}</td>
            <td class="num-cell">${fmt(e.credit)}</td>
            <td style="color:var(--text-muted);">${e.remarks || ''}</td>
          </tr>`;
        });
        document.getElementById('drilldown-tbody').innerHTML = tbody || '<tr><td colspan="6" style="text-align:center;padding:20px;">No transaction entries found.</td></tr>';
      } catch (e) {
        console.error(e);
      }
    }

    function closeDrilldown() {
      document.getElementById('drilldown-modal').classList.remove('open');
    }

    async function openStockDrilldown(itemCode) {
      document.getElementById('stock-modal').classList.add('open');
      document.getElementById('stock-modal-title').innerText = `Stock Ledger: ${itemCode}`;
      const toDate = document.getElementById('input-to-date').value;

      try {
        const data = await fetchFinancialAPI({ report_type: 'stock_ledger_drilldown', item_code: itemCode, to_date: toDate });
        document.getElementById('stock-modal-summary').innerHTML = `
          <span>Total Received IN: <strong style="color:var(--positive-color);">${data.total_in || 0}</strong></span>
          <span>Total Issued OUT: <strong style="color:var(--warning-color);">${data.total_out || 0}</strong></span>
          <span>Running Balance ON HAND: <strong style="color:var(--accent-blue);">${data.ending_qty || 0}</strong></span>
          <span>Stock Valuation: <strong style="color:var(--text-primary);">${fmt(data.ending_value)}</strong></span>
        `;
        let tbody = '';
        (data.entries || []).forEach(e => {
          tbody += `<tr>
            <td style="font-family:var(--font-mono);">${e.posting_date} ${e.posting_time || ''}</td>
            <td><span class="badge badge-neutral">${e.company}</span></td>
            <td>${e.warehouse || '-'}</td>
            <td>${e.voucher_type}</td>
            <td style="font-family:var(--font-mono);font-weight:600;">${e.voucher_no}</td>
            <td class="num-cell" style="color:${e.actual_qty > 0 ? 'var(--positive-color)' : 'var(--warning-color)'};">${fmtQty(e.actual_qty)}</td>
            <td class="num-cell" style="font-weight:700;">${fmtQty(e.qty_after_transaction)}</td>
            <td class="num-cell">${fmt(e.valuation_rate)}</td>
            <td class="num-cell">${fmt(e.stock_value)}</td>
          </tr>`;
        });
        document.getElementById('stock-modal-tbody').innerHTML = tbody || '<tr><td colspan="9" style="text-align:center;padding:20px;">No stock ledger entries found.</td></tr>';
      } catch (e) {
        console.error(e);
      }
    }

    function closeStockDrilldown() {
      document.getElementById('stock-modal').classList.remove('open');
    }

    // ── Theme Toggle ──
    function toggleTheme() {
      const html = document.documentElement;
      const curr = html.getAttribute('data-theme');
      const next = curr === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
    }

    // ── Initial Setup ──
    document.addEventListener('DOMContentLoaded', () => {
      const hash = window.location.hash.replace('#', '');
      if (['pnl', 'balance_sheet', 'cash_flow', 'ar_aging', 'ap_aging', 'general_ledger', 'inventory_audit'].includes(hash)) {
        switchTab(hash);
      } else {
        switchTab('pnl');
      }
    });
  </script>
</body>
</html>
"""

# Write to frappe-bench/apps/vehicle_management/vehicle_management/www/consolidated_financials.html
dest1 = r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\consolidated_financials.html"
with open(dest1, "w", encoding="utf-8") as f:
    f.write(html_code)
print("Saved to", dest1)

# Write to vps_migration/consolidated_financials.html
dest2 = r"c:\Users\josem\erpnext-system\vps_migration\consolidated_financials.html"
with open(dest2, "w", encoding="utf-8") as f:
    f.write(html_code)
print("Saved to", dest2)
