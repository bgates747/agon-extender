// EVP1 experimental final-colour palette packing. Produces canonical EVF1.
function unpackPackedFrame(buffer) {
 if (!(buffer instanceof ArrayBuffer) || buffer.byteLength<4)return buffer;
 const a=new Uint8Array(buffer),v=new DataView(buffer);
 if(String.fromCharCode(...a.subarray(0,4))!=="EVP1")return buffer;
 const fail=()=>{throw new Error("Invalid EVP1 packed frame");};
 if(a.length<38||a[4]!==1||a[5]!==32||a[6]!==2)fail();
 const n=v.getUint32(20,true),w=v.getUint16(12,true),h=v.getUint16(14,true);
 if(!w||!h||w>1024||h>768||n!==w*h||v.getUint32(16,true)!==w)fail();
 const bits=a[32],count=a[33];
 if(bits===6){
  if(count||a[34]||a[35]||a.length!==36+Math.ceil(n*6/8))fail();
  const unused=(8-(n*6)%8)%8;
  if(unused&&(a[a.length-1]&((1<<unused)-1)))fail();
  const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
  let p=0,j=36;
  for(;p+4<=n;p+=4,j+=3){const x=a[j],y=a[j+1],z=a[j+2];
   out[32+p]=x>>2;out[33+p]=((x&3)<<4)|(y>>4);
   out[34+p]=((y&15)<<2)|(z>>6);out[35+p]=z&63;}
  for(;p<n;++p){const bit=p*6,k=36+(bit>>3),shift=bit&7;
   out[32+p]=(((a[k]<<8)|(a[k+1]||0))>>(10-shift))&63;}
  return out.buffer;
 }

 if(![1,2,4].includes(bits)||!count||count>(1<<bits)||a[34]||a[35])fail();
 const start=36+count,bytes=Math.ceil(n*bits/8);
 if(a.length!==start+bytes)fail();
 const seen=new Set();for(let i=36;i<start;++i){if(a[i]>63||seen.has(a[i]))fail();seen.add(a[i]);}
 const unused=(8-(n*bits)%8)%8;if(unused&&(a[a.length-1]&((1<<unused)-1)))fail();
 const out=new Uint8Array(32+n);out.set(a.subarray(0,32));out[2]=70;
 const mask=(1<<bits)-1;
 for(let p=0;p<n;++p){const bit=p*bits,index=(a[start+(bit>>3)]>>(8-bits-(bit&7)))&mask;
  if(index>=count)fail();out[32+p]=a[36+index];}
 return out.buffer;
}
