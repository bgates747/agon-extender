import fs from 'node:fs';import assert from 'node:assert/strict';
const text=fs.readFileSync(new URL('./web_decode.js',import.meta.url),'utf8');
const {unpackRLE2Frame}=await import('data:text/javascript;base64,'+Buffer.from(text).toString('base64'));
function frame(payload,n=3){const a=new Uint8Array(46+payload.length),v=new DataView(a.buffer);a.set(Buffer.from('EVR1'));a.set([1,32,2,1],4);v.setUint16(12,n,true);v.setUint16(14,1,true);v.setUint32(16,n,true);v.setUint32(20,n,true);a.set(Buffer.from('Cmpr'),32);v.setUint32(36,n,true);a.set(Buffer.from('RLE2'),40);a[44]=1;a.set(payload,46);return a;}
for(let c=0;c<64;c++){let a=frame([0,c|192]);let b=new Uint8Array(unpackRLE2Frame(a.buffer));assert.equal(Buffer.from(b.subarray(0,4)).toString(),'EVF1');assert.deepEqual([...b.subarray(32)],[c,c,c]);}
for(const a of [frame([0]),frame([127,192]),frame([0,192,192]),frame([128,128,128]),frame([0,0])])assert.throws(()=>unpackRLE2Frame(a.buffer));
let a=frame([0,192]);for(let n=4;n<a.length;n++)assert.throws(()=>unpackRLE2Frame(a.slice(0,n).buffer));
console.log('64 colours, malformed inputs and every truncated message: pass');
// Validate retained physical compressed frames using the actual browser decoder.
if(process.argv[2])for(const path of fs.readdirSync(process.argv[2]).filter(x=>x.endsWith('.frame'))){const file=fs.readFileSync(process.argv[2]+'/'+path);const input=file.buffer.slice(file.byteOffset,file.byteOffset+file.byteLength);const result=unpackRLE2Frame(input);assert.equal(Buffer.from(result).subarray(0,4).toString(),'EVF1');}
