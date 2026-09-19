// EVQ1 pair-RLE, reconstructing canonical EVF1 final RGB222 pixels.
function unpackPairFrame(buffer){
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<4)return buffer;
 const a=new Uint8Array(buffer),v=new DataView(buffer);
 if(String.fromCharCode(...a.subarray(0,4))!=="EVQ1")return buffer;
 const fail=()=>{throw new Error("Invalid EVQ1 pair-RLE frame");};
 if(a.length<33||a[4]!==1||a[5]!==32||a[6]!==2)fail();
 const w=v.getUint16(12,true),h=v.getUint16(14,true),n=v.getUint32(20,true);
 if(!w||!h||w>1024||h>768||n!==w*h||v.getUint32(16,true)!==w||a.length>32+n)fail();
 const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
 let i=32,p=32;const end=32+(n&~1);
 while(p<end){
  if(i+2>a.length)fail();const word=a[i]|(a[i+1]<<8);i+=2;
  const count=(word>>>12)+1,x=(word>>>6)&63,y=word&63;
  if(p+count*2>end)fail();
  for(let j=0;j<count;++j){out[p++]=x;out[p++]=y;}
 }
 if(n&1){if(i>=a.length||a[i]>63)fail();out[p++]=a[i++];}
 if(i!==a.length)fail();return out.buffer;
}
