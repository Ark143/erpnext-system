      // Native SVG is required: jQuery parses SVG strings as HTML and hides paths.
      // Keep arrows in the canvas coordinate system so they follow zoom and pan.
      {
        const svgNS = 'http://www.w3.org/2000/svg';
        const layer = $svgEdges[0];
        const make = (tag, attrs, text) => {
          const el = document.createElementNS(svgNS, tag);
          Object.entries(attrs || {}).forEach(([key, value]) => el.setAttribute(key, String(value)));
          if (text !== undefined) el.textContent = text;
          return el;
        };
        $nodesLayer.find('.sap-node-card').each(function () {
          const c = nodeCoords[this.getAttribute('data-node-id')];
          if (c) { c.bottom = c.top + this.offsetHeight; c.cy = (c.top + c.bottom) / 2; }
        });
        const positions = Object.values(nodeCoords);
        const lowerLane = Math.max(0, ...positions.map(c => c.bottom)) + 35;
        const graphWidth = Math.max(0, ...positions.map(c => c.right)) + 150;
        const graphHeight = lowerLane + 180;
        layer.ownerSVGElement.setAttribute('width', graphWidth);
        layer.ownerSVGElement.setAttribute('height', graphHeight);
        layer.replaceChildren();
        edges.forEach((edge, index) => {
          const from = nodeCoords[edge.from], to = nodeCoords[edge.to];
          if (!from || !to || edge.from === edge.to) return;
          const sameColumn = from.x === to.x;
          const direction = to.x >= from.x ? 1 : -1;
          const start = {x: direction > 0 ? from.right + 2 : from.left - 2, y: from.cy};
          const end = {x: direction > 0 ? to.left - 7 : to.right + 7, y: to.cy};
          let path, labelX, labelY, arrowDirection = direction;
          if (sameColumn) {
            start.x = from.right + 2; end.x = to.right + 7;
            const lane = Math.max(from.right, to.right) + 45 + (index % 4) * 13;
            path = `M ${start.x} ${start.y} C ${lane} ${start.y}, ${lane} ${end.y}, ${end.x} ${end.y}`;
            labelX = lane; labelY = (start.y + end.y) / 2;
            arrowDirection = -1;
          } else if (Math.abs(to.x - from.x) > cardWidth + colGap + 5) {
            // Skip-stage links travel below the cards rather than through them.
            const lane = lowerLane + (index % 6) * 24;
            const outX = start.x + direction * 24, inX = end.x - direction * 24;
            path = `M ${start.x} ${start.y} L ${outX} ${start.y} L ${outX} ${lane} L ${inX} ${lane} L ${inX} ${end.y} L ${end.x} ${end.y}`;
            labelX = (outX + inX) / 2; labelY = lane;
          } else {
            const dx = Math.abs(end.x - start.x) / 2;
            path = `M ${start.x} ${start.y} C ${start.x + direction * dx} ${start.y}, ${end.x - direction * dx} ${end.y}, ${end.x} ${end.y}`;
            labelX = (start.x + end.x) / 2; labelY = (start.y + end.y) / 2;
          }
          const label = String(edge.label || 'Related document');
          const color = edge.type === 'accounting' || /payment/i.test(label) ? '#15803d' :
            edge.type === 'reference' ? '#7e22ce' : /converted|procured/i.test(label) ? '#b45309' : '#2563eb';
          const group = make('g', {'class':'sap-edge-group','data-from':edge.from,'data-to':edge.to,'aria-label':`${edge.from} → ${edge.to}: ${label}`});
          group.appendChild(make('title', {}, `${edge.from} → ${edge.to}: ${label}`));
          group.appendChild(make('path', {d:path,fill:'none',stroke:color,'stroke-width':3,'stroke-linejoin':'round','stroke-dasharray':edge.type === 'reference' ? '6 4' : 'none'}));
          // Explicit polygon avoids duplicate marker IDs when two maps are open.
          group.appendChild(make('polygon', {'class':'sap-edge-arrow',points:`${end.x},${end.y} ${end.x-arrowDirection*13},${end.y-6} ${end.x-arrowDirection*13},${end.y+6}`,fill:color}));
          group.appendChild(make('circle', {cx:start.x,cy:start.y,r:3,fill:color}));
          const shown = label.length > 24 ? label.slice(0,21)+'…' : label;
          const width = Math.max(66, shown.length * 5.7 + 12);
          group.appendChild(make('rect', {x:labelX-width/2,y:labelY-10,width,height:20,rx:10,fill:'#fff',stroke:color}));
          group.appendChild(make('text', {x:labelX,y:labelY+3.5,'text-anchor':'middle','font-size':10,'font-weight':600,fill:color}, shown));
          layer.appendChild(group);
        });
      }
