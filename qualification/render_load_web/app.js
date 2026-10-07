'use strict';
const DATA = JSON.parse(document.getElementById('benchmark-data').textContent);
const $ = id => document.getElementById(id);
const COLORS = {static:'#7b8580',fills:'#9662ac',primitives:'#287caf',bitmaps:'#cf8134',sprites:'#1b927c',overlap:'#bd5c73',text_scroll:'#998b25',mixed:'#525db3'};
const NAMES = {static:'Static control',fills:'Rectangle fills',primitives:'Primitives',bitmaps:'Bitmaps',sprites:'Moving sprites',overlap:'Sprite overlap',text_scroll:'Text / scroll',mixed:'Mixed objects'};
const fmt = (n, digits=2) => Number.isFinite(n) ? n.toFixed(digits) : '—';
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const key = r => `${r.family}/${r.variant}`;
const label = r => `${NAMES[r.family]}${r.variant===r.family||r.variant==='static'?'':` · ${r.variant}`}`;
let visibleRows=[], selectedCase=null, plotEventsBound=false, renderVersion=0;
const metricKeys = () => $('metric').value==='median'
  ? ['mainboard_completion_median_ms','p4_completion_median_ms'] : ['mainboard_p95_ms','p4_p95_ms'];
const difference = r => {const [a,b]=metricKeys();return (r[b]/r[a]-1)*100;};
const CONFIG={responsive:true,displaylogo:false,scrollZoom:false,toImageButtonOptions:{format:'svg',filename:'agon-rendering-completion'},modeBarButtonsToRemove:['lasso2d','select2d']};
const baseLayout = () => ({font:{family:'system-ui, sans-serif',size:12,color:'#41564a'},paper_bgcolor:'#fff',plot_bgcolor:'#fff',margin:{l:72,r:32,t:48,b:82},hovermode:'closest',legend:{orientation:'h',x:0,y:-.2,font:{size:10}},uirevision:'filtered-view'});
const axis = title => ({title:{text:title,standoff:12},type:$('scale').value,gridcolor:'#e5ebe6',zeroline:false,showline:true,linecolor:'#bac9be',ticks:'outside'});
const budgetLine = (orientation, value=1000/60) => orientation==='horizontal'
  ? {type:'line',xref:'x domain',x0:0,x1:1,y0:value,y1:value,line:{color:'#b54e3e',width:1.5,dash:'dot'}}
  : {type:'line',yref:'y domain',y0:0,y1:1,x0:value,x1:value,line:{color:'#b54e3e',width:1.5,dash:'dot'}};

function hover(r){
  const [a,b]=metricKeys();
  return `<b>${esc(label(r))} · load ${r.level}</b><br>Case ${r.case}<br>Mainboard: ${fmt(r[a],3)} ms<br>P4: ${fmt(r[b],3)} ms<br>P4 / mainboard: ${fmt(r[b]/r[a],2)}× (${difference(r)>=0?'+':''}${fmt(difference(r),1)}%)<br>Paired passes: ${r.paired_passes.join(', ')} / planned 3<br>P4 framebuffer submissions: ${fmt(r.p4_conversion_updates_per_second)} /s`;
}

function comparisonTraces(rows){
  const [a,b]=metricKeys(), traces=[];
  for(const family of Object.keys(NAMES)){
    const rr=rows.filter(r=>r.family===family);
    if(!rr.length)continue;
    traces.push({type:'scatter',mode:'markers',name:NAMES[family],legendgroup:family,
      x:rr.map(r=>r[a]),y:rr.map(r=>r[b]),customdata:rr.map(r=>r.case),
      hovertext:rr.map(hover),hovertemplate:'%{hovertext}<extra></extra>',
      marker:{color:COLORS[family],size:rr.map(r=>5+2*Math.log2(Math.max(1,r.level))),opacity:.88,line:{color:'#fff',width:1}},
      error_x:{type:'data',symmetric:false,visible:$('ranges').checked,
        array:rr.map(r=>Math.max(0,r.mainboard_completion_range_ms[1]-r[a])),
        arrayminus:rr.map(r=>Math.max(0,r[a]-r.mainboard_completion_range_ms[0])),color:COLORS[family],thickness:1},
      error_y:{type:'data',symmetric:false,visible:$('ranges').checked,
        array:rr.map(r=>Math.max(0,r.p4_completion_range_ms[1]-r[b])),
        arrayminus:rr.map(r=>Math.max(0,r[b]-r.p4_completion_range_ms[0])),color:COLORS[family],thickness:1}});
  }
  if($('connect').checked){
    const groups=new Map();
    rows.filter(r=>r.level>0).forEach(r=>{if(!groups.has(key(r)))groups.set(key(r),[]);groups.get(key(r)).push(r);});
    for(const rr of groups.values()){
      rr.sort((x,y)=>x.level-y.level);
      const xs=[],ys=[];
      rr.forEach((r,i)=>{if(i && DATA.levels.indexOf(r.level)!==DATA.levels.indexOf(rr[i-1].level)+1){xs.push(null);ys.push(null);}xs.push(r[a]);ys.push(r[b]);});
      traces.unshift({type:'scatter',mode:'lines',x:xs,y:ys,showlegend:false,hoverinfo:'skip',line:{color:COLORS[rr[0].family],width:1.1},opacity:.45});
    }
  }
  return traces;
}

function curveTraces(rows){
  const [a,b]=metricKeys(), traces=[];
  for(const [endpoint,k,color,symbol] of [['Mainboard VDP',a,'#3d5549','square'],['P4 VDP',b,'#257baa','circle']]){
    const ordered=DATA.levels.map(level=>rows.find(r=>r.level===level));
    traces.push({type:'scatter',name:endpoint,mode:'lines+markers',x:DATA.levels,
      y:ordered.map(r=>r?r[k]:null),customdata:ordered.map(r=>r?r.case:null),connectgaps:false,
      hovertext:ordered.map(r=>r?hover(r):''),hovertemplate:'%{hovertext}<extra>'+endpoint+'</extra>',
      line:{color,width:2.2},marker:{color,size:9,symbol},
      error_y:{type:'data',symmetric:false,visible:$('ranges').checked,
        array:ordered.map(r=>r?Math.max(0,r[endpoint==='P4 VDP'?'p4_completion_range_ms':'mainboard_completion_range_ms'][1]-r[k]):0),
        arrayminus:ordered.map(r=>r?Math.max(0,r[k]-r[endpoint==='P4 VDP'?'p4_completion_range_ms':'mainboard_completion_range_ms'][0]):0)}});
  }
  return traces;
}

function updateWorkloads(){
  const old=$('workload').value, family=$('family').value, mode=+$('mode').value, style=$('style').value;
  const groups=new Map();
  DATA.rows.filter(r=>r.mode===mode&&r.style===style&&r.level>0&&(family==='all'||r.family===family)).forEach(r=>groups.set(key(r),label(r)));
  $('workload').replaceChildren(...[...groups].sort((a,b)=>a[1].localeCompare(b[1])).map(([value,text])=>new Option(text,value)));
  if(groups.has(old))$('workload').value=old;
  else if(groups.has('primitives/circles'))$('workload').value='primitives/circles';
  $('workload').disabled=!groups.size;
}

async function render(){
  const ticket=++renderVersion;window.renderReady=false;
  const mode=+$('mode').value, style=$('style').value, family=$('family').value, [a,b]=metricKeys();
  visibleRows=DATA.rows.filter(r=>r.mode===mode&&r.style===style&&(family==='all'||r.family===family));
  const stat=$('metric').value==='median'?'median completion':'per-pass p95 completion';
  $('ranges').disabled=$('metric').value!=='median';
  if($('ranges').disabled)$('ranges').checked=false;
  const m=DATA.modes[mode];
  const passes=[...new Set(visibleRows.map(r=>r.paired_passes.length))].sort();
  $('scope').textContent=`${visibleRows.length} matched workloads · ${passes.join(' or ')||'0'} of 3 paired passes available · ${m.double_buffered?'Double-buffer swap waits included.':'Single-buffer mode.'} ${$('metric').value==='median'?'Median of paired pass medians.':'Median of paired per-pass 95th percentiles.'} Larger dots indicate higher load. Lines follow each variant’s load order; missing levels remain gaps.`;
  const values=visibleRows.flatMap(r=>[r[a],r[b]]), low=Math.min(.5,...values)/1.15, high=Math.max(1000/60,...values)*1.14;
  const scatterLayout={...baseLayout(),xaxis:axis(`Mainboard ${stat} (ms)`),yaxis:axis(`P4 ${stat} (ms)`),shapes:[{type:'line',x0:$('scale').value==='log'?low:0,y0:$('scale').value==='log'?low:0,x1:high,y1:high,line:{color:'#84988a',width:1.3,dash:'dash'}},budgetLine('horizontal'),budgetLine('vertical')]};
  scatterLayout.title={text:`Mode ${mode} · ${m.width}×${m.height} · ${m.colours} colours · ${m.double_buffered?'double':'single'} · ${style}`,font:{size:12},x:.05};
  const domain=$('scale').value==='log'?[Math.log10(low),Math.log10(high)]:[0,high];
  scatterLayout.xaxis.range=domain;scatterLayout.yaxis.range=domain;
  scatterLayout.xaxis.constrain='domain';scatterLayout.yaxis.constrain='domain';
  scatterLayout.yaxis.scaleanchor='x';scatterLayout.yaxis.scaleratio=1;
  const curveRows=visibleRows.filter(r=>key(r)===$('workload').value);
  const curveLayout={...baseLayout(),xaxis:{...axis('Load level'),type:'log',tickmode:'array',tickvals:DATA.levels,ticktext:DATA.levels.map(String),range:[-.12,Math.log10(64)+.12]},yaxis:axis(`${stat[0].toUpperCase()+stat.slice(1)} (ms)`),shapes:[budgetLine('horizontal')]};
  curveLayout.title={text:`Mode ${mode} · ${style} · ${curveRows.length?esc(label(curveRows[0])):'static controls'}`,font:{size:12},x:.05};
  if($('scale').value==='linear')curveLayout.yaxis.rangemode='tozero';
  if(!curveRows.length)curveLayout.annotations=[{text:'No matched load ramp in this selection',xref:'paper',yref:'paper',x:.5,y:.5,showarrow:false}];
  $('curve-caption').textContent=curveRows.length?`Load = ${DATA.level_meanings[curveRows[0].family]}. The load axis spaces levels 1, 4, 16, 64 evenly; hover shows each exact value.`:'Static controls have no increasing-load curve.';
  const imageConfig=id=>({...CONFIG,toImageButtonOptions:{format:'svg',filename:`agon-mode${mode}-${style}-${$('metric').value}-${id}`}});
  await Promise.all([Plotly.react('scatter',comparisonTraces(visibleRows),scatterLayout,imageConfig('scatter')),Plotly.react('curve',curveTraces(curveRows),curveLayout,imageConfig('curve'))]);
  if(ticket!==renderVersion)return;
  if(!plotEventsBound){
    for(const id of ['scatter','curve'])$(id).on('plotly_click',e=>{const caseId=e.points[0].customdata;if(caseId!=null)selectCase(caseId);});
    plotEventsBound=true;
  }
  $('main-heading').textContent=`Mainboard ${$('metric').value} ms`;$('p4-heading').textContent=`P4 ${$('metric').value} ms`;
  const sorted=[...visibleRows].sort((x,y)=>difference(y)-difference(x));
  $('rows').innerHTML=sorted.map(r=>`<tr data-case="${r.case}" tabindex="0"><td>${r.case} · ${esc(label(r))}</td><td>${r.level}</td><td>${fmt(r[a],3)}</td><td>${fmt(r[b],3)}</td><td class="${difference(r)>=0?'slow':'fast'}">${difference(r)>=0?'+':''}${fmt(difference(r),1)}%</td><td class="${r.p4_conversion_updates_per_second===0?'zero':''}">${fmt(r.p4_conversion_updates_per_second)}</td><td>${r.paired_passes.length}/3</td></tr>`).join('');
  for(const tr of $('rows').children){tr.addEventListener('click',()=>selectCase(+tr.dataset.case));tr.addEventListener('keydown',e=>{if(e.key==='Enter')selectCase(+tr.dataset.case);});}
  if(selectedCase!=null && visibleRows.some(r=>r.case===selectedCase))selectCase(selectedCase);
  else{selectedCase=null;$('detail').innerHTML='<h2>Inspect a workload</h2><p>Click a plotted point or a row to compare completion with application updates and P4 HDMI submissions.</p>';}
  window.renderReady=true;
}

function selectCase(id){
  const r=visibleRows.find(r=>r.case===id);if(!r)return;
  selectedCase=id;const [a,b]=metricKeys();
  const cards=[['Mainboard completion',`${fmt(r[a],3)} ms`],['P4 completion',`${fmt(r[b],3)} ms`],['P4 / mainboard',`${fmt(r[b]/r[a])}×`],['P4 framebuffer submissions',`${fmt(r.p4_conversion_updates_per_second)} /s`],['Mainboard application updates',`${fmt(r.mainboard_app_updates_per_second)} /s`],['P4 application updates',`${fmt(r.p4_app_updates_per_second)} /s`],['P4 DMA scanout proxy',`${fmt(r.p4_dma_scanouts_per_second)} Hz`],['Matching pass numbers',r.paired_passes.join(', ')+' / planned 3']];
  $('detail').innerHTML=`<h2>Case ${r.case} · ${esc(label(r))} · load ${r.level}</h2><dl class="detail-grid">${cards.map(([name,value])=>`<div><dt>${esc(name)}</dt><dd>${esc(value)}</dd></div>`).join('')}</dl><p>${r.variant==='hardware'?'Hardware-sprite recurring composition is outside the command fence. ':''}${r.p4_conversion_updates_per_second===0?'No accepted P4 framebuffer submission occurred in these paired windows. ':''}Completion times and output counters describe different work. ${r.style==='paced'?'Application updates are deliberately paced toward 60 Hz.':''}</p><p class="runs">Mainboard runs: ${esc(r.runs.mainboard.join(' · '))}<br>P4 runs: ${esc(r.runs.p4.join(' · '))}</p>`;
  for(const tr of $('rows').children)tr.classList.toggle('selected',+tr.dataset.case===id);
}

function exportCsv(){
  const [a,b]=metricKeys(), fields=['mode','case','family','variant','level','style',a,b,'difference_percent','p4_conversion_updates_per_second','paired_passes'];
  const quote=x=>'"'+String(x).replace(/"/g,'""')+'"';
  const text=[fields.map(quote).join(','),...visibleRows.map(r=>fields.map(k=>quote(k==='difference_percent'?difference(r):k==='paired_passes'?r[k].join(';'):r[k])).join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'})),link=document.createElement('a');link.href=url;link.download=`agon-completion-mode${$('mode').value}-${$('style').value}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

for(const mode of [20,8,136,21,149]){
  const m=DATA.modes[mode];$('mode').add(new Option(`${mode} · ${m.width}×${m.height} · ${m.colours} colours · ${m.double_buffered?'double':'single'}`,mode));
}
for(const [family,name] of Object.entries(NAMES))$('family').add(new Option(name,family));
$('source').textContent=`${DATA.source_label} · ${DATA.contract}`;
$('coverage-badge').textContent=DATA.coverage.complete?'Complete valid coverage':'Partial campaign';
$('paired-count').textContent=DATA.rows.length;
$('valid-count').textContent=DATA.audit.valid_measurements.toLocaleString();
$('failed-count').textContent=DATA.audit.failed_or_invalid_executions;
$('pending-count').textContent=(DATA.audit.expected_case_executions-DATA.audit.executions_accounted).toLocaleString();
$('audit-note').textContent=`Raw provenance audit passes; ${DATA.snapshot_hashes_verified?'snapshot input hashes verified.':'input hashes recorded; no snapshot manifest supplied.'} ${DATA.zero_submission_windows} retained normal-HDMI windows have zero submissions. ${DATA.exclusions} excluded run/case entries remain in the retained analysis. Held/off controls and complete three-pass coverage remain pending in this snapshot.`;
$('generated').textContent=`Generated ${DATA.generated_utc} · inputs and generator hashes in the adjacent provenance file`;
for(const id of ['mode','style','metric','scale','family','connect','ranges'])$(id).addEventListener('change',()=>{updateWorkloads();render().catch(showError);});
$('workload').addEventListener('change',()=>render().catch(showError));$('csv').addEventListener('click',exportCsv);
function showError(error){$('scope').textContent='Plot error: '+error.message;console.error(error);}
updateWorkloads();render().catch(showError);
