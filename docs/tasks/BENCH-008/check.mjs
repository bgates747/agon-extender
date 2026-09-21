import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=process.argv[2];
const {DeltaFrameDecoder}=await import(process.argv[3]);
const decoder=new DeltaFrameDecoder();
const ab=b=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);
let deltas=0,full=0,firstDelta=null,periodicFull=0;
for(const row of fs.readFileSync(root+'/cases.tsv','utf8').trim().split('\n')){
 const [n,label,reset,kind]=row.split('\t');if(reset==='1')decoder.reset();
 const wire=ab(fs.readFileSync(`${root}/${n}.wire`));const frame=decoder.decode(wire);
 assert.deepEqual(Buffer.from(frame.pixels),fs.readFileSync(`${root}/${n}.pixels`));
 if(kind==='D'){deltas++;firstDelta??=wire;}else{full++;if(label==='periodic')periodicFull++;}
}
assert(periodicFull>0);assert.throws(()=>new DeltaFrameDecoder().decode(firstDelta));
const first=ab(fs.readFileSync(root+'/0.wire'));decoder.reset();decoder.decode(first);
const bad=firstDelta.slice(0);new DataView(bad).setUint32(28,777,true);
assert.throws(()=>decoder.decode(bad));assert.equal(decoder.reference,null);
decoder.decode(first);assert.throws(()=>decoder.decode(firstDelta.slice(0,-1)));assert.equal(decoder.reference,null);
console.log(JSON.stringify({exact_reconstructions:deltas+full,deltas,full,periodicFull,missing_reference_rejected:true,wrong_reference_rejected:true,truncation_rejected:true}));
