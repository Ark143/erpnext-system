/**
 * VMS Relationship Map Engine for Vehicle Management
 * (c) Autometrik / ULTRA MRF
 *
 * Provides full visual document flow, items/services breakdown, accounting posting graph,
 * zoom/pan interactive canvas, and document inspector drawer.
 */

(function () {
  window.SAPRelationshipMap = window.SAPRelationshipMap || {};

  const DOCTYPE_COLORS = {
    "Customer": { bg: "#f1f5f9", border: "#64748b", text: "#0f172a", icon: "octicon octicon-person", tag: "Customer Master" },
    "Customer Vehicle": { bg: "#e0f2fe", border: "#0284c7", text: "#0369a1", icon: "fa fa-car", tag: "Vehicle Master" },
    "Vehicle Estimate": { bg: "#f3e8ff", border: "#9333ea", text: "#7e22ce", icon: "fa fa-calculator", tag: "Estimate / Quote" },
    "Vehicle Inspection": { bg: "#e0e7ff", border: "#4f46e5", text: "#3730a3", icon: "fa fa-check-circle", tag: "Multi-Point Inspection" },
    "Vehicle Job Order": { bg: "#fef3c7", border: "#d97706", text: "#b45309", icon: "fa fa-wrench", tag: "Job Order" },
    "Vehicle POS Invoice": { bg: "#ccfbf1", border: "#0d9488", text: "#0f766e", icon: "fa fa-receipt", tag: "Vehicle POS Invoice" },
    "POS Invoice": { bg: "#dcfce7", border: "#16a34a", text: "#15803d", icon: "fa fa-cash-register", tag: "POS Invoice" },
    "Sales Invoice": { bg: "#d1fae5", border: "#059669", text: "#047857", icon: "fa fa-file-invoice-dollar", tag: "Sales Invoice" },
    "Payment Entry": { bg: "#ecfdf5", border: "#10b981", text: "#065f46", icon: "fa fa-money-check-alt", tag: "Payment Entry" },
    "GL Entry": { bg: "#f8fafc", border: "#475569", text: "#334155", icon: "fa fa-book", tag: "General Ledger" },
    "Stock Entry": { bg: "#cffafe", border: "#0891b2", text: "#0e7490", icon: "fa fa-boxes", tag: "Stock Movement" },
    "Vehicle Service Reminder": { bg: "#ffedd5", border: "#ea580c", text: "#c2410c", icon: "fa fa-bell", tag: "Service Reminder" }
  };

  const STATUS_COLORS = {
    "Draft": { bg: "#e2e8f0", text: "#475569" },
    "Open": { bg: "#fef3c7", text: "#d97706" },
    "In Progress": { bg: "#dbeafe", text: "#1d4ed8" },
    "Pending Parts": { bg: "#fee2e2", text: "#b91c1c" },
    "Approved": { bg: "#dcfce7", text: "#15803d" },
    "Completed": { bg: "#d1fae5", text: "#047857" },
    "Invoiced": { bg: "#ccfbf1", text: "#0f766e" },
    "Released": { bg: "#d1fae5", text: "#065f46" },
    "Paid": { bg: "#dcfce7", text: "#166534" },
    "Submitted": { bg: "#e0e7ff", text: "#4338ca" },
    "Posted": { bg: "#f1f5f9", text: "#334155" },
    "Cancelled": { bg: "#ffe4e6", text: "#be123c" }
  };

  class SAPMapViewer {
    constructor(opts) {
      this.doctype = opts.doctype || "Vehicle Job Order";
      this.docname = opts.docname || "";
      this.vehicle = opts.vehicle || "";
      this.customer = opts.customer || "";
      this.container = opts.container || null;
      this.isModal = !!opts.isModal;
      this.dialog = opts.dialog || null;
      this.zoom = 1;
      this.panX = 40;
      this.panY = 40;
      this.isDragging = false;
      this.startX = 0;
      this.startY = 0;
      this.currentMode = "flow"; // "flow" | "items" | "accounting"
      this.data = null;
      this.selectedNode = null;
      this.init();
    }

    init() {
      this.renderSkeleton();
      this.fetchData();
    }

    renderSkeleton() {
      const html = `
        <div class="sap-map-container ${this.isModal ? 'sap-map-modal-mode' : ''}">
          <!-- Top VMS Toolbar -->
          <div class="sap-map-header">
            <div class="sap-map-title-bar">
              <div class="sap-b1-badge">
                <span class="sap-b1-logo">VMS</span>
                <span class="sap-b1-sub">RELATIONSHIP MAP</span>
              </div>
              <div class="sap-map-doc-title" id="sapMapDocTitle">
                <span class="text-muted">Loading Relationship Map for</span> <strong>${this.doctype}: ${this.docname || this.vehicle}</strong>
              </div>
            </div>

            <div class="sap-map-controls">
              <!-- Mode Selector -->
              <div class="btn-group sap-mode-toggle" role="group">
                <button type="button" class="btn btn-default btn-xs active" data-mode="flow">
                  <i class="fa fa-sitemap"></i> <span>Document Flow</span>
                </button>
                <button type="button" class="btn btn-default btn-xs" data-mode="items">
                  <i class="fa fa-list-alt"></i> <span>Related Items</span>
                </button>
                <button type="button" class="btn btn-default btn-xs" data-mode="accounting">
                  <i class="fa fa-balance-scale"></i> <span>Accounting Flow</span>
                </button>
              </div>

              <!-- Search / Switch Document -->
              <div class="sap-search-box">
                <i class="fa fa-search sap-search-icon"></i>
                <input type="text" class="form-control input-xs" id="sapSearchDoc" placeholder="Search Plate / JO / SI / Doc ID..." />
                <button class="btn btn-default btn-xs sap-search-btn" id="sapSearchBtn">Go</button>
              </div>

              <!-- Zoom & Action Tools -->
              <div class="btn-group sap-zoom-tools">
                <button class="btn btn-default btn-xs" id="sapZoomIn" title="Zoom In (+)"><i class="fa fa-search-plus"></i></button>
                <button class="btn btn-default btn-xs" id="sapZoomOut" title="Zoom Out (-)"><i class="fa fa-search-minus"></i></button>
                <button class="btn btn-default btn-xs" id="sapZoomFit" title="Fit to Screen"><i class="fa fa-expand"></i></button>
                <button class="btn btn-default btn-xs" id="sapZoomReset" title="Reset View"><i class="fa fa-crosshairs"></i></button>
                <button class="btn btn-default btn-xs" id="sapPrint" title="Print Relationship Map"><i class="fa fa-print"></i></button>
                <button class="btn btn-primary btn-xs" id="sapRefresh" title="Refresh Graph"><i class="fa fa-sync"></i></button>
              </div>
            </div>
          </div>

          <!-- Summary Financial Metric Ribbon -->
          <div class="sap-map-metrics" id="sapMapMetrics">
            <div class="sap-metric-item">
              <span class="sap-metric-lbl">Vehicle:</span>
              <span class="sap-metric-val font-weight-bold" id="sapMetricPlate">-</span>
            </div>
            <div class="sap-metric-item">
              <span class="sap-metric-lbl">Customer:</span>
              <span class="sap-metric-val" id="sapMetricCust">-</span>
            </div>
            <div class="sap-metric-item">
              <span class="sap-metric-lbl">Total Flow Value:</span>
              <span class="sap-metric-val text-primary" id="sapMetricVal">₱ 0.00</span>
            </div>
            <div class="sap-metric-item">
              <span class="sap-metric-lbl">Total Paid:</span>
              <span class="sap-metric-val text-success" id="sapMetricPaid">₱ 0.00</span>
            </div>
            <div class="sap-metric-item">
              <span class="sap-metric-lbl">Outstanding Balance:</span>
              <span class="sap-metric-val text-danger" id="sapMetricOutst">₱ 0.00</span>
            </div>
            <div class="sap-metric-item ml-auto">
              <span class="sap-metric-lbl">Flow Status:</span>
              <span class="sap-status-pill" id="sapMetricStatus">In Progress</span>
            </div>
          </div>

          <!-- Interactive Workspace Canvas & Drawer -->
          <div class="sap-map-workspace">
            <div class="sap-map-viewport" id="sapViewport">
              <div class="sap-map-canvas" id="sapCanvas">
                <svg class="sap-map-svg-layer" id="sapSvgLayer">
                  <defs>
                    <marker id="sapArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#0284c7" />
                    </marker>
                    <marker id="sapArrowGold" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706" />
                    </marker>
                    <marker id="sapArrowGreen" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a" />
                    </marker>
                  </defs>
                  <g id="sapSvgEdges"></g>
                </svg>
                <div class="sap-map-nodes-layer" id="sapNodesLayer">
                  <div class="sap-loading-spinner text-center p-5">
                    <i class="fa fa-spinner fa-spin fa-2x text-muted"></i>
                    <p class="mt-2 text-muted">Tracing document relations and journal entries...</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Side Inspector Drawer -->
            <div class="sap-map-drawer" id="sapDrawer">
              <div class="sap-drawer-header">
                <div class="sap-drawer-title" id="sapDrawerTitle">Document Details</div>
                <button type="button" class="close sap-drawer-close" id="sapDrawerClose">&times;</button>
              </div>
              <div class="sap-drawer-body" id="sapDrawerBody">
                <div class="text-muted p-3 text-center">Click on any card to view detailed breakdown & line items</div>
              </div>
              <div class="sap-drawer-footer" id="sapDrawerFooter" style="display:none;">
                <button class="btn btn-primary btn-sm btn-block" id="sapOpenDocBtn">
                  <i class="fa fa-external-link-alt"></i> Open Full Document
                </button>
              </div>
            </div>
          </div>
        </div>
      `;

      if (this.container) {
        $(this.container).html(html);
      }

      this.bindEvents();
    }

    bindEvents() {
      const $c = $(this.container || document);

      // Mode switch
      $c.find('.sap-mode-toggle button').on('click', (e) => {
        $c.find('.sap-mode-toggle button').removeClass('active btn-primary').addClass('btn-default');
        const $btn = $(e.currentTarget);
        $btn.addClass('active btn-primary').removeClass('btn-default');
        this.currentMode = $btn.data('mode');
        this.renderGraph();
      });

      // Zoom In / Out / Reset / Fit
      $c.find('#sapZoomIn').on('click', () => this.adjustZoom(0.15));
      $c.find('#sapZoomOut').on('click', () => this.adjustZoom(-0.15));
      $c.find('#sapZoomReset').on('click', () => {
        this.zoom = 1;
        this.panX = 40;
        this.panY = 40;
        this.applyTransform();
      });
      $c.find('#sapZoomFit').on('click', () => this.fitToScreen());
      $c.find('#sapRefresh').on('click', () => this.fetchData());

      // Print Map
      $c.find('#sapPrint').on('click', () => window.print());

      // Search Box
      $c.find('#sapSearchBtn').on('click', () => this.handleSearch());
      $c.find('#sapSearchDoc').on('keypress', (e) => {
        if (e.which === 13) this.handleSearch();
      });

      // Close drawer
      $c.find('#sapDrawerClose').on('click', () => {
        $c.find('#sapDrawer').removeClass('open');
      });

      // Pan Drag Events
      const viewport = $c.find('#sapViewport')[0];
      if (viewport) {
        $(viewport).on('mousedown', (e) => {
          if ($(e.target).closest('.sap-node-card, .sap-map-drawer, button, input').length) return;
          this.isDragging = true;
          this.startX = e.clientX - this.panX;
          this.startY = e.clientY - this.panY;
          $(viewport).addClass('grabbing');
        });

        $(document).on('mousemove', (e) => {
          if (!this.isDragging) return;
          this.panX = e.clientX - this.startX;
          this.panY = e.clientY - this.startY;
          this.applyTransform();
        });

        $(document).on('mouseup', () => {
          if (this.isDragging) {
            this.isDragging = false;
            $(viewport).removeClass('grabbing');
          }
        });

        // Mousewheel zoom
        viewport.addEventListener('wheel', (e) => {
          e.preventDefault();
          const delta = e.deltaY < 0 ? 0.08 : -0.08;
          this.adjustZoom(delta);
        }, { passive: false });
      }
    }

    adjustZoom(delta) {
      this.zoom = Math.max(0.3, Math.min(2.2, this.zoom + delta));
      this.applyTransform();
    }

    applyTransform() {
      const $canvas = $(this.container || document).find('#sapCanvas');
      $canvas.css({
        transform: `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`,
        transformOrigin: '0 0'
      });
    }

    handleSearch() {
      const q = $(this.container || document).find('#sapSearchDoc').val().trim();
      if (!q) return;

      // Detect search type
      if (q.startsWith('JO-') || q.startsWith('jo-')) {
        this.doctype = 'Vehicle Job Order';
        this.docname = q.toUpperCase();
      } else if (q.startsWith('EST-') || q.startsWith('est-')) {
        this.doctype = 'Vehicle Estimate';
        this.docname = q.toUpperCase();
      } else if (q.startsWith('INSP-') || q.startsWith('insp-')) {
        this.doctype = 'Vehicle Inspection';
        this.docname = q.toUpperCase();
      } else if (q.startsWith('VMSPOS-') || q.startsWith('vmspos-')) {
        this.doctype = 'Vehicle POS Invoice';
        this.docname = q.toUpperCase();
      } else if (q.startsWith('ACC-SINV') || q.startsWith('acc-sinv')) {
        this.doctype = 'Sales Invoice';
        this.docname = q.toUpperCase();
      } else if (q.startsWith('ACC-PAY') || q.startsWith('acc-pay')) {
        this.doctype = 'Payment Entry';
        this.docname = q.toUpperCase();
      } else {
        // Assume Vehicle Plate or Customer
        this.doctype = 'Customer Vehicle';
        this.docname = q;
        this.vehicle = q;
      }

      this.fetchData();
    }

    fetchData() {
      const $c = $(this.container || document);
      $c.find('#sapNodesLayer').html(`
        <div class="sap-loading-spinner text-center p-5">
          <i class="fa fa-spinner fa-spin fa-2x text-primary"></i>
          <p class="mt-2 text-muted">Building relationship graph for ${this.doctype}: ${this.docname}...</p>
        </div>
      `);
      $c.find('#sapSvgEdges').empty();

      const params = {
        doctype: this.doctype,
        docname: this.docname,
        vehicle: this.vehicle,
        customer: this.customer
      };

      frappe.call({
        method: "vm_relationship_map",
        args: params,
        callback: (r) => {
          if (r.message && r.message.nodes) {
            this.data = r.message;
            this.renderSummary();
            this.renderGraph();
          } else {
            $c.find('#sapNodesLayer').html(`
              <div class="alert alert-warning m-4">
                <strong>No relationships found</strong> for ${this.doctype}: ${this.docname || this.vehicle}.
              </div>
            `);
          }
        },
        error: () => {
          $c.find('#sapNodesLayer').html(`
            <div class="alert alert-danger m-4">
              <strong>Error loading SAP Relationship Map.</strong> Please check backend connection.
            </div>
          `);
        }
      });
    }

    renderSummary() {
      const sum = this.data.summary || {};
      const $c = $(this.container || document);

      $c.find('#sapMapDocTitle').html(`
        <span class="badge badge-info mr-2">${sum.focal_doctype || this.doctype}</span>
        <strong>${sum.focal_docname || this.docname || sum.vehicle_plate || 'Overview'}</strong>
      `);

      $c.find('#sapMetricPlate').text(sum.vehicle_plate || 'N/A');
      $c.find('#sapMetricCust').text(sum.customer_name || 'N/A');
      $c.find('#sapMetricVal').text(format_currency(sum.total_transaction_value || 0, 'PHP'));
      $c.find('#sapMetricPaid').text(format_currency(sum.total_paid_value || 0, 'PHP'));
      $c.find('#sapMetricOutst').text(format_currency(sum.total_outstanding_value || 0, 'PHP'));

      const $status = $c.find('#sapMetricStatus');
      if (sum.status_flow_complete) {
        $status.text('Completed & Reconciled').removeClass('sap-status-open').addClass('sap-status-paid');
      } else {
        $status.text('Open / In Progress').removeClass('sap-status-paid').addClass('sap-status-open');
      }
    }

    renderGraph() {
      if (!this.data) return;
      const $c = $(this.container || document);
      const $nodesLayer = $c.find('#sapNodesLayer');
      const $svgEdges = $c.find('#sapSvgEdges');

      $nodesLayer.empty();
      $svgEdges.empty();

      if (this.currentMode === "items") {
        this.renderItemsMatrix();
        return;
      }

      if (this.currentMode === "accounting") {
        this.renderAccountingFlow();
        return;
      }

      // ── Standard Document Flow Layout ──
      const nodes = this.data.nodes || [];
      const edges = this.data.edges || [];

      // Group nodes by Level / Column
      // Level 0: Masters (Customer, Vehicle)
      // Level 1: Inquiries / Diagnostics (Estimate, Inspection)
      // Level 2: Execution (Job Order, Stock Entry)
      // Level 3: Invoicing (Sales Invoice, Vehicle POS Invoice, POS Invoice)
      // Level 4: Settlement (Payment Entry, GL Entry)

      const columns = { 0: [], 1: [], 2: [], 3: [], 4: [] };
      const levelTitles = {
        0: "Master Profiles",
        1: "Estimates & Inspections",
        2: "Workshop Execution",
        3: "Billing & Invoicing",
        4: "Payments & General Ledger"
      };

      nodes.forEach((n) => {
        let lvl = n.level;
        if (lvl === undefined || lvl === null) {
          if (n.doctype === "Customer" || n.doctype === "Customer Vehicle") lvl = 0;
          else if (n.doctype === "Vehicle Estimate" || n.doctype === "Vehicle Inspection") lvl = 1;
          else if (n.doctype === "Vehicle Job Order" || n.doctype === "Stock Entry") lvl = 2;
          else if (n.doctype === "Sales Invoice" || n.doctype === "Vehicle POS Invoice" || n.doctype === "POS Invoice") lvl = 3;
          else if (n.doctype === "Payment Entry" || n.doctype === "GL Entry") lvl = 4;
          else lvl = 2;
        }
        if (!columns[lvl]) columns[lvl] = [];
        columns[lvl].push(n);
      });

      const cardWidth = 260;
      const colGap = 120;
      const rowGap = 35;
      const cardHeight = 155;
      const startX = 60;
      const startY = 80;

      const nodeCoords = {};

      // Render columns
      let colIndex = 0;
      for (let lvl = 0; lvl <= 4; lvl++) {
        const colNodes = columns[lvl] || [];
        if (colNodes.length === 0) continue;

        const colX = startX + (colIndex * (cardWidth + colGap));

        // Column Header Ribbon
        const colHeaderHtml = `
          <div class="sap-col-header" style="left: ${colX}px; top: ${startY - 45}px; width: ${cardWidth}px;">
            <span>${levelTitles[lvl] || 'Phase ' + lvl}</span>
            <span class="badge badge-light">${colNodes.length}</span>
          </div>
        `;
        $nodesLayer.append(colHeaderHtml);

        colNodes.forEach((node, rIndex) => {
          const colY = startY + (rIndex * (cardHeight + rowGap));
          nodeCoords[node.id] = {
            x: colX,
            y: colY,
            cx: colX + (cardWidth / 2),
            cy: colY + (cardHeight / 2),
            left: colX,
            right: colX + cardWidth,
            top: colY,
            bottom: colY + cardHeight,
            node: node
          };

          const cardHtml = this.createNodeCardHtml(node, colX, colY, cardWidth, cardHeight);
          $nodesLayer.append(cardHtml);
        });

        colIndex++;
      }

      // Draw SVG Connecting Lines
      setTimeout(() => {
        edges.forEach((edge) => {
          const fromCoord = nodeCoords[edge.from];
          const toCoord = nodeCoords[edge.to];
          if (!fromCoord || !toCoord) return;

          const p1 = { x: fromCoord.right, y: fromCoord.cy };
          const p2 = { x: toCoord.left, y: toCoord.cy };

          // If reverse flow, adjust start & end
          let startPt = p1;
          let endPt = p2;
          if (fromCoord.x > toCoord.x) {
            startPt = { x: fromCoord.left, y: fromCoord.cy };
            endPt = { x: toCoord.right, y: toCoord.cy };
          }

          const dx = Math.abs(endPt.x - startPt.x) / 2;
          const cp1x = startPt.x + (fromCoord.x <= toCoord.x ? dx : -dx);
          const cp1y = startPt.y;
          const cp2x = endPt.x - (fromCoord.x <= toCoord.x ? dx : -dx);
          const cp2y = endPt.y;

          const pathD = `M ${startPt.x} ${startPt.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endPt.x} ${endPt.y}`;
          const midX = (startPt.x + endPt.x) / 2;
          const midY = (startPt.y + endPt.y) / 2;

          let strokeColor = "#0284c7";
          let markerUrl = "url(#sapArrow)";
          if (edge.type === "accounting") {
            strokeColor = "#16a34a";
            markerUrl = "url(#sapArrowGreen)";
          } else if (edge.label && edge.label.includes("Converted")) {
            strokeColor = "#d97706";
            markerUrl = "url(#sapArrowGold)";
          }

          const edgeSvg = `
            <g class="sap-edge-group">
              <path d="${pathD}" fill="none" stroke="${strokeColor}" stroke-width="2.5" stroke-dasharray="${edge.type === 'reference' ? '5,5' : 'none'}" marker-end="${markerUrl}" />
              ${edge.label ? `
                <rect x="${midX - 45}" y="${midY - 11}" width="90" height="20" rx="10" fill="#ffffff" stroke="${strokeColor}" stroke-width="1" />
                <text x="${midX}" y="${midY + 3}" fill="${strokeColor}" font-size="10" font-weight="700" text-anchor="middle">${edge.label}</text>
              ` : ''}
            </g>
          `;
          $svgEdges.append(edgeSvg);
        });

        // Set canvas sizing
        const totalW = (colIndex * (cardWidth + colGap)) + 200;
        const totalH = Math.max(600, 4 * (cardHeight + rowGap) + 200);
        $c.find('#sapSvgLayer').attr('width', totalW).attr('height', totalH);
        $c.find('#sapCanvas').css({ width: totalW, height: totalH });
      }, 50);

      // Card Click Handler
      $nodesLayer.find('.sap-node-card').on('click', (e) => {
        const nodeId = $(e.currentTarget).data('node-id');
        const node = nodes.find(n => n.id === nodeId);
        if (node) this.selectNode(node);
      });

      // Card Double Click Handler (Direct Open in Desk)
      $nodesLayer.find('.sap-node-card').on('dblclick', (e) => {
        const dt = $(e.currentTarget).data('doctype');
        const nm = $(e.currentTarget).data('name');
        if (dt && nm) {
          if (this.dialog) this.dialog.hide();
          frappe.set_route('Form', dt, nm);
        }
      });
    }

    createNodeCardHtml(node, x, y, width, height) {
      const dtConfig = DOCTYPE_COLORS[node.doctype] || { bg: "#f8fafc", border: "#64748b", text: "#334155", icon: "fa fa-file", tag: node.doctype };
      const stConfig = STATUS_COLORS[node.status] || { bg: "#e2e8f0", text: "#475569" };
      const isCurrent = node.is_current;

      return `
        <div class="sap-node-card ${isCurrent ? 'sap-node-current' : ''}" data-node-id="${node.id}" data-doctype="${node.doctype}" data-name="${node.name}" style="left: ${x}px; top: ${y}px; width: ${width}px; min-height: ${height}px; border-left: 5px solid ${dtConfig.border};">
          ${isCurrent ? '<div class="sap-active-indicator"><i class="fa fa-dot-circle"></i> ACTIVE DOCUMENT</div>' : ''}
          
          <div class="sap-node-head">
            <div class="sap-node-dt-badge" style="color: ${dtConfig.text};">
              <i class="${dtConfig.icon} mr-1"></i>
              <span>${dtConfig.tag || node.doctype}</span>
            </div>
            <span class="sap-node-status" style="background: ${stConfig.bg}; color: ${stConfig.text};">
              ${node.status}
            </span>
          </div>

          <div class="sap-node-id" title="${node.name}">
            ${node.name}
          </div>

          <div class="sap-node-info-grid">
            ${node.vehicle ? `
              <div class="sap-node-info-row">
                <span class="text-muted"><i class="fa fa-car"></i> Plate:</span>
                <span class="font-weight-bold">${node.vehicle}</span>
              </div>
            ` : ''}
            ${node.customer ? `
              <div class="sap-node-info-row">
                <span class="text-muted"><i class="fa fa-user"></i> Cust:</span>
                <span class="text-truncate" style="max-width: 140px;" title="${node.customer}">${node.customer}</span>
              </div>
            ` : ''}
            ${node.posting_date ? `
              <div class="sap-node-info-row">
                <span class="text-muted"><i class="fa fa-calendar-alt"></i> Date:</span>
                <span>${node.posting_date}</span>
              </div>
            ` : ''}
          </div>

          <div class="sap-node-footer">
            <div class="sap-node-amt">
              ${node.grand_total > 0 ? `
                <span class="sap-amt-val">${format_currency(node.grand_total, node.currency || 'PHP')}</span>
              ` : (node.items_count > 0 ? `<span>${node.items_count} Items</span>` : `<span class="text-muted">No charge</span>`)}
            </div>
            <div class="sap-node-actions">
              <button class="btn btn-default btn-xs sap-quick-view-btn" title="View Document Details">
                <i class="fa fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    }

    renderItemsMatrix() {
      const $c = $(this.container || document);
      const $nodesLayer = $c.find('#sapNodesLayer');
      const nodes = this.data.nodes || [];

      let rowsHtml = '';
      nodes.forEach(n => {
        if (n.items && n.items.length > 0) {
          n.items.forEach(it => {
            rowsHtml += `
              <tr>
                <td><span class="badge badge-info">${n.doctype}</span> <strong>${n.name}</strong></td>
                <td><span class="badge ${it.type.includes('Labor') ? 'badge-warning' : 'badge-primary'}">${it.type}</span></td>
                <td><strong>${it.item_code}</strong><br><small class="text-muted">${it.description || ''}</small></td>
                <td class="text-right">${it.qty}</td>
                <td class="text-right">${format_currency(it.rate, 'PHP')}</td>
                <td class="text-right font-weight-bold">${format_currency(it.amount, 'PHP')}</td>
              </tr>
            `;
          });
        }
      });

      if (!rowsHtml) {
        rowsHtml = `<tr><td colspan="6" class="text-center text-muted p-4">No item or service lines found for these documents.</td></tr>`;
      }

      $nodesLayer.html(`
        <div class="sap-items-matrix-view p-4" style="max-width: 960px; margin: 0 auto;">
          <h4 class="font-weight-bold mb-3"><i class="fa fa-list-alt text-primary"></i> Consolidated Items & Labor Matrix</h4>
          <div class="table-responsive bg-white rounded shadow-sm border">
            <table class="table table-hover table-striped mb-0">
              <thead class="thead-light">
                <tr>
                  <th>Document</th>
                  <th>Category</th>
                  <th>Item / Service Description</th>
                  <th class="text-right">Qty / Hrs</th>
                  <th class="text-right">Rate</th>
                  <th class="text-right">Total Amount</th>
                </tr>
              </thead>
              <tbody>${rowsHtml}</tbody>
            </table>
          </div>
        </div>
      `);
    }

    renderAccountingFlow() {
      const $c = $(this.container || document);
      const $nodesLayer = $c.find('#sapNodesLayer');
      const nodes = this.data.nodes || [];

      const acctNodes = nodes.filter(n => ["Sales Invoice", "POS Invoice", "Payment Entry", "GL Entry"].includes(n.doctype));

      let acctCards = '';
      acctNodes.forEach(n => {
        acctCards += `
          <div class="card mb-3 shadow-sm border">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <div>
                <span class="badge badge-success mr-2">${n.doctype}</span>
                <strong>${n.name}</strong>
              </div>
              <div>
                <span class="badge badge-info">${n.status}</span>
                <span class="ml-2 font-weight-bold text-success">${format_currency(n.grand_total, 'PHP')}</span>
              </div>
            </div>
            <div class="card-body py-2">
              <p class="mb-1 text-muted"><i class="fa fa-info-circle"></i> ${n.remarks || n.title || 'Ledger Posting'}</p>
              ${n.posting_date ? `<small class="text-muted"><i class="fa fa-calendar"></i> Date: ${n.posting_date}</small>` : ''}
            </div>
          </div>
        `;
      });

      if (!acctCards) {
        acctCards = `<div class="alert alert-info">No accounting or GL entries posted yet for this workflow.</div>`;
      }

      $nodesLayer.html(`
        <div class="sap-accounting-view p-4" style="max-width: 800px; margin: 0 auto;">
          <h4 class="font-weight-bold mb-3"><i class="fa fa-balance-scale text-success"></i> Accounting & General Ledger Postings</h4>
          ${acctCards}
        </div>
      `);
    }

    selectNode(node) {
      this.selectedNode = node;
      const $c = $(this.container || document);
      const $drawer = $c.find('#sapDrawer');

      $drawer.addClass('open');
      $c.find('#sapDrawerTitle').html(`
        <span class="badge badge-primary mr-1">${node.doctype}</span>
        <strong>${node.name}</strong>
      `);

      let itemsHtml = '';
      if (node.items && node.items.length > 0) {
        itemsHtml = `
          <div class="sap-drawer-sec">
            <div class="sap-drawer-sec-title">Line Items & Services (${node.items.length})</div>
            <div class="table-responsive">
              <table class="table table-sm table-bordered">
                <thead class="thead-light">
                  <tr>
                    <th>Item</th>
                    <th class="text-right">Qty</th>
                    <th class="text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  ${node.items.map(it => `
                    <tr>
                      <td><small><strong>${it.item_code}</strong><br>${it.description || ''}</small></td>
                      <td class="text-right"><small>${it.qty}</small></td>
                      <td class="text-right font-weight-bold"><small>${format_currency(it.amount, 'PHP')}</small></td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        `;
      }

      const bodyHtml = `
        <div class="sap-drawer-sec">
          <div class="sap-drawer-sec-title">Document Information</div>
          <table class="table table-sm table-borderless">
            <tr><td class="text-muted" style="width: 40%;">Status:</td><td><span class="badge badge-info">${node.status}</span></td></tr>
            <tr><td class="text-muted">Posting Date:</td><td>${node.posting_date || 'N/A'}</td></tr>
            <tr><td class="text-muted">Customer:</td><td><strong>${node.customer || 'N/A'}</strong></td></tr>
            <tr><td class="text-muted">Vehicle Plate:</td><td><strong>${node.vehicle || 'N/A'}</strong></td></tr>
            <tr><td class="text-muted">Company:</td><td>${node.company || 'ULTRA MRF'}</td></tr>
            ${node.grand_total > 0 ? `<tr><td class="text-muted">Grand Total:</td><td class="font-weight-bold text-primary">${format_currency(node.grand_total, node.currency || 'PHP')}</td></tr>` : ''}
            ${node.paid_amount > 0 ? `<tr><td class="text-muted">Paid Amount:</td><td class="font-weight-bold text-success">${format_currency(node.paid_amount, node.currency || 'PHP')}</td></tr>` : ''}
            ${node.outstanding_amount > 0 ? `<tr><td class="text-muted">Balance Due:</td><td class="font-weight-bold text-danger">${format_currency(node.outstanding_amount, node.currency || 'PHP')}</td></tr>` : ''}
          </table>
        </div>

        ${node.remarks ? `
          <div class="sap-drawer-sec">
            <div class="sap-drawer-sec-title">Remarks & Complaints</div>
            <div class="p-2 bg-light rounded text-muted"><small>${node.remarks}</small></div>
          </div>
        ` : ''}

        ${itemsHtml}
      `;

      $c.find('#sapDrawerBody').html(bodyHtml);
      $c.find('#sapDrawerFooter').show();

      $c.find('#sapOpenDocBtn').off('click').on('click', () => {
        if (this.dialog) this.dialog.hide();
        frappe.set_route('Form', node.doctype, node.name);
      });
    }

    fitToScreen() {
      this.zoom = 0.85;
      this.panX = 20;
      this.panY = 20;
      this.applyTransform();
    }
  }

  window.SAPRelationshipMap.ViewerClass = SAPMapViewer;

  // ─────────────────────────────────────────────
  // Global Launch Function (Modal or Page)
  // ─────────────────────────────────────────────
  window.SAPRelationshipMap.open = function (opts) {
    opts = opts || {};
    const d = new frappe.ui.Dialog({
      title: `<span class="sap-b1-title-logo"><i class="fa fa-sitemap mr-1 text-primary"></i> VMS Relationship Map</span>`,
      size: "extra-large",
      fields: [
        {
          fieldtype: "HTML",
          fieldname: "map_canvas_html",
        }
      ]
    });

    d.show();
    d.$wrapper.find('.modal-dialog').addClass('sap-map-dialog-xl');
    d.$wrapper.find('.modal-body').addClass('p-0 sap-map-dialog-body');

    const container = d.get_field("map_canvas_html").$wrapper[0];
    new SAPMapViewer({
      doctype: opts.doctype || cur_frm?.doctype || "Vehicle Job Order",
      docname: opts.docname || cur_frm?.doc?.name || "",
      vehicle: opts.vehicle || cur_frm?.doc?.vehicle || cur_frm?.doc?.plate_no || "",
      customer: opts.customer || cur_frm?.doc?.customer || "",
      container: container,
      isModal: true,
      dialog: d
    });
  };

  // Keyboard shortcut: Alt+M or Alt+R
  $(document).on('keydown', (e) => {
    if (e.altKey && (e.key === 'm' || e.key === 'M' || e.key === 'r' || e.key === 'R')) {
      if (cur_frm && cur_frm.doc && cur_frm.doc.name) {
        e.preventDefault();
        window.SAPRelationshipMap.open({
          doctype: cur_frm.doctype,
          docname: cur_frm.doc.name
        });
      }
    }
  });

})();
