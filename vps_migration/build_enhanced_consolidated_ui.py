# Build and Deploy Enhanced Consolidated Financials UI with Exploded Horizontal Cash Flow and Zero-Overlap Layout

import os, requests, json

BASE_URL = 'http://38.247.138.224:10017'

HTML_TEMPLATE = r'''<!DOCTYPE html>
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
      white-space: nowrap;
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
      white-space: nowrap;
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
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      background: var(--bg-canvas);
    }
    .kpi-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      border-radius: 10px;
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
      min-width: 200px;
      overflow: hidden;
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
      white-space: nowrap;
    }
    .kpi-value {
      font-family: var(--font-mono);
      font-size: 19px;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .kpi-subtext {
      font-size: 11px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
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

    /* ── Tables & Multi-Column Matrix (Anti-Overlap Engine) ── */
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
      position: relative;
    }
    .table-matrix {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
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
    
    /* ── Sticky First Column with High Z-Index & Clean Border ── */
    .table-matrix th.sticky-col,
    .table-matrix td.sticky-col {
      position: sticky;
      left: 0;
      z-index: 25;
      background: var(--bg-surface) !important;
      font-weight: 600;
      color: var(--text-primary);
      border-right: 2px solid var(--border-subtle);
      min-width: 260px;
      max-width: 320px;
      box-shadow: 2px 0 6px rgba(0, 0, 0, 0.4);
    }
    .table-matrix thead th.sticky-col {
      z-index: 35;
      background: var(--bg-surface-elevated) !important;
    }

    /* ── Sticky Total Column on Right ── */
    .table-matrix th.sticky-total,
    .table-matrix td.sticky-total {
      position: sticky;
      right: 0;
      z-index: 25;
      background: var(--bg-surface-elevated) !important;
      font-weight: 700;
      border-left: 2px solid var(--border-subtle);
      text-align: right;
      min-width: 160px;
      box-shadow: -2px 0 6px rgba(0, 0, 0, 0.4);
    }
    .table-matrix thead th.sticky-total {
      z-index: 35;
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
      background: rgba(255, 255, 255, 0.04) !important;
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

    /* Number & Accounting Formatting (Anti-Overlap) */
    .num-cell {
      font-family: var(--font-mono);
      text-align: right;
      font-variant-numeric: tabular-nums;
      cursor: pointer;
      min-width: 130px;
      white-space: nowrap;
      padding: 10px 14px;
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

    /* ── Exploded Horizontal Cash Flow Header Buttons & Styles ── */
    .cf-explode-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 700;
      background: var(--bg-surface-hover);
      border: 1px solid var(--border-strong);
      color: var(--text-primary);
      cursor: pointer;
      margin-left: 6px;
      transition: all 0.15s ease;
    }
    .cf-explode-badge:hover {
      background: var(--accent-solid);
      color: var(--accent-contrast);
      border-color: var(--accent-solid);
    }
    .cf-explode-badge.active {
      background: var(--accent-blue);
      color: #000;
      border-color: var(--accent-blue);
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
      white-space: nowrap;
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
      border: 1px solid var(--badge-neutral-border);
      color: var(--text-secondary);
    }

    /* ── Print Stylesheet ── */
    @media print {
      body {
        background: #fff !important;
        color: #000 !important;
      }
      .top-header, .nav-tabs-bar, .matrix-toolbar, .date-pill-group, .btn-action, .company-dropdown-popover, .kpi-ribbon {
        display: none !important;
      }
      .tab-content {
        display: block !important;
      }
      .matrix-card {
        border: none !important;
        box-shadow: none !important;
      }
      .table-container {
        max-height: none !important;
        overflow: visible !important;
      }
      .table-matrix th, .table-matrix td {
        border: 1px solid #ccc !important;
        color: #000 !important;
        background: #fff !important;
      }
    }
  </style>
</head>
<body>

  <div class="app-shell">
    
    <!-- ── 1. Top Header Bar ── -->
    <header class="top-header">
      <div class="brand-section">
        <div class="brand-logo">CF</div>
        <div class="brand-title-wrap">
          <h1 class="brand-title">Financial Statements &amp; Cash Flow Suite</h1>
          <span class="brand-subtitle">Multi-Company Consolidated Accounting</span>
        </div>
      </div>

      <div class="header-controls">
        <!-- Date Presets -->
        <div class="date-pill-group">
          <button class="date-preset-btn" onclick="setPreset('today')">Today</button>
          <button class="date-preset-btn" onclick="setPreset('mtd')">MTD</button>
          <button class="date-preset-btn" onclick="setPreset('qtd')">QTD</button>
          <button class="date-preset-btn active" onclick="setPreset('ytd')">YTD 2026</button>
          <button class="date-preset-btn" onclick="setPreset('all')">All Time</button>
        </div>

        <!-- Date Range Inputs -->
        <div class="date-inputs">
          <input type="date" id="input-from-date" class="date-input" value="2026-01-01" onchange="reloadActiveTab()">
          <span style="color: var(--text-muted);">to</span>
          <input type="date" id="input-to-date" class="date-input" value="2026-12-31" onchange="reloadActiveTab()">
        </div>

        <!-- Multi-Company Filter Button & Popover -->
        <div style="position: relative;">
          <button class="btn-action" id="btn-company-filter" onclick="toggleCompanyPopover()">
            <span id="company-filter-label">🏢 Companies (All)</span>
            <span style="font-size: 9px;">▾</span>
          </button>

          <div class="company-dropdown-popover" id="company-popover">
            <div class="popover-header">
              <span>Filter Operating Companies</span>
              <span class="badge badge-neutral" id="popover-selected-count">13 selected</span>
            </div>
            <div class="popover-list" id="company-checkboxes-container">
              <!-- Rendered dynamically -->
            </div>
            <div class="popover-footer">
              <div style="display: flex; gap: 6px;">
                <button class="btn-action" style="padding: 4px 8px; font-size: 11px;" onclick="selectAllCompanies(true)">Select All</button>
                <button class="btn-action" style="padding: 4px 8px; font-size: 11px;" onclick="selectAllCompanies(false)">Clear</button>
              </div>
              <button class="btn-action btn-primary" style="padding: 4px 12px; font-size: 11px;" onclick="applyCompanyFilter()">Apply</button>
            </div>
          </div>
        </div>

        <!-- Export & Print Actions -->
        <button class="btn-action" onclick="exportActiveTabToExcel()" title="Export active report to Microsoft Excel (.xlsx)">
          <span>📥 Excel</span>
        </button>
        <button class="btn-action" onclick="window.print()" title="Print / Save PDF">
          <span>🖨️ Print</span>
        </button>
      </div>
    </header>

    <!-- ── 2. Tab Navigation Bar ── -->
    <nav class="nav-tabs-bar">
      <ul class="tabs-list">
        <li class="tab-item active" id="tab-nav-cash_flow" onclick="switchTab('cash_flow')">
          <span>💵 Cash Flow Statement</span>
          <span class="tab-badge" id="badge-cf-tag">Daily/Monthly/Yearly</span>
        </li>
        <li class="tab-item" id="tab-nav-ar_aging" onclick="switchTab('ar_aging')">
          <span>📥 AR Aging Analysis</span>
          <span class="tab-badge" id="badge-ar-count">30-60-90d</span>
        </li>
        <li class="tab-item" id="tab-nav-ap_aging" onclick="switchTab('ap_aging')">
          <span>📤 AP Aging Analysis</span>
          <span class="tab-badge" id="badge-ap-count">30-60-90d</span>
        </li>
        <li class="tab-item" id="tab-nav-pnl" onclick="switchTab('pnl')">
          <span>📈 Profit &amp; Loss</span>
          <span class="tab-badge">Statement</span>
        </li>
        <li class="tab-item" id="tab-nav-balance_sheet" onclick="switchTab('balance_sheet')">
          <span>⚖️ Balance Sheet</span>
          <span class="tab-badge">Financial Position</span>
        </li>
        <li class="tab-item" id="tab-nav-general_ledger" onclick="switchTab('general_ledger')">
          <span>🔍 General Ledger</span>
          <span class="tab-badge">Audit Trail</span>
        </li>
        <li class="tab-item" id="tab-nav-inventory_audit" onclick="switchTab('inventory_audit')">
          <span>📦 Inventory Audit</span>
          <span class="tab-badge">Stock Valuation</span>
        </li>
      </ul>
    </nav>

    <!-- ── 3. KPI Ribbon ── -->
    <section class="kpi-ribbon" id="kpi-ribbon-container">
      <!-- Dynamic KPI Cards injected here -->
    </section>

    <!-- ── 4. Main Content Viewport ── -->
    <main class="content-viewport">
      
      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 1: CASH FLOW STATEMENT (DAILY, MONTHLY, YEARLY & EXPLODED VIEW)
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content active" id="tab-cash_flow">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-cf"><div class="spinner"></div></div>
          
          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>💵 Cash Flow Statement</span>
              <span class="badge badge-info" id="cf-date-badge">Monthly</span>
            </div>

            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <!-- View Switcher -->
              <div class="date-pill-group">
                <button class="date-preset-btn active" id="cf-view-exploded" onclick="setCashFlowView('exploded')">💥 Exploded Time-Series</button>
                <button class="date-preset-btn" id="cf-view-matrix" onclick="setCashFlowView('matrix')">🏢 Company Matrix</button>
                <button class="date-preset-btn" id="cf-view-periods" onclick="setCashFlowView('periods')">📊 Periodic Trends</button>
              </div>

              <!-- Scope selector for Exploded View -->
              <div id="cf-exploded-scope-wrap" style="display: inline-flex; align-items: center; gap: 6px;">
                <select id="cf-exploded-company-select" class="btn-action" style="padding: 4px 8px; font-size: 11px;" onchange="renderCashFlowExplodedTable()">
                  <option value="__CONSOLIDATED__">🏢 Consolidated Group (All Selected)</option>
                  <!-- Populated dynamically -->
                </select>

                <!-- Explode Quick Controls -->
                <div class="date-pill-group">
                  <button class="date-preset-btn" id="cf-explode-level-year" onclick="setExplodeLevel('year')">🏛️ Years</button>
                  <button class="date-preset-btn active" id="cf-explode-level-month" onclick="setExplodeLevel('month')">📆 Months</button>
                  <button class="date-preset-btn" id="cf-explode-level-all" onclick="setExplodeLevel('all_days')">💥 Explode All Days</button>
                </div>
              </div>

              <!-- Search filter -->
              <div class="search-box-wrap">
                <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
                <input type="text" class="search-input" placeholder="Search cash flow activities..." oninput="filterCashFlowRows(this.value)">
              </div>
            </div>
          </div>

          <!-- 1. Exploded Horizontal Time Series Table Container -->
          <div class="table-container" id="cf-exploded-container" style="display: block;">
            <table class="table-matrix" id="table-cf-exploded">
              <thead id="thead-cf-exploded"></thead>
              <tbody id="tbody-cf-exploded"></tbody>
            </table>
          </div>

          <!-- 2. Company Matrix Container -->
          <div class="table-container" id="cf-matrix-container" style="display: none;">
            <table class="table-matrix" id="table-cf-matrix">
              <thead id="thead-cf-matrix"></thead>
              <tbody id="tbody-cf-matrix"></tbody>
            </table>
          </div>

          <!-- 3. Periodic Trends Container -->
          <div class="table-container" id="cf-periods-container" style="display: none;">
            <table class="table-matrix" id="table-cf-periods">
              <thead>
                <tr>
                  <th>Period</th>
                  <th style="text-align: right;">Opening Cash (₱)</th>
                  <th style="text-align: right;">Cash Inflows (₱)</th>
                  <th style="text-align: right;">Cash Outflows (₱)</th>
                  <th style="text-align: right;">Net Cash Flow (₱)</th>
                  <th style="text-align: right;">Ending Cash (₱)</th>
                  <th style="text-align: center;">Transactions</th>
                </tr>
              </thead>
              <tbody id="tbody-cf-periods"></tbody>
            </table>
          </div>

        </div>
      </section>

      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 2: ACCOUNTS RECEIVABLE (AR) AGING ANALYSIS (30, 60, 90 DAYS)
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content" id="tab-ar_aging">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-ar"><div class="spinner"></div></div>

          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📥 Accounts Receivable (AR) Aging Analysis</span>
              <span class="badge badge-info" id="ar-asof-badge">As of Today</span>
            </div>

            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <div class="date-pill-group">
                <button class="date-preset-btn active" id="ar-view-summary" onclick="setARView('summary')">👥 Customer Summary</button>
                <button class="date-preset-btn" id="ar-view-companies" onclick="setARView('companies')">🏢 Branch Matrix</button>
                <button class="date-preset-btn" id="ar-view-details" onclick="setARView('details')">📄 Invoices Breakdown</button>
              </div>

              <div class="search-box-wrap">
                <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
                <input type="text" class="search-input" placeholder="Search customer or invoice..." oninput="filterARRows(this.value)">
              </div>
            </div>
          </div>

          <!-- AR Customer Summary Table -->
          <div class="table-container" id="ar-summary-container">
            <table class="table-matrix" id="table-ar-summary">
              <thead>
                <tr>
                  <th class="sticky-col">Customer Name</th>
                  <th>Primary Branch</th>
                  <th style="text-align: right;">Current (₱)</th>
                  <th style="text-align: right;">1 - 30 Days (₱)</th>
                  <th style="text-align: right;">31 - 60 Days (₱)</th>
                  <th style="text-align: right;">61 - 90 Days (₱)</th>
                  <th style="text-align: right;">90+ Days Overdue (₱)</th>
                  <th class="sticky-total">Total Outstanding (₱)</th>
                  <th style="text-align: center;">Invoices</th>
                </tr>
              </thead>
              <tbody id="tbody-ar-summary"></tbody>
            </table>
          </div>

          <!-- AR Company Summary Table -->
          <div class="table-container" id="ar-companies-container" style="display: none;">
            <table class="table-matrix" id="table-ar-companies">
              <thead>
                <tr>
                  <th class="sticky-col">Operating Branch</th>
                  <th>Code</th>
                  <th style="text-align: right;">Current (₱)</th>
                  <th style="text-align: right;">1 - 30 Days (₱)</th>
                  <th style="text-align: right;">31 - 60 Days (₱)</th>
                  <th style="text-align: right;">61 - 90 Days (₱)</th>
                  <th style="text-align: right;">90+ Days Overdue (₱)</th>
                  <th class="sticky-total">Total AR Balance (₱)</th>
                  <th style="text-align: center;">Active Invoices</th>
                </tr>
              </thead>
              <tbody id="tbody-ar-companies"></tbody>
            </table>
          </div>

          <!-- AR Details Table -->
          <div class="table-container" id="ar-details-container" style="display: none;">
            <table class="table-matrix" id="table-ar-details">
              <thead>
                <tr>
                  <th>Invoice No</th>
                  <th>Customer</th>
                  <th>Branch</th>
                  <th>Posting Date</th>
                  <th>Due Date (Terms)</th>
                  <th style="text-align: center;">Overdue</th>
                  <th style="text-align: center;">Aging Bucket</th>
                  <th style="text-align: right;">Grand Total (₱)</th>
                  <th style="text-align: right;">Outstanding (₱)</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="tbody-ar-details"></tbody>
            </table>
          </div>

        </div>
      </section>

      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 3: ACCOUNTS PAYABLE (AP) AGING ANALYSIS (30, 60, 90 DAYS)
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content" id="tab-ap_aging">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-ap"><div class="spinner"></div></div>

          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📤 Accounts Payable (AP) Aging Analysis</span>
              <span class="badge badge-warning" id="ap-asof-badge">As of Today</span>
            </div>

            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <div class="date-pill-group">
                <button class="date-preset-btn active" id="ap-view-summary" onclick="setAPView('summary')">🏢 Supplier Summary</button>
                <button class="date-preset-btn" id="ap-view-companies" onclick="setAPView('companies')">🏢 Branch Matrix</button>
                <button class="date-preset-btn" id="ap-view-details" onclick="setAPView('details')">📄 Bills Breakdown</button>
              </div>

              <div class="search-box-wrap">
                <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
                <input type="text" class="search-input" placeholder="Search supplier or bill..." oninput="filterAPRows(this.value)">
              </div>
            </div>
          </div>

          <!-- AP Supplier Summary Table -->
          <div class="table-container" id="ap-summary-container">
            <table class="table-matrix" id="table-ap-summary">
              <thead>
                <tr>
                  <th class="sticky-col">Supplier Name</th>
                  <th>Primary Branch</th>
                  <th style="text-align: right;">Current (₱)</th>
                  <th style="text-align: right;">1 - 30 Days (₱)</th>
                  <th style="text-align: right;">31 - 60 Days (₱)</th>
                  <th style="text-align: right;">61 - 90 Days (₱)</th>
                  <th style="text-align: right;">90+ Days Overdue (₱)</th>
                  <th class="sticky-total">Total Outstanding (₱)</th>
                  <th style="text-align: center;">Bills</th>
                </tr>
              </thead>
              <tbody id="tbody-ap-summary"></tbody>
            </table>
          </div>

          <!-- AP Company Summary Table -->
          <div class="table-container" id="ap-companies-container" style="display: none;">
            <table class="table-matrix" id="table-ap-companies">
              <thead>
                <tr>
                  <th class="sticky-col">Operating Branch</th>
                  <th>Code</th>
                  <th style="text-align: right;">Current (₱)</th>
                  <th style="text-align: right;">1 - 30 Days (₱)</th>
                  <th style="text-align: right;">31 - 60 Days (₱)</th>
                  <th style="text-align: right;">61 - 90 Days (₱)</th>
                  <th style="text-align: right;">90+ Days Overdue (₱)</th>
                  <th class="sticky-total">Total AP Balance (₱)</th>
                  <th style="text-align: center;">Active Bills</th>
                </tr>
              </thead>
              <tbody id="tbody-ap-companies"></tbody>
            </table>
          </div>

          <!-- AP Details Table -->
          <div class="table-container" id="ap-details-container" style="display: none;">
            <table class="table-matrix" id="table-ap-details">
              <thead>
                <tr>
                  <th>Purchase Bill No</th>
                  <th>Supplier</th>
                  <th>Branch</th>
                  <th>Bill Date</th>
                  <th>Due Date (Terms)</th>
                  <th style="text-align: center;">Overdue</th>
                  <th style="text-align: center;">Aging Bucket</th>
                  <th style="text-align: right;">Total Amount (₱)</th>
                  <th style="text-align: right;">Outstanding (₱)</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="tbody-ap-details"></tbody>
            </table>
          </div>

        </div>
      </section>

      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 4: PROFIT & LOSS STATEMENT
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content" id="tab-pnl">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-pnl"><div class="spinner"></div></div>

          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📈 Consolidated Profit &amp; Loss Statement</span>
              <span class="badge badge-success" id="pnl-date-badge">2026-01-01 to 2026-12-31</span>
            </div>
            <div class="search-box-wrap">
              <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
              <input type="text" class="search-input" placeholder="Search accounts..." oninput="filterTableRows('table-pnl', this.value)">
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

      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 5: BALANCE SHEET
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content" id="tab-balance_sheet">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-bs"><div class="spinner"></div></div>

          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>⚖️ Consolidated Statement of Financial Position</span>
              <span class="badge badge-info" id="bs-date-badge">As of 2026-12-31</span>
            </div>
            <div class="search-box-wrap">
              <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
              <input type="text" class="search-input" placeholder="Search asset, liability, equity..." oninput="filterTableRows('table-bs', this.value)">
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

      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 6: GENERAL LEDGER EXPLORER
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content" id="tab-general_ledger">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-gl"><div class="spinner"></div></div>

          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>🔍 Multi-Company General Ledger Audit Trail</span>
              <span class="badge badge-neutral" id="gl-record-badge">0 Entries</span>
            </div>

            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <select id="select-gl-voucher-type" class="btn-action" style="padding: 4px 8px; font-size: 11px;" onchange="loadGLData()">
                <option value="">All Voucher Types</option>
                <option value="Sales Invoice">Sales Invoice</option>
                <option value="POS Invoice">POS Invoice</option>
                <option value="Purchase Invoice">Purchase Invoice</option>
                <option value="Payment Entry">Payment Entry</option>
                <option value="Journal Entry">Journal Entry</option>
                <option value="Stock Entry">Stock Entry</option>
              </select>

              <div class="search-box-wrap">
                <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
                <input type="text" class="search-input" id="input-gl-search" placeholder="Search voucher # or account..." onkeydown="if(event.key==='Enter') loadGLData()">
              </div>
            </div>
          </div>

          <div class="table-container">
            <table class="table-matrix" id="table-gl">
              <thead>
                <tr>
                  <th>Posting Date</th>
                  <th>Branch</th>
                  <th>Voucher Type</th>
                  <th>Voucher No</th>
                  <th>Account</th>
                  <th>Against Account</th>
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

      <!-- ═══════════════════════════════════════════════════════════════════════
           TAB 7: INVENTORY AUDIT & STOCK VALUATION
           ═══════════════════════════════════════════════════════════════════════ -->
      <section class="tab-content" id="tab-inventory_audit">
        <div class="matrix-card" style="position: relative;">
          <div class="loading-overlay" id="loading-inv"><div class="spinner"></div></div>

          <div class="matrix-toolbar">
            <div class="matrix-title">
              <span>📦 Consolidated Stock Valuation &amp; Inventory Audit</span>
              <span class="badge badge-neutral" id="inv-count-badge">0 Items</span>
            </div>
            <div class="search-box-wrap">
              <span style="color: var(--text-muted); font-size: 11px;">🔍</span>
              <input type="text" class="search-input" id="input-inv-search" placeholder="Search item code or name..." onkeydown="if(event.key==='Enter') loadInventoryData()">
            </div>
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

    <!-- ── 5. Drilldown Modal ── -->
    <div class="modal-overlay" id="modal-drilldown">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title" id="drilldown-title">Account GL Drilldown</h3>
          <button class="btn-action" onclick="closeDrilldown()">✕</button>
        </div>
        <div class="modal-body">
          <table class="table-matrix" style="width: 100%;">
            <thead>
              <tr>
                <th>Date</th>
                <th>Branch</th>
                <th>Voucher Type</th>
                <th>Voucher No</th>
                <th>Against</th>
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

    <!-- ── 6. Stock Ledger Drilldown Modal ── -->
    <div class="modal-overlay" id="modal-stock-drilldown">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title" id="stock-modal-title">Item Stock Movements</h3>
          <button class="btn-action" onclick="closeStockDrilldown()">✕</button>
        </div>
        <div class="modal-body">
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
    let activeTab = 'cash_flow';
    let allAvailableCompanies = [];
    let selectedCompanies = [];
    let cfView = 'exploded';
    let explodeLevel = 'month'; // 'year', 'month', 'all_days'
    let explodedMonthMap = {}; // Tracks which specific months are exploded to days
    let explodedYearMap = {};  // Tracks which specific years are exploded to months
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
      populateExplodedCompanySelect();
    }

    function populateExplodedCompanySelect() {
      const sel = document.getElementById('cf-exploded-company-select');
      if (!sel) return;
      const curr = sel.value;
      let opts = `<option value="__CONSOLIDATED__">🏢 Consolidated Group (All Selected)</option>`;
      allAvailableCompanies.forEach(c => {
        opts += `<option value="${c}">${c}</option>`;
      });
      sel.innerHTML = opts;
      if (curr && allAvailableCompanies.includes(curr)) {
        sel.value = curr;
      }
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

      if (tabId === 'cash_flow') {
        document.getElementById('loading-cf').classList.add('active');
        document.getElementById('cf-date-badge').innerText = `${fromDate} to ${toDate}`;
        try {
          const data = await fetchFinancialAPI({ report_type: 'cash_flow', from_date: fromDate, to_date: toDate, period: 'monthly' });
          currentData.cash_flow = data;
          if (data.all_companies && allAvailableCompanies.length === 0) {
            renderCompanyCheckboxes(data.all_companies);
          }
          renderCashFlowSuite(data);
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
      } else if (tabId === 'pnl') {
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

      if (activeTab === 'cash_flow' && currentData.cash_flow) {
        const d = currentData.cash_flow;
        const s = d.summary || {};
        container.innerHTML = `
          <div class="kpi-card" onclick="switchTab('cash_flow')">
            <div class="kpi-label"><span>Beginning Cash Balance</span><span class="badge badge-neutral">Opening</span></div>
            <div class="kpi-value">${fmtPlain(s.opening_consolidated)}</div>
            <div class="kpi-subtext">Cash & bank prior to start</div>
          </div>
          <div class="kpi-card" onclick="switchTab('cash_flow')">
            <div class="kpi-label"><span>Total Cash Inflows</span><span class="badge badge-success">Collections</span></div>
            <div class="kpi-value" style="color: var(--positive-color);">${fmtPlain(s.inflows_consolidated)}</div>
            <div class="kpi-subtext">Customer & POS receipts</div>
          </div>
          <div class="kpi-card" onclick="switchTab('cash_flow')">
            <div class="kpi-label"><span>Total Cash Outflows</span><span class="badge badge-warning">Disbursements</span></div>
            <div class="kpi-value" style="color: var(--warning-color);">${fmtPlain(s.outflows_consolidated)}</div>
            <div class="kpi-subtext">Supplier & operating expenses</div>
          </div>
          <div class="kpi-card" onclick="switchTab('cash_flow')">
            <div class="kpi-label"><span>Net Cash Flow</span><span class="badge ${s.net_consolidated >= 0 ? 'badge-success' : 'badge-danger'}">${s.net_consolidated >= 0 ? '+ Positive' : '- Deficit'}</span></div>
            <div class="kpi-value" style="color: ${s.net_consolidated >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmtPlain(s.net_consolidated)}</div>
            <div class="kpi-subtext">Period net movement</div>
          </div>
          <div class="kpi-card" onclick="switchTab('cash_flow')">
            <div class="kpi-label"><span>Ending Cash Balance</span><span class="badge badge-info">Closing</span></div>
            <div class="kpi-value" style="color: var(--accent-blue);">${fmtPlain(s.ending_consolidated)}</div>
            <div class="kpi-subtext">Running cash on hand</div>
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
      } else if (activeTab === 'pnl' && currentData.pnl) {
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
      }
    }

    // ── Cash Flow Suite Master Dispatcher ──
    function setCashFlowView(view) {
      cfView = view;
      document.querySelectorAll('#tab-cash_flow .date-pill-group button[id^="cf-view-"]').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById(`cf-view-${view}`);
      if (activeBtn) activeBtn.classList.add('active');

      document.getElementById('cf-exploded-container').style.display = view === 'exploded' ? 'block' : 'none';
      document.getElementById('cf-matrix-container').style.display = view === 'matrix' ? 'block' : 'none';
      document.getElementById('cf-periods-container').style.display = view === 'periods' ? 'block' : 'none';
      document.getElementById('cf-exploded-scope-wrap').style.display = view === 'exploded' ? 'inline-flex' : 'none';

      if (currentData.cash_flow) {
        if (view === 'exploded') renderCashFlowExplodedTable();
        else if (view === 'matrix') renderCashFlowMatrixTable(currentData.cash_flow);
        else if (view === 'periods') renderCashFlowPeriodsTable(currentData.cash_flow);
      }
    }

    function setExplodeLevel(level) {
      explodeLevel = level;
      document.querySelectorAll('#cf-exploded-scope-wrap .date-pill-group button').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById(`cf-explode-level-${level === 'all_days' ? 'all' : level}`);
      if (activeBtn) activeBtn.classList.add('active');

      const data = currentData.cash_flow;
      if (!data || !data.hierarchy) return;

      const years = data.hierarchy.years || [];
      if (level === 'year') {
        explodedYearMap = {};
        explodedMonthMap = {};
      } else if (level === 'month') {
        years.forEach(y => { explodedYearMap[y.period_key] = true; });
        explodedMonthMap = {};
      } else if (level === 'all_days') {
        years.forEach(y => {
          explodedYearMap[y.period_key] = true;
          (y.months || []).forEach(m => {
            explodedMonthMap[m.period_key] = true;
          });
        });
      }
      renderCashFlowExplodedTable();
    }

    function toggleExplodeYear(yKey) {
      explodedYearMap[yKey] = !explodedYearMap[yKey];
      renderCashFlowExplodedTable();
    }

    function toggleExplodeMonth(mKey) {
      explodedMonthMap[mKey] = !explodedMonthMap[mKey];
      renderCashFlowExplodedTable();
    }

    function renderCashFlowSuite(data) {
      // Default: ensure years are expanded if month or all_days
      if (explodeLevel === 'month' || explodeLevel === 'all_days') {
        (data.hierarchy?.years || []).forEach(y => {
          explodedYearMap[y.period_key] = true;
          if (explodeLevel === 'all_days') {
            (y.months || []).forEach(m => { explodedMonthMap[m.period_key] = true; });
          }
        });
      }
      renderCashFlowExplodedTable();
      renderCashFlowMatrixTable(data);
      renderCashFlowPeriodsTable(data);
    }

    // ── 1. EXPLODED HORIZONTAL TIME SERIES CASH FLOW RENDERER ──
    function renderCashFlowExplodedTable() {
      const data = currentData.cash_flow;
      if (!data || !data.hierarchy) return;

      const targetCo = document.getElementById('cf-exploded-company-select')?.value || '__CONSOLIDATED__';
      const isConsolidated = targetCo === '__CONSOLIDATED__';

      const hierarchy = data.hierarchy;
      const years = hierarchy.years || [];

      // Determine active horizontal columns
      let columns = []; // [{ key, label, type: 'year'|'month'|'day', refObj, parentYearKey, parentMonthKey }]

      years.forEach(y => {
        const isYearExploded = explodedYearMap[y.period_key];
        if (!isYearExploded) {
          // Column is the Year
          columns.push({
            key: y.period_key,
            label: y.period_label,
            type: 'year',
            refObj: y,
            canExplode: true,
            isExploded: false
          });
        } else {
          // Year is exploded into its months
          const months = y.months || [];
          months.forEach(m => {
            const isMonthExploded = explodedMonthMap[m.period_key];
            if (!isMonthExploded) {
              // Column is the Month
              columns.push({
                key: m.period_key,
                label: m.month_abbr || m.period_label,
                fullLabel: m.period_label,
                type: 'month',
                refObj: m,
                parentYearKey: y.period_key,
                canExplode: (m.days && m.days.length > 0),
                isExploded: false
              });
            } else {
              // Month is exploded into its individual Days!
              const days = m.days || [];
              days.forEach(d => {
                columns.push({
                  key: d.period_key,
                  label: d.period_label,
                  fullLabel: d.full_label || d.period_label,
                  type: 'day',
                  refObj: d,
                  parentYearKey: y.period_key,
                  parentMonthKey: m.period_key,
                  canExplode: false,
                  isExploded: true
                });
              });
            }
          });
        }
      });

      // Build 2-Tier Header
      // Tier 1: Breadcrumb groupings (Year / Month badges)
      // Tier 2: Column Headers
      let theadHtml = `<tr>
        <th class="sticky-col" style="vertical-align: bottom;">
          <div>Financial Line Item</div>
          <div style="font-size: 10px; color: var(--text-muted); font-weight: 500;">
            ${isConsolidated ? 'Consolidated Group' : targetCo}
          </div>
        </th>`;

      columns.forEach(col => {
        let badgeHtml = '';
        if (col.type === 'year') {
          badgeHtml = `<button class="cf-explode-badge" onclick="toggleExplodeYear('${col.key}')" title="Explode into Months">➕ Months</button>`;
        } else if (col.type === 'month') {
          badgeHtml = `<button class="cf-explode-badge" onclick="toggleExplodeMonth('${col.key}')" title="Explode into Days">💥 Days</button>`;
        } else if (col.type === 'day') {
          badgeHtml = `<span style="font-size: 9px; color: var(--accent-blue); font-weight: 700;">● Day</span>`;
        }

        theadHtml += `<th style="text-align: right; min-width: ${col.type === 'day' ? '120px' : '140px'};">
          <div style="display: flex; align-items: center; justify-content: flex-end; gap: 4px;">
            <span>${col.label}</span>
            ${badgeHtml}
          </div>
        </th>`;
      });

      theadHtml += `<th class="sticky-total">Total Consolidated (PHP)</th></tr>`;
      document.getElementById('thead-cf-exploded').innerHTML = theadHtml;

      // Extract values helper
      function getVal(obj, path, cat = null) {
        if (!obj) return 0;
        if (cat) {
          if (path === 'inflows') {
            const br = obj.inflow_breakdown && obj.inflow_breakdown[cat];
            if (!br) return 0;
            return isConsolidated ? Object.values(br).reduce((a,b)=>a+b,0) : (br[targetCo] || 0);
          } else if (path === 'outflows') {
            const br = obj.outflow_breakdown && obj.outflow_breakdown[cat];
            if (!br) return 0;
            return isConsolidated ? Object.values(br).reduce((a,b)=>a+b,0) : (br[targetCo] || 0);
          }
        }
        if (path === 'opening') {
          return isConsolidated ? (obj.opening_total || 0) : ((obj.opening_balance && obj.opening_balance[targetCo]) || 0);
        }
        if (path === 'inflows_total') {
          return isConsolidated ? (obj.inflow_total || 0) : ((obj.inflows && obj.inflows[targetCo]) || 0);
        }
        if (path === 'outflows_total') {
          return isConsolidated ? (obj.outflow_total || 0) : ((obj.outflows && obj.outflows[targetCo]) || 0);
        }
        if (path === 'net') {
          return isConsolidated ? (obj.net_total || 0) : ((obj.net && obj.net[targetCo]) || 0);
        }
        if (path === 'ending') {
          return isConsolidated ? (obj.ending_total || 0) : ((obj.ending_balance && obj.ending_balance[targetCo]) || 0);
        }
        return 0;
      }

      const summary = data.summary || {};
      const totOpening = isConsolidated ? (summary.opening_consolidated || 0) : (summary.opening_balance?.[targetCo] || 0);
      const totInflows = isConsolidated ? (summary.inflows_consolidated || 0) : (summary.inflows_total?.[targetCo] || 0);
      const totOutflows = isConsolidated ? (summary.outflows_consolidated || 0) : (summary.outflows_total?.[targetCo] || 0);
      const totNet = isConsolidated ? (summary.net_consolidated || 0) : (summary.net_cash_flow?.[targetCo] || 0);
      const totEnding = isConsolidated ? (summary.ending_consolidated || 0) : (summary.ending_balance?.[targetCo] || 0);

      const inCats = data.inflow_categories || {};
      const outCats = data.outflow_categories || {};

      let tbodyHtml = '';

      // 1. Beginning Balance Row
      tbodyHtml += `<tr class="row-section-total">
        <td class="sticky-col"><strong>Beginning Cash &amp; Bank Balance</strong></td>`;
      columns.forEach(col => {
        tbodyHtml += `<td class="num-cell">${fmt(getVal(col.refObj, 'opening'))}</td>`;
      });
      tbodyHtml += `<td class="sticky-total">${fmt(totOpening)}</td></tr>`;

      // 2. Inflows Section
      tbodyHtml += `<tr class="row-section-header"><td colspan="${columns.length + 2}">Operating Cash Inflows &amp; Collections</td></tr>`;
      Object.keys(inCats).forEach(k => {
        const cat = inCats[k];
        tbodyHtml += `<tr><td class="sticky-col" style="padding-left: 20px;">↳ ${cat.label}</td>`;
        columns.forEach(col => {
          tbodyHtml += `<td class="num-cell">${fmt(getVal(col.refObj, 'inflows', k))}</td>`;
        });
        const catTot = isConsolidated ? (cat.total || 0) : (cat.companies?.[targetCo] || 0);
        tbodyHtml += `<td class="sticky-total">${fmt(catTot)}</td></tr>`;
      });
      // Total Inflows
      tbodyHtml += `<tr class="row-section-total">
        <td class="sticky-col"><strong>Total Cash Inflows</strong></td>`;
      columns.forEach(col => {
        tbodyHtml += `<td class="num-cell" style="color: var(--positive-color); font-weight: 700;">${fmt(getVal(col.refObj, 'inflows_total'))}</td>`;
      });
      tbodyHtml += `<td class="sticky-total" style="color: var(--positive-color); font-weight: 800;">${fmt(totInflows)}</td></tr>`;

      // 3. Outflows Section
      tbodyHtml += `<tr class="row-section-header"><td colspan="${columns.length + 2}">Operating Cash Outflows &amp; Disbursements</td></tr>`;
      Object.keys(outCats).forEach(k => {
        const cat = outCats[k];
        tbodyHtml += `<tr><td class="sticky-col" style="padding-left: 20px;">↳ ${cat.label}</td>`;
        columns.forEach(col => {
          tbodyHtml += `<td class="num-cell">${fmt(getVal(col.refObj, 'outflows', k))}</td>`;
        });
        const catTot = isConsolidated ? (cat.total || 0) : (cat.companies?.[targetCo] || 0);
        tbodyHtml += `<td class="sticky-total">${fmt(catTot)}</td></tr>`;
      });
      // Total Outflows
      tbodyHtml += `<tr class="row-section-total">
        <td class="sticky-col"><strong>Total Cash Outflows</strong></td>`;
      columns.forEach(col => {
        tbodyHtml += `<td class="num-cell" style="color: var(--warning-color); font-weight: 700;">${fmt(getVal(col.refObj, 'outflows_total'))}</td>`;
      });
      tbodyHtml += `<td class="sticky-total" style="color: var(--warning-color); font-weight: 800;">${fmt(totOutflows)}</td></tr>`;

      // 4. Net Cash Flow Row
      tbodyHtml += `<tr class="row-section-total" style="border-top: 2px solid var(--border-highlight);">
        <td class="sticky-col"><strong>Net Cash Flow for Period</strong></td>`;
      columns.forEach(col => {
        const netVal = getVal(col.refObj, 'net');
        tbodyHtml += `<td class="num-cell" style="font-weight: 700; color: ${netVal >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmt(netVal)}</td>`;
      });
      tbodyHtml += `<td class="sticky-total" style="font-weight: 800; color: ${totNet >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmt(totNet)}</td></tr>`;

      // 5. Ending Cash Balance Row
      tbodyHtml += `<tr class="row-grand-total">
        <td class="sticky-col"><strong>Ending Cash &amp; Bank Balance</strong></td>`;
      columns.forEach(col => {
        tbodyHtml += `<td class="num-cell" style="color: var(--accent-blue); font-weight: 800;">${fmt(getVal(col.refObj, 'ending'))}</td>`;
      });
      tbodyHtml += `<td class="sticky-total" style="color: var(--accent-blue); font-weight: 900;">${fmt(totEnding)}</td></tr>`;

      document.getElementById('tbody-cf-exploded').innerHTML = tbodyHtml;
    }

    // ── 2. COMPANY MATRIX CASH FLOW RENDERER ──
    function renderCashFlowMatrixTable(data) {
      const companies = data.companies || [];
      const meta = data.company_meta || {};
      const summary = data.summary || {};
      const inflows = data.inflow_categories || {};
      const outflows = data.outflow_categories || {};

      let thead = '<tr><th class="sticky-col">Cash Flow Activities</th>';
      companies.forEach(c => {
        const abbr = meta[c]?.abbr || c.substring(0, 4);
        thead += `<th style="text-align: right;" title="${c}">${abbr}</th>`;
      });
      thead += '<th class="sticky-total">Consolidated (PHP)</th></tr>';
      document.getElementById('thead-cf-matrix').innerHTML = thead;

      let tbody = '';
      tbody += `<tr class="row-section-total">
        <td class="sticky-col"><strong>Beginning Cash &amp; Bank Balance</strong></td>`;
      companies.forEach(c => {
        tbody += `<td class="num-cell">${fmt((summary.opening_balance && summary.opening_balance[c]) || 0)}</td>`;
      });
      tbody += `<td class="sticky-total">${fmt(summary.opening_consolidated || 0)}</td></tr>`;

      tbody += `<tr class="row-section-header"><td colspan="${companies.length + 2}">Operating Cash Inflows &amp; Receipts</td></tr>`;
      Object.keys(inflows).forEach(k => {
        const cat = inflows[k];
        tbody += `<tr><td class="sticky-col">↳ ${cat.label}</td>`;
        companies.forEach(c => {
          tbody += `<td class="num-cell">${fmt((cat.companies && cat.companies[c]) || 0)}</td>`;
        });
        tbody += `<td class="sticky-total">${fmt(cat.total || 0)}</td></tr>`;
      });
      tbody += `<tr class="row-section-total"><td class="sticky-col"><strong>Total Cash Inflows</strong></td>`;
      companies.forEach(c => {
        tbody += `<td class="num-cell" style="color: var(--positive-color);">${fmt((summary.inflows_total && summary.inflows_total[c]) || 0)}</td>`;
      });
      tbody += `<td class="sticky-total" style="color: var(--positive-color);">${fmt(summary.inflows_consolidated || 0)}</td></tr>`;

      tbody += `<tr class="row-section-header"><td colspan="${companies.length + 2}">Operating Cash Outflows &amp; Disbursements</td></tr>`;
      Object.keys(outflows).forEach(k => {
        const cat = outflows[k];
        tbody += `<tr><td class="sticky-col">↳ ${cat.label}</td>`;
        companies.forEach(c => {
          tbody += `<td class="num-cell">${fmt((cat.companies && cat.companies[c]) || 0)}</td>`;
        });
        tbody += `<td class="sticky-total">${fmt(cat.total || 0)}</td></tr>`;
      });
      tbody += `<tr class="row-section-total"><td class="sticky-col"><strong>Total Cash Outflows</strong></td>`;
      companies.forEach(c => {
        tbody += `<td class="num-cell" style="color: var(--warning-color);">${fmt((summary.outflows_total && summary.outflows_total[c]) || 0)}</td>`;
      });
      tbody += `<td class="sticky-total" style="color: var(--warning-color);">${fmt(summary.outflows_consolidated || 0)}</td></tr>`;

      tbody += `<tr class="row-section-total" style="border-top: 2px solid var(--border-highlight);">
        <td class="sticky-col"><strong>Net Cash Flow for Period</strong></td>`;
      companies.forEach(c => {
        tbody += `<td class="num-cell" style="font-weight: 700;">${fmt((summary.net_cash_flow && summary.net_cash_flow[c]) || 0)}</td>`;
      });
      tbody += `<td class="sticky-total" style="font-weight: 800;">${fmt(summary.net_consolidated || 0)}</td></tr>`;

      tbody += `<tr class="row-grand-total">
        <td class="sticky-col"><strong>Ending Cash &amp; Bank Balance</strong></td>`;
      companies.forEach(c => {
        tbody += `<td class="num-cell" style="color: var(--accent-blue);">${fmt((summary.ending_balance && summary.ending_balance[c]) || 0)}</td>`;
      });
      tbody += `<td class="sticky-total" style="color: var(--accent-blue);">${fmt(summary.ending_consolidated || 0)}</td></tr>`;

      document.getElementById('tbody-cf-matrix').innerHTML = tbody;
    }

    // ── 3. PERIODIC TRENDS CASH FLOW RENDERER ──
    function renderCashFlowPeriodsTable(data) {
      const periods = data.periods || [];
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
      filterTableRows('table-cf-exploded', query);
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

      let dbody = '';
      bills.forEach(b => {
        let bBadge = '<span class="badge badge-success">Current</span>';
        if (b.bucket === 'range_1_30') bBadge = '<span class="badge badge-warning">1-30d</span>';
        else if (b.bucket === 'range_31_60') bBadge = '<span class="badge badge-warning" style="background:rgba(249,115,22,0.15);color:#f97316;">31-60d</span>';
        else if (b.bucket === 'range_61_90') bBadge = '<span class="badge badge-danger">61-90d</span>';
        else if (b.bucket === 'range_90_plus') bBadge = '<span class="badge badge-danger" style="font-weight:800;">90+d</span>';

        dbody += `<tr>
          <td style="font-family:var(--font-mono);font-weight:600;">${b.name}</td>
          <td>${b.supplier_name}</td>
          <td><span class="badge badge-neutral">${b.company_abbr}</span></td>
          <td style="font-family:var(--font-mono);">${b.posting_date}</td>
          <td style="font-family:var(--font-mono);">${b.due_date} <small style="color:var(--text-muted)">(${b.terms})</small></td>
          <td style="text-align: center; font-family:var(--font-mono); font-weight:700; color:${b.days_overdue > 0 ? 'var(--negative-color)' : 'var(--positive-color)'};">${b.days_overdue} d</td>
          <td style="text-align: center;">${bBadge}</td>
          <td class="num-cell">${fmt(b.grand_total)}</td>
          <td class="num-cell" style="font-weight:700;">${fmt(b.amount_aged)}</td>
          <td><span class="badge ${b.status === 'Paid' ? 'badge-success' : 'badge-neutral'}">${b.status}</span></td>
        </tr>`;
      });
      document.getElementById('tbody-ap-details').innerHTML = dbody;
    }

    function filterAPRows(query) {
      filterTableRows('table-ap-summary', query);
      filterTableRows('table-ap-companies', query);
      filterTableRows('table-ap-details', query);
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

    // ── General Ledger Loader ──
    async function loadGLData() {
      document.getElementById('loading-gl').classList.add('active');
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      const vType = document.getElementById('select-gl-voucher-type')?.value;
      const search = document.getElementById('input-gl-search')?.value;

      try {
        const data = await fetchFinancialAPI({
          report_type: 'general_ledger',
          from_date: fromDate,
          to_date: toDate,
          voucher_type: vType || '',
          search_text: search || '',
          page_length: 150
        });
        currentData.general_ledger = data;
        document.getElementById('gl-record-badge').innerText = `${data.total_records || 0} Entries`;

        let tbody = '';
        (data.rows || []).forEach(r => {
          tbody += `<tr>
            <td style="font-family: var(--font-mono);">${r.posting_date}</td>
            <td><span class="badge badge-neutral">${r.company}</span></td>
            <td><span class="badge badge-info">${r.voucher_type}</span></td>
            <td style="font-family: var(--font-mono); font-weight: 600;">${r.voucher_no}</td>
            <td>${r.account}</td>
            <td style="color: var(--text-muted);">${r.against || '-'}</td>
            <td class="num-cell">${fmt(r.debit)}</td>
            <td class="num-cell">${fmt(r.credit)}</td>
            <td style="color: var(--text-muted); max-width: 250px; overflow: hidden; text-overflow: ellipsis;">${r.remarks || '-'}</td>
          </tr>`;
        });
        document.getElementById('tbody-gl').innerHTML = tbody;
      } catch (e) {
        console.error(e);
      } finally {
        document.getElementById('loading-gl').classList.remove('active');
      }
    }

    // ── Inventory Audit Loader ──
    async function loadInventoryData() {
      document.getElementById('loading-inv').classList.add('active');
      const toDate = document.getElementById('input-to-date').value;
      const search = document.getElementById('input-inv-search')?.value;

      try {
        const data = await fetchFinancialAPI({
          report_type: 'inventory_audit',
          to_date: toDate,
          search_text: search || ''
        });
        currentData.inventory_audit = data;
        const companies = data.companies || [];
        const meta = data.company_meta || {};
        const rows = data.rows || [];
        const totals = data.totals || {};

        document.getElementById('inv-count-badge').innerText = `${rows.length} Items`;

        let thead = `<tr>
          <th class="sticky-col">Item Details</th>
          <th>UOM</th>
          <th style="text-align: right;">Valuation (₱)</th>`;
        companies.forEach(c => {
          const abbr = meta[c]?.abbr || c.substring(0, 4);
          thead += `<th style="text-align: right;" title="${c}">${abbr} (Qty)</th>`;
        });
        thead += `<th style="text-align: right;">Total Balance Qty</th>
          <th class="sticky-total">Total Valuation (PHP)</th>
        </tr>`;
        document.getElementById('thead-inv').innerHTML = thead;

        let tbody = '';
        rows.forEach(r => {
          tbody += `<tr>
            <td class="sticky-col">
              <div style="font-weight: 600;">${r.item_code}</div>
              <div style="font-size: 11px; color: var(--text-muted);">${r.item_name}</div>
            </td>
            <td><span class="badge badge-neutral">${r.stock_uom}</span></td>
            <td class="num-cell">${fmt(r.avg_valuation_rate)}</td>`;
          companies.forEach(c => {
            const q = r.companies_qty[c] || 0;
            tbody += `<td class="num-cell" onclick="openStockDrilldown('${r.item_code}', '${c}')">${fmtQty(q)}</td>`;
          });
          tbody += `<td class="num-cell" style="font-weight: 700;">${fmtQty(r.total_qty, r.stock_uom)}</td>
            <td class="sticky-total">${fmt(r.total_val)}</td>
          </tr>`;
        });

        tbody += `<tr class="row-grand-total">
          <td class="sticky-col">Grand Total Inventory (${rows.length} Items)</td>
          <td>-</td>
          <td class="num-cell">-</td>`;
        companies.forEach(c => {
          const cq = totals.company_qty?.[c] || 0;
          tbody += `<td class="num-cell">${fmtQty(cq)}</td>`;
        });
        tbody += `<td class="num-cell" style="font-weight: 800;">${fmtQty(totals.total_qty || 0)}</td>
          <td class="sticky-total" style="color: var(--positive-color); font-weight: 900;">${fmt(totals.total_val || 0)}</td>
        </tr>`;
        document.getElementById('tbody-inv').innerHTML = tbody;
      } catch (e) {
        console.error(e);
      } finally {
        document.getElementById('loading-inv').classList.remove('active');
      }
    }

    // ── Table Row Filter Utility ──
    function filterTableRows(tableId, query) {
      const q = (query || '').toLowerCase().trim();
      const rows = document.querySelectorAll(`#${tableId} tbody tr`);
      rows.forEach(r => {
        if (r.classList.contains('row-section-header') || r.classList.contains('row-section-total') || r.classList.contains('row-grand-total')) {
          r.style.display = '';
          return;
        }
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(q) ? '' : 'none';
      });
    }

    // ── Drilldown Modals ──
    async function openDrilldown(company, account) {
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      document.getElementById('drilldown-title').innerText = `${account} ${company ? `(${company})` : '(Consolidated)'}`;
      document.getElementById('modal-drilldown').classList.add('open');
      const tbody = document.getElementById('drilldown-tbody');
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;"><div class="spinner" style="margin:0 auto;"></div></td></tr>`;

      try {
        const res = await fetchFinancialAPI({
          report_type: 'drilldown',
          company: company || '',
          account: account || '',
          from_date: fromDate,
          to_date: toDate
        });
        let h = '';
        (res.entries || []).forEach(e => {
          h += `<tr>
            <td style="font-family:var(--font-mono);">${e.posting_date}</td>
            <td><span class="badge badge-neutral">${e.company}</span></td>
            <td><span class="badge badge-info">${e.voucher_type}</span></td>
            <td style="font-family:var(--font-mono);font-weight:600;">${e.voucher_no}</td>
            <td style="color:var(--text-muted);">${e.against || '-'}</td>
            <td class="num-cell">${fmt(e.debit)}</td>
            <td class="num-cell">${fmt(e.credit)}</td>
            <td style="color:var(--text-muted);max-width:200px;overflow:hidden;text-overflow:ellipsis;">${e.remarks || '-'}</td>
          </tr>`;
        });
        tbody.innerHTML = h || `<tr><td colspan="8" style="text-align:center;padding:20px;color:var(--text-muted);">No GL records found.</td></tr>`;
      } catch(err) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--negative-color);">Failed to load drilldown.</td></tr>`;
      }
    }

    function closeDrilldown() {
      document.getElementById('modal-drilldown').classList.remove('open');
    }

    async function openStockDrilldown(itemCode, company) {
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      document.getElementById('stock-modal-title').innerText = `${itemCode} - ${company}`;
      document.getElementById('modal-stock-drilldown').classList.add('open');
      const tbody = document.getElementById('stock-modal-tbody');
      tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:24px;"><div class="spinner" style="margin:0 auto;"></div></td></tr>`;

      try {
        const res = await fetchFinancialAPI({
          report_type: 'stock_ledger_drilldown',
          item_code: itemCode,
          company: company,
          from_date: fromDate,
          to_date: toDate
        });
        let h = '';
        (res.entries || []).forEach(e => {
          h += `<tr>
            <td style="font-family:var(--font-mono);">${e.posting_date} ${e.posting_time || ''}</td>
            <td><span class="badge badge-neutral">${e.company}</span></td>
            <td>${e.warehouse}</td>
            <td><span class="badge badge-info">${e.voucher_type}</span></td>
            <td style="font-family:var(--font-mono);font-weight:600;">${e.voucher_no}</td>
            <td class="num-cell" style="color:${e.actual_qty >= 0 ? 'var(--positive-color)' : 'var(--negative-color)'};">${fmtQty(e.actual_qty)}</td>
            <td class="num-cell" style="font-weight:700;">${fmtQty(e.qty_after_transaction)}</td>
            <td class="num-cell">${fmt(e.valuation_rate)}</td>
            <td class="num-cell" style="font-weight:700;">${fmt(e.stock_value_difference)}</td>
          </tr>`;
        });
        tbody.innerHTML = h || `<tr><td colspan="9" style="text-align:center;padding:20px;color:var(--text-muted);">No stock movements recorded.</td></tr>`;
      } catch(err) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;color:var(--negative-color);">Failed to load movements.</td></tr>`;
      }
    }

    function closeStockDrilldown() {
      document.getElementById('modal-stock-drilldown').classList.remove('open');
    }

    // ── Excel (.xlsx) Exporter ──
    function exportActiveTabToExcel() {
      const fromDate = document.getElementById('input-from-date').value;
      const toDate = document.getElementById('input-to-date').value;
      let targetTableId = '';
      let filename = `Financial_Report_${fromDate}_to_${toDate}`;

      if (activeTab === 'cash_flow') {
        targetTableId = cfView === 'exploded' ? 'table-cf-exploded' : (cfView === 'matrix' ? 'table-cf-matrix' : 'table-cf-periods');
        filename = `Cash_Flow_${cfView}_${fromDate}_to_${toDate}`;
      } else if (activeTab === 'ar_aging') {
        targetTableId = arView === 'summary' ? 'table-ar-summary' : (arView === 'companies' ? 'table-ar-companies' : 'table-ar-details');
        filename = `AR_Aging_${arView}_${toDate}`;
      } else if (activeTab === 'ap_aging') {
        targetTableId = apView === 'summary' ? 'table-ap-summary' : (apView === 'companies' ? 'table-ap-companies' : 'table-ap-details');
        filename = `AP_Aging_${apView}_${toDate}`;
      } else if (activeTab === 'pnl') {
        targetTableId = 'table-pnl';
        filename = `Profit_and_Loss_${fromDate}_to_${toDate}`;
      } else if (activeTab === 'balance_sheet') {
        targetTableId = 'table-bs';
        filename = `Balance_Sheet_As_Of_${toDate}`;
      } else if (activeTab === 'general_ledger') {
        targetTableId = 'table-gl';
        filename = `General_Ledger_${fromDate}_to_${toDate}`;
      } else if (activeTab === 'inventory_audit') {
        targetTableId = 'table-inv';
        filename = `Inventory_Stock_Audit_${toDate}`;
      }

      const tbl = document.getElementById(targetTableId);
      if (!tbl) {
        alert('Active report table not found for export.');
        return;
      }

      const wb = XLSX.utils.table_to_book(tbl, { sheet: "Financial Report" });
      XLSX.writeFile(wb, `${filename}.xlsx`);
    }

    // ── Initial Bootstrap ──
    window.addEventListener('DOMContentLoaded', () => {
      const hash = window.location.hash.replace('#', '');
      const validTabs = ['cash_flow', 'ar_aging', 'ap_aging', 'pnl', 'balance_sheet', 'general_ledger', 'inventory_audit'];
      if (hash && validTabs.includes(hash)) {
        switchTab(hash);
      } else {
        switchTab('cash_flow');
      }
    });
  </script>
</body>
</html>
'''

def main():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
    if r.status_code != 200:
        print("Login failed:", r.status_code)
        return

    print("Logged in successfully to VPS!")

    # 1. Update Frappe Web Page doc on VPS
    web_page_payload = {
        "doctype": "Web Page",
        "name": "consolidated-multi-company-financials-inventory-audit",
        "title": "Consolidated Multi-Company Financials, Cash Flow & Inventory Audit Suite",
        "route": "consolidated-financials",
        "published": 1,
        "full_width": 1,
        "show_sidebar": 0,
        "show_title": 0,
        "content_type": "HTML",
        "dynamic_template": 0,
        "main_section_html": HTML_TEMPLATE,
        "main_section": HTML_TEMPLATE
    }

    res = s.put(f"{BASE_URL}/api/resource/Web%20Page/consolidated-multi-company-financials-inventory-audit", json=web_page_payload)
    print("Updated Web Page on VPS:", res.status_code)

    # 2. Write to local repo files
    paths_to_write = [
        r"c:\Users\josem\erpnext-system\vps_migration\consolidated_financials.html",
        r"c:\Users\josem\erpnext-system\frappe-bench\apps\vehicle_management\vehicle_management\www\consolidated_financials.html",
        r"c:\Users\josem\erpnext-system\public\consolidated_financials.html",
        r"c:\Users\josem\erpnext-system\gh_pages_build\consolidated_financials.html",
        r"c:\Users\josem\erpnext-system\gh_pages_build\consolidated-financials.html"
    ]

    for p in paths_to_write:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(HTML_TEMPLATE)
            print(f"Written: {p}")
        except Exception as e:
            print(f"Failed to write {p}: {e}")

if __name__ == '__main__':
    main()
