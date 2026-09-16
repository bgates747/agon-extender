// P01h clean-sheet RLE2 v1 decoder. Returns a standard EVF1 ArrayBuffer.
export function unpackRLE2Frame(buffer) {
 if (!(buffer instanceof ArrayBuffer) || buffer.byteLength<4) return buffer;
 const a=new Uint8Array(buffer),v=new DataView(buffer);
 if(String.fromCharCode(...a.subarray(0,4))!=="EVR1")return buffer;
 const fail=()=>{throw new Error("Invalid EVR1/RLE2 frame");};
 if(a.length<46||a[4]!==1||a[5]!==32||a[6]!==2)fail();
 const n=v.getUint32(20,true),w=v.getUint16(12,true),h=v.getUint16(14,true);
 if(!w||!h||n>196608||n!==w*h||v.getUint32(16,true)!==w)fail();
 if(String.fromCharCode(...a.subarray(32,36))!=="Cmpr"||v.getUint32(36,true)!==n||String.fromCharCode(...a.subarray(40,44))!=="RLE2"||a[44]!==1||a[45]!==0)fail();
 const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
 let i=46,o=32;
 while(i<a.length){const t=a[i++];if(t&128){if(!(t&64)||o===out.length)fail();out[o++]=t&63;}
 else{const count=t+3;if(i===a.length||count>out.length-o)fail();const p=a[i++];if((p&192)!==192)fail();out.fill(p&63,o,o+count);o+=count;}}
 if(o!==out.length)fail();return out.buffer;
}
