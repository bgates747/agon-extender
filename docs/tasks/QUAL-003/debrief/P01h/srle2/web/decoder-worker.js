import createSzip from './szip.js';
import {unpackRLE2Frame} from './web_decode.js';
let modulePromise;
export async function decodeSRLE2(buffer) {
 const start=performance.now(),a=new Uint8Array(buffer),v=new DataView(buffer);
 const fail=()=>{throw new Error('Invalid EVS1/SRLE2 frame');};
 if(a.length<54 || String.fromCharCode(...a.slice(0,4))!=='EVS1'||a[4]!==1||a[5]!==40||a[6]!==2||(a[7]&~3)||!(a[7]&1)||v.getUint32(28,true)!==0)fail();
 const w=v.getUint16(12,true),h=v.getUint16(14,true),n=v.getUint32(20,true),enc=v.getUint32(32,true),mid=v.getUint32(36,true);
 if(!w||!h||w>512||h>384||n!==w*h||n>196608||v.getUint32(16,true)!==w||enc<14||enc>2097152||a.length!==40+enc||mid<14||mid>196622)fail();
 if(String.fromCharCode(...a.slice(40,44))!=='CmpS'||v.getUint32(44,true)!==mid)fail();
 const m=await (modulePromise??=createSzip());
 let input=0,output=0,count=0;
 try {
  input=m._malloc(enc);output=m._malloc(mid);count=m._malloc(4);
  if(!input||!output||!count)throw new Error('Decoder allocation failed');
  m.HEAPU8.set(a.subarray(40),input);const t=performance.now();
  const status=m._p4_szip(1,input,enc,output,mid,count);const szipMs=performance.now()-t;
  if(status!==0||m.HEAPU32[count>>>2]!==mid)throw new Error(`Szip decode failed (${status})`);
  const intermediate=m.HEAPU8.slice(output,output+mid);
  const rle=new Uint8Array(32+mid);rle.set(a.subarray(0,32));rle[2]=82;rle[5]=32;rle.set(intermediate,32);
  const r=performance.now(),result=unpackRLE2Frame(rle.buffer),rleMs=performance.now()-r;
  return {buffer:result,metrics:{szipMs,rleMs,totalMs:performance.now()-start,wasmMemoryBytes:m.HEAPU8.length,encodedBytes:enc}};
 }finally{if(input)m._free(input);if(output)m._free(output);if(count)m._free(count);}
}
self.onmessage=async e=>{
 const {id,buffer}=e.data;
 try {const result=await decodeSRLE2(buffer);self.postMessage({id,...result},[result.buffer]);}
 catch(error){self.postMessage({id,error:String(error.message||error)});}
};
