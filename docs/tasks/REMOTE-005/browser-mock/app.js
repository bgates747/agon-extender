/* Isolated simulation; no network or user-file content access.
   ESPFMfGK layout/serial-upload idioms informed this adaptation, full upstream notice
   retained. Queue, synthetic backend, selection and event handling are new. */
'use strict';
const $ = id => document.getElementById(id);
const dir = children => ({kind:'folder',children});
const file = size => ({kind:'file',size});
const seed = () => dir({extender:dir({'readme.txt':file(2400),install:dir({'emos.bin':file(125000)})}),mystuff:dir({nurples:dir({'nurples.bin':file(47000),'tiles.agnb':file(88000),saves:dir({})}),slideshow:dir({'scene01.rgb':file(76800),'scene02.rgb':file(76800)})}),stress:dir({...Object.fromEntries(Array.from({length:128},(_,i)=>[`asset-${String(i+1).padStart(3,'0')}.bin`,file(1024+i*13)])),'empty-folder':dir({})}),'autoexec.txt':file(95)});
let tree=seed(), current='/', selected=new Set(), queue=[], timer=null, failNext=false, job=0;
const parts=p=>p.split('/').filter(Boolean);
const join=(p,n)=>(p==='/'?'':p)+'/'+n;
const node=p=>parts(p).reduce((n,k)=>n.children[k],tree);
const bytes=n=>n<1024?n+' B':n<1048576?(n/1024).toFixed(1)+' KiB':(n/1048576).toFixed(1)+' MiB';
const say=s=>{$('message').textContent=s;};
function visible(){const q=$('filter').value.toLowerCase();return Object.entries(node(current).children).filter(([n])=>n.toLowerCase().includes(q)).sort(([a,x],[b,y])=>(x.kind===y.kind?0:x.kind==='folder'?-1:1)||a.localeCompare(b));}
function button(text,fn){const b=document.createElement('button');b.textContent=text;b.onclick=fn;return b;}
function openPath(p){current=p;selected.clear();$('filter').value='';render();}
function render(){
 $('path').replaceChildren(button('Agon SD',()=>openPath('/')));let path='';for(const name of parts(current)){path+='/'+name;const target=path;$('path').append(' / ',button(name,()=>openPath(target)));}
 $('up').disabled=current==='/';$('listing').replaceChildren();const entries=visible();
 for(const [name,n] of entries){const path=join(current,name),tr=document.createElement('tr');tr.className=selected.has(path)?'selected':'';const cell=document.createElement('td'),check=document.createElement('input');check.type='checkbox';check.checked=selected.has(path);check.setAttribute('aria-label','Select '+name);check.onchange=()=>{check.checked?selected.add(path):selected.delete(path);render();};cell.append(check);tr.append(cell);
 const label=document.createElement('td');if(n.kind==='folder')label.append(button('▸ '+name,()=>openPath(path)));else label.textContent=name;tr.append(label);
 const kind=document.createElement('td');kind.textContent=n.kind;tr.append(kind);const size=document.createElement('td');size.className='number';size.textContent=n.kind==='file'?bytes(n.size):'—';tr.append(size);$('listing').append(tr);}
 const all=entries.length>0&&entries.every(([n])=>selected.has(join(current,n)));$('all').textContent=all?'Deselect all':'Select all';$('all').disabled=!entries.length;
 $('selection').textContent=`${selected.size} selected`;$('download').disabled=!selected.size||$('service').value!=='ready';
 $('listing-note').textContent=`${entries.length} of ${Object.keys(node(current).children).length} entries shown. Select all applies to this filtered directory; selected folders include their contents.`;
}
function expand(p,n,items){if(n.kind==='folder'){items.push({path:p,kind:'folder',size:0});for(const [name,child]of Object.entries(n.children))expand(join(p,name),child,items);}else items.push({path:p,kind:'file',size:n.size});}
function enqueue(items,label){if($('service').value!=='ready'){say('Service unavailable. Nothing queued.');return;}const id=++job;queue.push(...items.map(i=>({...i,job:id,label,state:'queued',progress:0})));say(`${items.length} items queued. Simulation only.`);renderQueue();pump();}
function renderQueue(){const done=queue.filter(x=>x.state==='done').length;const counts={};for(const x of queue)counts[x.state]=(counts[x.state]||0)+1;
 $('queue-summary').textContent=queue.length?`${done}/${queue.length} complete · ${Object.entries(counts).filter(([k])=>k!=='done').map(([k,v])=>`${v} ${k}`).join(' · ')||'Finished'}${$('service').value!=='ready'?' · service '+$('service').value:''}`:'No transfers queued.';
 $('overall').value=queue.length?queue.reduce((s,x)=>s+x.progress,0)/queue.length:0;$('queue-list').replaceChildren();
 for(const x of queue){const li=document.createElement('li'),name=document.createElement('span'),status=document.createElement('span');name.textContent=`${x.label} · ${x.path}${x.kind==='folder'?' /':''}`;status.textContent=x.state==='running'?`${Math.round(x.progress)}%`:x.state;li.append(name,status);$('queue-list').append(li);}
 $('cancel').disabled=!queue.some(x=>['queued','running'].includes(x.state));$('retry').disabled=!queue.some(x=>['failed','cancelled'].includes(x.state))||$('service').value!=='ready';$('clear').disabled=!queue.some(x=>x.state==='done');
}
function pump(){if(timer||$('service').value!=='ready')return;const x=queue.find(x=>x.state==='queued');if(!x)return;x.state='running';renderQueue();timer=setInterval(()=>{if($('service').value!=='ready'){clearInterval(timer);timer=null;x.state='queued';renderQueue();return;}x.progress=Math.min(100,x.progress+(x.kind==='folder'?100:25));if(failNext){failNext=false;x.state='failed';x.progress=0;clearInterval(timer);timer=null;say('Simulated item failure. Other items continue; retry incomplete when ready.');}else if(x.progress===100){x.state='done';clearInterval(timer);timer=null;}renderQueue();if(!timer)pump();},140);}
$('up').onclick=()=>openPath('/'+parts(current).slice(0,-1).join('/'));
$('filter').oninput=()=>{selected.clear();render();};
$('all').onclick=()=>{const paths=visible().map(([n])=>join(current,n));const all=paths.every(p=>selected.has(p));for(const p of paths)all?selected.delete(p):selected.add(p);render();};
$('download').onclick=()=>{const items=[];for(const p of selected)expand(p,node(p),items);enqueue(items,'Download ZIP');};
$('upload').onclick=()=>$('files').click();$('folder').onclick=()=>$('folders').click();
function chosen(input,isFolder){const items=[],seen=new Set();for(const f of input.files){const relative=f.webkitRelativePath||f.name;const names=relative.split('/');for(let i=1;i<names.length;i++){const path=join(current,names.slice(0,i).join('/'));if(!seen.has(path)){seen.add(path);items.push({path,kind:'folder',size:0});}}items.push({path:join(current,relative),kind:'file',size:f.size});}enqueue(items,'Upload');if(isFolder)say('Simulated folder upload. File-picker metadata cannot describe empty folders; those require an additional mechanism. No file contents read.');input.value='';}
$('files').onchange=()=>chosen($('files'),false);$('folders').onchange=()=>chosen($('folders'),true);
$('cancel').onclick=()=>{clearInterval(timer);timer=null;for(const x of queue)if(['queued','running'].includes(x.state))x.state='cancelled';renderQueue();say('Remaining simulated work cancelled. Completed items retained.');};
$('retry').onclick=()=>{for(const x of queue)if(['failed','cancelled'].includes(x.state)){x.state='queued';x.progress=0;}renderQueue();pump();};
$('clear').onclick=()=>{queue=queue.filter(x=>x.state!=='done');renderQueue();};
$('service').onchange=()=>{render();renderQueue();pump();};$('fail').onclick=()=>{failNext=true;say('Next simulated item will fail once.');};
$('reset').onclick=()=>{clearInterval(timer);timer=null;queue=[];tree=seed();failNext=false;$('service').value='ready';openPath('/');renderQueue();say('Synthetic files reset.');};
$('mkdir').onclick=()=>{$('new-name').value='';$('new-folder').showModal();};
$('create-folder').onclick=e=>{const name=$('new-name').value.trim();if(!name||/[\\/]/.test(name)||name==='.'||name==='..'||node(current).children[name]){e.preventDefault();say('Choose a new single folder name.');return;}if($('service').value!=='ready'){e.preventDefault();say('Service unavailable.');return;}node(current).children[name]=dir({});render();say('Synthetic folder created.');};
render();renderQueue();
