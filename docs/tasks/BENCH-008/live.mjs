import fs from 'node:fs';
import assert from 'node:assert/strict';
const [url,folder,moduleURL]=process.argv.slice(2);
const {DeltaFrameDecoder}=await import(moduleURL);
const socketURL=url.replace(/^http/,'ws')+'/video?rle2=1&delta=1';
async function connect(){const ws=new WebSocket(socketURL);ws.binaryType='arraybuffer';await new Promise((yes,no)=>{ws.addEventListener('open',yes,{once:true});ws.addEventListener('error',no,{once:true});});return ws;}
async function frame(ws){return await new Promise((yes,no)=>{const timer=setTimeout(()=>no(new Error('frame timeout')),10000);ws.addEventListener('message',ev=>{clearTimeout(timer);yes(ev.data);},{once:true});ws.send('frame');});}
let firstPixels;let deltas=0,full=0;const records=[];
let ws=await connect();const dec=new DeltaFrameDecoder();
for(let i=0;i<123;++i){
 const raw=await frame(ws),magic=String.fromCharCode(...new Uint8Array(raw,0,4));
 const f=dec.decode(raw);if(i===0){assert.notEqual(magic,'EVD1');firstPixels=Buffer.from(f.pixels);}
 assert.deepEqual(Buffer.from(f.pixels),firstPixels,'Static reconstruction changed');
 if(magic==='EVD1')deltas++;else full++;
 if(i<3||magic!=='EVD1')fs.writeFileSync(`${folder}/live-${i}.wire`,Buffer.from(raw));
 records.push({sequence:f.sequence,magic,bytes:raw.byteLength});
 await new Promise(r=>setTimeout(r,35));
}
assert(deltas>0);assert(full>=2,'Periodic full recovery absent');
const closed=new Promise(r=>ws.addEventListener('close',r,{once:true}));
const takeover=await connect();const raw=await frame(takeover);assert.notEqual(String.fromCharCode(...new Uint8Array(raw,0,4)),'EVD1');
assert.deepEqual(Buffer.from(new DeltaFrameDecoder().decode(raw).pixels),firstPixels);
await Promise.race([closed,new Promise((_,no)=>setTimeout(()=>no(new Error('old viewer not closed')),3000))]);
takeover.close();await new Promise(r=>setTimeout(r,200));
ws=await connect();const reconnect=await frame(ws);assert.notEqual(String.fromCharCode(...new Uint8Array(reconnect,0,4)),'EVD1');
assert.deepEqual(Buffer.from(new DeltaFrameDecoder().decode(reconnect).pixels),firstPixels);ws.close();
const result={frames:123,deltas,full,exact_static_reconstruction:true,takeover_first_full:true,reconnect_first_full:true,records};
fs.writeFileSync(folder+'/live.json',JSON.stringify(result,null,2));console.log(JSON.stringify({...result,records:undefined}));
