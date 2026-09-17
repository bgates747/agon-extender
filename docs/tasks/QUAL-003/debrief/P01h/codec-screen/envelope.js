import {unpackRLE2Frame} from './web_decode.js';
export function header(buffer){
 const a=new Uint8Array(buffer),v=new DataView(buffer),fail=()=>{throw Error('Invalid EVC1 frame');};
 if(a.length<32||String.fromCharCode(...a.subarray(0,4))!=='EVC1'||a[4]!==1||a[5]!==32||a[6]>4||a[7]||v.getUint32(24,true)||v.getUint32(28,true))fail();
 const width=v.getUint16(12,true),height=v.getUint16(14,true),n=v.getUint32(16,true),size=v.getUint32(20,true);
 if(!width||!height||width>512||height>384||n!==width*height||size>2097152||a.length!==32+size)fail();
 return {a,v,kind:a[6],width,height,n,size};
}
export function normalize(h,pixels){if(pixels.length!==h.n)throw Error('Wrong pixel length');const b=new Uint8Array(32+h.n),v=new DataView(b.buffer);b.set([69,86,70,49,1,32,2,1]);v.setUint32(8,h.v.getUint32(8,true),true);v.setUint16(12,h.width,true);v.setUint16(14,h.height,true);v.setUint32(16,h.width,true);v.setUint32(20,h.n,true);v.setUint32(24,33333,true);b.set(pixels,32);return b.buffer;}
export function expand(h,payload){const b=new Uint8Array(32+payload.length),v=new DataView(b.buffer);b.set([69,86,82,49,1,32,2,1]);v.setUint16(12,h.width,true);v.setUint16(14,h.height,true);v.setUint32(16,h.width,true);v.setUint32(20,h.n,true);b.set(payload,32);return new Uint8Array(unpackRLE2Frame(b.buffer),32);}
export function simple(buffer){const start=performance.now(),h=header(buffer);let p=h.a.subarray(32);if(h.kind===1)p=expand(h,p);else if(h.kind!==0)throw Error('Not simple codec');if(p.some(x=>x>63))throw Error('Invalid palette index');return {buffer:normalize(h,p),metrics:{decodeMs:performance.now()-start}};}
