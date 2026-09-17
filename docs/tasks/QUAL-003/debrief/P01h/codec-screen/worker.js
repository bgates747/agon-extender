import createSzip from './szip.js';
import {header,normalize,expand} from './envelope.js';
let modulePromise;
self.onmessage=async e=>{
 const {id,buffer,verify}=e.data;
 try {
  const h=header(buffer),start=performance.now();let result;
  if(h.kind===4){
   const png=h.a.subarray(32),pv=new DataView(png.buffer,png.byteOffset,png.byteLength);
   if(png.length<33||png[0]!==137||String.fromCharCode(...png.subarray(1,4))!=='PNG'||pv.getUint32(8)!==13||String.fromCharCode(...png.subarray(12,16))!=='IHDR'||pv.getUint32(16)!==h.width||pv.getUint32(20)!==h.height||png[24]!==8||png[25]!==3)throw Error('Invalid PNG header');
   const bitmap=await createImageBitmap(new Blob([h.a.subarray(32)],{type:'image/png'}),{premultiplyAlpha:'none',colorSpaceConversion:'none'});
   if(bitmap.width!==h.width||bitmap.height!==h.height){bitmap.close();throw Error('PNG geometry mismatch');}
   const decodeMs=performance.now()-start;let pixels;
   if(verify){const c=new OffscreenCanvas(h.width,h.height),ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(bitmap,0,0);const rgba=ctx.getImageData(0,0,h.width,h.height).data;pixels=new Uint8Array(h.n);
    for(let i=0;i<h.n;i++){let j=i*4;if(rgba[j]%85||rgba[j+1]%85||rgba[j+2]%85||rgba[j+3]!==255)throw Error('PNG changed palette');pixels[i]=rgba[j]/85|(rgba[j+1]/85)<<2|(rgba[j+2]/85)<<4;}}
   result={bitmap,pixels,metrics:{decodeMs,verificationMs:performance.now()-start-decodeMs}};
  }else{
   if(h.kind!==2&&h.kind!==3)throw Error('Wrong worker codec');const m=await(modulePromise??=createSzip());let input=0,output=0,count=0;
   try{
    const p=h.a.subarray(32);if(p.length<14||String.fromCharCode(...p.subarray(0,4))!=='CmpS')throw Error('Invalid CmpS');
    const n=new DataView(p.buffer,p.byteOffset,p.byteLength).getUint32(4,true);if(n!==(h.kind===2?h.n:n)||n>196622||!n)throw Error('Invalid decoded size');
    input=m._malloc(p.length);output=m._malloc(n);count=m._malloc(4);if(!input||!output||!count)throw Error('Allocation failed');m.HEAPU8.set(p,input);
    const t=performance.now(),status=m._p4_szip(1,input,p.length,output,n,count),szipMs=performance.now()-t;if(status||m.HEAPU32[count>>>2]!==n)throw Error('Szip rejected '+status);
    let pixels=m.HEAPU8.slice(output,output+n);const t2=performance.now();if(h.kind===3)pixels=expand(h,pixels);if(pixels.length!==h.n||pixels.some(x=>x>63))throw Error('Invalid pixel output');
    result={buffer:normalize(h,pixels),metrics:{decodeMs:performance.now()-start,szipMs,expandMs:performance.now()-t2,wasmBytes:m.HEAPU8.length}};
   }finally{if(input)m._free(input);if(output)m._free(output);if(count)m._free(count);}
  }
  self.postMessage({id,...result},result.bitmap?[result.bitmap]:[result.buffer]);
 }catch(error){self.postMessage({id,error:String(error.message||error)});}
};
