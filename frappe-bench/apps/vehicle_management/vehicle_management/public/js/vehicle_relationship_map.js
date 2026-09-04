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
    "Customer": { bg: "#f1f5f9", border: "#64748b", text: "#0f172a", icon: "fa fa-user", tag: "Customer Profile" },
    "Customer Vehicle": { bg: "#e0f2fe", border: "#0284c7", text: "#0369a1", icon: "fa fa-car", tag: "Customer Vehicle" },
    "Vehicle Estimate": { bg: "#f3e8ff", border: "#9333ea", text: "#7e22ce", icon: "fa fa-calculator", tag: "Estimate / Quote" },
    "Vehicle Inspection": { bg: "#e0e7ff", border: "#4f46e5", text: "#3730a3", icon: "fa fa-check-circle", tag: "Multi-Point Inspection" },
    "Vehicle Job Order": { bg: "#fef3c7", border: "#d97706", text: "#b45309", icon: "fa fa-wrench", tag: "Vehicle Job Order" },
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
      this.itemFilter = "all";
      this.itemSearchTerm = "";
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
          <!-- Print-Only Audit Header -->
          <div class="sap-print-header" id="sapPrintHeader">
            <div class="sap-print-header-left">
              <h3 class="sap-print-company" id="sapPrintCompany">ULTRA MRF</h3>
              <div class="sap-print-address text-muted" id="sapPrintAddress"></div>
              <div class="sap-print-doc-meta mt-1">
                <strong>VMS Relationship Map & Audit Trace:</strong>
                <span id="sapPrintDocTitle"></span>
              </div>
            </div>
            <div class="sap-print-header-right">
              <div class="sap-print-audit-box">
                <div><strong>Printed By:</strong> <span id="sapPrintUser"></span></div>
                <div><strong>Date Generated:</strong> <span id="sapPrintDate"></span></div>
                <div><strong>Flow Status:</strong> <span id="sapPrintStatus"></span></div>
              </div>
            </div>
          </div>

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
                <button type="button" class="btn btn-primary btn-xs active" data-mode="flow">
                  <i class="fa fa-sitemap mr-1"></i> <span>Document Flow</span>
                </button>
                <button type="button" class="btn btn-default btn-xs" data-mode="items">
                  <i class="fa fa-list-alt mr-1"></i> <span>Related Items</span>
                </button>
                <button type="button" class="btn btn-default btn-xs" data-mode="accounting">
                  <i class="fa fa-balance-scale mr-1"></i> <span>Accounting Flow</span>
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
              <span class="sap-metric-lbl">Vehicle Plate:</span>
              <span class="sap-metric-val font-weight-bold" id="sapMetricPlate">-</span>
            </div>
            <div class="sap-metric-item">
              <span class="sap-metric-lbl">Customer:</span>
              <span class="sap-metric-val font-weight-bold" id="sapMetricCust">-</span>
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
              <span class="sap-metric-lbl">Settlement Status:</span>
              <span class="sap-status-pill" id="sapMetricStatus">In Progress</span>
            </div>
          </div>

          <!-- Main Interactive Viewport & Drawer -->
          <div class="sap-map-workspace">
            <!-- 1. Document Flow Interactive Canvas View -->
            <div class="sap-view-pane" id="sapFlowView" style="display: flex; flex: 1; position: relative; overflow: hidden; width: 100%; height: 100%;">
              <div class="sap-map-viewport" id="sapViewport">
                <div class="sap-map-canvas" id="sapCanvas">
                  <!-- SVG Layer for Bezier Connectors -->
                  <svg class="sap-map-svg-layer" id="sapSvgLayer" width="3000" height="2000">
                    <defs>
                      <marker id="sapArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284c7" />
                      </marker>
                      <marker id="sapArrowGreen" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#16a34a" />
                      </marker>
                      <marker id="sapArrowGold" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706" />
                      </marker>
                    </defs>
                    <g id="sapSvgEdges"></g>
                  </svg>

                  <!-- HTML Nodes Layer -->
                  <div class="sap-map-nodes-layer" id="sapNodesLayer"></div>
                </div>
              </div>
            </div>

            <!-- 2. Related Items Scrollable Table View -->
            <div class="sap-view-pane" id="sapItemsView" style="display: none; flex: 1; overflow-y: auto; width: 100%; height: 100%; padding: 20px; background: #f8fafc;"></div>

            <!-- 3. Accounting Flow Scrollable Ledger View -->
            <div class="sap-view-pane" id="sapAccountingView" style="display: none; flex: 1; overflow-y: auto; width: 100%; height: 100%; padding: 20px; background: #f8fafc;"></div>

            <!-- Right Inspector Drawer -->
            <div class="sap-map-drawer" id="sapDrawer">
              <div class="sap-drawer-header">
                <div class="sap-drawer-title" id="sapDrawerTitle">Document Details</div>
                <button type="button" class="close" id="sapDrawerClose">&times;</button>
              </div>
              <div class="sap-drawer-body" id="sapDrawerBody">
                <p class="text-muted">Click any document card to inspect items, financial postings, and full history.</p>
              </div>
              <div class="sap-drawer-footer" id="sapDrawerFooter" style="display:none;">
                <button class="btn btn-primary btn-sm btn-block" id="sapOpenDocBtn">
                  <i class="fa fa-external-link-alt mr-1"></i> Open Full Document Form
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

        viewport.addEventListener('wheel', (e) => {
          if (this.currentMode !== "flow") return;
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
        this.doctype = 'Customer Vehicle';
        this.docname = q;
        this.vehicle = q;
      }

      this.fetchData();
    }

    fetchData() {
      const $c = $(this.container || document);
      $c.find('#sapNodesLayer').html(`
        <div class="sap-loading-spinner text-center p-5" style="width: 100%; min-width: 600px;">
          <i class="fa fa-spinner fa-spin fa-2x text-primary"></i>
          <p class="mt-2 text-muted">Building relationship graph for ${this.doctype}: ${this.docname || this.vehicle}...</p>
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
              <strong>Error loading Relationship Map.</strong> Please check backend connection.
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
      const statusText = sum.status_flow_complete ? 'Completed & Reconciled' : 'Open / In Progress';
      if (sum.status_flow_complete) {
        $status.text(statusText).removeClass('sap-status-open').addClass('sap-status-paid');
      } else {
        $status.text(statusText).removeClass('sap-status-paid').addClass('sap-status-open');
      }

      // Populate Print Audit Header
      const userName = (frappe.session && (frappe.session.user_fullname || frappe.session.user)) || 'Authorized User';
      const nowFormatted = frappe.datetime && frappe.datetime.now_datetime ? frappe.datetime.str_to_user(frappe.datetime.now_datetime()) : new Date().toLocaleString();
      const compName = sum.company || 'ULTRA MRF';
      const compAddr = sum.company_address || '';

      $c.find('#sapPrintCompany').text(compName);
      if (compAddr) {
        $c.find('#sapPrintAddress').text(compAddr).show();
      } else {
        $c.find('#sapPrintAddress').hide();
      }
      $c.find('#sapPrintDocTitle').text(`${sum.focal_doctype || this.doctype}: ${sum.focal_docname || this.docname || sum.vehicle_plate || 'Workflow'}`);
      $c.find('#sapPrintUser').text(userName);
      $c.find('#sapPrintDate').text(nowFormatted);
      $c.find('#sapPrintStatus').text(statusText);
    }

    renderGraph() {
      if (!this.data) return;
      const $c = $(this.container || document);

      if (this.currentMode === "items") {
        $c.find('#sapFlowView').hide();
        $c.find('#sapAccountingView').hide();
        $c.find('#sapItemsView').show();
        this.renderItemsMatrix();
        return;
      }

      if (this.currentMode === "accounting") {
        $c.find('#sapFlowView').hide();
        $c.find('#sapItemsView').hide();
        $c.find('#sapAccountingView').show();
        this.renderAccountingFlow();
        return;
      }

      // Default: Document Flow Canvas View
      $c.find('#sapItemsView').hide();
      $c.find('#sapAccountingView').hide();
      $c.find('#sapFlowView').show();

      const $nodesLayer = $c.find('#sapNodesLayer');
      const $svgEdges = $c.find('#sapSvgEdges');

      $nodesLayer.empty();
      $svgEdges.empty();

      // ── Standard Document Flow Layout ──
      const nodes = this.data.nodes || [];
      const edges = this.data.edges || [];

      // Group nodes by 5 Sequential Columns:
      // Column 0: Master Profiles (Customer, Customer Vehicle)
      // Column 1: Estimates & Diagnostics (Vehicle Estimate, Vehicle Inspection)
      // Column 2: Workshop Execution (Vehicle Job Order, Stock Entry)
      // Column 3: Billing & Invoicing (Sales Invoice, Vehicle POS Invoice, POS Invoice)
      // Column 4: Payments & Settlements (Payment Entry, GL Entry)
      const columns = { 0: [], 1: [], 2: [], 3: [], 4: [] };
      const levelTitles = {
        0: "Master Profiles",
        1: "Estimates & Diagnostics",
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
      const cardHeight = 160;
      const startX = 60;
      const startY = 80;

      const nodeCoords = {};
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

      // Draw SVG Bezier Connecting Lines
      setTimeout(() => {
        edges.forEach((edge) => {
          const fromCoord = nodeCoords[edge.from];
          const toCoord = nodeCoords[edge.to];
          if (!fromCoord || !toCoord) return;

          const p1 = { x: fromCoord.right, y: fromCoord.cy };
          const p2 = { x: toCoord.left, y: toCoord.cy };

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
              <rect x="${midX - 50}" y="${midY - 11}" width="100" height="22" rx="11" fill="#ffffff" stroke="${strokeColor}" stroke-width="1.2" />
              <text x="${midX}" y="${midY + 4}" text-anchor="middle" font-size="10" font-weight="700" fill="#334155">${edge.label}</text>
            </g>
          `;
          $svgEdges.append(edgeSvg);
        });
      }, 50);

      // Bind node interactions
      $nodesLayer.find('.sap-node-card').on('click', (e) => {
        const nodeId = $(e.currentTarget).data('node-id');
        const node = nodes.find(n => n.id === nodeId);
        if (node) this.selectNode(node);
      });

      $nodesLayer.find('.sap-node-card').on('dblclick', (e) => {
        const dt = $(e.currentTarget).data('doctype');
        const nm = $(e.currentTarget).data('name');
        if (dt && nm && dt !== "GL Entry") {
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
          ${isCurrent ? '<div class="sap-active-indicator"><i class="fa fa-dot-circle mr-1"></i> ACTIVE DOCUMENT</div>' : ''}
          
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
                <span class="text-muted"><i class="fa fa-car mr-1"></i> Plate:</span>
                <span class="font-weight-bold">${node.vehicle}</span>
              </div>
            ` : ''}
            ${node.customer ? `
              <div class="sap-node-info-row">
                <span class="text-muted"><i class="fa fa-user mr-1"></i> Cust:</span>
                <span class="text-truncate" style="max-width: 140px;" title="${node.customer}">${node.customer}</span>
              </div>
            ` : ''}
            ${node.posting_date ? `
              <div class="sap-node-info-row">
                <span class="text-muted"><i class="fa fa-calendar-alt mr-1"></i> Date:</span>
                <span>${node.posting_date}</span>
              </div>
            ` : ''}
          </div>

          <div class="sap-node-footer">
            <div class="sap-node-amt">
              ${node.grand_total > 0 ? `
                <span class="sap-amt-val">${format_currency(node.grand_total, node.currency || 'PHP')}</span>
              ` : (node.items_count > 0 ? `<span>${node.items_count} Items</span>` : `<span class="text-muted">Master Info</span>`)}
            </div>
            <div class="sap-node-actions">
              <button class="btn btn-default btn-xs sap-quick-view-btn" title="Inspect Document">
                <i class="fa fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    }

    renderItemsMatrix() {
      const $c = $(this.container || document);
      const $itemsView = $c.find('#sapItemsView');
      const items = this.data.items || [];
      const sum = this.data.summary || {};

      // Calculate totals using deduplicated metrics
      const totalLaborVal = sum.dedup_services_total !== undefined ? sum.dedup_services_total : 0;
      const totalPartsVal = sum.dedup_parts_total !== undefined ? sum.dedup_parts_total : 0;
      const uniquePartsCount = sum.unique_parts_count !== undefined ? sum.unique_parts_count : 0;
      const uniqueLaborCount = sum.unique_services_count !== undefined ? sum.unique_services_count : 0;
      
      const billedItems = items.filter(it => it.doc_type === 'Sales Invoice' || it.doc_type === 'POS Invoice' || it.doc_type === 'Vehicle POS Invoice');
      const totalBilledVal = billedItems.length > 0 
        ? billedItems.reduce((a, b) => a + (b.amount || 0), 0)
        : (sum.total_transaction_value || 0);

      // Filtering logic
      let filtered = items;
      if (this.itemFilter === "labor") {
        filtered = items.filter(it => (it.category === 'service' || (it.type || '').toLowerCase().includes('labor') || (it.type || '').toLowerCase().includes('service')));
      } else if (this.itemFilter === "parts") {
        filtered = items.filter(it => (it.category === 'part' || (it.type || '').toLowerCase().includes('part') || (it.type || '').toLowerCase().includes('material')));
      } else if (this.itemFilter === "billed") {
        filtered = items.filter(it => (it.type || '').toLowerCase().includes('billed') || it.doc_type === 'Sales Invoice' || it.doc_type === 'POS Invoice');
      }

      if (this.itemSearchTerm) {
        const term = this.itemSearchTerm.toLowerCase();
        filtered = filtered.filter(it => 
          (it.item_code || '').toLowerCase().includes(term) ||
          (it.description || '').toLowerCase().includes(term) ||
          (it.doc_name || '').toLowerCase().includes(term)
        );
      }

      let rowsHtml = '';
      filtered.forEach((it, idx) => {
        const typeClass = (it.type || '').includes('Labor') || (it.type || '').includes('Service') 
          ? 'badge-warning' 
          : ((it.type || '').includes('Billed') ? 'badge-success' : 'badge-primary');

        rowsHtml += `
          <tr>
            <td class="text-muted"><small>${idx + 1}</small></td>
            <td>
              <span class="badge badge-info">${it.doc_type}</span><br>
              <a href="javascript:void(0)" class="sap-doc-link font-weight-bold" data-dt="${it.doc_type}" data-dn="${it.doc_name}">${it.doc_name}</a>
            </td>
            <td><span class="badge ${typeClass}">${it.type}</span></td>
            <td>
              <strong class="text-dark">${it.item_code}</strong>
              ${it.description && it.description !== it.item_code ? `<br><small class="text-muted">${it.description}</small>` : ''}
            </td>
            <td class="text-right font-weight-bold" style="white-space: nowrap !important;">${it.qty} ${it.uom || ''}</td>
            <td class="text-right" style="white-space: nowrap !important; min-width: 110px;">${format_currency(it.rate, 'PHP')}</td>
            <td class="text-right font-weight-bold text-primary" style="white-space: nowrap !important; min-width: 120px;">${format_currency(it.amount, 'PHP')}</td>
            <td style="white-space: nowrap;"><small class="text-muted">${it.account || 'Income / Expense'}</small></td>
          </tr>
        `;
      });

      if (!rowsHtml) {
        rowsHtml = `<tr><td colspan="8" class="text-center text-muted p-4">No line items matching the current filter.</td></tr>`;
      }

      const totalUniqueItems = (uniquePartsCount + uniqueLaborCount) || 1;

      $itemsView.html(`
        <div class="sap-items-container" style="max-width: 1100px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; padding: 24px;">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h4 class="font-weight-bold m-0 text-dark"><i class="fa fa-list-alt text-primary mr-2"></i> Consolidated Related Items & Services Matrix</h4>
              <p class="text-muted mb-0 font-size-sm">Full lifecycle trace of all services, labor, parts, materials, and billed items in this workflow.</p>
            </div>
            <div class="sap-items-filter-bar btn-group">
              <button class="btn btn-xs ${this.itemFilter === 'all' ? 'btn-primary' : 'btn-default'} sap-item-filter-btn" data-filter="all">All (${items.length})</button>
              <button class="btn btn-xs ${this.itemFilter === 'labor' ? 'btn-primary' : 'btn-default'} sap-item-filter-btn" data-filter="labor"><i class="fa fa-wrench mr-1"></i> Labor / Services (${uniqueLaborCount})</button>
              <button class="btn btn-xs ${this.itemFilter === 'parts' ? 'btn-primary' : 'btn-default'} sap-item-filter-btn" data-filter="parts"><i class="fa fa-cogs mr-1"></i> Parts / Materials (${uniquePartsCount})</button>
              <button class="btn btn-xs ${this.itemFilter === 'billed' ? 'btn-primary' : 'btn-default'} sap-item-filter-btn" data-filter="billed"><i class="fa fa-check-circle mr-1"></i> Invoiced Lines</button>
            </div>
          </div>

          <!-- KPI Cards Ribbon -->
          <div class="row mb-3">
            <div class="col-md-3">
              <div class="p-2 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Total Services / Labor</small>
                <div class="font-weight-bold text-warning font-size-lg" style="white-space: nowrap;">${format_currency(totalLaborVal, 'PHP')} (${uniqueLaborCount} items)</div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="p-2 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Total Spare Parts</small>
                <div class="font-weight-bold text-primary font-size-lg" style="white-space: nowrap;">${format_currency(totalPartsVal, 'PHP')} (${uniquePartsCount} items)</div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="p-2 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Final Billed Value</small>
                <div class="font-weight-bold text-success font-size-lg" style="white-space: nowrap;">${format_currency(totalBilledVal, 'PHP')}</div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="p-2 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Distinct Workflow Items</small>
                <div class="font-weight-bold text-dark font-size-lg" style="white-space: nowrap;">${totalUniqueItems} Item (${items.length} Doc Lines)</div>
              </div>
            </div>
          </div>

          <div class="table-responsive rounded border">
            <table class="table table-hover table-striped mb-0">
              <thead class="thead-light">
                <tr>
                  <th style="width: 40px; white-space: nowrap;">#</th>
                  <th style="white-space: nowrap; min-width: 140px;">Source Document</th>
                  <th style="white-space: nowrap; min-width: 140px;">Category</th>
                  <th style="min-width: 180px;">Item / Service Code & Name</th>
                  <th class="text-right" style="white-space: nowrap; min-width: 90px;">Qty / Hours</th>
                  <th class="text-right" style="white-space: nowrap; min-width: 110px;">Rate</th>
                  <th class="text-right" style="white-space: nowrap; min-width: 120px;">Total Amount</th>
                  <th style="white-space: nowrap; min-width: 160px;">Accounting / Cost Account</th>
                </tr>
              </thead>
              <tbody>${rowsHtml}</tbody>
            </table>
          </div>
        </div>
      `);

      // Bind filter buttons
      $itemsView.find('.sap-item-filter-btn').on('click', (e) => {
        this.itemFilter = $(e.currentTarget).data('filter');
        this.renderItemsMatrix();
      });

      $itemsView.find('.sap-doc-link').on('click', (e) => {
        const dt = $(e.currentTarget).data('dt');
        const dn = $(e.currentTarget).data('dn');
        if (dt && dn) {
          if (this.dialog) this.dialog.hide();
          frappe.set_route('Form', dt, dn);
        }
      });
    }

    renderAccountingFlow() {
      const $c = $(this.container || document);
      const $acctView = $c.find('#sapAccountingView');
      const acct = this.data.accounting || {};
      const sum = this.data.summary || {};
      const glEntries = acct.gl_entries || [];
      const vouchersGlMap = acct.vouchers_gl_map || {};
      const pleList = acct.payment_ledger || [];

      let voucherCardsHtml = '';
      const voucherKeys = Object.keys(vouchersGlMap);

      if (voucherKeys.length === 0) {
        voucherCardsHtml = `
          <div class="alert alert-info text-center p-4">
            <i class="fa fa-info-circle fa-2x mb-2"></i>
            <h5>No Accounting or GL Postings Found</h5>
            <p class="mb-0 text-muted">This transaction is currently in draft or has not yet posted financial journal entries to the General Ledger.</p>
          </div>
        `;
      } else {
        voucherKeys.forEach(vKey => {
          const [vType, vNo] = vKey.split('::');
          const entries = vouchersGlMap[vKey] || [];
          const postDate = entries[0]?.posting_date || '';

          let glRows = '';
          entries.forEach(gl => {
            glRows += `
              <tr>
                <td style="white-space: nowrap !important;"><strong>${gl.account}</strong></td>
                <td style="white-space: nowrap !important;"><small class="text-muted">${gl.cost_center || '-'}</small></td>
                <td class="text-right font-weight-bold ${gl.debit > 0 ? 'text-primary' : 'text-muted'}" style="white-space: nowrap !important; min-width: 120px;">${gl.debit > 0 ? format_currency(gl.debit, 'PHP') : '-'}</td>
                <td class="text-right font-weight-bold ${gl.credit > 0 ? 'text-success' : 'text-muted'}" style="white-space: nowrap !important; min-width: 120px;">${gl.credit > 0 ? format_currency(gl.credit, 'PHP') : '-'}</td>
                <td><small class="text-muted">${gl.remarks || ''}</small></td>
              </tr>
            `;
          });

          voucherCardsHtml += `
            <div class="card mb-4 shadow-sm border" style="border-radius: 10px; overflow: hidden;">
              <div class="card-header bg-light d-flex justify-content-between align-items-center py-2 px-3 border-bottom">
                <div style="white-space: nowrap !important;">
                  <span class="badge ${vType === 'Sales Invoice' ? 'badge-primary' : 'badge-success'} mr-2 font-size-sm">${vType}</span>
                  <a href="javascript:void(0)" class="sap-doc-link font-weight-bold text-dark" data-dt="${vType}" data-dn="${vNo}">${vNo}</a>
                </div>
                <div style="white-space: nowrap !important;">
                  <span class="text-muted"><i class="fa fa-calendar-alt mr-1"></i> Posting Date: <strong>${postDate || '-'}</strong></span>
                </div>
              </div>
              <div class="table-responsive mb-0">
                <table class="table table-sm table-hover mb-0">
                  <thead class="thead-light">
                    <tr>
                      <th style="width: 35%; white-space: nowrap !important;">Ledger Account</th>
                      <th style="width: 15%; white-space: nowrap !important;">Cost Center</th>
                      <th class="text-right" style="width: 15%; white-space: nowrap !important; min-width: 120px;">Debit (Dr)</th>
                      <th class="text-right" style="width: 15%; white-space: nowrap !important; min-width: 120px;">Credit (Cr)</th>
                      <th style="width: 20%; white-space: nowrap !important;">Remarks</th>
                    </tr>
                  </thead>
                  <tbody>${glRows}</tbody>
                </table>
              </div>
            </div>
          `;
        });
      }

      // Reconciliation / PLE Table
      let pleRowsHtml = '';
      pleList.forEach(p => {
        pleRowsHtml += `
          <tr>
            <td style="white-space: nowrap !important;"><span class="badge badge-info mr-1">${p.voucher_type}</span> <strong>${p.voucher_no}</strong></td>
            <td style="white-space: nowrap !important;"><span class="badge badge-secondary mr-1">${p.against_voucher_type || '-'}</span> ${p.against_voucher_no || '-'}</td>
            <td style="white-space: nowrap !important;">${p.account}</td>
            <td style="white-space: nowrap !important;">${p.party || '-'}</td>
            <td class="text-right font-weight-bold ${p.amount < 0 ? 'text-success' : 'text-primary'}" style="white-space: nowrap !important; min-width: 120px;">${format_currency(p.amount, 'PHP')}</td>
          </tr>
        `;
      });

      const totalRevenueVal = acct.total_revenue || sum.total_transaction_value || 0;
      const totalCollectedVal = acct.total_collected || sum.total_paid_value || 0;
      const outstandingVal = sum.total_outstanding_value !== undefined ? sum.total_outstanding_value : 0;

      $acctView.html(`
        <div class="sap-accounting-container" style="max-width: 1000px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; padding: 24px;">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h4 class="font-weight-bold m-0 text-dark"><i class="fa fa-balance-scale text-success mr-2"></i> Accounting & General Ledger Postings</h4>
              <p class="text-muted mb-0 font-size-sm">Double-entry accounting journal entries, debit/credit ledger breakdown, and reconciliation flow.</p>
            </div>
            <div style="white-space: nowrap !important;">
              <span class="badge ${acct.is_balanced ? 'badge-success' : 'badge-danger'} p-2 font-size-sm" title="Gross GL Turnover: Dr ${format_currency(acct.total_debit || 0, 'PHP')} | Cr ${format_currency(acct.total_credit || 0, 'PHP')}">
                <i class="fa ${acct.is_balanced ? 'fa-check-circle' : 'fa-exclamation-triangle'} mr-1"></i>
                ${acct.is_balanced ? 'Double-Entry Balanced' : 'Ledger Imbalance Detected'}
              </span>
            </div>
          </div>

          <!-- KPI Summary Ribbon -->
          <div class="row mb-4">
            <div class="col-md-4">
              <div class="p-3 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Total Invoiced / GL Revenue</small>
                <div class="font-weight-bold text-primary font-size-lg" style="white-space: nowrap !important;">${format_currency(totalRevenueVal, 'PHP')}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="p-3 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Total Collections (Cash/Bank)</small>
                <div class="font-weight-bold text-success font-size-lg" style="white-space: nowrap !important;">${format_currency(totalCollectedVal, 'PHP')}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="p-3 border rounded bg-light text-center">
                <small class="text-muted text-uppercase font-weight-bold">Party Net Receivable Balance</small>
                <div class="font-weight-bold ${outstandingVal === 0 ? 'text-success' : 'text-danger'} font-size-lg" style="white-space: nowrap !important;">
                  ${format_currency(outstandingVal, 'PHP')}
                </div>
              </div>
            </div>
          </div>

          <!-- Voucher Journal Breakdown Cards -->
          <h5 class="font-weight-bold text-dark mb-3"><i class="fa fa-book-open text-primary mr-1"></i> Journal Vouchers & GL Impact</h5>
          ${voucherCardsHtml}

          <!-- Payment Ledger Reconciliation Trace -->
          ${pleRowsHtml ? `
            <div class="mt-4 pt-3 border-top">
              <h5 class="font-weight-bold text-dark mb-3"><i class="fa fa-handshake text-info mr-1"></i> Payment Ledger Entry (PLE) Settlement Trace</h5>
              <div class="table-responsive rounded border">
                <table class="table table-sm table-hover mb-0">
                  <thead class="thead-light">
                    <tr>
                      <th style="white-space: nowrap !important;">Voucher</th>
                      <th style="white-space: nowrap !important;">Against Voucher</th>
                      <th style="white-space: nowrap !important;">Account</th>
                      <th style="white-space: nowrap !important;">Party</th>
                      <th class="text-right" style="white-space: nowrap !important; min-width: 120px;">Allocated Amount</th>
                    </tr>
                  </thead>
                  <tbody>${pleRowsHtml}</tbody>
                </table>
              </div>
            </div>
          ` : ''}
        </div>
      `);

      $acctView.find('.sap-doc-link').on('click', (e) => {
        const dt = $(e.currentTarget).data('dt');
        const dn = $(e.currentTarget).data('dn');
        if (dt && dn) {
          if (this.dialog) this.dialog.hide();
          frappe.set_route('Form', dt, dn);
        }
      });
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
                      <td class="text-right"><small>${it.qty} ${it.uom || ''}</small></td>
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

        ${itemsHtml}

        ${node.remarks ? `
          <div class="sap-drawer-sec">
            <div class="sap-drawer-sec-title">Remarks / Notes</div>
            <p class="small text-muted p-2 bg-light rounded">${node.remarks}</p>
          </div>
        ` : ''}
      `;

      $c.find('#sapDrawerBody').html(bodyHtml);
      $c.find('#sapDrawerFooter').show();

      $c.find('#sapOpenDocBtn').off('click').on('click', () => {
        if (this.dialog) this.dialog.hide();
        frappe.set_route('Form', node.doctype, node.name);
      });
    }

    fitToScreen() {
      const $viewport = $(this.container || document).find('#sapViewport');
      const vWidth = $viewport.width();
      const vHeight = $viewport.height();

      this.zoom = Math.min(vWidth / 1300, vHeight / 800, 1.2);
      this.panX = 30;
      this.panY = 30;
      this.applyTransform();
    }
  }

  window.SAPRelationshipMap.Viewer = SAPMapViewer;

  window.SAPRelationshipMap.openModal = function (doctype, docname, vehicle, customer) {
    const d = new frappe.ui.Dialog({
      title: `<span class="badge badge-info mr-1">VMS</span> Relationship Map & Document Flow`,
      size: 'extra-large',
      fields: [
        {
          fieldtype: 'HTML',
          fieldname: 'sap_map_area'
        }
      ]
    });

    d.show();
    d.$wrapper.find('.modal-dialog').css({
      'max-width': '96vw',
      'width': '96vw',
      'height': '92vh',
      'margin': '2vh auto'
    });
    d.$wrapper.find('.modal-content').css({
      'height': '92vh',
      'display': 'flex',
      'flex-direction': 'column'
    });
    d.$wrapper.find('.modal-body').css({
      'padding': '0',
      'flex': '1',
      'overflow': 'hidden',
      'position': 'relative',
      'display': 'flex',
      'flex-direction': 'column'
    });
    d.$wrapper.find('.modal-body .form-layout, .modal-body .form-page, .modal-body .form-section, .modal-body .form-column, .modal-body [data-fieldname="sap_map_area"]').css({
      'height': '100%',
      'min-height': '100%',
      'display': 'flex',
      'flex-direction': 'column',
      'flex': '1',
      'padding': '0',
      'margin': '0'
    });

    const container = d.fields_dict.sap_map_area.$wrapper[0];
    $(container).css({
      'height': '100%',
      'min-height': '100%',
      'display': 'flex',
      'flex-direction': 'column',
      'flex': '1'
    });

    new SAPMapViewer({
      doctype: doctype,
      docname: docname,
      vehicle: vehicle,
      customer: customer,
      container: container,
      isModal: true,
      dialog: d
    });
  };

  // Attach button to supported DocTypes
  const targetDocTypes = [
    'Vehicle Job Order',
    'Vehicle Estimate',
    'Vehicle Inspection',
    'Vehicle POS Invoice',
    'Customer Vehicle',
    'Sales Invoice',
    'Payment Entry'
  ];

  targetDocTypes.forEach(dt => {
    frappe.ui.form.on(dt, {
      refresh: function (frm) {
        if (!frm.is_new()) {
          frm.add_custom_button(__('VMS Relationship Map'), function () {
            let veh = frm.doc.plate_no || frm.doc.vehicle || frm.doc.custom_vehicle_plate || '';
            let cust = frm.doc.customer_name || frm.doc.customer || frm.doc.party_name || '';
            window.SAPRelationshipMap.openModal(frm.doctype, frm.doc.name, veh, cust);
          }, __('View'));
        }
      }
    });
  });

})();
