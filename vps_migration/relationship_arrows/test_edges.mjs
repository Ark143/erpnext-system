import fs from 'node:fs';
import assert from 'node:assert/strict';
const ns='http://www.w3.org/2000/svg';
function element(tag,namespaceURI=ns){return {tag,namespaceURI,attrs:{},children:[],setAttribute(k,v){this.attrs[k]=String(v);},appendChild(el){this.children.push(el);},replaceChildren(){this.children=[];}};}
const document={createElementNS:(namespace,tag)=>element(tag,namespace)};
const layer=element('g');layer.ownerSVGElement=element('svg');
const coord=(x,y)=>({x,y,left:x,right:x+265,top:y,bottom:y+165,cy:y+82.5});
const coords={a:coord(60,80),b:coord(445,80),c:coord(830,80),d:coord(60,280)};
const edges=[{from:'a',to:'b',label:'Received'},{from:'b',to:'a',label:'Return'},
 {from:'a',to:'c',label:'<img src=x onerror=alert(1)>',type:'reference'},
 {from:'a',to:'d',label:'Inspection'}, {from:'ghost',to:'b'}, {from:'a',to:'a'}];
const run=new Function('document','$svgEdges','$nodesLayer','nodeCoords','edges','cardWidth','colGap',fs.readFileSync(new URL('./draw_edges.js',import.meta.url),'utf8'));
for(let pass=0;pass<2;pass++){
 run(document,[layer],{find:()=>({each(){}})},coords,edges,265,120);
 assert.equal(layer.children.length,4,'valid links only; repeat render must replace');
 for(const group of layer.children){
  assert(group.children.every(e=>e.namespaceURI===ns));
  assert.equal(group.children.filter(e=>e.tag==='polygon').length,1);
  assert(!group.children.find(e=>e.tag==='path').attrs.d.includes('NaN'));
 }
 assert(layer.children[2].children.find(e=>e.tag==='path').attrs.d.includes(' L '),'skip link uses outer lane');
 assert.equal(layer.children[2].children.find(e=>e.tag==='path').attrs['stroke-dasharray'],'6 4');
 assert(layer.children[2].children.find(e=>e.tag==='text').textContent.startsWith('<img'),'untrusted labels remain text');
}
console.log('PASS: native SVG, forward/reverse/same-column/skip-stage links, arrowheads, safe labels, missing links and repeat rendering');
